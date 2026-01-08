"""
Deterministic Skill Router for Claude Scientific Writer Plugin.

This package provides keyword-based routing to reduce LLM interpretation
for clear-cut skill selection tasks.

Usage:
    from skills.skill_router import route_request, RoutingDecision

    result = route_request("Create a bar chart of my results")
    print(result.primary_skill)  # "plotting-libraries"
    print(result.confidence)     # 0.85
"""

from .route import RoutingDecision, SkillRouter, get_router, route_request

__all__ = ["RoutingDecision", "SkillRouter", "get_router", "route_request"]
__version__ = "1.0.0"
