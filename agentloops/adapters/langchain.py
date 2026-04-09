"""LangChain adapter — auto-tracks LLM calls and chain runs.

Implements LangChain's BaseCallbackHandler to automatically log every
chain run to AgentLoops. Works with any LangChain chain, agent, or LLM.

Usage:
    from agentloops.adapters.langchain import AgentLoopsCallback

    loops = AgentLoops("my-agent", agent_type="customer-support")
    callback = AgentLoopsCallback(loops)

    # Use with any LangChain chain
    chain = prompt | llm
    result = chain.invoke({"input": "help me"}, config={"callbacks": [callback]})

    # Or attach to an LLM directly
    llm = ChatAnthropic(model="claude-sonnet-4-6", callbacks=[callback])
"""

from __future__ import annotations

import time
from typing import Any
from uuid import UUID

from agentloops.core import AgentLoops


class AgentLoopsCallback:
    """LangChain callback handler that auto-tracks runs to AgentLoops.

    Captures chain/LLM inputs, outputs, and timing. Automatically calls
    loops.track() on every chain completion.

    Implements the LangChain callback protocol without importing langchain
    at module level (so agentloops works without langchain installed).
    """

    def __init__(
        self,
        loops: AgentLoops,
        outcome_fn: Any | None = None,
        track_llm_calls: bool = False,
    ) -> None:
        """Initialize the callback.

        Args:
            loops: AgentLoops instance to track runs to.
            outcome_fn: Optional function(input, output) -> str that determines
                        the outcome. If None, all completions are "success".
            track_llm_calls: If True, also track individual LLM calls
                            (not just chain-level). Default False to avoid noise.
        """
        self.loops = loops
        self._outcome_fn = outcome_fn
        self._track_llm_calls = track_llm_calls
        self._chain_starts: dict[str, dict[str, Any]] = {}
        self._llm_starts: dict[str, dict[str, Any]] = {}

    # -- Chain callbacks ---------------------------------------------------

    def on_chain_start(
        self,
        serialized: dict[str, Any],
        inputs: dict[str, Any],
        *,
        run_id: UUID,
        parent_run_id: UUID | None = None,
        **kwargs: Any,
    ) -> None:
        """Record chain start time and inputs."""
        self._chain_starts[str(run_id)] = {
            "inputs": inputs,
            "start_time": time.time(),
            "chain_name": serialized.get("name", "unknown"),
        }

    def on_chain_end(
        self,
        outputs: dict[str, Any],
        *,
        run_id: UUID,
        parent_run_id: UUID | None = None,
        **kwargs: Any,
    ) -> None:
        """Track the completed chain run."""
        rid = str(run_id)
        start_info = self._chain_starts.pop(rid, None)
        if not start_info:
            return

        input_str = _serialize(start_info["inputs"])
        output_str = _serialize(outputs)
        latency = time.time() - start_info["start_time"]

        outcome = "success"
        if self._outcome_fn:
            try:
                outcome = self._outcome_fn(start_info["inputs"], outputs)
            except Exception:
                outcome = "unknown"

        self.loops.track(
            input=input_str,
            output=output_str,
            outcome=outcome,
            metadata={
                "source": "langchain",
                "chain_name": start_info["chain_name"],
                "latency_ms": round(latency * 1000),
            },
        )

    def on_chain_error(
        self,
        error: BaseException,
        *,
        run_id: UUID,
        parent_run_id: UUID | None = None,
        **kwargs: Any,
    ) -> None:
        """Track failed chain runs."""
        rid = str(run_id)
        start_info = self._chain_starts.pop(rid, None)
        if not start_info:
            return

        input_str = _serialize(start_info["inputs"])
        latency = time.time() - start_info["start_time"]

        self.loops.track(
            input=input_str,
            output=f"ERROR: {type(error).__name__}: {error}",
            outcome="failure",
            metadata={
                "source": "langchain",
                "chain_name": start_info["chain_name"],
                "latency_ms": round(latency * 1000),
                "error_type": type(error).__name__,
            },
        )

    # -- LLM callbacks (optional) ------------------------------------------

    def on_llm_start(
        self,
        serialized: dict[str, Any],
        prompts: list[str],
        *,
        run_id: UUID,
        parent_run_id: UUID | None = None,
        **kwargs: Any,
    ) -> None:
        """Record LLM call start."""
        if self._track_llm_calls:
            self._llm_starts[str(run_id)] = {
                "prompts": prompts,
                "start_time": time.time(),
                "model": serialized.get("kwargs", {}).get("model", "unknown"),
            }

    def on_llm_end(
        self,
        response: Any,
        *,
        run_id: UUID,
        parent_run_id: UUID | None = None,
        **kwargs: Any,
    ) -> None:
        """Track completed LLM call."""
        if not self._track_llm_calls:
            return

        rid = str(run_id)
        start_info = self._llm_starts.pop(rid, None)
        if not start_info:
            return

        input_str = "\n".join(start_info["prompts"][:2])[:500]
        output_str = str(response)[:500] if response else ""
        latency = time.time() - start_info["start_time"]

        self.loops.track(
            input=input_str,
            output=output_str,
            outcome="success",
            metadata={
                "source": "langchain_llm",
                "model": start_info["model"],
                "latency_ms": round(latency * 1000),
            },
        )


def _serialize(data: Any) -> str:
    """Convert chain input/output to a string for tracking."""
    if isinstance(data, str):
        return data
    if isinstance(data, dict):
        # Common LangChain patterns
        for key in ("input", "query", "question", "text", "output", "result", "answer"):
            if key in data:
                return str(data[key])
        return str(data)
    return str(data)
