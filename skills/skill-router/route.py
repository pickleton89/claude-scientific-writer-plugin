#!/usr/bin/env python3
"""
Deterministic Skill Router for Claude Scientific Writer Plugin

This module provides first-pass deterministic routing based on keyword matching
and regex triggers, reducing reliance on LLM interpretation for clear-cut cases.

Usage:
    from skills.skill_router.route import route_request, RoutingDecision

    result = route_request("Create a bar chart of my experimental results")
    print(result.primary_skill)  # "plotting-libraries"
    print(result.confidence)     # 0.85
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from html import escape as html_escape
from pathlib import Path
from typing import Optional

import yaml


@dataclass
class RoutingDecision:
    """Result of skill routing analysis."""

    primary_skill: str
    supporting_skills: list[str] = field(default_factory=list)
    confidence: float = 0.0
    requires_clarification: bool = False
    clarification_questions: Optional[list[str]] = None
    matched_keywords: list[str] = field(default_factory=list)
    matched_triggers: list[str] = field(default_factory=list)
    category: Optional[str] = None
    rationale: str = ""

    def to_xml(self) -> str:
        """Format as XML for structured output."""
        supporting = "\n".join(
            f"    <skill>{html_escape(s)}</skill>" for s in self.supporting_skills
        )
        return f"""<routing_decision>
  <primary_skill>{html_escape(self.primary_skill)}</primary_skill>
  <supporting_skills>
{supporting}
  </supporting_skills>
  <confidence>{self.confidence:.2f}</confidence>
  <requires_clarification>{str(self.requires_clarification).lower()}</requires_clarification>
  <rationale>{html_escape(self.rationale)}</rationale>
