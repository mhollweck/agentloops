"""Shared fixtures for AgentLoops tests."""

from __future__ import annotations

from datetime import datetime, timedelta

import pytest

from agentloops.models import Convention, Rule, Run
from agentloops.storage.file import FileStorage


@pytest.fixture
def storage(tmp_path):
    """Create a FileStorage instance in a temp directory."""
    return FileStorage(tmp_path / ".agentloops", "test-agent")


@pytest.fixture
def sample_runs(storage):
    """Create and persist a set of sample runs with varied outcomes."""
    runs = []
    base_time = datetime.utcnow() - timedelta(days=10)
    for i in range(10):
        run = Run(
            input=f"test input {i}",
            output=f"test output {i}",
            outcome="success" if i % 3 != 0 else "failure",
            agent_name="test-agent",
            metadata={"index": i},
            rules_applied=["rule-1"] if i >= 5 else [],
            created_at=(base_time + timedelta(days=i)).isoformat(),
        )
        storage.save_run(run)
        runs.append(run)
    return runs


@pytest.fixture
def sample_rules(storage):
    """Create and persist a set of sample rules with varying confidence."""
    rules = []
    for i, (text, conf) in enumerate([
        ("IF user asks about pricing THEN include comparison table", 0.9),
        ("IF email is cold outreach THEN personalize first line", 0.7),
        ("IF question is technical THEN include code examples", 0.5),
        ("IF user is frustrated THEN acknowledge emotion first", 0.2),
    ]):
        rule = Rule(
            text=text,
            confidence=conf,
            evidence=[f"evidence-{i}"],
            evidence_count=1,
        )
        storage.save_rule(rule)
        rules.append(rule)
    return rules


@pytest.fixture
def old_rule(storage):
    """Create an old, low-confidence rule eligible for pruning."""
    rule = Rule(
        text="IF old condition THEN old action",
        confidence=0.2,
        created_at=(datetime.utcnow() - timedelta(days=30)).isoformat(),
        last_validated=(datetime.utcnow() - timedelta(days=30)).isoformat(),
    )
    storage.save_rule(rule)
    return rule


@pytest.fixture
def high_confidence_old_rule(storage):
    """Create an old but high-confidence rule that should NOT be pruned."""
    rule = Rule(
        text="IF important condition THEN critical action",
        confidence=0.9,
        created_at=(datetime.utcnow() - timedelta(days=30)).isoformat(),
        last_validated=(datetime.utcnow() - timedelta(days=30)).isoformat(),
    )
    storage.save_rule(rule)
    return rule


@pytest.fixture
def old_convention(storage):
    """Create an old convention eligible for pruning."""
    conv = Convention(
        text="Always greet the user by name",
        source="manual",
        created_at=(datetime.utcnow() - timedelta(days=30)).isoformat(),
        updated_at=(datetime.utcnow() - timedelta(days=30)).isoformat(),
    )
    storage.save_convention(conv)
    return conv
