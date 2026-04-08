"""AgentLoops — main orchestrator.

The single entry point that wires together all learning mechanisms:
reflection, rule generation, convention evolution, forgetting, and tracking.

Usage:
    from agentloops import AgentLoops

    loops = AgentLoops("my-agent")
    loops.track(input="...", output="...", outcome="success")
    reflection = loops.reflect()
    enhanced = loops.enhance_prompt("You are a helpful agent.")
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from agentloops.convention_store import ConventionStore
from agentloops.forgetter import Forgetter
from agentloops.models import Reflection, Run
from agentloops.reflector import Reflector
from agentloops.rule_engine import RuleEngine
from agentloops.storage.base import BaseStorage
from agentloops.storage.file import FileStorage
from agentloops.tracker import Tracker


class AgentLoops:
    """Main orchestrator — the single entry point for adding self-learning to any agent.

    Wires together: Tracker, Reflector, RuleEngine, ConventionStore, and Forgetter.
    Zero-config to start: just provide an agent name and everything works with
    file-based storage in `.agentloops/`.
    """

    def __init__(
        self,
        agent_name: str,
        storage: str | BaseStorage = "file",
        storage_path: str | Path | None = None,
        reflection_model: str = "claude-sonnet-4-6",
        api_key: str | None = None,
    ) -> None:
        """Initialize AgentLoops.

        Args:
            agent_name: Unique name for this agent.
            storage: Either "file" for file-based storage or a BaseStorage instance.
            storage_path: Directory for file storage. Defaults to ".agentloops".
            reflection_model: Anthropic model to use for reflection/rule generation.
            api_key: Anthropic API key. Uses ANTHROPIC_API_KEY env var if not set.
        """
        self._agent_name = agent_name

        # Initialize storage
        if isinstance(storage, str):
            if storage == "file":
                path = Path(storage_path) if storage_path else Path(".agentloops")
                self._storage = FileStorage(path, agent_name)
            else:
                raise ValueError(f"Unknown storage type: {storage}. Use 'file' or pass a BaseStorage instance.")
        else:
            self._storage = storage

        # Initialize components
        self._tracker = Tracker(self._storage, agent_name)
        self._reflector = Reflector(self._storage, agent_name, reflection_model, api_key)
        self._rule_engine = RuleEngine(self._storage, agent_name, reflection_model, api_key)
        self._convention_store = ConventionStore(self._storage, agent_name, reflection_model, api_key)
        self._forgetter = Forgetter(self._storage)

    def track(
        self,
        input: str,
        output: str,
        outcome: str,
        metadata: dict[str, Any] | None = None,
    ) -> Run:
        """Log a run with its outcome.

        Args:
            input: The prompt or input given to the agent.
            output: The agent's response.
            outcome: Result — "success", "failure", or a numeric score as string.
            metadata: Optional key-value pairs (latency, tokens, etc.).

        Returns:
            The persisted Run object.
        """
        active_rule_ids = [r.id for r in self._rule_engine.active()]
        return self._tracker.log_run(
            input=input,
            output=output,
            outcome=outcome,
            metadata=metadata,
            rules_applied=active_rule_ids,
        )

    def reflect(self, last_n: int = 5) -> Reflection:
        """Trigger reflection on recent runs.

        Analyzes the last N runs, produces a structured critique, and suggests
        new IF/THEN rules based on patterns found.

        Args:
            last_n: Number of recent runs to analyze.

        Returns:
            A Reflection with critique, suggested rules, and confidence scores.
        """
        return self._reflector.reflect(last_n=last_n)

    def enhance_prompt(self, base_prompt: str) -> str:
        """Inject active rules and conventions into an agent prompt.

        Appends the current rules and conventions to the base prompt so the
        agent benefits from everything the system has learned.

        Args:
            base_prompt: The agent's base system prompt.

        Returns:
            The enhanced prompt with rules and conventions appended.
        """
        rules = self._rule_engine.active()
        conventions = self._convention_store.get_conventions()

        if not rules and not conventions:
            return base_prompt

        sections: list[str] = [base_prompt, ""]

        if rules:
            sections.append("## Decision Rules (learned from past performance)")
            for rule in rules:
                sections.append(f"- {rule.text} [confidence: {rule.confidence:.2f}]")
            sections.append("")

        if conventions:
            sections.append("## Conventions (self-learned behavioral patterns)")
            for conv in conventions:
                sections.append(f"- {conv.text}")
            sections.append("")

        return "\n".join(sections)

    def forget(
        self,
        strategy: str = "decay",
        max_age_days: int = 21,
    ) -> dict[str, list[str]]:
        """Prune stale entries from memory.

        Args:
            strategy: "decay" (age-based), "importance" (confidence-weighted),
                     or "hybrid" (both).
            max_age_days: Maximum age in days before pruning.

        Returns:
            Dict with lists of pruned rule and convention IDs.
        """
        return self._forgetter.prune(strategy=strategy, max_age_days=max_age_days)

    @property
    def rules(self) -> RuleEngine:
        """Access the rule engine directly."""
        return self._rule_engine

    @property
    def conventions(self) -> ConventionStore:
        """Access the convention store directly."""
        return self._convention_store

    @property
    def tracker(self) -> Tracker:
        """Access the tracker directly."""
        return self._tracker

    @property
    def agent_name(self) -> str:
        """The name of the agent this instance manages."""
        return self._agent_name
