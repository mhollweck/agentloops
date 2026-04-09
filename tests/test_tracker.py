"""Tests for the Tracker module."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

from agentloops.models import Run
from agentloops.tracker import Tracker


class TestLogRun:
    def test_log_run_returns_run_object(self, storage):
        tracker = Tracker(storage, "test-agent")
        run = tracker.log_run(
            input="hello",
            output="world",
            outcome="success",
        )
        assert isinstance(run, Run)
        assert run.input == "hello"
        assert run.output == "world"
        assert run.outcome == "success"
        assert run.agent_name == "test-agent"

    def test_log_run_persists(self, storage):
        tracker = Tracker(storage, "test-agent")
        tracker.log_run(input="a", output="b", outcome="success")
        tracker.log_run(input="c", output="d", outcome="failure")

        runs = tracker.get_runs()
        assert len(runs) == 2

    def test_log_run_with_metadata(self, storage):
        tracker = Tracker(storage, "test-agent")
        run = tracker.log_run(
            input="x",
            output="y",
            outcome="success",
            metadata={"latency_ms": 150, "tokens": 500},
        )
        assert run.metadata["latency_ms"] == 150
        assert run.metadata["tokens"] == 500

    def test_log_run_with_rules_applied(self, storage):
        tracker = Tracker(storage, "test-agent")
        run = tracker.log_run(
            input="x",
            output="y",
            outcome="success",
            rules_applied=["rule-1", "rule-2"],
        )
        assert run.rules_applied == ["rule-1", "rule-2"]


class TestGetRuns:
    def test_get_runs_all(self, storage, sample_runs):
        tracker = Tracker(storage, "test-agent")
        runs = tracker.get_runs()
        assert len(runs) == 10

    def test_get_runs_last_n(self, storage, sample_runs):
        tracker = Tracker(storage, "test-agent")
        runs = tracker.get_runs(last_n=3)
        assert len(runs) == 3
        # Should be the last 3
        assert runs[-1].input == "test input 9"

    def test_get_runs_outcome_filter(self, storage, sample_runs):
        tracker = Tracker(storage, "test-agent")
        successes = tracker.get_runs(outcome_filter="success")
        failures = tracker.get_runs(outcome_filter="failure")
        assert all(r.outcome == "success" for r in successes)
        assert all(r.outcome == "failure" for r in failures)
        assert len(successes) + len(failures) == 10

    def test_get_runs_empty(self, storage):
        tracker = Tracker(storage, "test-agent")
        assert tracker.get_runs() == []


class TestCorrelate:
    def test_correlate_with_and_without_rule(self, storage, sample_runs):
        tracker = Tracker(storage, "test-agent")
        result = tracker.correlate("rule-1")
        assert result["rule_id"] == "rule-1"
        assert result["with_rule"]["count"] == 5  # runs 5-9
        assert result["without_rule"]["count"] == 5  # runs 0-4

    def test_correlate_nonexistent_rule(self, storage, sample_runs):
        tracker = Tracker(storage, "test-agent")
        result = tracker.correlate("nonexistent")
        assert result["with_rule"]["count"] == 0
        assert result["without_rule"]["count"] == 10

    def test_correlate_empty_runs(self, storage):
        tracker = Tracker(storage, "test-agent")
        result = tracker.correlate("rule-1")
        assert result["with_rule"]["count"] == 0
        assert result["without_rule"]["count"] == 0


class TestImprovementCurve:
    def test_improvement_curve_success_rate(self, storage, sample_runs):
        tracker = Tracker(storage, "test-agent")
        curve = tracker.improvement_curve(metric="success_rate", window_days=3)
        assert len(curve) > 0
        for point in curve:
            assert "success_rate" in point
            assert "run_count" in point
            assert 0 <= point["success_rate"] <= 1

    def test_improvement_curve_empty(self, storage):
        tracker = Tracker(storage, "test-agent")
        curve = tracker.improvement_curve()
        assert curve == []

    def test_improvement_curve_avg_score(self, storage):
        tracker = Tracker(storage, "test-agent")
        base_time = datetime.now(timezone.utc) - timedelta(days=5)
        for i in range(5):
            run = Run(
                input=f"input {i}",
                output=f"output {i}",
                outcome=str(float(i + 1)),
                agent_name="test-agent",
                created_at=(base_time + timedelta(days=i)).isoformat(),
            )
            storage.save_run(run)

        curve = tracker.improvement_curve(metric="avg_score", window_days=2)
        assert len(curve) > 0
        for point in curve:
            assert "avg_score" in point
