"""Tests for the AgentLoops MCP server tools."""

import sys
import os

# Ensure project root is on path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from agentloops_mcp.server import (
    recall,
    remember,
    reflect,
    get_rules,
    check,
    enhance_prompt,
    list_agent_types_tool,
    _instances,
)


def setup_function():
    """Clear instance cache between tests."""
    _instances.clear()


# --- recall ---


def test_recall_no_data():
    result = recall("customer asking about refund", agent_name="mcp-test-empty")
    assert "No rules learned yet" in result


def test_recall_with_seed_rules():
    result = recall("cold outreach CTO", agent_name="mcp-test-sdr", agent_type="sales-sdr")
    assert "Rules" in result or "rules" in result
    assert "confidence" in result.lower() or "%" in result


def test_recall_returns_relevant_rules():
    # First add some data
    remember("Sent email about pricing", outcome="success", agent_name="mcp-test-recall")
    # Manually add a rule via the instance
    loops = _instances[("mcp-test-recall", "default")]
    loops.rules.add_rule(text="IF customer mentions pricing THEN include comparison table", confidence=0.9)
    loops.rules.add_rule(text="IF prospect is enterprise THEN involve sales team", confidence=0.8)

    result = recall("customer asking about pricing", agent_name="mcp-test-recall")
    assert "pricing" in result.lower()


# --- remember ---


def test_remember_tracks_run():
    result = remember(
        "Handled refund request for new customer",
        outcome="resolved",
        agent_name="mcp-test-remember",
        context="customer signed up 2 weeks ago",
    )
    assert "Tracked" in result
    assert "Run ID" in result
    assert "Active rules" in result


def test_remember_with_metadata():
    result = remember(
        "Sent cold email",
        outcome="meeting_booked",
        agent_name="mcp-test-meta",
        metadata={"latency_ms": 150, "tokens": 500},
    )
    assert "Tracked" in result


# --- get_rules ---


def test_get_rules_empty():
    result = get_rules(agent_name="mcp-test-no-rules")
    assert "No rules found" in result
    assert "Available agent types" in result


def test_get_rules_with_agent_type():
    result = get_rules(agent_name="mcp-test-rules-type", agent_type="customer-support")
    assert "Rules for" in result
    assert "%" in result  # confidence percentages


def test_get_rules_sorted_by_confidence():
    result = get_rules(agent_name="mcp-test-sorted", agent_type="sales-sdr")
    lines = [l for l in result.split("\n") if l.startswith("- [")]
    assert len(lines) >= 2
    # Extract confidence values
    confidences = []
    for line in lines:
        pct = line.split("]")[0].replace("- [", "").replace("%", "")
        confidences.append(int(pct))
    # Should be descending
    assert confidences == sorted(confidences, reverse=True)


# --- check ---


def test_check_passes_good_output():
    result = check(
        output="Hi Sarah, I noticed your API handles 99.9% uptime.",
        agent_name="mcp-test-check",
    )
    assert "PASS" in result


def test_check_fails_empty_output():
    result = check(output="", agent_name="mcp-test-check-empty")
    assert "FAIL" in result


# --- enhance_prompt ---


def test_enhance_prompt_no_rules():
    result = enhance_prompt("You are a helpful agent.", agent_name="mcp-test-enhance-empty")
    assert result == "You are a helpful agent."


def test_enhance_prompt_with_rules():
    result = enhance_prompt(
        "You are a sales agent.",
        agent_name="mcp-test-enhance",
        agent_type="sales-sdr",
    )
    assert "You are a sales agent." in result
    assert "Decision Rules" in result


# --- list_agent_types ---


def test_list_agent_types():
    result = list_agent_types_tool()
    assert "sales-sdr" in result
    assert "customer-support" in result
    assert "code-generator" in result
    assert "starter rules" in result


# --- reflect ---


def test_reflect_no_runs():
    result = reflect(agent_name="mcp-test-reflect-empty")
    assert "Cannot reflect" in result or "Reflection" in result


def test_reflect_after_runs():
    # Track some runs first
    for i in range(5):
        remember(
            f"Test run {i}",
            outcome="success" if i % 2 == 0 else "failure",
            agent_name="mcp-test-reflect",
        )
    # reflect() will fail without an LLM API key, which is expected in tests
    result = reflect(agent_name="mcp-test-reflect", last_n=5)
    # Should either succeed or fail gracefully
    assert isinstance(result, str)
    assert len(result) > 0


# --- namespace isolation ---


def test_namespace_isolation():
    remember("Test in ns1", outcome="success", agent_name="shared-agent", namespace="ns1")
    remember("Test in ns2", outcome="failure", agent_name="shared-agent", namespace="ns2")

    # Each namespace should have its own instance
    assert ("shared-agent", "ns1") in _instances
    assert ("shared-agent", "ns2") in _instances
    assert _instances[("shared-agent", "ns1")] is not _instances[("shared-agent", "ns2")]


# --- instance caching ---


def test_instance_reuse():
    recall("test", agent_name="cache-test", agent_type="sales-sdr")
    instance1 = _instances[("cache-test", "default")]
    recall("test again", agent_name="cache-test")
    instance2 = _instances[("cache-test", "default")]
    assert instance1 is instance2
