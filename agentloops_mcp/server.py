"""AgentLoops MCP Server.

Exposes AgentLoops memory + learning to any MCP-compatible agent runtime:
  - Claude Managed Agents (YAML config, no code)
  - Local claude CLI
  - Any MCP-compatible framework

Tools:
  recall(query, agent_type?, namespace?)     -> relevant IF/THEN rules + recent learnings
  remember(session_summary, outcome, context) -> stores memory, triggers rule extraction
  reflect(agent_name)                         -> auto-extract learnings from recent runs
  get_rules(agent_name, agent_type?)          -> full ruleset for this agent
  check(output, agent_name, input?)           -> quality gate validation
  enhance_prompt(base_prompt, agent_name)     -> inject learned rules into prompt

Run:
  python -m agentloops_mcp                     (stdio, for local MCP clients)
  python -m agentloops_mcp --transport sse    (SSE, for remote/web MCP clients)
"""

from __future__ import annotations

import logging
import os
import tempfile
from pathlib import Path
from typing import Any

from mcp.server.fastmcp import FastMCP

from agentloops import AgentLoops
from agentloops.seed_rules import get_seed_rules, list_agent_types

logger = logging.getLogger("agentloops.mcp")

# --- Server setup ---

mcp = FastMCP(
    "AgentLoops",
    instructions=(
        "Self-learning for AI agents. Your agents have memory — now give them a brain. "
        "Track outcomes, extract IF/THEN rules, and inject learned intelligence into prompts."
    ),
)

# --- Instance cache ---
# Keyed by (agent_name, namespace). Reuses AgentLoops instances across calls.

_instances: dict[tuple[str, str], AgentLoops] = {}


def _get_instance(agent_name: str, namespace: str = "default", agent_type: str | None = None) -> AgentLoops:
    """Get or create an AgentLoops instance for the given agent + namespace."""
    key = (agent_name, namespace)
    if key not in _instances:
        # Determine storage path — use AGENTLOOPS_STORAGE_PATH env or temp dir
        base_path = os.environ.get("AGENTLOOPS_STORAGE_PATH", os.path.join(tempfile.gettempdir(), "agentloops-mcp"))
        storage_path = Path(base_path) / namespace / agent_name

        # Check for API key (for LLM-powered reflection)
        api_key = os.environ.get("ANTHROPIC_API_KEY") or os.environ.get("OPENAI_API_KEY")
        llm_provider = "openai" if os.environ.get("OPENAI_API_KEY") and not os.environ.get("ANTHROPIC_API_KEY") else "anthropic"

        _instances[key] = AgentLoops(
            agent_name=agent_name,
            storage_path=str(storage_path),
            agent_type=agent_type,
            api_key=api_key,
            llm_provider=llm_provider,
            auto_learn=True,
        )
    return _instances[key]


# --- MCP Tools ---


@mcp.tool()
def recall(
    query: str,
    agent_name: str = "default",
    agent_type: str | None = None,
    namespace: str = "default",
) -> str:
    """Recall relevant rules and learnings for a given situation.

    Call this BEFORE your agent generates a response. Returns IF/THEN rules
    learned from past performance that should guide the agent's behavior.

    Args:
        query: Description of the current situation (e.g., "customer asking about refund")
        agent_name: Name of the agent to recall rules for
        agent_type: Optional agent type for pre-seeded rules (e.g., "sales-sdr", "customer-support")
        namespace: Namespace for isolation (defaults to "default")

    Returns:
        Formatted rules and conventions to inject into the agent's context.
    """
    loops = _get_instance(agent_name, namespace, agent_type)
    rules = loops.rules.active()
    conventions = loops.conventions.get_conventions()

    if not rules and not conventions:
        # If no learned rules yet but we have an agent type, return seed rules
        if agent_type:
            seeds = get_seed_rules(agent_type)
            if seeds:
                lines = [f"## Starter Rules for {agent_type} (from collective intelligence)\n"]
                for rule in seeds:
                    lines.append(f"- {rule.text} [confidence: {rule.confidence:.0%}]")
                lines.append(f"\nQuery context: {query}")
                lines.append("These are starter rules. Track outcomes to learn rules specific to your agent.")
                return "\n".join(lines)
        return f"No rules learned yet for agent '{agent_name}'. Track some outcomes first with remember()."

    sections: list[str] = []

    if rules:
        # Filter rules relevant to the query (simple keyword match)
        query_lower = query.lower()
        relevant = [r for r in rules if any(word in r.text.lower() for word in query_lower.split() if len(word) > 3)]
        display_rules = relevant if relevant else rules  # Fall back to all rules if no match

        sections.append("## Decision Rules (learned from past performance)\n")
        for rule in display_rules:
            sections.append(f"- {rule.text} [confidence: {rule.confidence:.0%}]")

    if conventions:
        sections.append("\n## Conventions (behavioral patterns)\n")
        for conv in conventions:
            sections.append(f"- {conv.text}")

    sections.append(f"\n---\nQuery: {query}")
    sections.append(f"Total rules: {len(rules)} | Conventions: {len(conventions)}")

    return "\n".join(sections)


