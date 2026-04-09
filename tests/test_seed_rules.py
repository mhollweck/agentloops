"""Tests for pre-seeded agent type rules."""

from __future__ import annotations

import pytest

from agentloops.core import AgentLoops
from agentloops.seed_rules import SEED_RULES, get_seed_rules, list_agent_types


class TestSeedRules:
    """Test the seed rules module."""

    def test_all_agent_types_have_rules(self):
        for agent_type in list_agent_types():
            rules = get_seed_rules(agent_type)
            assert len(rules) >= 2, f"{agent_type} should have at least 2 seed rules"

    def test_unknown_type_returns_empty(self):
        rules = get_seed_rules("nonexistent-type")
        assert rules == []

    def test_rules_have_valid_confidence(self):
        for agent_type in list_agent_types():
            for rule in get_seed_rules(agent_type):
                assert 0.0 <= rule.confidence <= 1.0, f"Invalid confidence for {agent_type}: {rule.confidence}"

    def test_rules_have_evidence(self):
        for agent_type in list_agent_types():
            for rule in get_seed_rules(agent_type):
                assert len(rule.evidence) > 0, f"No evidence for rule in {agent_type}: {rule.text[:50]}"

    def test_rules_are_if_then_format(self):
        for agent_type in list_agent_types():
            for rule in get_seed_rules(agent_type):
                text_lower = rule.text.lower()
                assert "if" in text_lower and "then" in text_lower, (
                    f"Rule not in IF/THEN format for {agent_type}: {rule.text[:50]}"
                )

    def test_list_agent_types_returns_all(self):
        types = list_agent_types()
        assert "sales-sdr" in types
        assert "customer-support" in types
        assert "content-creator" in types
        assert "code-generator" in types
        assert len(types) == 10  # All 10 agent types

    def test_seed_rules_data_consistency(self):
        """Verify SEED_RULES dict structure is valid."""
        for agent_type, rules in SEED_RULES.items():
            for text, confidence, evidence in rules:
                assert isinstance(text, str) and len(text) > 10
                assert isinstance(confidence, float) and 0.0 <= confidence <= 1.0
                assert isinstance(evidence, list) and all(isinstance(e, str) for e in evidence)


class TestSeedRulesIntegration:
    """Test seed rules loading through AgentLoops."""

    def test_agent_type_loads_seed_rules(self, tmp_path):
        loops = AgentLoops(
            "test-sdr",
            storage_path=tmp_path / ".agentloops",
            agent_type="sales-sdr",
        )
        rules = loops.rules.active()
        assert len(rules) >= 2  # Should have seed rules
        # Check that at least one seed rule text is present
        rule_texts = [r.text for r in rules]
        assert any("VP" in t or "prospect" in t.lower() for t in rule_texts)

    def test_seed_rules_not_loaded_without_type(self, tmp_path):
        loops = AgentLoops(
            "test-generic",
            storage_path=tmp_path / ".agentloops",
        )
        rules = loops.rules.active()
        assert len(rules) == 0

    def test_seed_rules_not_loaded_if_rules_exist(self, tmp_path):
        # First instance — loads seeds
        loops1 = AgentLoops(
            "test-sdr",
            storage_path=tmp_path / ".agentloops",
            agent_type="sales-sdr",
        )
        initial_count = len(loops1.rules.active())
        assert initial_count >= 2

        # Add a manual rule
        loops1.rules.add_rule("IF test THEN test", confidence=0.5)

        # Second instance — should NOT reload seeds (rules already exist)
        loops2 = AgentLoops(
            "test-sdr",
            storage_path=tmp_path / ".agentloops",
            agent_type="sales-sdr",
        )
        final_count = len(loops2.rules.active())
        assert final_count == initial_count + 1  # Only the manually added rule, no new seeds

    def test_enhance_prompt_includes_seed_rules(self, tmp_path):
        loops = AgentLoops(
            "test-support",
            storage_path=tmp_path / ".agentloops",
            agent_type="customer-support",
        )
        enhanced = loops.enhance_prompt("You are a support agent.")
        assert "Decision Rules" in enhanced
        assert "frustration" in enhanced.lower() or "escalat" in enhanced.lower()

    def test_all_agent_types_load_without_error(self, tmp_path):
        for agent_type in list_agent_types():
            loops = AgentLoops(
                f"test-{agent_type}",
                storage_path=tmp_path / ".agentloops",
                agent_type=agent_type,
            )
            rules = loops.rules.active()
            assert len(rules) >= 2, f"{agent_type} should load at least 2 rules"
