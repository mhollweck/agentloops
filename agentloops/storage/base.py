"""Abstract storage interface for AgentLoops."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any

from agentloops.models import Convention, Reflection, Rule, Run


class BaseStorage(ABC):
    """Abstract base class for all storage backends."""

    @abstractmethod
    def save_run(self, run: Run) -> None:
        """Persist a run record."""
        ...

    @abstractmethod
    def get_runs(
        self,
        agent_name: str | None = None,
        last_n: int | None = None,
        outcome_filter: str | None = None,
    ) -> list[Run]:
        """Retrieve runs, optionally filtered."""
        ...

    @abstractmethod
    def save_rule(self, rule: Rule) -> None:
        """Persist a rule."""
        ...

    @abstractmethod
    def get_rules(self, active_only: bool = True) -> list[Rule]:
        """Retrieve rules."""
        ...

    @abstractmethod
    def save_convention(self, convention: Convention) -> None:
        """Persist a convention."""
        ...

    @abstractmethod
    def get_conventions(self, active_only: bool = True) -> list[Convention]:
        """Retrieve conventions."""
        ...

    @abstractmethod
    def save_reflection(self, reflection: Reflection) -> None:
        """Persist a reflection."""
        ...

    @abstractmethod
    def get_reflections(self, last_n: int | None = None) -> list[Reflection]:
        """Retrieve reflections."""
        ...

    @abstractmethod
    def delete(self, collection: str, id: str) -> bool:
        """Delete an item by collection name and id. Returns True if found."""
        ...
