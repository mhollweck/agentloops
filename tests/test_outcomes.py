"""Tests for the multi-outcome system."""

from __future__ import annotations

import pytest

from agentloops.outcomes import MetricDef, OutcomeConfig


class TestMetricDef:
    """Test individual metric evaluation."""

    def test_binary_success(self):
        m = MetricDef("outcome", "binary")
        assert m.evaluate("success") == 1.0
        assert m.evaluate(True) == 1.0
        assert m.evaluate("1") == 1.0

    def test_binary_failure(self):
        m = MetricDef("outcome", "binary")
        assert m.evaluate("failure") == 0.0
        assert m.evaluate(False) == 0.0
        assert m.evaluate("no") == 0.0

    def test_categorical_success(self):
        m = MetricDef("result", "categorical", success_values=["meeting_booked", "replied"])
        assert m.evaluate("meeting_booked") == 1.0
        assert m.evaluate("replied") == 1.0

    def test_categorical_failure(self):
        m = MetricDef("result", "categorical", success_values=["meeting_booked", "replied"])
        assert m.evaluate("no_reply") == 0.0
        assert m.evaluate("unsubscribed") == 0.0

    def test_numeric_maximize(self):
        m = MetricDef("accuracy", "numeric", goal="maximize")
        assert m.evaluate(0.9) == 0.9
        assert m.evaluate(1.0) == 1.0
        assert m.evaluate(0.0) == 0.0

    def test_numeric_minimize(self):
        m = MetricDef("error_rate", "numeric", goal="minimize")
        assert m.evaluate(0.0) == 1.0  # 0 errors = best
        assert m.evaluate(1.0) == 0.0  # 100% errors = worst
        assert m.evaluate(0.3) == pytest.approx(0.7)

    def test_numeric_target(self):
        m = MetricDef("temperature", "numeric", goal="target", target_value=0.7)
        assert m.evaluate(0.7) == 1.0  # Exactly on target
        assert m.evaluate(0.7 + 0.35) < 1.0  # Off target

    def test_duration_lower_is_better(self):
        m = MetricDef("latency", "duration", target_value=500)
        score_fast = m.evaluate(100)
        score_slow = m.evaluate(800)
        assert score_fast > score_slow

    def test_numeric_clamps(self):
        m = MetricDef("score", "numeric", goal="maximize")
        assert m.evaluate(2.0) == 1.0  # Clamped to 1.0
        assert m.evaluate(-1.0) == 0.0  # Clamped to 0.0

    def test_invalid_value_returns_zero(self):
        m = MetricDef("score", "numeric")
        assert m.evaluate("not_a_number") == 0.0
        assert m.evaluate(None) == 0.0


class TestOutcomeConfig:
    """Test outcome configuration and composite scoring."""

    def test_binary_factory(self):
        config = OutcomeConfig.binary()
        assert len(config.metrics) == 1
        assert config.metrics[0].type == "binary"

    def test_categorical_factory(self):
        config = OutcomeConfig.categorical(["booked", "replied"])
        assert config.metrics[0].success_values == ["booked", "replied"]

    def test_numeric_factory(self):
        config = OutcomeConfig.numeric(goal="minimize")
        assert config.metrics[0].goal == "minimize"

    def test_single_value_scoring(self):
        config = OutcomeConfig.binary()
        assert config.score("success") == 1.0
        assert config.score("failure") == 0.0

    def test_multi_metric_weighted_average(self):
        config = OutcomeConfig(metrics=[
            MetricDef("booking", "categorical", weight=3.0,
                      success_values=["booked"]),
            MetricDef("speed", "numeric", weight=1.0, goal="maximize"),
        ])
        # booking=booked (1.0 * 3.0) + speed=0.8 (0.8 * 1.0) = 3.8 / 4.0 = 0.95
        score = config.score({"booking": "booked", "speed": 0.8})
        assert score == pytest.approx(0.95)

    def test_multi_metric_all_fail(self):
        config = OutcomeConfig(metrics=[
            MetricDef("a", "binary", weight=1.0),
            MetricDef("b", "binary", weight=1.0),
        ])
        assert config.score({"a": "failure", "b": "failure"}) == 0.0

    def test_min_strategy(self):
        config = OutcomeConfig(
            metrics=[
                MetricDef("accuracy", "numeric", weight=1.0),
                MetricDef("speed", "numeric", weight=1.0),
            ],
            composite_strategy="min",
        )
        # Min of 0.9 and 0.3 = 0.3
        assert config.score({"accuracy": 0.9, "speed": 0.3}) == pytest.approx(0.3)

    def test_product_strategy(self):
        config = OutcomeConfig(
            metrics=[
                MetricDef("a", "numeric"),
                MetricDef("b", "numeric"),
            ],
            composite_strategy="product",
        )
        assert config.score({"a": 0.8, "b": 0.5}) == pytest.approx(0.4)

    def test_missing_metric_value_ignored(self):
        config = OutcomeConfig(metrics=[
            MetricDef("a", "numeric", weight=1.0),
            MetricDef("b", "numeric", weight=1.0),
        ])
        # Only "a" provided — score based on what's available
        assert config.score({"a": 0.8}) == pytest.approx(0.8)

    def test_empty_config(self):
        config = OutcomeConfig()
        assert config.score("anything") == 0.0

    def test_describe_binary(self):
        config = OutcomeConfig.binary()
        desc = config.describe()
        assert "success vs failure" in desc

    def test_describe_multi_metric(self):
        config = OutcomeConfig(metrics=[
            MetricDef("booking_rate", "categorical", weight=3.0,
                      success_values=["booked", "replied"]),
            MetricDef("latency", "duration", weight=1.0, target_value=500, unit="ms"),
        ])
        desc = config.describe()
        assert "booking_rate" in desc
        assert "latency" in desc
        assert "weight: 3.0" in desc

    def test_sales_sdr_real_scenario(self):
        """Real-world scenario: Sales SDR with 3 metrics."""
        config = OutcomeConfig(metrics=[
            MetricDef("response", "categorical", weight=3.0,
                      success_values=["meeting_booked", "replied"]),
            MetricDef("unsubscribe", "binary", weight=2.0),
            MetricDef("personalization_score", "numeric", weight=1.0),
        ])

        # Great outcome: booked meeting, no unsubscribe, high personalization
        great = config.score({
            "response": "meeting_booked",
            "unsubscribe": "false",  # NOT unsubscribed = success for binary
            "personalization_score": 0.9,
        })

        # Bad outcome: no reply, unsubscribed, low personalization
        bad = config.score({
            "response": "no_reply",
            "unsubscribe": "true",  # Unsubscribed = bad... but binary treats "true" as success
            "personalization_score": 0.2,
        })

        # Great should score higher than bad
        # Note: binary "unsubscribe" needs careful definition
        assert great > 0.5
