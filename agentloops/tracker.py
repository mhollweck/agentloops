"""Performance outcome correlation and run logging."""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any

from agentloops.models import Run
from agentloops.storage.base import BaseStorage


class Tracker:
    """Tracks agent runs and correlates performance with applied rules."""

    def __init__(self, storage: BaseStorage, agent_name: str) -> None:
        self._storage = storage
        self._agent_name = agent_name

    def log_run(
        self,
        input: str,
        output: str,
        outcome: str,
        metadata: dict[str, Any] | None = None,
        rules_applied: list[str] | None = None,
    ) -> Run:
        """Log a completed agent run with its outcome.

        Args:
            input: The prompt or input given to the agent.
            output: The agent's response or output.
            outcome: Result — "success", "failure", or a numeric score as string.
            metadata: Optional key-value pairs (latency, tokens, etc.).
            rules_applied: IDs of rules that were active during this run.

        Returns:
            The persisted Run object.
        """
        run = Run(
            input=input,
            output=output,
            outcome=outcome,
            agent_name=self._agent_name,
            metadata=metadata or {},
            rules_applied=rules_applied or [],
        )
        self._storage.save_run(run)
        return run

    def get_runs(
        self,
        last_n: int | None = None,
        agent_name: str | None = None,
        outcome_filter: str | None = None,
    ) -> list[Run]:
        """Retrieve runs with optional filters.

        Args:
            last_n: Return only the N most recent runs.
            agent_name: Filter by agent name (defaults to this tracker's agent).
            outcome_filter: Filter by outcome value.

        Returns:
            List of matching Run objects.
        """
        name = agent_name or self._agent_name
        return self._storage.get_runs(
            agent_name=name,
            last_n=last_n,
            outcome_filter=outcome_filter,
        )

    def correlate(self, rule_id: str) -> dict[str, Any]:
        """Show performance before and after a rule was applied.

        Splits all runs into two groups — those where the rule was applied and
        those where it wasn't — and computes success rates for each group.

        Args:
            rule_id: The ID of the rule to correlate.

        Returns:
            Dict with 'with_rule' and 'without_rule' stats.
        """
        all_runs = self._storage.get_runs(agent_name=self._agent_name)

        with_rule: list[Run] = []
        without_rule: list[Run] = []

        for run in all_runs:
            if rule_id in run.rules_applied:
                with_rule.append(run)
            else:
                without_rule.append(run)

        return {
            "rule_id": rule_id,
            "with_rule": _compute_stats(with_rule),
            "without_rule": _compute_stats(without_rule),
        }

    def improvement_curve(
        self, metric: str = "success_rate", window_days: int = 7
    ) -> list[dict[str, Any]]:
        """Calculate improvement over time using a sliding window.

        Args:
            metric: Which metric to track — "success_rate" or "avg_score".
            window_days: Size of the sliding window in days.

        Returns:
            List of dicts with 'window_start', 'window_end', and metric value.
        """
        all_runs = self._storage.get_runs(agent_name=self._agent_name)
        if not all_runs:
            return []

        # Parse dates and sort
        dated_runs = []
        for run in all_runs:
            try:
                dt = datetime.fromisoformat(run.created_at)
            except (ValueError, TypeError):
                continue
            dated_runs.append((dt, run))
        dated_runs.sort(key=lambda x: x[0])

        if not dated_runs:
            return []

        start = dated_runs[0][0]
        end = dated_runs[-1][0]
        delta = timedelta(days=window_days)
        curve: list[dict[str, Any]] = []

        window_start = start
        while window_start <= end:
            window_end = window_start + delta
            window_runs = [
                run for dt, run in dated_runs if window_start <= dt < window_end
            ]

            if window_runs:
                if metric == "success_rate":
                    successes = sum(1 for r in window_runs if r.outcome == "success")
                    value = successes / len(window_runs)
                elif metric == "avg_score":
                    scores = []
                    for r in window_runs:
                        try:
                            scores.append(float(r.outcome))
                        except (ValueError, TypeError):
                            pass
                    value = sum(scores) / len(scores) if scores else 0.0
                else:
                    value = 0.0

                curve.append(
                    {
                        "window_start": window_start.isoformat(),
                        "window_end": window_end.isoformat(),
                        metric: round(value, 4),
                        "run_count": len(window_runs),
                    }
                )

            window_start += delta

        return curve


def _compute_stats(runs: list[Run]) -> dict[str, Any]:
    """Compute basic outcome stats for a list of runs."""
    if not runs:
        return {"count": 0, "success_rate": None}

    successes = sum(1 for r in runs if r.outcome == "success")
    scores: list[float] = []
    for r in runs:
        try:
            scores.append(float(r.outcome))
        except (ValueError, TypeError):
            pass

    stats: dict[str, Any] = {
        "count": len(runs),
        "success_rate": round(successes / len(runs), 4),
    }
    if scores:
        stats["avg_score"] = round(sum(scores) / len(scores), 4)
    return stats