</routing_decision>"""

    def to_dict(self) -> dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "primary_skill": self.primary_skill,
            "supporting_skills": self.supporting_skills,
            "confidence": round(self.confidence, 3),
            "requires_clarification": self.requires_clarification,
            "clarification_questions": self.clarification_questions,
            "matched_keywords": self.matched_keywords,
            "matched_triggers": self.matched_triggers,
            "category": self.category,
            "rationale": self.rationale,
        }


class SkillRouter:
    """Deterministic skill router using keyword matching and regex triggers."""

    def __init__(self, triggers_path: Optional[Path] = None):
        """Initialize router with skill triggers configuration.

        Args:
            triggers_path: Path to skill_triggers.yaml. If None, uses default location.
        """
        if triggers_path is None:
            triggers_path = Path(__file__).parent / "skill_triggers.yaml"

        with open(triggers_path, encoding="utf-8") as f:
            config = yaml.safe_load(f)

        self.skills = config.get("skills", {})
        self.routing_config = config.get("routing_config", {})

        # Extract thresholds
        self.high_threshold = self.routing_config.get("high_confidence_threshold", 0.7)
        self.low_threshold = self.routing_config.get("low_confidence_threshold", 0.3)
        self.trigger_boost = self.routing_config.get("trigger_boost", 0.2)
        self.max_trigger_boost = self.routing_config.get("max_trigger_boost", 0.4)
        self.category_defaults = self.routing_config.get("category_defaults", {})

    def _normalize_text(self, text: str) -> str:
        """Normalize text for matching."""
        # Lowercase and remove extra whitespace
        text = text.lower().strip()
        text = re.sub(r"\s+", " ", text)
        return text

    def _tokenize(self, text: str) -> set[str]:
        """Extract tokens and n-grams from text."""
        text = self._normalize_text(text)

        # Single words
        words = set(re.findall(r"\b\w+\b", text))

        # Bigrams (for multi-word keywords like "bar chart")
        word_list = re.findall(r"\b\w+\b", text)
        bigrams = {f"{word_list[i]} {word_list[i+1]}"
                   for i in range(len(word_list) - 1)}

        # Trigrams
        trigrams = {f"{word_list[i]} {word_list[i+1]} {word_list[i+2]}"
                    for i in range(len(word_list) - 2)}

        return words | bigrams | trigrams

    def _score_skill(
        self,
        skill_config: dict,
        request: str,
        tokens: set[str]
    ) -> tuple[float, list[str], list[str]]:
        """Calculate confidence score for a skill.

        Scoring logic:
        - 1 keyword match = 0.35 base
        - 2 keyword matches = 0.55 base
        - 3+ keyword matches = 0.65 base
        - Each trigger match adds trigger_boost (default 0.2, configurable)
        - Trigger boost capped at max_trigger_boost (default 0.4, configurable)
        - Total capped at 1.0

        Returns:
            Tuple of (score, matched_keywords, matched_triggers)
        """
        keywords = [kw.lower() for kw in skill_config.get("keywords", [])]
        triggers = skill_config.get("triggers", [])
        negative_keywords = [nk.lower() for nk in skill_config.get("negative_keywords", [])]

        # Check negative keywords first - strong signal to exclude
        for neg_kw in negative_keywords:
            if neg_kw in tokens:
                return (0.0, [], [])

        # Count keyword matches
        matched_keywords = []
        for kw in keywords:
            if kw in tokens or kw in request.lower():
                matched_keywords.append(kw)

        # Base score from keyword count (not percentage)
        # This rewards matching ANY keywords rather than penalizing large keyword lists
        num_matches = len(matched_keywords)
        if num_matches == 0:
            keyword_score = 0.0
        elif num_matches == 1:
            keyword_score = 0.35
        elif num_matches == 2:
            keyword_score = 0.55
        elif num_matches == 3:
            keyword_score = 0.65
        else:
            # 4+ matches: scale up but cap at 0.8 to leave room for triggers
            keyword_score = min(0.65 + (num_matches - 3) * 0.05, 0.8)

        # Check trigger patterns (regex) - strong signal
        matched_triggers = []
        request_lower = request.lower()
        for pattern in triggers:
            try:
                if re.search(pattern, request_lower):
                    matched_triggers.append(pattern)
            except re.error:
                continue  # Skip invalid patterns

        # Trigger boost - each trigger match is a strong signal
        trigger_score = min(
            len(matched_triggers) * self.trigger_boost,
            self.max_trigger_boost,
        )

        # Combined score
        total_score = min(keyword_score + trigger_score, 1.0)

        return (total_score, matched_keywords, matched_triggers)

    def route(self, request: str) -> RoutingDecision:
        """Route a request to the appropriate skill(s).

        Args:
            request: Natural language request from user

        Returns:
            RoutingDecision with primary skill, confidence, and metadata
        """
        if not request or not request.strip():
            return RoutingDecision(
                primary_skill="scientific-writing",
                confidence=0.0,
                requires_clarification=True,
                clarification_questions=["What would you like to create or do?"],
                rationale="Empty request"
            )

        request_normalized = self._normalize_text(request)
        tokens = self._tokenize(request)

        # Score all skills
        scores: dict[str, tuple[float, list[str], list[str]]] = {}
        categories: dict[str, str] = {}

        for skill_name, skill_config in self.skills.items():
            score, matched_kw, matched_tr = self._score_skill(
                skill_config, request_normalized, tokens
            )
            if score > 0:
                scores[skill_name] = (score, matched_kw, matched_tr)
                categories[skill_name] = skill_config.get("category", "unknown")

        if not scores:
            # No matches - use category detection for fallback
            category = self._detect_category(tokens)
            default_skill = self.category_defaults.get(category, "scientific-writing")
            return RoutingDecision(
                primary_skill=default_skill,
                confidence=0.1,
                requires_clarification=True,
                clarification_questions=self._get_clarification_questions(category),
                category=category,
                rationale=f"No keyword matches; defaulting to {category} category"
            )

        # Sort by score, then keyword count, trigger count, and explicit priority
        sorted_skills = sorted(
            scores.items(),
            key=lambda x: (
                x[1][0],                                      # total score
                len(x[1][1]),                                  # keyword match count
                len(x[1][2]),                                  # trigger match count
                self.skills[x[0]].get("priority", 0),         # explicit priority
            ),
            reverse=True,
        )
        top_skill, (top_score, top_kw, top_tr) = sorted_skills[0]

        # Determine supporting skills (second-highest if close in score)
        supporting = []
        if len(sorted_skills) > 1:
            second_skill, (second_score, _, _) = sorted_skills[1]
            if second_score > 0.3 and (top_score - second_score) < 0.2:
                supporting.append(second_skill)

        # Build rationale
        rationale_parts = []
        if top_kw:
            rationale_parts.append(f"Keywords: {', '.join(top_kw[:5])}")
        if top_tr:
            rationale_parts.append(f"Triggers: {len(top_tr)} pattern(s)")
        rationale = "; ".join(rationale_parts) if rationale_parts else "Low confidence match"

        # Determine if clarification needed
        requires_clarification = top_score < self.high_threshold
        clarification_questions = None
        if requires_clarification:
            category = categories.get(top_skill)
            clarification_questions = self._get_clarification_questions(category)

        return RoutingDecision(
            primary_skill=top_skill,
            supporting_skills=supporting,
            confidence=top_score,
            requires_clarification=requires_clarification,
            clarification_questions=clarification_questions,
            matched_keywords=top_kw,
            matched_triggers=top_tr,
            category=categories.get(top_skill),
            rationale=rationale
        )

    def _detect_category(self, tokens: set[str]) -> str:
        """Detect broad category from tokens when no skill matches."""
        category_indicators = {
            "visual": {"figure", "image", "visual", "diagram", "chart", "plot", "draw"},
            "document": {"write", "paper", "document", "draft", "text", "manuscript"},
            "research": {"find", "search", "papers", "literature", "review", "cite"},
            "analysis": {"analyze", "statistics", "test", "data", "code"},
            "conversion": {"convert", "export", "transform"},
            "biological_research": {"target", "drug", "gene", "protein", "compound", "druggability", "validation", "dossier", "profile"},
            "brand": {"brand", "oligon", "corporate", "identity", "logo"},
            "document_output": {"docx", "pptx", "xlsx", "word", "excel", "powerpoint", "spreadsheet"},
        }

        best_category = "document"  # Default
        best_overlap = 0

        for category, indicators in category_indicators.items():
            overlap = len(tokens & indicators)
            if overlap > best_overlap:
                best_overlap = overlap
                best_category = category

        return best_category

    def _get_clarification_questions(self, category: Optional[str]) -> list[str]:
        """Get clarification questions for a category."""
        disambiguation = self.routing_config.get("disambiguation", {})

        if category and category in disambiguation:
            questions = disambiguation[category]
            return [q.get("question", "") for q in questions[:2]]

        # Generic questions
        return [
            "What type of output do you need (document, visual, analysis)?",
            "Can you describe your task in more detail?"
        ]

    def get_skill_info(self, skill_name: str) -> Optional[dict]:
        """Get configuration info for a specific skill."""
        return self.skills.get(skill_name)

    def list_skills(self, category: Optional[str] = None) -> list[str]:
        """List all skills, optionally filtered by category."""
        if category is None:
            return list(self.skills.keys())
        return [
            name for name, config in self.skills.items()
            if config.get("category") == category
        ]


# Module-level convenience functions
_router: Optional[SkillRouter] = None


def get_router() -> SkillRouter:
    """Get or create the global router instance."""
    global _router
    if _router is None:
        _router = SkillRouter()
    return _router


def route_request(request: str) -> RoutingDecision:
    """Route a request using the global router instance.

    Args:
        request: Natural language request from user

    Returns:
        RoutingDecision with routing results
    """
    return get_router().route(request)


def main():
    """CLI interface for testing routing."""
    import argparse
    import json
    import sys

    parser = argparse.ArgumentParser(
        description="Deterministic skill router for scientific writing tasks"
    )
    parser.add_argument(
        "request",
        nargs="?",
        help="Request to route (or use --interactive)"
    )
    parser.add_argument(
        "--interactive", "-i",
        action="store_true",
        help="Interactive mode - enter requests one at a time"
    )
    parser.add_argument(
        "--format", "-f",
        choices=["text", "json", "xml"],
        default="text",
        help="Output format"
    )
    parser.add_argument(
        "--list-skills",
        action="store_true",
        help="List all available skills"
    )
    parser.add_argument(
        "--category", "-c",
        help="Filter skills by category (with --list-skills)"
    )

    args = parser.parse_args()
    router = get_router()

    if args.list_skills:
        skills = router.list_skills(args.category)
        print(f"Skills ({len(skills)}):")
        for skill in sorted(skills):
            info = router.get_skill_info(skill)
            desc = info.get("description", "") if info else ""
            print(f"  {skill}: {desc}")
        return

    def process_request(request: str) -> None:
        result = router.route(request)

        if args.format == "json":
            print(json.dumps(result.to_dict(), indent=2))
        elif args.format == "xml":
            print(result.to_xml())
        else:
            print(f"\nRequest: {request}")
            print(f"Primary skill: {result.primary_skill}")
            print(f"Confidence: {result.confidence:.2f}")
            if result.supporting_skills:
                print(f"Supporting: {', '.join(result.supporting_skills)}")
            if result.requires_clarification:
                print("Needs clarification: Yes")
                if result.clarification_questions:
                    print(f"Questions: {result.clarification_questions}")
            print(f"Rationale: {result.rationale}")

    if args.interactive:
        print("Skill Router - Interactive Mode")
        print("Enter requests (Ctrl+C to exit):\n")
        try:
            while True:
                request = input("> ").strip()
                if request:
                    process_request(request)
        except (KeyboardInterrupt, EOFError):
            print("\nExiting.")
    elif args.request:
        process_request(args.request)
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
