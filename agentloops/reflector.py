"""Reflector — evaluates agent runs and produces structured critiques.

After every agent run, evaluate what worked, what failed, and what
rules should change. Inspired by the Reflexion architecture (Shinn et al.).
"""

from __future__ import annotations

import json
from typing import Any

from agentloops.models import Reflection, Run
from agentloops.storage.base import BaseStorage


# Default reflection prompt template
_REFLECTION_PROMPT = """You are a self-reflection engine for an AI agent named "{agent_name}".

Analyze these recent runs and produce a structured critique. For each run you see the input given to the agent, the output it produced, and the outcome (success/failure/score).

## Recent Runs
{runs_text}

## Active Rules (currently applied)
{rules_text}

## Active Conventions
{conventions_text}

## Your Task
1. Identify what worked well and what failed.
2. Look for patterns — are certain types of inputs consistently failing?
3. Suggest new rules based on the evidence. Choose the best format:
   - **IF/THEN** (default): For simple binary patterns. "IF <condition> THEN <action> — because <evidence>"
   - **SCORING**: For multi-factor decisions with 3+ contributing factors. Output as a dict with rule_type, spec, confidence.
   - **DECISION TABLE**: For decisions where factor combinations matter. Output as a dict with rule_type, spec, confidence.
   Most rules should be IF/THEN. Only use scoring/table when the pattern genuinely requires it.
4. Flag any existing rules that seem wrong or outdated.
5. Rate your confidence in each suggestion (0.0 to 1.0).

## Output Format (JSON only, no markdown fences)
{{
  "critique": "2-3 paragraph analysis of what's working and what isn't",
  "suggested_rules": [
    "IF <condition> THEN <action> — because <evidence>",
    {{"rule_type": "scoring", "spec": {{"decision": "...", "factors": [...], "thresholds": [...], "scale": [0, 100]}}, "confidence": 0.85}}
  ],
  "confidence_scores": {{
    "rule text here": 0.85
  }},
  "rules_to_reconsider": ["rule IDs that may be outdated or wrong"]
}}"""


class Reflector:
    """Evaluates agent runs and produces structured critiques using an LLM.

    Uses the Anthropic SDK by default. The reflection prompt asks the model to
    analyze recent runs, identify patterns, and suggest new rules.
    """

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
        self._meta_guidance: list[str] = []  # Injected by MetaLearner

    def reflect(self, last_n: int = 5) -> Reflection:
        """Run a reflection pass over recent agent runs.

        Args:
            last_n: Number of recent runs to analyze.

        Returns:
            A Reflection object with critique, suggested rules, and confidence scores.

        Raises:
            ValueError: If there are no runs to reflect on.
        """
        runs = self._storage.get_runs(agent_name=self._agent_name, last_n=last_n)
        if not runs:
            raise ValueError(f"No runs found for agent '{self._agent_name}'")

        rules = self._storage.get_rules(active_only=True)
        conventions = self._storage.get_conventions(active_only=True)

        prompt = self._build_prompt(runs, rules, conventions)
        result = self._call_llm(prompt)

        reflection = Reflection(
            agent_name=self._agent_name,
            critique=result.get("critique", ""),
            suggested_rules=result.get("suggested_rules", []),
            confidence_scores=result.get("confidence_scores", {}),
            run_ids=[r.id for r in runs],
        )

        self._storage.save_reflection(reflection)
        return reflection

    def _build_prompt(self, runs: list[Run], rules: list, conventions: list) -> str:
        """Build the reflection prompt from runs and current state."""
        runs_text = ""
        for i, run in enumerate(runs, 1):
            runs_text += f"\n### Run {i} (id: {run.id})\n"
            runs_text += f"**Input:** {run.input[:500]}\n"
            runs_text += f"**Output:** {run.output[:500]}\n"
            runs_text += f"**Outcome:** {run.outcome}\n"
            if run.rules_applied:
                runs_text += f"**Rules applied:** {', '.join(run.rules_applied)}\n"

        rules_text = "\n".join(
            f"- [{r.id}] {r.text} (confidence: {r.confidence})" for r in rules
        ) or "No active rules yet."

        conventions_text = "\n".join(
            f"- {c.text}" for c in conventions
        ) or "No conventions yet."

        prompt = _REFLECTION_PROMPT.format(
            agent_name=self._agent_name,
            runs_text=runs_text,
            rules_text=rules_text,
            conventions_text=conventions_text,
        )

        # Inject meta-learnings (what has worked in past reflections)
        if self._meta_guidance:
            guidance = "\n".join(f"- {g}" for g in self._meta_guidance)
            prompt += f"\n\n## Meta-Learning (from past reflection performance)\n{guidance}\n"
            self._meta_guidance = []  # Reset after use

        return prompt

    def _call_llm(self, prompt: str) -> dict[str, Any]:
        """Call the Anthropic API and parse the JSON response."""
        import anthropic

        client = anthropic.Anthropic(api_key=self._api_key)

        message = client.messages.create(
            model=self._model,
            max_tokens=2000,
            messages=[{"role": "user", "content": prompt}],
        )

        # Extract text content
        text = ""
        for block in message.content:
            if hasattr(block, "text"):
                text += block.text

        # Parse JSON — strip markdown fences if present
        text = text.strip()
        if text.startswith("```"):
            # Remove opening fence
            first_newline = text.index("\n")
            text = text[first_newline + 1 :]
            # Remove closing fence
            if text.endswith("```"):
                text = text[:-3].strip()

        try:
            return json.loads(text)
        except json.JSONDecodeError:
            # If parsing fails, return a minimal structure
            return {
                "critique": text,
                "suggested_rules": [],
                "confidence_scores": {},
            }
