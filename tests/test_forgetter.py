"""Tests for the Forgetter module."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

from agentloops.forgetter import Forgetter
from agentloops.models import Convention, Rule


class TestDecayStrategy:
    def test_old_rule_gets_pruned(self, storage, old_rule):
        forgetter = Forgetter(storage)
        result = forgetter.prune(strategy="decay", max_age_days=21)
        assert old_rule.id in result["rules_pruned"]

    def test_recent_rule_not_pruned(self, storage):
        rule = Rule(
            text="Recent rule",
            confidence=0.3,
            created_at=datetime.now(timezone.utc).isoformat(),
            last_validated=datetime.now(timezone.utc).isoformat(),
        )
        storage.save_rule(rule)

        forgetter = Forgetter(storage)
        result = forgetter.prune(strategy="decay", max_age_days=21)
        assert rule.id not in result["rules_pruned"]

    def test_old_convention_gets_pruned(self, storage, old_convention):
        forgetter = Forgetter(storage)
        result = forgetter.prune(strategy="decay", max_age_days=21)
        assert old_convention.id in result["conventions_pruned"]

    def test_recent_convention_not_pruned(self, storage):
        conv = Convention(
            text="Recent convention",
            source="manual",
            created_at=datetime.now(timezone.utc).isoformat(),
            updated_at=datetime.now(timezone.utc).isoformat(),
        )
        storage.save_convention(conv)

        forgetter = Forgetter(storage)
        result = forgetter.prune(strategy="decay", max_age_days=21)
        assert conv.id not in result["conventions_pruned"]


class TestImportanceStrategy:
    def test_low_confidence_rule_gets_pruned(self, storage):
        rule = Rule(
            text="Low confidence rule",
            confidence=0.1,
            created_at=datetime.now(timezone.utc).isoformat(),
            last_validated=(datetime.now(timezone.utc) - timedelta(days=30)).isoformat(),
        )
        storage.save_rule(rule)

        forgetter = Forgetter(storage)
        result = forgetter.prune(strategy="importance", min_confidence=0.3)
        assert rule.id in result["rules_pruned"]

    def test_medium_confidence_rule_not_pruned(self, storage):
        rule = Rule(
            text="Medium confidence rule",
            confidence=0.5,
            created_at=datetime.now(timezone.utc).isoformat(),
            last_validated=(datetime.now(timezone.utc) - timedelta(days=30)).isoformat(),
        )
        storage.save_rule(rule)

        forgetter = Forgetter(storage)
        result = forgetter.prune(strategy="importance", min_confidence=0.3)
        assert rule.id not in result["rules_pruned"]

    def test_importance_does_not_prune_conventions(self, storage, old_convention):
        """Importance strategy doesn't apply to conventions (no confidence score)."""
        forgetter = Forgetter(storage)
        result = forgetter.prune(strategy="importance")
        assert old_convention.id not in result["conventions_pruned"]


class TestHighConfidenceProtection:
    def test_high_confidence_old_rule_never_pruned_decay(self, storage, high_confidence_old_rule):
        forgetter = Forgetter(storage)
        result = forgetter.prune(strategy="decay", max_age_days=21)
        assert high_confidence_old_rule.id not in result["rules_pruned"]

    def test_high_confidence_old_rule_never_pruned_importance(self, storage, high_confidence_old_rule):
        forgetter = Forgetter(storage)
        result = forgetter.prune(strategy="importance", min_confidence=0.3)
        assert high_confidence_old_rule.id not in result["rules_pruned"]

    def test_high_confidence_old_rule_never_pruned_hybrid(self, storage, high_confidence_old_rule):
        forgetter = Forgetter(storage)
        result = forgetter.prune(strategy="hybrid", max_age_days=21, min_confidence=0.3)
        assert high_confidence_old_rule.id not in result["rules_pruned"]


class TestHybridStrategy:
    def test_hybrid_prunes_old_low_confidence(self, storage, old_rule):
        forgetter = Forgetter(storage)
        result = forgetter.prune(strategy="hybrid", max_age_days=21, min_confidence=0.3)
        assert old_rule.id in result["rules_pruned"]

    def test_hybrid_prunes_recent_but_very_low_confidence(self, storage):
        rule = Rule(
            text="Very low confidence",
            confidence=0.1,
            created_at=datetime.now(timezone.utc).isoformat(),
            last_validated=(datetime.now(timezone.utc) - timedelta(days=30)).isoformat(),
        )
        storage.save_rule(rule)

        forgetter = Forgetter(storage)
        result = forgetter.prune(strategy="hybrid", max_age_days=21, min_confidence=0.3)
        assert rule.id in result["rules_pruned"]


class TestRecentlyValidatedProtection:
    def test_recently_validated_rule_not_pruned(self, storage):
        """Even old rules are kept if they were recently validated."""
        rule = Rule(
            text="Old but recently validated",
            confidence=0.4,
            created_at=(datetime.now(timezone.utc) - timedelta(days=60)).isoformat(),
            last_validated=datetime.now(timezone.utc).isoformat(),
        )
        storage.save_rule(rule)

        forgetter = Forgetter(storage)
        result = forgetter.prune(strategy="decay", max_age_days=21)
        assert rule.id not in result["rules_pruned"]
