"""Quality Gate — pre-flight checks before agent output is used.

Mechanism #7: validates agent output against learned rules and conventions
before it reaches the user. Catches regressions, anti-patterns, and
known failure modes. Returns a pass/fail verdict with reasons.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable

from agentloops.models import Rule, _new_id, _now
from agentloops.storage.base import BaseStorage


@dataclass
class GateResult:
    """Result of a quality gate check."""

    passed: bool
    score: float  # 0.0 to 1.0
    checks_passed: int
    checks_failed: int
    checks_total: int
    failures: list[dict[str, Any]] = field(default_factory=list)
    warnings: list[dict[str, Any]] = field(default_factory=list)
    id: str = field(default_factory=_new_id)
    created_at: str = field(default_factory=_now)

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "passed": self.passed,
            "score": self.score,
            "checks_passed": self.checks_passed,
            "checks_failed": self.checks_failed,
            "checks_total": self.checks_total,
            "failures": self.failures,
            "warnings": self.warnings,
            "created_at": self.created_at,
        }


# Built-in check functions
def _check_not_empty(output: str, **kwargs: Any) -> dict[str, Any] | None:
    """Fail if output is empty or whitespace-only."""
    if not output or not output.strip():
        return {"check": "not_empty", "severity": "fail", "message": "Output is empty"}
    return None


def _check_min_length(output: str, min_length: int = 10, **kwargs: Any) -> dict[str, Any] | None:
    """Warn if output is suspiciously short."""
    if len(output.strip()) < min_length:
        return {
            "check": "min_length",
            "severity": "warn",
            "message": f"Output is only {len(output.strip())} chars (min: {min_length})",
        }
    return None


def _check_max_length(output: str, max_length: int = 50000, **kwargs: Any) -> dict[str, Any] | None:
    """Warn if output is suspiciously long."""
    if len(output) > max_length:
        return {
            "check": "max_length",
            "severity": "warn",
            "message": f"Output is {len(output)} chars (max: {max_length})",
        }
    return None


def _check_no_hallucination_markers(output: str, **kwargs: Any) -> dict[str, Any] | None:
    """Warn if output contains common hallucination signals."""
    markers = [
        "I don't have access to",
        "I cannot verify",
        "As an AI language model",
        "I apologize, but I",
        "I'm not able to",
    ]
    for marker in markers:
        if marker.lower() in output.lower():
            return {
                "check": "hallucination_markers",
                "severity": "warn",
                "message": f"Output contains hallucination marker: '{marker}'",
            }
    return None


CheckFn = Callable[..., dict[str, Any] | None]

# Default checks applied to every gate
DEFAULT_CHECKS: list[CheckFn] = [
    _check_not_empty,
    _check_min_length,
    _check_max_length,
    _check_no_hallucination_markers,
]


class QualityGate:
    """Pre-flight validation for agent outputs.

    Runs a set of checks against the agent's output before it's used.
    Checks include built-in validators and rule-based checks derived
    from the agent's learned rules.

    Usage:
        gate = QualityGate(storage, "my-agent")
        result = gate.check(output="Hello world", input="Greet the user")
        if not result.passed:
            # Handle failure — retry, flag, or escalate
            print(result.failures)
    """

    def __init__(
        self,
        storage: BaseStorage,
        agent_name: str,
        pass_threshold: float = 0.7,
        custom_checks: list[CheckFn] | None = None,
    ) -> None:
        """Initialize the quality gate.

        Args:
            storage: Storage backend for reading rules.
            agent_name: Name of the agent to gate.
            pass_threshold: Minimum score to pass (0.0 to 1.0).
            custom_checks: Additional check functions to run.
        """
        self._storage = storage
        self._agent_name = agent_name
        self._pass_threshold = pass_threshold
        self._custom_checks: list[CheckFn] = custom_checks or []

    def check(
        self,
        output: str,
        input: str = "",
        metadata: dict[str, Any] | None = None,
    ) -> GateResult:
        """Run all quality checks against an output.

        Args:
            output: The agent's output to validate.
            input: The original input (for context-aware checks).
            metadata: Optional metadata for custom checks.

        Returns:
            GateResult with pass/fail verdict, score, and details.
        """
        failures: list[dict[str, Any]] = []
        warnings: list[dict[str, Any]] = []
        checks_run = 0

        extra = {"input": input, "metadata": metadata or {}}

        # Run built-in checks
        for check_fn in DEFAULT_CHECKS:
            checks_run += 1
            result = check_fn(output=output, **extra)
            if result:
                if result.get("severity") == "fail":
                    failures.append(result)
                else:
                    warnings.append(result)

        # Run custom checks
        for check_fn in self._custom_checks:
            checks_run += 1
            result = check_fn(output=output, **extra)
            if result:
                if result.get("severity") == "fail":
                    failures.append(result)
                else:
                    warnings.append(result)

        # Run rule-based checks — check output against "THEN avoid" rules
        rule_checks = self._check_against_rules(output, input)
        for rc in rule_checks:
            checks_run += 1
            if rc.get("severity") == "fail":
                failures.append(rc)
            else:
                warnings.append(rc)

        checks_passed = checks_run - len(failures)
        score = checks_passed / checks_run if checks_run > 0 else 1.0

        return GateResult(
            passed=len(failures) == 0 and score >= self._pass_threshold,
            score=round(score, 4),
            checks_passed=checks_passed,
            checks_failed=len(failures),
            checks_total=checks_run,
            failures=failures,
            warnings=warnings,
        )

    def _check_against_rules(self, output: str, input: str) -> list[dict[str, Any]]:
        """Check output against learned 'avoid' rules.

        Scans active rules for negative patterns (rules containing 'avoid',
        'never', 'don't') and checks if the output might violate them.
        """
        results: list[dict[str, Any]] = []
        rules = self._storage.get_rules(active_only=True)

        for rule in rules:
            text_lower = rule.text.lower()
            # Only check rules that express what to avoid
            if not any(kw in text_lower for kw in ("avoid", "never", "don't", "do not")):
                continue

            # Extract the thing to avoid from the rule
            violation = self._detect_rule_violation(rule, output, input)
            if violation:
                severity = "fail" if rule.confidence >= 0.8 else "warn"
                results.append({
                    "check": "rule_violation",
                    "rule_id": rule.id,
                    "rule_text": rule.text,
                    "severity": severity,
                    "message": violation,
                    "confidence": rule.confidence,
                })

        return results

    def _detect_rule_violation(self, rule: Rule, output: str, input: str) -> str | None:
        """Simple keyword-based violation detection.

        Checks if the output contains patterns that a rule says to avoid.
        This is intentionally simple — no LLM needed.
        """
        text_lower = rule.text.lower()
        output_lower = output.lower()
        input_lower = input.lower()

        # Pattern: "IF X AND subject style is listicle THEN avoid"
        if "listicle" in text_lower and any(
            marker in output_lower
            for marker in ["top 5", "top 10", "3 ways", "5 reasons", "7 tips", "things you", "tools compared"]
        ):
            return f"Output uses listicle pattern which rule says to avoid"

        # Pattern: "IF financial services THEN avoid casual tone"
        if "casual" in text_lower and "financial" in text_lower:
            if any(kw in input_lower for kw in ["financial", "bank", "fintech", "wells fargo"]):
                casual_markers = ["hey ", "hey,", "what's up", "gonna", "wanna", "btw"]
                if any(m in output_lower for m in casual_markers):
                    return f"Output uses casual tone for financial services prospect"

        return None

    @property
    def pass_threshold(self) -> float:
        """Current pass threshold."""
        return self._pass_threshold

    @pass_threshold.setter
    def pass_threshold(self, value: float) -> None:
        """Update the pass threshold."""
        if not 0.0 <= value <= 1.0:
            raise ValueError("pass_threshold must be between 0.0 and 1.0")
        self._pass_threshold = value
