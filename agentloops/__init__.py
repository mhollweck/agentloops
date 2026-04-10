"""AgentLoops — the intelligence layer for AI agents.

Self-learning loops that make your agents smarter over time.

Usage:
    from agentloops import AgentLoops

    loops = AgentLoops("my-agent")

    # Track a run
    loops.track(input="...", output="...", outcome="success")

    # Reflect on recent performance
    reflection = loops.reflect(last_n=5)

    # Enhance a prompt with learned rules
    prompt = loops.enhance_prompt("You are a helpful agent.")

    # Prune stale memory
    loops.forget(strategy="hybrid", max_age_days=21)
"""

from agentloops.convention_store import ConventionStore
from agentloops.core import AgentLoops
from agentloops.forgetter import Forgetter
from agentloops.models import Convention, Reflection, Rule, Run
from agentloops.outcomes import MetricDef, OutcomeConfig
from agentloops.quality_gate import GateResult, QualityGate
from agentloops.reflector import Reflector
from agentloops.rule_engine import RuleEngine
from agentloops.seed_rules import get_seed_rules, list_agent_types
from agentloops.tracker import Tracker

__version__ = "0.1.3"

__all__ = [
    "AgentLoops",
    "Convention",
    "ConventionStore",
    "Forgetter",
    "GateResult",
    "MetricDef",
    "OutcomeConfig",
    "QualityGate",
    "Reflection",
    "Reflector",
    "Rule",
    "RuleEngine",
    "Run",
    "Tracker",
    "get_seed_rules",
    "list_agent_types",
]