@mcp.tool()
def remember(
    session_summary: str,
    outcome: str,
    agent_name: str = "default",
    context: str = "",
    agent_type: str | None = None,
    namespace: str = "default",
    metadata: dict[str, Any] | None = None,
) -> str:
    """Store a session outcome and trigger learning.

    Call this AFTER your agent completes a task. AgentLoops will track the
    outcome and, when enough data accumulates, automatically extract IF/THEN
    rules that improve future performance.

    Args:
        session_summary: What the agent did (input + output summary)
        outcome: Result — "success", "failure", "meeting_booked", "resolved", or any string
        agent_name: Name of the agent
        context: Additional context about the session
        agent_type: Agent type for collective intelligence
        namespace: Namespace for isolation
        metadata: Optional key-value pairs (latency, tokens, customer_tier, etc.)

    Returns:
        Confirmation with current rule count and any auto-learning triggered.
    """
    loops = _get_instance(agent_name, namespace, agent_type)

    input_text = context if context else session_summary
    output_text = session_summary

    run = loops.track(
        input=input_text,
        output=output_text,
        outcome=outcome,
        metadata=metadata or {},
    )

    rules_count = len(loops.rules.active())
    auto_learn = run.metadata.get("auto_learn", {})

    parts = [f"Tracked. Run ID: {run.id}"]
    parts.append(f"Active rules: {rules_count}")

    if auto_learn:
        if "reflection" in auto_learn:
            trigger = auto_learn["reflection"]["trigger"]
            new_rules = auto_learn["reflection"].get("suggested_rules", [])
            parts.append(f"Auto-reflection triggered ({trigger}): {len(new_rules)} new rules suggested")
            for r in new_rules[:3]:
                parts.append(f"  - {r[:100]}")
        if "spike" in auto_learn:
            parts.append(f"Spike detected: score={auto_learn['spike']['score']}, deviation={auto_learn['spike']['deviation']}x")
        if "evolution" in auto_learn:
            parts.append("Convention evolution triggered")

    return "\n".join(parts)


@mcp.tool()
def reflect(
    agent_name: str = "default",
    last_n: int = 10,
    namespace: str = "default",
) -> str:
    """Analyze recent runs and extract learnings.

    Triggers a reflection pass that analyzes the last N runs, identifies
    patterns, and generates new IF/THEN rules. Call this periodically or
    after a batch of runs.

    Args:
        agent_name: Name of the agent to reflect on
        last_n: Number of recent runs to analyze (default: 10)
        namespace: Namespace for isolation

    Returns:
        Reflection summary with critique and suggested rules.
    """
    loops = _get_instance(agent_name, namespace)

    try:
        reflection = loops.reflect(last_n=last_n)
    except ValueError as e:
        return f"Cannot reflect: {e}"
    except Exception as e:
        if "API key" in str(e) or "api_key" in str(e).lower():
            return (
                "Reflection requires an LLM API key. Set ANTHROPIC_API_KEY or OPENAI_API_KEY "
                "environment variable before starting the MCP server."
            )
        return f"Reflection failed: {e}"

    parts = [f"## Reflection for {agent_name}\n"]
    parts.append(f"**Critique:** {reflection.critique}\n")

    if reflection.suggested_rules:
        parts.append("**Suggested Rules:**")
        for rule in reflection.suggested_rules:
            conf = reflection.confidence_scores.get(rule, 0.5)
            parts.append(f"- [{conf:.0%}] {rule}")

    parts.append(f"\nRuns analyzed: {len(reflection.run_ids)}")
    return "\n".join(parts)


