"""Data models for AgentLoops."""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any


def _new_id() -> str:
    return uuid.uuid4().hex[:12]


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


@dataclass
class Run:
    """A single agent run with its input, output, and outcome."""

    input: str
    output: str
    outcome: str  # "success", "failure", or a numeric score
    agent_name: str
    id: str = field(default_factory=_new_id)
    metadata: dict[str, Any] = field(default_factory=dict)
    rules_applied: list[str] = field(default_factory=list)
    created_at: str = field(default_factory=_now)

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "agent_name": self.agent_name,
            "input": self.input,
            "output": self.output,
            "outcome": self.outcome,
            "metadata": self.metadata,
            "rules_applied": self.rules_applied,
            "created_at": self.created_at,
        }

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> Run:
        return cls(
            id=d["id"],
            agent_name=d["agent_name"],
            input=d["input"],
            output=d["output"],
            outcome=d["outcome"],
            metadata=d.get("metadata", {}),
            rules_applied=d.get("rules_applied", []),
            created_at=d["created_at"],
        )


@dataclass
class Rule:
    """An IF/THEN decision rule derived from performance data."""

    text: str
    confidence: float  # 0.0 to 1.0
    evidence_count: int = 1
    id: str = field(default_factory=_new_id)
    evidence: list[str] = field(default_factory=list)
    created_at: str = field(default_factory=_now)
    last_validated: str = field(default_factory=_now)
    active: bool = True

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "text": self.text,
            "confidence": self.confidence,
            "evidence_count": self.evidence_count,
            "evidence": self.evidence,
            "created_at": self.created_at,
            "last_validated": self.last_validated,
            "active": self.active,
        }

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> Rule:
        return cls(
            id=d["id"],
            text=d["text"],
            confidence=d["confidence"],
            evidence_count=d.get("evidence_count", 1),
            evidence=d.get("evidence", []),
            created_at=d["created_at"],
            last_validated=d.get("last_validated", d["created_at"]),
            active=d.get("active", True),
        )


@dataclass
class Convention:
    """A behavioral rule that evolves over time."""

    text: str
    source: str  # which rule or reflection produced this
    id: str = field(default_factory=_new_id)
    created_at: str = field(default_factory=_now)
    updated_at: str = field(default_factory=_now)
    status: str = "active"  # "active", "superseded", "contradicted", "pruned"

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "text": self.text,
            "source": self.source,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "status": self.status,
        }

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> Convention:
        return cls(
            id=d["id"],
            text=d["text"],
            source=d["source"],
            created_at=d["created_at"],
            updated_at=d.get("updated_at", d["created_at"]),
            status=d.get("status", "active"),
        )


@dataclass
class Reflection:
    """Structured output from a reflection pass."""

    agent_name: str
    critique: str
    suggested_rules: list[str]
    confidence_scores: dict[str, float]
    id: str = field(default_factory=_new_id)
    run_ids: list[str] = field(default_factory=list)
    created_at: str = field(default_factory=_now)

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "agent_name": self.agent_name,
            "critique": self.critique,
            "suggested_rules": self.suggested_rules,
            "confidence_scores": self.confidence_scores,
            "run_ids": self.run_ids,
            "created_at": self.created_at,
        }

    @classmethod
    def from_dict(cls, d: dict[str, Any]) -> Reflection:
        return cls(
            id=d["id"],
            agent_name=d["agent_name"],
            critique=d["critique"],
            suggested_rules=d.get("suggested_rules", []),
            confidence_scores=d.get("confidence_scores", {}),
            run_ids=d.get("run_ids", []),
            created_at=d["created_at"],
        )
