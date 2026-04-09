"""Tests for framework adapters (LangChain, CrewAI)."""

from __future__ import annotations

from uuid import uuid4

import pytest

from agentloops.adapters.langchain import AgentLoopsCallback, _serialize
from agentloops.adapters.crewai import AgentLoopsCrewCallback
from agentloops.core import AgentLoops


class TestLangChainAdapter:
    """Test the LangChain callback adapter."""

    def test_chain_start_and_end_tracks_run(self, tmp_path):
        loops = AgentLoops("test-agent", storage_path=tmp_path / ".agentloops")
        callback = AgentLoopsCallback(loops)

        run_id = uuid4()
        callback.on_chain_start(
            serialized={"name": "test_chain"},
            inputs={"input": "What is the weather?"},
            run_id=run_id,
        )
        callback.on_chain_end(
            outputs={"output": "It's sunny and 72°F"},
            run_id=run_id,
        )

        runs = loops.tracker.get_runs()
        assert len(runs) == 1
        assert runs[0].outcome == "success"
        assert runs[0].metadata["source"] == "langchain"
        assert runs[0].metadata["chain_name"] == "test_chain"
        assert "latency_ms" in runs[0].metadata

    def test_chain_error_tracks_failure(self, tmp_path):
        loops = AgentLoops("test-agent", storage_path=tmp_path / ".agentloops")
        callback = AgentLoopsCallback(loops)

        run_id = uuid4()
        callback.on_chain_start(
            serialized={"name": "failing_chain"},
            inputs={"input": "trigger error"},
            run_id=run_id,
        )
        callback.on_chain_error(
            error=ValueError("Something went wrong"),
            run_id=run_id,
        )

        runs = loops.tracker.get_runs()
        assert len(runs) == 1
        assert runs[0].outcome == "failure"
        assert "ValueError" in runs[0].output
        assert runs[0].metadata["error_type"] == "ValueError"

    def test_custom_outcome_function(self, tmp_path):
        loops = AgentLoops("test-agent", storage_path=tmp_path / ".agentloops")

        def outcome_fn(inputs, outputs):
            return "booked" if "meeting" in str(outputs).lower() else "missed"

        callback = AgentLoopsCallback(loops, outcome_fn=outcome_fn)

        run_id = uuid4()
        callback.on_chain_start(
            serialized={"name": "sales_chain"},
            inputs={"input": "reach out to CEO"},
            run_id=run_id,
        )
        callback.on_chain_end(
            outputs={"output": "Meeting booked for Tuesday"},
            run_id=run_id,
        )

        runs = loops.tracker.get_runs()
        assert runs[0].outcome == "booked"

    def test_orphaned_end_ignored(self, tmp_path):
        loops = AgentLoops("test-agent", storage_path=tmp_path / ".agentloops")
        callback = AgentLoopsCallback(loops)

        # End without start — should not crash or track
        callback.on_chain_end(
            outputs={"output": "orphaned"},
            run_id=uuid4(),
        )
        assert len(loops.tracker.get_runs()) == 0

    def test_llm_tracking_disabled_by_default(self, tmp_path):
        loops = AgentLoops("test-agent", storage_path=tmp_path / ".agentloops")
        callback = AgentLoopsCallback(loops)

        run_id = uuid4()
        callback.on_llm_start(
            serialized={"kwargs": {"model": "claude-sonnet-4-6"}},
            prompts=["Hello"],
            run_id=run_id,
        )
        callback.on_llm_end(response="Hi!", run_id=run_id)

        assert len(loops.tracker.get_runs()) == 0

    def test_llm_tracking_enabled(self, tmp_path):
        loops = AgentLoops("test-agent", storage_path=tmp_path / ".agentloops")
        callback = AgentLoopsCallback(loops, track_llm_calls=True)

        run_id = uuid4()
        callback.on_llm_start(
            serialized={"kwargs": {"model": "claude-sonnet-4-6"}},
            prompts=["Hello"],
            run_id=run_id,
        )
        callback.on_llm_end(response="Hi!", run_id=run_id)

        runs = loops.tracker.get_runs()
        assert len(runs) == 1
        assert runs[0].metadata["source"] == "langchain_llm"


class TestCrewAIAdapter:
    """Test the CrewAI callback adapter."""

    def test_task_complete_tracks_run(self, tmp_path):
        loops = AgentLoops("test-crew", storage_path=tmp_path / ".agentloops")
        callback = AgentLoopsCrewCallback(loops)

        # Mock a CrewAI task
        class MockTask:
            description = "Research competitor pricing"
            agent = type("Agent", (), {"role": "Researcher"})()

        callback.on_task_complete(MockTask(), output="Found 5 competitors with pricing data")

        runs = loops.tracker.get_runs()
        assert len(runs) == 1
        assert "competitor" in runs[0].input.lower()
        assert runs[0].metadata["source"] == "crewai"
        assert runs[0].metadata["agent_role"] == "Researcher"

    def test_crew_complete_tracks_run(self, tmp_path):
        loops = AgentLoops("test-crew", storage_path=tmp_path / ".agentloops")
        callback = AgentLoopsCrewCallback(loops)

        class MockTask:
            description = "Step 1"

        class MockCrew:
            tasks = [MockTask()]

        crew = MockCrew()
        callback.on_crew_start(crew)
        import time; time.sleep(0.01)  # Ensure measurable latency
        callback.on_crew_complete(crew, result="Crew completed all tasks")

        runs = loops.tracker.get_runs()
        assert len(runs) == 1
        assert runs[0].metadata["source"] == "crewai_crew"
        assert "latency_ms" in runs[0].metadata

    def test_custom_outcome_function(self, tmp_path):
        loops = AgentLoops("test-crew", storage_path=tmp_path / ".agentloops")

        def outcome_fn(desc, output):
            return "0.9" if "success" in output.lower() else "0.3"

        callback = AgentLoopsCrewCallback(loops, outcome_fn=outcome_fn)

        class MockTask:
            description = "Check support ticket"
            agent = None

        callback.on_task_complete(MockTask(), output="Successfully resolved ticket")
        runs = loops.tracker.get_runs()
        assert runs[0].outcome == "0.9"


class TestSerialize:
    """Test the _serialize helper."""

    def test_string_passthrough(self):
        assert _serialize("hello") == "hello"

    def test_dict_with_input_key(self):
        assert _serialize({"input": "test", "other": "data"}) == "test"

    def test_dict_with_output_key(self):
        assert _serialize({"output": "result"}) == "result"

    def test_dict_without_known_keys(self):
        result = _serialize({"foo": "bar"})
        assert "foo" in result

    def test_other_types(self):
        assert _serialize(42) == "42"
        assert _serialize([1, 2, 3]) == "[1, 2, 3]"
