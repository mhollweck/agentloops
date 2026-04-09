"""CrewAI adapter — auto-tracks task completions and crew runs.

Wraps CrewAI's task execution to automatically log outcomes to AgentLoops.
Works with any CrewAI crew, agent, or task.

Usage:
    from agentloops.adapters.crewai import AgentLoopsCrewCallback

    loops = AgentLoops("support-crew", agent_type="customer-support")
    callback = AgentLoopsCrewCallback(loops)

    # Wrap task execution
    crew = Crew(agents=[agent], tasks=[task])
    result = crew.kickoff()
    callback.on_crew_complete(crew, result)

    # Or wrap individual tasks
    callback.on_task_complete(task, task_output)
"""

from __future__ import annotations

import time
from typing import Any

from agentloops.core import AgentLoops


class AgentLoopsCrewCallback:
    """CrewAI callback that auto-tracks task and crew completions.

    Designed to work without importing crewai at module level.
    """

    def __init__(
        self,
        loops: AgentLoops,
        outcome_fn: Any | None = None,
    ) -> None:
        """Initialize the callback.

        Args:
            loops: AgentLoops instance to track runs to.
            outcome_fn: Optional function(task_description, output) -> str
                        that determines the outcome. If None, all completions
                        are "success".
        """
        self.loops = loops
        self._outcome_fn = outcome_fn
        self._crew_start_time: float | None = None

    def on_crew_start(self, crew: Any) -> None:
        """Record crew kickoff time."""
        self._crew_start_time = time.time()

    def on_task_complete(
        self,
        task: Any,
        output: Any,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """Track a completed CrewAI task.

        Args:
            task: The CrewAI Task object.
            output: The task's output (TaskOutput or string).
            metadata: Optional additional metadata.
        """
        task_desc = getattr(task, "description", str(task))[:500]
        output_str = str(output)[:500]
        agent_name = ""
        if hasattr(task, "agent") and task.agent:
            agent_name = getattr(task.agent, "role", str(task.agent))

        outcome = "success"
        if self._outcome_fn:
            try:
                outcome = self._outcome_fn(task_desc, output_str)
            except Exception:
                outcome = "unknown"

        meta = {
            "source": "crewai",
            "agent_role": agent_name,
            **(metadata or {}),
        }

        self.loops.track(
            input=task_desc,
            output=output_str,
            outcome=outcome,
            metadata=meta,
        )

    def on_crew_complete(
        self,
        crew: Any,
        result: Any,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """Track a completed crew run (all tasks).

        Args:
            crew: The CrewAI Crew object.
            result: The crew's final result.
            metadata: Optional additional metadata.
        """
        crew_desc = ""
        if hasattr(crew, "tasks") and crew.tasks:
            task_descs = [
                getattr(t, "description", "")[:100] for t in crew.tasks[:5]
            ]
            crew_desc = " → ".join(task_descs)
        else:
            crew_desc = str(crew)[:500]

        output_str = str(result)[:500]
        latency = None
        if self._crew_start_time:
            latency = round((time.time() - self._crew_start_time) * 1000)
            self._crew_start_time = None

        outcome = "success"
        if self._outcome_fn:
            try:
                outcome = self._outcome_fn(crew_desc, output_str)
            except Exception:
                outcome = "unknown"

        meta = {
            "source": "crewai_crew",
            **({"latency_ms": latency} if latency else {}),
            **(metadata or {}),
        }

        self.loops.track(
            input=crew_desc,
            output=output_str,
            outcome=outcome,
            metadata=meta,
        )
