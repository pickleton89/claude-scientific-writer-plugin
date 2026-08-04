"""Tests for the JSON-spec translator and patch helpers."""

from __future__ import annotations

import copy
import json
import sys
from pathlib import Path

import pytest

_SCRIPTS = Path(__file__).resolve().parent.parent / "scripts"
sys.path.insert(0, str(_SCRIPTS))

from spec_patch import JsonPatchError, apply_patch  # noqa: E402
from spec_translator import load_schema, translate_spec  # noqa: E402

_EXAMPLE_PATH = (
    Path(__file__).resolve().parent.parent
    / "references"
    / "examples"
    / "spec_egfr_inhibition.json"
)


@pytest.fixture
def example_spec() -> dict:
    return json.loads(_EXAMPLE_PATH.read_text(encoding="utf-8"))


class TestSchema:
    def test_example_validates(self, example_spec: dict):
        import jsonschema

        jsonschema.validate(instance=example_spec, schema=load_schema())

    def test_unknown_top_level_key_rejected(self, example_spec: dict):
        import jsonschema

        bad = copy.deepcopy(example_spec)
        bad["scientific_figure"]["bogus"] = 1
        with pytest.raises(jsonschema.ValidationError):
            jsonschema.validate(instance=bad, schema=load_schema())

    def test_invalid_component_id_rejected(self, example_spec: dict):
        import jsonschema

        bad = copy.deepcopy(example_spec)
        bad["scientific_figure"]["components"][0]["id"] = "Bad-ID"
        with pytest.raises(jsonschema.ValidationError):
            jsonschema.validate(instance=bad, schema=load_schema())

    def test_invalid_color_rejected(self, example_spec: dict):
        import jsonschema

        bad = copy.deepcopy(example_spec)
        bad["scientific_figure"]["brand"]["primary_color"] = "blue"
        with pytest.raises(jsonschema.ValidationError):
            jsonschema.validate(instance=bad, schema=load_schema())


class TestTranslator:
    def test_returns_two_strings(self, example_spec: dict):
        ctx, intent = translate_spec(example_spec)
        assert isinstance(ctx, str) and ctx.strip()
        assert isinstance(intent, str) and intent.strip()

    def test_determinism(self, example_spec: dict):
        a = translate_spec(example_spec)
        b = translate_spec(copy.deepcopy(example_spec))
        assert a == b

    def test_components_sorted_by_id(self, example_spec: dict):
        ctx, _ = translate_spec(example_spec)
        ids_in_order = [
            c["id"]
            for c in sorted(
                example_spec["scientific_figure"]["components"], key=lambda c: c["id"]
            )
        ]
        labels_in_order = [
            next(
                c["label"]
                for c in example_spec["scientific_figure"]["components"]
                if c["id"] == cid
            )
            for cid in ids_in_order
        ]
        positions = [ctx.find(label) for label in labels_in_order]
        assert all(p >= 0 for p in positions)
        assert positions == sorted(positions)

    def test_key_message_in_intent(self, example_spec: dict):
        _, intent = translate_spec(example_spec)
        assert example_spec["scientific_figure"]["narrative"]["key_message"] in intent

    def test_oligon_brand_phrase(self, example_spec: dict):
        _, intent = translate_spec(example_spec)
        assert "Oligon" in intent

    def test_relationship_renders(self, example_spec: dict):
        ctx, _ = translate_spec(example_spec)
        assert "Erlotinib" in ctx and "EGFR kinase domain" in ctx
        assert "binds" in ctx

    def test_graphical_abstract_budget_hint_present(self, example_spec: dict):
        assert (
            example_spec["scientific_figure"]["meta"]["doc_type"]
            == "graphical_abstract"
        ), "fixture precondition: the worked example is a graphical abstract"
        _, intent = translate_spec(example_spec)
        assert "Graphical-abstract budgets" in intent
        assert "thumbnail" in intent
        assert "provisional/uncalibrated" in intent

    def test_budget_hint_absent_for_other_doc_types(self, example_spec: dict):
        other = copy.deepcopy(example_spec)
        other["scientific_figure"]["meta"]["doc_type"] = "methodology"
        _, intent = translate_spec(other)
        assert "Graphical-abstract budgets" not in intent
        assert "thumbnail" not in intent
        assert intent == intent.strip(), "an empty hint must not leave trailing space"

    def test_budget_hint_is_appended_not_reordered(self, example_spec: dict):
        """The hint is the 5th part: the first four render byte-identically."""
        _, ga_intent = translate_spec(example_spec)
        other = copy.deepcopy(example_spec)
        other["scientific_figure"]["meta"]["doc_type"] = "methodology"
        _, base_intent = translate_spec(other)

        assert ga_intent.startswith(base_intent + " "), (
            "hint must be appended, not inserted"
        )
        assert ga_intent.startswith(
            example_spec["scientific_figure"]["narrative"]["key_message"]
        ), "key_message must remain the first element of intent_parts"

    def test_budget_hint_is_deterministic(self, example_spec: dict):
        a = translate_spec(example_spec)
        b = translate_spec(copy.deepcopy(example_spec))
        assert a == b

    def test_missing_meta_renders_without_hint(self, example_spec: dict):
        """validate=False specs may omit meta entirely; that must not raise."""
        bare = copy.deepcopy(example_spec)
        del bare["scientific_figure"]["meta"]
        _, intent = translate_spec(bare, validate=False)
        assert "Graphical-abstract budgets" not in intent
        assert intent.strip()

    def test_validation_off_skips_jsonschema(self, example_spec: dict):
        bad = copy.deepcopy(example_spec)
        bad["scientific_figure"]["meta"]["doc_type"] = "not_in_enum"
        with pytest.raises(Exception):
            translate_spec(bad, validate=True)
        ctx, intent = translate_spec(bad, validate=False)
        assert ctx and intent


