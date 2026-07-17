"""Routing — Variable routing rules for pipeline customization.

IOP: Just data. Rules that modify pipeline before execution.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class RouteRule:
    """Route a variable through a processor at a specific point."""
    intent_name: str
    variable: str
    through: str
    before: str | None = None  # None = append at end


# Global routing rules: intent_name → list of rules
_rules: dict[str, list[RouteRule]] = {}


def route_variable(
    intent_name: str,
    variable: str,
    through: str,
    before: str | None = None,
) -> None:
    """Route a variable through a processor.

    Usage:
        route_variable("GET:/users/{id}", "user_id", "enrich_user", before="authorize")
    """
    if intent_name not in _rules:
        _rules[intent_name] = []
    _rules[intent_name].append(RouteRule(
        intent_name=intent_name,
        variable=variable,
        through=through,
        before=before,
    ))


def get_rules(intent_name: str) -> list[RouteRule]:
    """Get routing rules for an intent."""
    return _rules.get(intent_name, [])


def apply_routing(
    pipeline: tuple[str, ...],
    intent_name: str,
) -> tuple[str, ...]:
    """Apply routing rules to a pipeline. Returns modified pipeline."""
    rules = get_rules(intent_name)
    if not rules:
        return pipeline

    result = list(pipeline)
    for rule in rules:
        if rule.through in result:
            continue  # already in pipeline

        if rule.before and rule.before in result:
            idx = result.index(rule.before)
            result.insert(idx, rule.through)
        else:
            result.append(rule.through)

    return tuple(result)


def clear_rules() -> None:
    """Clear all routing rules."""
    _rules.clear()
