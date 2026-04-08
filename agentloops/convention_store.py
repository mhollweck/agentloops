"""Convention store — manages evolving behavioral rules with contradiction detection.

Inspired by the conventions.md pattern in maria-os: self-learned patterns that
all agents read at startup. Conventions evolve as rules are validated or invalidated.
"""

from __future__ import annotations

import json
from typing import Any

from agentloops.models import Convention, Rule
from agentloops.storage.base import BaseStorage


_EVOLUTION_PROMPT = """You are a convention evolution engine. Conventions are behavioral rules that agents follow. You must:

1. Review the current conventions and new rules.
2. Identify which conventions are reinforced by new evidence.
3. Detect contradictions — two conventions that give opposite advice.
4. Suggest merges — two conventions that say similar things should become one.
5. Suggest removals — conventions with no supporting rules or evidence.
6. Suggest new conventions from high-confidence rules not yet captured.

## Current Conventions
{conventions_text}

## Active Rules (evidence base)
{rules_text}

## Output Format (JSON only, no markdown fences)
{{
  "new_conventions": [
    {{"text": "convention text", "source": "derived from rule: <rule text>"}}
  ],
  "contradictions": [
    {{
      "convention_ids": ["id1", "id2"],
      "description": "what the contradiction is",
      "suggested_resolution": "which one to keep and why"
    }}
  ],
  "to_remove": ["convention_id — reason"],
  "to_merge": [
    {{
      "convention_ids": ["id1", "id2"],
      "merged_text": "the combined convention"
    }}
  ]
}}"""


class ConventionStore:
    """Manages evolving behavioral conventions with contradiction detection."""

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

    def evolve(self) -> dict[str, Any]:
        """Trigger convention evolution: compare rules, detect contradictions, update.

        Compares current conventions against active rules, uses an LLM to find
        contradictions and suggest merges, then applies the changes.

        Returns:
            Dict summarizing what changed: new, removed, merged, contradictions.
        """
        conventions = self._storage.get_conventions(active_only=True)
        rules = self._storage.get_rules(active_only=True)

        if not rules and not conventions:
            return {"new": [], "removed": [], "merged": [], "contradictions": []}

        prompt = self._build_evolution_prompt(conventions, rules)
        result = self._call_llm(prompt)

        changes: dict[str, Any] = {
            "new": [],
            "removed": [],
            "merged": [],
            "contradictions": result.get("contradictions", []),
        }

        # Add new conventions
        for item in result.get("new_conventions", []):
            convention = Convention(
                text=item["text"],
                source=item.get("source", "evolution"),
            )
            self._storage.save_convention(convention)
            changes["new"].append(convention.to_dict())

        # Mark removals
        for removal in result.get("to_remove", []):
            # Parse "id — reason" format
            conv_id = removal.split("—")[0].split("-")[0].strip() if "—" in removal else removal.strip()
            # Try to find and mark as pruned
            for conv in conventions:
                if conv.id == conv_id:
                    conv.status = "pruned"
                    self._storage.save_convention(conv)
                    changes["removed"].append(conv_id)
                    break

        # Apply merges
        for merge in result.get("to_merge", []):
            merged_conv = Convention(
                text=merge["merged_text"],
                source=f"merged from {', '.join(merge['convention_ids'])}",
            )
            self._storage.save_convention(merged_conv)
            changes["merged"].append(merged_conv.to_dict())

            # Supersede originals
            for conv_id in merge["convention_ids"]:
                for conv in conventions:
                    if conv.id == conv_id:
                        conv.status = "superseded"
                        self._storage.save_convention(conv)
                        break

        return changes

    def get_conventions(self) -> list[Convention]:
        """Return all active conventions.

        Returns:
            List of active Convention objects.
        """
        return self._storage.get_conventions(active_only=True)

    def add(self, text: str, source: str = "manual") -> Convention:
        """Add a new convention.

        Args:
            text: The convention text.
            source: Where this convention came from.

        Returns:
            The created Convention object.
        """
        convention = Convention(text=text, source=source)
        self._storage.save_convention(convention)
        return convention

    def detect_contradictions(self) -> list[dict[str, Any]]:
        """Find conflicting conventions using LLM analysis.

        Returns:
            List of contradiction dicts with convention_ids, description,
            and suggested_resolution.
        """
        conventions = self._storage.get_conventions(active_only=True)
        if len(conventions) < 2:
            return []

        prompt = f"""Analyze these conventions for contradictions — two conventions that give conflicting advice.

## Conventions
{chr(10).join(f'- [{c.id}] {c.text}' for c in conventions)}

## Output Format (JSON only, no markdown fences)
{{
  "contradictions": [
    {{
      "convention_ids": ["id1", "id2"],
      "description": "what the contradiction is",
      "suggested_resolution": "which one to keep and why"
    }}
  ]
}}

If no contradictions found, return {{"contradictions": []}}"""

        result = self._call_llm(prompt)
        return result.get("contradictions", [])

    def resolve_contradiction(
        self,
        convention_ids: list[str],
        resolution: str,
    ) -> Convention:
        """Resolve a conflict between conventions.

        Marks the conflicting conventions as "contradicted" and creates a new
        convention with the resolution.

        Args:
            convention_ids: IDs of the conflicting conventions.
            resolution: The resolved convention text.

        Returns:
            The new Convention representing the resolution.
        """
        all_conventions = self._storage.get_conventions(active_only=False)

        for conv in all_conventions:
            if conv.id in convention_ids:
                conv.status = "contradicted"
                self._storage.save_convention(conv)

        resolved = Convention(
            text=resolution,
            source=f"resolved contradiction between {', '.join(convention_ids)}",
        )
        self._storage.save_convention(resolved)
        return resolved

    def _build_evolution_prompt(
        self, conventions: list[Convention], rules: list[Rule]
    ) -> str:
        conventions_text = "\n".join(
            f"- [{c.id}] {c.text} (status: {c.status}, source: {c.source})"
            for c in conventions
        ) or "No conventions yet."

        rules_text = "\n".join(
            f"- {r.text} (confidence: {r.confidence}, evidence: {r.evidence_count})"
            for r in rules
        ) or "No active rules."

        return _EVOLUTION_PROMPT.format(
            conventions_text=conventions_text,
            rules_text=rules_text,
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
            return {"new_conventions": [], "contradictions": [], "to_remove": [], "to_merge": []}
