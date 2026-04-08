"""Tests for the RuleEngine module."""

from __future__ import annotations

from agentloops.models import Rule
from agentloops.rule_engine import RuleEngine


class TestAddRule:
    def test_add_rule_basic(self, storage):
        engine = RuleEngine(storage, "test-agent")
        rule = engine.add_rule(
            text="IF user asks about pricing THEN show table",
            confidence=0.8,
        )
        assert isinstance(rule, Rule)
        assert rule.text == "IF user asks about pricing THEN show table"
        assert rule.confidence == 0.8
        assert rule.active is True

    def test_add_rule_with_evidence(self, storage):
        engine = RuleEngine(storage, "test-agent")
        rule = engine.add_rule(
            text="IF cold outreach THEN personalize",
            evidence=["run-1 showed higher reply rate", "run-5 confirmed"],
            confidence=0.9,
        )
        assert len(rule.evidence) == 2
        assert rule.evidence_count == 2

    def test_add_rule_default_confidence(self, storage):
        engine = RuleEngine(storage, "test-agent")
        rule = engine.add_rule(text="IF X THEN Y")
        assert rule.confidence == 0.7  # default

    def test_add_multiple_rules(self, storage):
        engine = RuleEngine(storage, "test-agent")
        engine.add_rule(text="Rule 1", confidence=0.6)
        engine.add_rule(text="Rule 2", confidence=0.9)
        engine.add_rule(text="Rule 3", confidence=0.3)
        assert len(engine.active()) == 3


class TestActive:
    def test_active_sorted_by_confidence(self, storage, sample_rules):
        engine = RuleEngine(storage, "test-agent")
        active = engine.active()
        assert len(active) == 4
        # Should be sorted descending by confidence
        confidences = [r.confidence for r in active]
        assert confidences == sorted(confidences, reverse=True)

    def test_active_highest_first(self, storage, sample_rules):
        engine = RuleEngine(storage, "test-agent")
        active = engine.active()
        assert active[0].confidence == 0.9
        assert active[-1].confidence == 0.2

    def test_active_empty(self, storage):
        engine = RuleEngine(storage, "test-agent")
        assert engine.active() == []


class TestDeactivateRule:
    def test_deactivate_removes_from_active(self, storage, sample_rules):
        engine = RuleEngine(storage, "test-agent")
        rule_to_deactivate = sample_rules[0]

        result = engine.deactivate_rule(rule_to_deactivate.id)
        assert result is True

        active = engine.active()
        active_ids = [r.id for r in active]
        assert rule_to_deactivate.id not in active_ids
        assert len(active) == 3

    def test_deactivate_nonexistent_returns_false(self, storage):
        engine = RuleEngine(storage, "test-agent")
        result = engine.deactivate_rule("nonexistent-id")
        assert result is False

    def test_deactivated_rule_still_in_all_rules(self, storage, sample_rules):
        engine = RuleEngine(storage, "test-agent")
        rule_id = sample_rules[0].id
        engine.deactivate_rule(rule_id)

        # Active only should not include it
        active = engine.active()
        assert all(r.id != rule_id for r in active)

        # But get_rules(active_only=False) should still have it
        all_rules = storage.get_rules(active_only=False)
        assert any(r.id == rule_id for r in all_rules)

    def test_deactivate_multiple_rules(self, storage, sample_rules):
        engine = RuleEngine(storage, "test-agent")
        engine.deactivate_rule(sample_rules[0].id)
        engine.deactivate_rule(sample_rules[1].id)
        assert len(engine.active()) == 2
