"""Tests for the AgentLoops core orchestrator."""

from __future__ import annotations

from unittest.mock import patch

from agentloops.core import AgentLoops
from agentloops.models import Rule
from agentloops.storage.file import FileStorage


class TestInitialization:
    def test_init_with_defaults(self, tmp_path):
        loops = AgentLoops("test-agent", storage_path=tmp_path / ".agentloops")
        assert loops.agent_name == "test-agent"

    def test_init_with_custom_storage(self, tmp_path):
        storage = FileStorage(tmp_path / ".agentloops", "test-agent")
        loops = AgentLoops("test-agent", storage=storage)
        assert loops.agent_name == "test-agent"

    def test_init_invalid_storage_string(self, tmp_path):
        import pytest
        with pytest.raises(ValueError, match="Unknown storage type"):
            AgentLoops("test-agent", storage="redis")

    def test_properties_accessible(self, tmp_path):
        loops = AgentLoops("test-agent", storage_path=tmp_path / ".agentloops")
        assert loops.tracker is not None
        assert loops.rules is not None
        assert loops.conventions is not None


class TestTrack:
    def test_track_stores_run(self, tmp_path):
        loops = AgentLoops("test-agent", storage_path=tmp_path / ".agentloops")
        run = loops.track(input="hello", output="world", outcome="success")
        assert run.input == "hello"
        assert run.output == "world"
        assert run.outcome == "success"

    def test_track_persists(self, tmp_path):
        loops = AgentLoops("test-agent", storage_path=tmp_path / ".agentloops")
        loops.track(input="a", output="b", outcome="success")
        loops.track(input="c", output="d", outcome="failure")

        runs = loops.tracker.get_runs()
        assert len(runs) == 2

    def test_track_includes_active_rule_ids(self, tmp_path):
        loops = AgentLoops("test-agent", storage_path=tmp_path / ".agentloops")
        rule = loops.rules.add_rule("IF X THEN Y", confidence=0.8)
        run = loops.track(input="a", output="b", outcome="success")
        assert rule.id in run.rules_applied

    def test_track_with_metadata(self, tmp_path):
        loops = AgentLoops("test-agent", storage_path=tmp_path / ".agentloops")
        run = loops.track(
            input="a",
            output="b",
            outcome="success",
            metadata={"latency": 100},
        )
        assert run.metadata["latency"] == 100


class TestEnhancePrompt:
    def test_no_rules_returns_base_unchanged(self, tmp_path):
        loops = AgentLoops("test-agent", storage_path=tmp_path / ".agentloops")
        base = "You are a helpful assistant."
        assert loops.enhance_prompt(base) == base

    def test_with_active_rules(self, tmp_path):
        loops = AgentLoops("test-agent", storage_path=tmp_path / ".agentloops")
        loops.rules.add_rule("IF pricing question THEN show table", confidence=0.9)

        enhanced = loops.enhance_prompt("You are a helpful assistant.")
        assert "Decision Rules" in enhanced
        assert "pricing question" in enhanced
        assert "confidence: 0.90" in enhanced

    def test_with_conventions(self, tmp_path):
        loops = AgentLoops("test-agent", storage_path=tmp_path / ".agentloops")
        loops.conventions.add("Always greet by name")

        enhanced = loops.enhance_prompt("Base prompt.")
        assert "Conventions" in enhanced
        assert "Always greet by name" in enhanced

    def test_with_rules_and_conventions(self, tmp_path):
        loops = AgentLoops("test-agent", storage_path=tmp_path / ".agentloops")
        loops.rules.add_rule("IF X THEN Y", confidence=0.8)
        loops.conventions.add("Be concise")

        enhanced = loops.enhance_prompt("Base prompt.")
        assert "Decision Rules" in enhanced
        assert "Conventions" in enhanced
        assert enhanced.startswith("Base prompt.")

    def test_enhance_prompt_preserves_base(self, tmp_path):
        loops = AgentLoops("test-agent", storage_path=tmp_path / ".agentloops")
        loops.rules.add_rule("IF X THEN Y", confidence=0.8)

        base = "You are an expert sales agent. Be persuasive."
        enhanced = loops.enhance_prompt(base)
        assert enhanced.startswith(base)


class TestForget:
    def test_forget_returns_pruned_ids(self, tmp_path):
        loops = AgentLoops("test-agent", storage_path=tmp_path / ".agentloops")
        result = loops.forget(strategy="decay", max_age_days=21)
        assert "rules_pruned" in result
        assert "conventions_pruned" in result
        assert isinstance(result["rules_pruned"], list)
        assert isinstance(result["conventions_pruned"], list)
