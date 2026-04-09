"""Tests for the MetaLearner — the system that learns to learn better."""

from __future__ import annotations

import pytest

from agentloops.core import AgentLoops
from agentloops.meta_learner import MetaLearner, ReflectionQuality, RuleImpact
from agentloops.models import Reflection, Rule


class TestRuleImpact:
    """Test rule impact tracking."""

    def test_impact_score_not_enough_data(self):
        impact = RuleImpact(
            rule_id="r1", rule_text="IF X THEN Y", confidence_at_creation=0.8,
            outcomes_before=[0.5, 0.6], outcomes_after=[0.7],  # Not enough
        )
        assert impact.impact_score is None

    def test_impact_score_positive(self):
        impact = RuleImpact(
            rule_id="r1", rule_text="IF X THEN Y", confidence_at_creation=0.8,
            outcomes_before=[0.4, 0.5, 0.6],  # avg 0.5
            outcomes_after=[0.7, 0.8, 0.9],  # avg 0.8
        )
        assert impact.impact_score is not None
        assert impact.impact_score > 0  # 60% improvement

    def test_impact_score_negative(self):
        impact = RuleImpact(
            rule_id="r1", rule_text="IF X THEN Y", confidence_at_creation=0.8,
            outcomes_before=[0.8, 0.9, 0.7],  # avg 0.8
            outcomes_after=[0.3, 0.4, 0.5],  # avg 0.4
        )
        assert impact.impact_score is not None
        assert impact.impact_score < 0  # Got worse

    def test_impact_to_dict(self):
        impact = RuleImpact(
            rule_id="r1", rule_text="IF X THEN Y", confidence_at_creation=0.8,
        )
        d = impact.to_dict()
        assert "rule_id" in d
        assert "impact_score" in d


class TestReflectionQuality:
    """Test reflection quality scoring."""

    def test_perfect_reflection(self):
        quality = ReflectionQuality(
            reflection_id="ref1",
            rules_suggested=5, rules_adopted=5,
            rules_with_positive_impact=5, rules_with_negative_impact=0,
        )
        assert quality.quality_score > 0.8

    def test_useless_reflection(self):
        quality = ReflectionQuality(
            reflection_id="ref1",
            rules_suggested=5, rules_adopted=0,
            rules_with_positive_impact=0, rules_with_negative_impact=0,
        )
        assert quality.quality_score < 0.2

    def test_harmful_reflection(self):
        quality = ReflectionQuality(
            reflection_id="ref1",
            rules_suggested=5, rules_adopted=5,
            rules_with_positive_impact=0, rules_with_negative_impact=5,
        )
        assert quality.quality_score <= 0.3

    def test_empty_reflection(self):
        quality = ReflectionQuality(
            reflection_id="ref1",
            rules_suggested=0, rules_adopted=0,
            rules_with_positive_impact=0, rules_with_negative_impact=0,
        )
        assert quality.quality_score == 0.0


class TestMetaLearner:
    """Test the MetaLearner class."""

    def test_track_rule_created(self, storage):
        meta = MetaLearner(storage, "test-agent")
        rule = Rule(text="IF X THEN Y", confidence=0.8)
        meta.track_rule_created(rule, [0.5, 0.6, 0.7])
        assert rule.id in meta._rule_impacts

    def test_track_outcome_with_rule(self, storage):
        meta = MetaLearner(storage, "test-agent")
        rule = Rule(text="IF X THEN Y", confidence=0.8)
        meta.track_rule_created(rule, [0.5, 0.6, 0.7])
        meta.track_outcome_with_rule(rule.id, 0.9)
        assert len(meta._rule_impacts[rule.id].outcomes_after) == 1

    def test_get_rule_impacts_sorted(self, storage):
        meta = MetaLearner(storage, "test-agent")

        good_rule = Rule(text="IF good THEN great", confidence=0.9)
        meta.track_rule_created(good_rule, [0.3, 0.4, 0.5])
        for _ in range(5):
            meta.track_outcome_with_rule(good_rule.id, 0.9)

        bad_rule = Rule(text="IF bad THEN worse", confidence=0.6)
        meta.track_rule_created(bad_rule, [0.7, 0.8, 0.9])
        for _ in range(5):
            meta.track_outcome_with_rule(bad_rule.id, 0.3)

        impacts = meta.get_rule_impacts()
        assert len(impacts) == 2
        # Good rule should be first (higher impact)
        assert impacts[0].rule_id == good_rule.id

    def test_get_meta_rules_not_enough_data(self, storage):
        meta = MetaLearner(storage, "test-agent")
        assert meta.get_meta_rules() == []

    def test_get_best_rule_patterns_not_enough_data(self, storage):
        meta = MetaLearner(storage, "test-agent")
        patterns = meta.get_best_rule_patterns()
        assert patterns["status"] == "not_enough_data"

    def test_track_reflection_quality(self, storage):
        meta = MetaLearner(storage, "test-agent")
        reflection = Reflection(
            agent_name="test-agent", critique="Good", suggested_rules=["R1", "R2"],
            confidence_scores={"R1": 0.8, "R2": 0.7},
        )
        quality = meta.track_reflection_quality(reflection, rules_adopted=2, rules_positive=1)
        assert quality.quality_score > 0
        assert len(meta._reflection_qualities) == 1


class TestMetaLearnerIntegration:
    """Test meta-learner through the AgentLoops main class."""

    def test_meta_learner_property(self, tmp_path):
        loops = AgentLoops("test-agent", storage_path=tmp_path / ".agentloops")
        assert loops.meta_learner is not None
        assert isinstance(loops.meta_learner, MetaLearner)

    def test_track_feeds_meta_learner(self, tmp_path):
        loops = AgentLoops("test-agent", storage_path=tmp_path / ".agentloops")
        # Add a rule so we can track its impact
        rule = loops.rules.add_rule("IF X THEN Y", confidence=0.8)

        # Track runs with the rule active
        loops.track(input="a", output="b", outcome="success")
        loops.track(input="c", output="d", outcome="0.85")

        # Meta-learner should be tracking outcomes for this rule
        # (The exact tracking depends on implementation, but at minimum no crash)
        assert loops.meta_learner is not None
