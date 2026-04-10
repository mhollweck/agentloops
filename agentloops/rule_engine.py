"""Rule engine — converts performance data into IF/THEN decision rules.

Prescriptive rules derived from actual performance data, not opinions.
"""

from __future__ import annotations

import json
from typing import Any

from typing import Any

from agentloops.models import Rule, Run
from agentloops.storage.base import BaseStorage


_RULE_GENERATION_PROMPT = """You are a rule generation engine. Analyze these agent runs and discover decision rules.

## Rule Types — Choose the Best Format

1. **IF/THEN** (default): Binary condition → single action.
   Use for: simple, observable patterns with one clear trigger.
   Output: {{"rule_type": "if_then", "text": "IF <condition> THEN <action> — because <evidence>"}}

2. **SCORING**: 3+ weighted factors → graduated action thresholds.
   Use for: decisions where multiple independent signals each contribute different amounts.
   Output: {{"rule_type": "scoring", "spec": {{"decision": "...", "factors": [{{"condition": "...", "weight": 30, "credibility": 0.85}}], "thresholds": [{{"min_score": 70, "max_score": 100, "action": "..."}}], "scale": [0, 100]}}}}

3. **DECISION TABLE**: 2-4 input dimensions → different action per combination.
   Use for: decisions where the COMBINATION of factors matters (not just the sum).
   Output: {{"rule_type": "decision_table", "spec": {{"decision": "...", "columns": ["Factor1", "Factor2"], "action_column": "Action", "rows": [{{"conditions": {{"Factor1": "value"}}, "action": "...", "confidence": 0.85}}], "fallback": "default action"}}}}

MOST rules should be IF/THEN. Only use scoring when you see 3+ independent factors contributing to one decision. Only use tables when different factor combinations need genuinely different actions.

## Runs to Analyze
{runs_text}

## Existing Rules (avoid duplicates)
{existing_rules}

## Output Format (JSON only, no markdown fences)
{{
  "rules": [
    {{
      "rule_type": "if_then",
      "text": "IF <condition> THEN <action> — because <evidence>",
      "confidence": 0.85,
      "evidence": ["run_id_1 showed X", "run_id_2 confirmed Y"]
    }}
  ]
}}

Only output rules with confidence >= 0.5. If you see no clear patterns, return an empty rules array."""


class RuleEngine:
    """Discovers and manages IF/THEN decision rules from performance data."""

    def __init__(
        self,
        storage: BaseStorage,
        agent_name: str,
        model: str = "claude-sonnet-4-6",
        api_key: str | None = None,
    ) -> None:
        self._storage = storage
        self._agent_name = agent_name
        self._model = model
        self._api_key = api_key

    def generate_rules(self, runs: list[Run] | None = None) -> list[Rule]:
        """Analyze runs to discover patterns and generate new rules.

        Supports 3 rule types: if_then, scoring, decision_table.
        The LLM chooses the best format based on the patterns it finds.

        Args:
            runs: Runs to analyze. If None, uses the last 20 runs.

        Returns:
            List of newly generated Rule objects (already persisted).
        """
        from agentloops.rule_renderer import render_from_spec

        if runs is None:
            runs = self._storage.get_runs(agent_name=self._agent_name, last_n=20)

        if not runs:
            return []

        existing_rules = self._storage.get_rules(active_only=True)
        prompt = self._build_prompt(runs, existing_rules)
        result = self._call_llm(prompt)

        new_rules: list[Rule] = []
        for item in result.get("rules", []):
            rule_type = item.get("rule_type", "if_then")
            spec = item.get("spec")
            confidence = item.get("confidence", 0.5)
            evidence = item.get("evidence", [])

            # For structured types, auto-generate text from spec
            if rule_type in ("scoring", "decision_table") and spec:
                text = render_from_spec(rule_type, spec, confidence)
            else:
                text = item.get("text", "")
                rule_type = "if_then"
                spec = None

            if not text:
                continue

            rule = Rule(
                text=text,
                confidence=confidence,
                evidence=evidence,
                evidence_count=len(evidence),
                rule_type=rule_type,
                spec=spec,
            )
            self._storage.save_rule(rule)
            new_rules.append(rule)

        return new_rules

    def active(self) -> list[Rule]:
        """Return currently active rules sorted by confidence (highest first).

        Returns:
            List of active Rule objects sorted by confidence descending.
        """
        rules = self._storage.get_rules(active_only=True)
        return sorted(rules, key=lambda r: r.confidence, reverse=True)

    def add_rule(
        self,
        text: str | None = None,
        evidence: list[str] | None = None,
        confidence: float = 0.7,
        rule_type: str = "if_then",
        spec: dict[str, Any] | None = None,
        priority: int = 0,
    ) -> Rule:
        """Manually add a rule.

        Args:
            text: The rule text. Auto-generated from spec for scoring/table types.
            evidence: List of evidence strings supporting the rule.
            confidence: Confidence score from 0.0 to 1.0.
            rule_type: "if_then", "scoring", or "decision_table".
            spec: Structured data for scoring/table rules.
            priority: Higher = injected first in prompt.

        Returns:
            The created Rule object.
        """
        from agentloops.rule_renderer import render_from_spec

        if text is None and spec and rule_type in ("scoring", "decision_table"):
            text = render_from_spec(rule_type, spec, confidence)

        if not text:
            raise ValueError("Rule must have text or a spec to render from")

        rule = Rule(
            text=text,
            confidence=confidence,
            evidence=evidence or [],
            evidence_count=len(evidence) if evidence else 0,
            rule_type=rule_type,
            spec=spec,
            priority=priority,
        )
        self._storage.save_rule(rule)
        return rule

    def deactivate_rule(self, rule_id: str) -> bool:
        """Soft-delete a rule by setting it inactive.

        Args:
            rule_id: The ID of the rule to deactivate.

        Returns:
            True if the rule was found and deactivated.
        """
        rules = self._storage.get_rules(active_only=False)
        for rule in rules:
            if rule.id == rule_id:
                rule.active = False
                self._storage.save_rule(rule)
                return True
        return False

    def _build_prompt(self, runs: list[Run], existing_rules: list[Rule]) -> str:
        runs_text = ""
        for run in runs:
            runs_text += f"\n- Run {run.id}: input='{run.input[:200]}' "
            runs_text += f"output='{run.output[:200]}' outcome={run.outcome}\n"

        existing = "\n".join(
            f"- {r.text} (confidence: {r.confidence})" for r in existing_rules
        ) or "None yet."

        return _RULE_GENERATION_PROMPT.format(
            runs_text=runs_text,
            existing_rules=existing,
        )

    def _call_llm(self, prompt: str) -> dict[str, Any]:
        import anthropic

        client = anthropic.Anthropic(api_key=self._api_key)

        message = client.messages.create(
            model=self._model,
            max_tokens=2000,
            messages=[{"role": "user", "content": prompt}],
        )

        text = ""
        for block in message.content:
            if hasattr(block, "text"):
                text += block.text

        text = text.strip()
        if text.startswith("```"):
            first_newline = text.index("\n")
            text = text[first_newline + 1 :]
            if text.endswith("```"):
                text = text[:-3].strip()

        try:
            return json.loads(text)
        except json.JSONDecodeError:
            return {"rules": []}
