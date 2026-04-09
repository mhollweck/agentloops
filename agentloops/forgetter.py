"""Forgetter — time-decay and importance-weighted memory pruning.

Inspired by the selective forgetting mechanism in maria-os: prune memory entries
older than 21 days, but never prune high-confidence rules or recently validated ones.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any

from agentloops.models import Convention, Rule
from agentloops.storage.base import BaseStorage


class Forgetter:
    """Time-decay + importance-weighted memory pruning."""

    def __init__(self, storage: BaseStorage) -> None:
        self._storage = storage

    def prune(
        self,
        strategy: str = "hybrid",
        max_age_days: int = 21,
        min_confidence: float = 0.3,
    ) -> dict[str, list[str]]:
        """Remove stale entries based on the chosen strategy.

        Strategies:
            - "decay": Pure age-based. Prunes anything older than max_age_days.
            - "importance": Confidence-weighted. Prunes low-confidence items regardless of age.
            - "hybrid": Both — prunes old items, but protects high-confidence or recently validated ones.

        Rules and conventions with high confidence (>= 0.8) or recent validation
        (within max_age_days) are never pruned, regardless of strategy.

        Args:
            strategy: "decay", "importance", or "hybrid".
            max_age_days: Maximum age before an item is eligible for pruning.
            min_confidence: Minimum confidence to keep (for importance/hybrid).

        Returns:
            Dict with 'rules_pruned' and 'conventions_pruned' — lists of IDs.
        """
        cutoff = datetime.now(timezone.utc) - timedelta(days=max_age_days)
        pruned: dict[str, list[str]] = {
            "rules_pruned": [],
            "conventions_pruned": [],
        }

        # Prune rules
        rules = self._storage.get_rules(active_only=True)
        for rule in rules:
            if self._should_prune_rule(rule, strategy, cutoff, min_confidence):
                rule.active = False
                self._storage.save_rule(rule)
                pruned["rules_pruned"].append(rule.id)

        # Prune conventions
        conventions = self._storage.get_conventions(active_only=True)
        for conv in conventions:
            if self._should_prune_convention(conv, strategy, cutoff):
                conv.status = "pruned"
                self._storage.save_convention(conv)
                pruned["conventions_pruned"].append(conv.id)

        return pruned

    def _should_prune_rule(
        self,
        rule: Rule,
        strategy: str,
        cutoff: datetime,
        min_confidence: float,
    ) -> bool:
        """Determine whether a rule should be pruned."""
        # Never prune high-confidence rules
        if rule.confidence >= 0.8:
            return False

        # Never prune recently validated rules
        try:
            validated = datetime.fromisoformat(rule.last_validated)
            if validated > cutoff:
                return False
        except (ValueError, TypeError):
            pass

        created = _parse_date(rule.created_at)

        if strategy == "decay":
            return created is not None and created < cutoff

        if strategy == "importance":
            return rule.confidence < min_confidence

        # hybrid
        if created is not None and created < cutoff:
            return True
        if rule.confidence < min_confidence:
            return True
        return False

    def _should_prune_convention(
        self,
        conv: Convention,
        strategy: str,
        cutoff: datetime,
    ) -> bool:
        """Determine whether a convention should be pruned."""
        updated = _parse_date(conv.updated_at)

        # Never prune recently updated conventions
        if updated is not None and updated > cutoff:
            return False

        created = _parse_date(conv.created_at)

        if strategy == "decay" or strategy == "hybrid":
            return created is not None and created < cutoff

        # importance strategy doesn't apply well to conventions (no confidence)
        # so we skip pruning in pure importance mode
        return False


def _parse_date(date_str: str | None) -> datetime | None:
    """Parse an ISO date string, returning None on failure."""
    if not date_str:
        return None
    try:
        return datetime.fromisoformat(date_str)
    except (ValueError, TypeError):
        return None
