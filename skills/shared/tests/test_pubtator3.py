"""Tests for skills/shared/scripts/pubtator3.py — fixture-based, no live HTTP."""

from __future__ import annotations

import io
import json
import sys
from contextlib import redirect_stdout, redirect_stderr
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

# Make the wrapper importable.
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

import pubtator3 as pt  # noqa: E402

FIXTURES = Path(__file__).parent / "fixtures" / "pubtator3"


def _load(name: str):
    return json.loads((FIXTURES / name).read_text())


# ---------------------------------------------------------- fixture sanity


class TestFixtures:
    def test_autocomplete_shape(self):
        data = _load("autocomplete_braf.json")
        assert isinstance(data, list) and data
        assert {"_id", "biotype", "db_id", "db", "name"} <= set(data[0])

    def test_search_shape(self):
        data = _load("search_with_pagination.json")
        assert {"results", "count", "current", "page_size", "total_pages"} <= set(data)
        assert isinstance(data["results"], list) and data["results"]
        assert {"pmid", "title"} <= set(data["results"][0])

    def test_annotations_shape(self):
        data = _load("annotations_24200969.json")
        assert "PubTator3" in data and isinstance(data["PubTator3"], list)
        doc = data["PubTator3"][0]
        assert "passages" in doc
        any_ann = any(p.get("annotations") for p in doc["passages"])
        assert any_ann, "expected at least one annotation in fixture"

    def test_relations_shape(self):
        data = _load("relations_braf.json")
        assert isinstance(data, list) and data
        assert {"type", "source", "target", "publications"} <= set(data[0])


# ---------------------------------------------------------- query composition


class TestComposeSearchText:
    def test_bare_symbols_get_tagged(self):
        q = pt.compose_search_text(None, ["BRAF"], ["Melanoma"], None, None, None)
        assert q == "@GENE_BRAF AND @DISEASE_Melanoma"

    def test_pre_tagged_pass_through(self):
        q = pt.compose_search_text(None, ["@GENE_BRAF"], None, None, None, None)
        assert q == "@GENE_BRAF"

    def test_text_appended(self):
        q = pt.compose_search_text("resistance", ["BRAF"], None, None, None, None)
        assert q == "@GENE_BRAF AND resistance"

    def test_multiple_per_type(self):
        q = pt.compose_search_text(None, ["BRAF", "MAP2K7"], None, ["vemurafenib"], None, None)
        assert q == "@GENE_BRAF AND @GENE_MAP2K7 AND @CHEMICAL_vemurafenib"

    def test_empty_raises(self):
        with pytest.raises(ValueError):
            pt.compose_search_text(None, None, None, None, None, None)


# ---------------------------------------------------------- summarizers


class TestSummarizers:
    def test_summarize_search_extracts_meta_and_hits(self):
        out = pt.summarize_search(_load("search_with_pagination.json"))
        assert out["total"] > 0
        assert out["page"] == 1
        assert out["page_size"] >= 1
        assert len(out["hits"]) >= 1
        h = out["hits"][0]
        assert {"pmid", "title", "doi", "year", "score"} == set(h)

    def test_summarize_annotations_tallies_entities(self):
        out = pt.summarize_annotations(_load("annotations_24200969.json"))
        assert len(out) == 1
        rec = out[0]
        assert rec["pmid"] == 24200969
        counts = rec["entity_counts"]
        assert "@GENE_BRAF" in counts.get("gene", {})
        assert "@DISEASE_Melanoma" in counts.get("disease", {})
        assert counts["gene"]["@GENE_BRAF"] >= 1

    def test_summarize_annotations_handles_empty_doc(self):
        empty = {"PubTator3": [{"pmid": 99, "id": "99", "passages": []}]}
        out = pt.summarize_annotations(empty)
        assert out == [{"pmid": 99, "id": "99", "entity_counts": {}}]

    def test_summarize_relations_groups_by_type_and_caps(self):
        out = pt.summarize_relations(_load("relations_braf.json"), top=3)
        assert out["total_relations"] > 0
        assert "associate" in out["by_type"]
        for rels in out["by_type"].values():
            assert len(rels) <= 3
        assoc = out["by_type"]["associate"]
        # sorted by publications desc
        pubs = [r["publications"] for r in assoc]
        assert pubs == sorted(pubs, reverse=True)


# ---------------------------------------------------------- HTTP client behavior


def _mock_response(status: int, payload, headers: dict | None = None):
    resp = MagicMock()
    resp.status_code = status
    resp.ok = 200 <= status < 300
    resp.text = json.dumps(payload) if not isinstance(payload, str) else payload
    resp.json.return_value = payload if not isinstance(payload, str) else None
    resp.headers = headers or {}
    return resp


