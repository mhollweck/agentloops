"""Rule renderer — converts structured rule specs into LLM-readable prompt text.

Each rule type has a canonical text representation that gets injected into
agent prompts via enhance_prompt(). The renderer produces this text from
the structured spec data.

For IF/THEN rules, the text field IS the canonical form (no rendering needed).
For scoring and decision_table rules, text is auto-generated from spec.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from agentloops.models import Rule


def render_rule(rule: Rule) -> str:
    """Render any rule type into LLM-readable prompt text."""
    if rule.rule_type == "scoring" and rule.spec:
        return _render_scoring(rule.spec, rule.confidence)
    elif rule.rule_type == "decision_table" and rule.spec:
        return _render_table(rule.spec, rule.confidence)
    return rule.text


def render_from_spec(rule_type: str, spec: dict[str, Any], confidence: float) -> str:
    """Render prompt text from a spec dict (without a Rule object)."""
    if rule_type == "scoring":
        return _render_scoring(spec, confidence)
    elif rule_type == "decision_table":
        return _render_table(spec, confidence)
    return ""


def _render_scoring(spec: dict[str, Any], confidence: float) -> str:
    """Render a scoring rule as a readable rubric.

    Output format:
        SCORING RULE: Email personalization effort
        Score (0-100):
          - VP/C-level title: +30 (credibility: 0.88)
          - Revenue >$100M: +20 (credibility: 0.85)
        Action thresholds:
          - Score 70-100: Deep research
          - Score 50-69: Standard template
        Confidence: 0.87
    """
    decision = spec.get("decision", "Unnamed decision")
    scale = spec.get("scale", [0, 100])
    factors = spec.get("factors", [])
    thresholds = spec.get("thresholds", [])

    lines = [f"SCORING RULE: {decision}"]
    lines.append(f"Score ({scale[0]}-{scale[1]}):")

    for f in factors:
        cred = f.get("credibility")
        cred_str = f" (credibility: {cred:.2f})" if cred is not None else ""
        lines.append(f"  - {f['condition']}: +{f['weight']}{cred_str}")

    if thresholds:
        lines.append("Action thresholds:")
        for t in thresholds:
            lines.append(f"  - Score {t['min_score']}-{t['max_score']}: {t['action']}")

    lines.append(f"Confidence: {confidence:.2f}")
    return "\n".join(lines)


def _render_table(spec: dict[str, Any], confidence: float) -> str:
    """Render a decision table as a readable markdown table.

    Output format:
        DECISION TABLE: CTA Selection
        | Prospect Level | Deal Stage | CTA | Confidence |
        |---|---|---|---|
        | C-level | Early | Schedule call | 0.88 |
        Fallback: If no row matches, use generic CTA.
    """
    decision = spec.get("decision", "Unnamed decision")
    columns = spec.get("columns", [])
    action_column = spec.get("action_column", "Action")
    rows = spec.get("rows", [])
    fallback = spec.get("fallback")

    lines = [f"DECISION TABLE: {decision}"]

    # Build header
    header_cols = columns + [action_column, "Confidence"]
    lines.append("| " + " | ".join(header_cols) + " |")
    lines.append("|" + "|".join(["---"] * len(header_cols)) + "|")

    # Build rows
    for row in rows:
        conditions = row.get("conditions", {})
        vals = [conditions.get(c, "Any") for c in columns]
        vals.append(row.get("action", ""))
        row_conf = row.get("confidence", confidence)
        vals.append(f"{row_conf:.2f}")
        lines.append("| " + " | ".join(str(v) for v in vals) + " |")

    if fallback:
        lines.append(f"Fallback: {fallback}")

    lines.append(f"Overall confidence: {confidence:.2f}")
    return "\n".join(lines)
