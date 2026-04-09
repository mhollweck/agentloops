"""Rule engine — converts performance data into IF/THEN decision rules.

Prescriptive rules derived from actual performance data, not opinions.
"""

from __future__ import annotations

import json
from typing import Any

from agentloops.models import Rule, Run
from agentloops.storage.base import BaseStorage


_RULE_GENERATION_PROMPT = """You are a rule generation engine. Analyze these agent runs and discover IF/THEN decision rules.

A good rule:
- Is specific and actionable (not vague advice)
- Has clear evidence from the runs
- Uses the format: IF <observable condition> THEN <specific action>
- Example: "IF the user asks about pricing THEN include the comparison table — because runs with tables had 90% success vs 45% without"

## Runs to Analyze
{runs_text}

## Existing Rules (avoid duplicates)
{existing_rules}

## Output Format (JSON only, no markdown fences)
{{
  "rules": [
    {{
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

        Args:
            runs: Runs to analyze. If None, uses the last 20 runs.

        Returns:
            List of newly generated Rule objects (already persisted).
        """
        if runs is None:
            runs = self._storage.get_runs(agent_name=self._agent_name, last_n=20)

        if not runs:
            return []

        existing_rules = self._storage.get_rules(active_only=True)
        prompt = self._build_prompt(runs, existing_rules)
        result = self._call_llm(prompt)

        new_rules: list[Rule] = []
        for item in result.get("rules", []):
            rule = Rule(
                text=item["text"],
                confidence=item.get("confidence", 0.5),
                evidence=item.get("evidence", []),
                evidence_count=len(item.get("evidence", [])),
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
        text: str,
        evidence: list[str] | None = None,
        confidence: float = 0.7,
    ) -> Rule:
        """Manually add a rule.

        Args:
            text: The IF/THEN rule text.
            evidence: List of evidence strings supporting the rule.
            confidence: Confidence score from 0.0 to 1.0.

        Returns:
            The created Rule object.
        """
        rule = Rule(
            text=text,
            confidence=confidence,
            evidence=evidence or [],
            evidence_count=len(evidence) if evidence else 0,
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