class TestClient:
    def test_session_headers_set(self):
        client = pt.PubTator3Client()
        assert client._session.headers["User-Agent"] == pt.USER_AGENT
        assert client._session.headers["Accept"] == "application/json"

    def test_get_returns_json_on_200(self):
        client = pt.PubTator3Client()
        with patch.object(client._session, "get", return_value=_mock_response(200, {"ok": True})):
            assert client._get("/x") == {"ok": True}

    def test_get_raises_on_4xx(self):
        client = pt.PubTator3Client()
        with patch.object(client._session, "get", return_value=_mock_response(400, "bad")):
            with pytest.raises(pt.PubTator3Error) as exc:
                client._get("/x")
        assert exc.value.status_code == 400

    def test_429_retries_and_succeeds(self):
        client = pt.PubTator3Client()
        responses = [
            _mock_response(429, "slow", headers={"Retry-After": "0"}),
            _mock_response(200, {"ok": True}),
        ]
        with patch.object(client._session, "get", side_effect=responses):
            with patch("pubtator3.time.sleep"):  # don't actually wait
                assert client._get("/x") == {"ok": True}

    def test_5xx_retries(self):
        client = pt.PubTator3Client()
        responses = [
            _mock_response(503, "down"),
            _mock_response(200, {"ok": True}),
        ]
        with patch.object(client._session, "get", side_effect=responses):
            with patch("pubtator3.time.sleep"):
                assert client._get("/x") == {"ok": True}

    def test_throttle_sleeps_when_calls_close(self):
        client = pt.PubTator3Client()
        client._last_call = 9e18  # force "we just called"
        with patch("pubtator3.time.sleep") as sleep:
            with patch("pubtator3.time.monotonic", side_effect=[9e18, 9e18]):
                client._throttle()
        # any sleep call satisfies — exact value depends on monotonic mock
        assert sleep.called

    def test_autocomplete_uses_correct_path(self):
        client = pt.PubTator3Client()
        with patch.object(client, "_get", return_value=[]) as g:
            client.autocomplete("BRAF", concept="gene", limit=5)
        g.assert_called_once_with("/entity/autocomplete/", {"query": "BRAF", "limit": 5, "concept": "gene"})

    def test_search_uses_correct_path(self):
        client = pt.PubTator3Client()
        with patch.object(client, "_get", return_value={}) as g:
            client.search("@GENE_BRAF", size=3, page=2)
        g.assert_called_once_with("/search/", {"text": "@GENE_BRAF", "size": 3, "page": 2})

    def test_annotations_joins_pmids(self):
        client = pt.PubTator3Client()
        with patch.object(client, "_get", return_value={}) as g:
            client.annotations([1, 2, "3"], full=True)
        g.assert_called_once_with(
            "/publications/export/biocjson", {"pmids": "1,2,3", "full": "true"}
        )

    def test_relations_omits_type_when_none(self):
        client = pt.PubTator3Client()
        with patch.object(client, "_get", return_value=[]) as g:
            client.relations("@GENE_BRAF")
        g.assert_called_once_with("/relations", {"e1": "@GENE_BRAF"})


# ---------------------------------------------------------- CLI argv contract


class TestCLI:
    def _run(self, argv: list[str], fixture: str | None = None, mock_payload=None) -> tuple[int, str, str]:
        out, err = io.StringIO(), io.StringIO()
        payload = _load(fixture) if fixture else mock_payload
        with patch.object(pt.PubTator3Client, "_get", return_value=payload):
            with redirect_stdout(out), redirect_stderr(err):
                code = pt.main(argv)
        return code, out.getvalue(), err.getvalue()

    def test_autocomplete_prints_json(self):
        code, out, err = self._run(["autocomplete", "BRAF"], fixture="autocomplete_braf.json")
        assert code == 0
        parsed = json.loads(out)
        assert parsed[0]["_id"] == "@GENE_BRAF"

    def test_autocomplete_rejects_bad_concept(self):
        # argparse rejects before client; exits via SystemExit
        with pytest.raises(SystemExit):
            pt.main(["autocomplete", "BRAF", "--concept", "nonsense"])

    def test_search_summary_prints_compact(self):
        code, out, err = self._run(
            ["search", "--gene", "BRAF", "--summary"],
            fixture="search_with_pagination.json",
        )
        assert code == 0
        parsed = json.loads(out)
        assert "hits" in parsed and "total" in parsed

    def test_search_requires_at_least_one_entity(self):
        code, out, err = self._run(["search"], mock_payload={})
        assert code == 1
        assert "search requires" in err

    def test_annotations_summary_prints_tally(self):
        code, out, err = self._run(
            ["annotations", "--pmids", "24200969", "--summary"],
            fixture="annotations_24200969.json",
        )
        assert code == 0
        parsed = json.loads(out)
        assert parsed[0]["pmid"] == 24200969
        assert "@GENE_BRAF" in parsed[0]["entity_counts"]["gene"]

    def test_relations_summary_prints(self):
        code, out, err = self._run(
            ["relations", "--entity", "@GENE_BRAF", "--summary"],
            fixture="relations_braf.json",
        )
        assert code == 0
        parsed = json.loads(out)
        assert "by_type" in parsed

    def test_remote_error_returns_exit_2(self):
        with patch.object(pt.PubTator3Client, "_get", side_effect=pt.PubTator3Error(500, "down")):
            err = io.StringIO()
            with redirect_stderr(err):
                code = pt.main(["autocomplete", "BRAF"])
        assert code == 2
        assert "PubTator3 500" in err.getvalue()
