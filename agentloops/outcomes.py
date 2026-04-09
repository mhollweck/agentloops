"""Outcome definitions — how agents know what to optimize for.

Outcomes tell the learning system what "good" looks like. AgentLoops supports
multiple outcome models:

1. Binary: "success" / "failure"
2. Categorical: "meeting_booked" / "replied" / "no_reply" / "unsubscribed"
3. Numeric: 0.0 to 1.0 score
4. Multi-metric: {"accuracy": 0.92, "latency_ms": 150, "user_satisfaction": 4.5}

The OutcomeConfig defines which metrics matter and how to weight them,
giving the reflection engine clear optimization targets.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class MetricDef:
    """Definition of a single outcome metric."""

    name: str
    type: str  # "binary", "categorical", "numeric", "duration"
    weight: float = 1.0  # Relative importance (for multi-metric)
    goal: str = "maximize"  # "maximize", "minimize", "target"
    target_value: float | None = None  # For goal="target"
    success_values: list[str] | None = None  # For categorical: which values count as success
    unit: str = ""  # Optional unit label ("ms", "%", "stars")

    def evaluate(self, value: Any) -> float:
        """Convert a raw value to a 0.0-1.0 score.

        Returns:
            Float between 0.0 (worst) and 1.0 (best).
        """
        if self.type == "binary":
            if isinstance(value, bool):
                return 1.0 if value else 0.0
            return 1.0 if str(value).lower() in ("true", "success", "1", "yes") else 0.0

        if self.type == "categorical":
            if self.success_values:
                return 1.0 if str(value) in self.success_values else 0.0
            return 1.0 if value else 0.0

        if self.type == "numeric":
            try:
                v = float(value)
            except (ValueError, TypeError):
                return 0.0

            if self.goal == "maximize":
                # Normalize: assume 0-1 range or clamp
                return max(0.0, min(1.0, v))
            elif self.goal == "minimize":
                # Lower is better: 1 - normalized value
                return max(0.0, min(1.0, 1.0 - v))
            elif self.goal == "target" and self.target_value is not None:
                # Closer to target is better
                distance = abs(v - self.target_value)
                max_distance = max(abs(self.target_value), 1.0)
                return max(0.0, 1.0 - (distance / max_distance))

        if self.type == "duration":
            try:
                v = float(value)
            except (ValueError, TypeError):
                return 0.0
            # Duration: lower is better, normalize against target or 1000ms
            target = self.target_value or 1000.0
            return max(0.0, min(1.0, 1.0 - (v / (target * 2))))

        return 0.0


@dataclass
class OutcomeConfig:
    """Configuration for how an agent's outcomes are evaluated.

    Supports single-metric and multi-metric modes. In multi-metric mode,
    individual scores are weighted to produce a composite score.

    Usage:
        # Simple binary
        config = OutcomeConfig.binary()

        # Sales SDR with multiple metrics
        config = OutcomeConfig(metrics=[
            MetricDef("booking_rate", "categorical", weight=3.0,
                      success_values=["meeting_booked", "replied"]),
            MetricDef("response_time", "duration", weight=1.0,
                      goal="minimize", target_value=500),
            MetricDef("unsubscribe_rate", "numeric", weight=2.0,
                      goal="minimize"),
        ])

        # Evaluate a run
        score = config.score({
            "booking_rate": "meeting_booked",
            "response_time": 350,
            "unsubscribe_rate": 0.02,
        })
    """

    metrics: list[MetricDef] = field(default_factory=list)
    composite_strategy: str = "weighted_average"  # "weighted_average" | "min" | "product"

    @classmethod
    def binary(cls) -> OutcomeConfig:
        """Simple success/failure config."""
        return cls(metrics=[MetricDef("outcome", "binary")])

    @classmethod
    def categorical(cls, success_values: list[str]) -> OutcomeConfig:
        """Categorical outcome with defined success values."""
        return cls(metrics=[
            MetricDef("outcome", "categorical", success_values=success_values)
        ])

    @classmethod
    def numeric(cls, goal: str = "maximize") -> OutcomeConfig:
        """Numeric 0.0-1.0 score."""
        return cls(metrics=[MetricDef("outcome", "numeric", goal=goal)])

    def score(self, values: dict[str, Any] | str | float) -> float:
        """Compute a composite score from outcome values.

        Args:
            values: Either a dict of metric_name → value (multi-metric),
                    or a single string/float value (single-metric).

        Returns:
            Composite score between 0.0 and 1.0.
        """
        if not self.metrics:
            return 0.0

        # Single value → apply to first metric
        if isinstance(values, (str, int, float, bool)):
            return self.metrics[0].evaluate(values)

        # Multi-metric → evaluate each and combine
        scores: list[tuple[float, float]] = []  # (score, weight)
        for metric in self.metrics:
            value = values.get(metric.name)
            if value is not None:
                s = metric.evaluate(value)
                scores.append((s, metric.weight))

        if not scores:
            return 0.0

        if self.composite_strategy == "weighted_average":
            total_weight = sum(w for _, w in scores)
            if total_weight == 0:
                return 0.0
            return sum(s * w for s, w in scores) / total_weight

        elif self.composite_strategy == "min":
            return min(s for s, _ in scores)

        elif self.composite_strategy == "product":
            result = 1.0
            for s, _ in scores:
                result *= s
            return result

        return 0.0

    def describe(self) -> str:
        """Human-readable description of what this agent optimizes for.

        This is injected into reflection prompts so the LLM knows
        what "good" and "bad" mean for this specific agent.
        """
        if not self.metrics:
            return "No outcome metrics defined."

        lines = ["This agent optimizes for:"]
        for m in self.metrics:
            weight_label = f" (weight: {m.weight})" if len(self.metrics) > 1 else ""
            if m.type == "binary":
                lines.append(f"  - {m.name}: success vs failure{weight_label}")
            elif m.type == "categorical":
                success = ", ".join(m.success_values or [])
                lines.append(f"  - {m.name}: success = [{success}]{weight_label}")
            elif m.type == "numeric":
                lines.append(f"  - {m.name}: {m.goal} ({m.unit or '0.0-1.0'}){weight_label}")
            elif m.type == "duration":
                target = f", target: {m.target_value}{m.unit}" if m.target_value else ""
                lines.append(f"  - {m.name}: lower is better{target}{weight_label}")

        return "\n".join(lines)