class TestPatch:
    def test_empty_patch_is_identity(self, example_spec: dict):
        result = apply_patch(example_spec, [])
        assert result == example_spec
        assert result is not example_spec

    def test_does_not_mutate_input(self, example_spec: dict):
        before = copy.deepcopy(example_spec)
        apply_patch(
            example_spec,
            [
                {
                    "op": "replace",
                    "path": "/scientific_figure/style/aesthetic",
                    "value": "infographic",
                }
            ],
        )
        assert example_spec == before

    def test_replace(self, example_spec: dict):
        result = apply_patch(
            example_spec,
            [
                {
                    "op": "replace",
                    "path": "/scientific_figure/style/aesthetic",
                    "value": "infographic",
                }
            ],
        )
        assert result["scientific_figure"]["style"]["aesthetic"] == "infographic"

    def test_add_to_array(self, example_spec: dict):
        new_comp = {"id": "node_extra", "label": "Extra node", "role": "concept"}
        result = apply_patch(
            example_spec,
            [
                {
                    "op": "add",
                    "path": "/scientific_figure/components/-",
                    "value": new_comp,
                }
            ],
        )
        ids = [c["id"] for c in result["scientific_figure"]["components"]]
        assert "node_extra" in ids
        assert len(result["scientific_figure"]["components"]) == (
            len(example_spec["scientific_figure"]["components"]) + 1
        )

    def test_remove(self, example_spec: dict):
        result = apply_patch(
            example_spec,
            [{"op": "remove", "path": "/scientific_figure/relationships/0"}],
        )
        assert len(result["scientific_figure"]["relationships"]) == (
            len(example_spec["scientific_figure"]["relationships"]) - 1
        )

    def test_unsupported_op_rejected(self, example_spec: dict):
        with pytest.raises(JsonPatchError):
            apply_patch(example_spec, [{"op": "move", "path": "/x", "from": "/y"}])

    def test_invalid_path_rejected(self, example_spec: dict):
        with pytest.raises(JsonPatchError):
            apply_patch(
                example_spec,
                [{"op": "replace", "path": "no-leading-slash", "value": 1}],
            )


class TestPatchTranslateIntegration:
    """The whole point: scoped patches produce scoped prose changes."""

    def test_aesthetic_only_patch_changes_intent_not_components(
        self, example_spec: dict
    ):
        ctx_v1, intent_v1 = translate_spec(example_spec)
        patched = apply_patch(
            example_spec,
            [
                {
                    "op": "replace",
                    "path": "/scientific_figure/style/aesthetic",
                    "value": "infographic",
                }
            ],
        )
        ctx_v2, intent_v2 = translate_spec(patched)

        assert ctx_v1 == ctx_v2, "aesthetic patch must not touch source_context"
        assert intent_v1 != intent_v2
        assert "infographic" in intent_v2 and "infographic" not in intent_v1

    def test_brand_color_patch_changes_intent_not_components(self, example_spec: dict):
        ctx_v1, intent_v1 = translate_spec(example_spec)
        patched = apply_patch(
            example_spec,
            [
                {
                    "op": "add",
                    "path": "/scientific_figure/brand/primary_color",
                    "value": "#A03DDC",
                }
            ],
        )
        ctx_v2, intent_v2 = translate_spec(patched)

        assert ctx_v1 == ctx_v2
        assert "#A03DDC" in intent_v2
        assert "#A03DDC" not in intent_v1

    def test_doc_type_patch_changes_intent_not_components(self, example_spec: dict):
        """Sibling of the aesthetic/brand cases: meta.doc_type is intent-scoped."""
        ctx_v1, intent_v1 = translate_spec(example_spec)
        patched = apply_patch(
            example_spec,
            [
                {
                    "op": "replace",
                    "path": "/scientific_figure/meta/doc_type",
                    "value": "methodology",
                }
            ],
        )
        ctx_v2, intent_v2 = translate_spec(patched)

        assert ctx_v1 == ctx_v2, "doc_type patch must not touch source_context"
        assert intent_v1 != intent_v2
        assert "Graphical-abstract budgets" in intent_v1
        assert "Graphical-abstract budgets" not in intent_v2

    def test_doc_type_patch_to_graphical_abstract_adds_budget_hint(
        self, example_spec: dict
    ):
        """The reverse direction: a spec re-declared as a GA gains the budgets."""
        methodology = copy.deepcopy(example_spec)
        methodology["scientific_figure"]["meta"]["doc_type"] = "methodology"
        ctx_v1, intent_v1 = translate_spec(methodology)
        patched = apply_patch(
            methodology,
            [
                {
                    "op": "replace",
                    "path": "/scientific_figure/meta/doc_type",
                    "value": "graphical_abstract",
                }
            ],
        )
        ctx_v2, intent_v2 = translate_spec(patched)

        assert ctx_v1 == ctx_v2
        assert "Graphical-abstract budgets" not in intent_v1
        assert intent_v2.startswith(intent_v1 + " ")
        assert "#A03DDC" not in intent_v1