@mcp.tool()
def get_rules(
    agent_name: str = "default",
    agent_type: str | None = None,
    namespace: str = "default",
    active_only: bool = True,
) -> str:
    """Get the full ruleset for an agent.

    Returns all active IF/THEN rules — both learned and seed rules.
    Use this to bootstrap a new agent session or audit what the agent has learned.

    Args:
        agent_name: Name of the agent
        agent_type: Agent type to include seed rules (e.g., "sales-sdr")
        namespace: Namespace for isolation
        active_only: Only return active rules (default: True)

    Returns:
        Formatted list of all rules with confidence scores.
    """
    loops = _get_instance(agent_name, namespace, agent_type)
    rules = loops._storage.get_rules(active_only=active_only)

    if not rules:
        available = list_agent_types()
        return (
            f"No rules found for agent '{agent_name}'.\n"
            f"Available agent types with starter rules: {', '.join(available)}\n"
            "Pass agent_type to get pre-seeded rules, or track outcomes to learn new ones."
        )

    parts = [f"## Rules for {agent_name} ({len(rules)} {'active' if active_only else 'total'})\n"]
    for rule in sorted(rules, key=lambda r: r.confidence, reverse=True):
        status = "ACTIVE" if rule.active else "INACTIVE"
        parts.append(
            f"- [{rule.confidence:.0%}] {rule.text}"
            + (f" ({status})" if not active_only else "")
        )

    return "\n".join(parts)


@mcp.tool()
def check(
    output: str,
    agent_name: str = "default",
    input: str = "",
    namespace: str = "default",
) -> str:
    """Validate agent output before sending it to users.

    Runs quality gate checks: built-in (empty output, hallucination markers,
    length) and rule-based (checks output against learned "avoid" rules).

    Args:
        output: The agent's output to validate
        agent_name: Name of the agent
        input: The original input for context
        namespace: Namespace for isolation

    Returns:
        PASS or FAIL with details and score.
    """
    loops = _get_instance(agent_name, namespace)
    result = loops.check(output=output, input=input)

    parts = []
    if result.passed:
        parts.append(f"PASS (score: {result.score:.2f})")
    else:
        parts.append(f"FAIL (score: {result.score:.2f})")

    if result.failures:
        parts.append("\nFailures:")
        for f in result.failures:
            parts.append(f"  - {f.get('message', f)}")

    if result.warnings:
        parts.append("\nWarnings:")
        for w in result.warnings:
            parts.append(f"  - {w.get('message', w)}")

    return "\n".join(parts)


@mcp.tool()
def enhance_prompt(
    base_prompt: str,
    agent_name: str = "default",
    agent_type: str | None = None,
    namespace: str = "default",
) -> str:
    """Inject learned rules and conventions into an agent prompt.

    Takes a base system prompt and appends all active rules and conventions.
    Use this to create an enhanced prompt that benefits from everything
    the agent has learned.

    Args:
        base_prompt: The agent's base system prompt
        agent_name: Name of the agent
        agent_type: Agent type for seed rules
        namespace: Namespace for isolation

    Returns:
        Enhanced prompt with rules and conventions appended.
    """
    loops = _get_instance(agent_name, namespace, agent_type)
    return loops.enhance_prompt(base_prompt)


@mcp.tool()
def list_agent_types_tool() -> str:
    """List all available agent types with pre-seeded starter rules.

    Returns the 10 agent types that come with curated IF/THEN rules
    out of the box. Pass one of these as agent_type to recall() or
    get_rules() to bootstrap your agent with proven patterns.

    Returns:
        List of agent types with descriptions.
    """
    types = list_agent_types()
    descriptions = {
        "sales-sdr": "Sales development — cold outreach, meeting booking",
        "customer-support": "Customer support — ticket resolution, escalation",
        "help-desk": "Help desk — guest services, upselling, preferences",
        "content-creator": "Content creation — engagement, formats, scheduling",
        "code-generator": "Code generation — error handling, testing, patterns",
        "recruiting": "Recruiting — candidate outreach, screening, follow-up",
        "legal-review": "Legal review — contract analysis, clause flagging",
        "insurance-claims": "Insurance claims — processing, fraud detection",
        "devops-incident": "DevOps incident response — triage, escalation",
        "ecommerce-rec": "E-commerce recommendations — personalization, upselling",
    }

    parts = ["## Available Agent Types\n"]
    for t in types:
        desc = descriptions.get(t, "")
        seeds = get_seed_rules(t)
        parts.append(f"- **{t}** — {desc} ({len(seeds)} starter rules)")

    parts.append("\nUse these with recall(agent_type='...') or get_rules(agent_type='...')")
    return "\n".join(parts)


# --- Entry point ---

def main():
    """Run the MCP server."""
    import argparse
    parser = argparse.ArgumentParser(description="AgentLoops MCP Server")
    parser.add_argument("--transport", choices=["stdio", "sse"], default="stdio", help="Transport mode")
    parser.add_argument("--port", type=int, default=8080, help="Port for SSE transport")
    args = parser.parse_args()

    if args.transport == "sse":
        mcp.run(transport="sse")
    else:
        mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
