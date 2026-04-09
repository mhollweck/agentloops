"""Tests for the Quality Gate mechanism."""

from __future__ import annotations

import pytest

from agentloops.core import AgentLoops
from agentloops.quality_gate import (
    GateResult,
    QualityGate,
    _check_max_length,
    _check_min_length,
    _check_no_hallucination_markers,
    _check_not_empty,
)
from agentloops.storage.file import FileStorage


class TestBuiltinChecks:
    """Test individual check functions."""

    def test_empty_output_fails(self):
        result = _check_not_empty("")
        assert result is not None
        assert result["severity"] == "fail"

    def test_whitespace_only_fails(self):
        result = _check_not_empty("   \n  ")
        assert result is not None
        assert result["severity"] == "fail"

    def test_valid_output_passes(self):
        result = _check_not_empty("Hello, world!")
        assert result is None

    def test_short_output_warns(self):
        result = _check_min_length("Hi", min_length=10)
        assert result is not None
        assert result["severity"] == "warn"

    def test_long_enough_output_passes(self):
        result = _check_min_length("This is long enough", min_length=10)
        assert result is None

    def test_too_long_output_warns(self):
        result = _check_max_length("x" * 60000, max_length=50000)
        assert result is not None
        assert result["severity"] == "warn"

    def test_normal_length_passes(self):
        result = _check_max_length("Normal output", max_length=50000)
        assert result is None

    def test_hallucination_marker_detected(self):
        result = _check_no_hallucination_markers("As an AI language model, I cannot help with that.")
        assert result is not None
        assert "hallucination" in result["check"]

    def test_no_hallucination_markers(self):
        result = _check_no_hallucination_markers("Here is the API monitoring report for Q4.")
        assert result is None

    def test_case_insensitive_hallucination_check(self):
        result = _check_no_hallucination_markers("i don't have access to that information")
        assert result is not None


class TestQualityGate:
    """Test the QualityGate class."""

    def test_empty_output_fails_gate(self, storage):
        gate = QualityGate(storage, "test-agent")
        result = gate.check(output="")
        assert not result.passed
        assert result.checks_failed > 0
        assert any(f["check"] == "not_empty" for f in result.failures)

    def test_valid_output_passes_gate(self, storage):
        gate = QualityGate(storage, "test-agent")
        result = gate.check(output="Here is your detailed API monitoring report with metrics.")
        assert result.passed
        assert result.score > 0.7

    def test_gate_result_structure(self, storage):
        gate = QualityGate(storage, "test-agent")
        result = gate.check(output="Valid output text for testing.")
        assert isinstance(result, GateResult)
        assert isinstance(result.passed, bool)
        assert 0.0 <= result.score <= 1.0
        assert result.checks_total > 0
        assert result.checks_passed + result.checks_failed == result.checks_total

    def test_custom_check_function(self, storage):
        def check_no_profanity(output: str, **kwargs) -> dict | None:
            bad_words = ["damn", "hell"]
            for word in bad_words:
                if word in output.lower():
                    return {"check": "profanity", "severity": "fail", "message": f"Contains: {word}"}
            return None

        gate = QualityGate(storage, "test-agent", custom_checks=[check_no_profanity])
        result = gate.check(output="What the hell is this?")
        assert not result.passed
        assert any(f["check"] == "profanity" for f in result.failures)

    def test_custom_check_passes(self, storage):
        def check_has_greeting(output: str, **kwargs) -> dict | None:
            if not any(g in output.lower() for g in ["hi", "hello", "hey"]):
                return {"check": "greeting", "severity": "warn", "message": "No greeting"}
            return None

        gate = QualityGate(storage, "test-agent", custom_checks=[check_has_greeting])
        result = gate.check(output="Hello! Here is your report.")
        assert result.passed

    def test_pass_threshold_configurable(self, storage):
        gate = QualityGate(storage, "test-agent", pass_threshold=1.0)
        # Short output triggers a warning (not a failure) — score still 1.0
        result = gate.check(output="Short")
        assert result.passed  # Warnings don't lower score
        assert len(result.warnings) > 0  # But warning is recorded

        # Empty output IS a failure — should not pass even at lower threshold
        gate2 = QualityGate(storage, "test-agent", pass_threshold=0.5)
        result2 = gate2.check(output="")
        assert not result2.passed

    def test_gate_to_dict(self, storage):
        gate = QualityGate(storage, "test-agent")
        result = gate.check(output="Valid output text for testing purposes.")
        d = result.to_dict()
        assert "passed" in d
        assert "score" in d
        assert "failures" in d
        assert "warnings" in d


class TestRuleBasedChecks:
    """Test quality gate's rule-based violation detection."""

    def test_listicle_rule_violation(self, storage, sample_rules):
        # Add an anti-listicle rule
        from agentloops.models import Rule
        rule = Rule(
            text="IF subject style is listicle AND enterprise THEN avoid — because listicles get ignored",
            confidence=0.85,
        )
        storage.save_rule(rule)

        gate = QualityGate(storage, "test-agent")
        result = gate.check(output="Subject: 'Top 5 API monitoring tools compared'\nBody: Here are the top 5...")
        # Should have a warning since rule confidence < 0.8... wait, 0.85 >= 0.8 so it's a fail
        assert any(
            item.get("check") == "rule_violation"
            for item in result.failures + result.warnings
        )

    def test_no_violation_when_no_avoid_rules(self, storage):
        from agentloops.models import Rule
        rule = Rule(
            text="IF prospect is VP THEN lead with a technical observation",
            confidence=0.9,
        )
        storage.save_rule(rule)

        gate = QualityGate(storage, "test-agent")
        result = gate.check(output="Top 5 tools compared")
        # Non-"avoid" rules don't trigger checks
        rule_violations = [
            item for item in result.failures + result.warnings
            if item.get("check") == "rule_violation"
        ]
        assert len(rule_violations) == 0


class TestQualityGateIntegration:
    """Test quality gate through the AgentLoops main class."""

    def test_check_method_accessible(self, tmp_path):
        loops = AgentLoops("test-agent", storage_path=tmp_path / ".agentloops")
        result = loops.check(output="Valid output for testing.")
        assert isinstance(result, GateResult)
        assert result.passed

    def test_check_empty_fails(self, tmp_path):
        loops = AgentLoops("test-agent", storage_path=tmp_path / ".agentloops")
        result = loops.check(output="")
        assert not result.passed

    def test_quality_gate_property(self, tmp_path):
        loops = AgentLoops("test-agent", storage_path=tmp_path / ".agentloops")
        assert loops.quality_gate is not None
        assert isinstance(loops.quality_gate, QualityGate)

    def test_gate_uses_learned_rules(self, tmp_path):
        loops = AgentLoops("test-agent", storage_path=tmp_path / ".agentloops")
        loops.rules.add_rule(
            "IF subject style is listicle THEN avoid — 0/2 success rate",
            confidence=0.9,
        )
        result = loops.check(output="Top 10 ways to improve your API monitoring")
        violations = [f for f in result.failures + result.warnings if f.get("check") == "rule_violation"]
        assert len(violations) > 0

    def test_pass_threshold_settable(self, tmp_path):
        loops = AgentLoops("test-agent", storage_path=tmp_path / ".agentloops")
        loops.quality_gate.pass_threshold = 0.5
        assert loops.quality_gate.pass_threshold == 0.5
