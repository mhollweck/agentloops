"""Meta-Learner — the learning system that learns to learn better.

This is the core innovation: AgentLoops' own reflection, rule extraction,
and forgetting systems are themselves AgentLoops agents. They track their
own outcomes and improve over time.

The meta-learner answers questions like:
  - Which reflection prompts produce rules that actually improve outcomes?
  - Which rule formats lead to the biggest performance gains?
  - Which forgetting strategies work best for this agent type?
  - What's the optimal reflection_threshold for this agent?
  - Do rules with "because <evidence>" outperform rules without evidence?

Architecture:
  User's Agent ──track()──> AgentLoops Core ──reflect()──> Reflector
                                                               │
                                                        MetaLearner tracks:
                                                        - reflection quality
                                                        - rule impact
                                                        - forgetting effectiveness
                                                               │
                                                        MetaLearner learns:
                                                        - better reflection prompts
                                                        - optimal thresholds
                                                        - rule format patterns

When collective intelligence is active, meta-learnings are contributed too.
This means the system doesn't just share WHAT agents learned — it shares
HOW BEST TO LEARN for each agent type.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any

from agentloops.models import Reflection, Rule, _new_id, _now
from agentloops.storage.base import BaseStorage

logger = logging.getLogger("agentloops.meta")


@dataclass
class RuleImpact:
    """Tracks whether a rule actually improved outcomes after being applied."""

    rule_id: str
    rule_text: str
    confidence_at_creation: float
    outcomes_before: list[float] = field(default_factory=list)
    outcomes_after: list[float] = field(default_factory=list)
    id: str = field(default_factory=_new_id)
    created_at: str = field(default_factory=_now)
    rule_type: str = "if_then"  # Track which rule type this is

    @property
    def impact_score(self) -> float | None:
        """How much did outcomes improve after this rule was applied?

        Returns None if not enough data yet. Positive = improvement.
        """
        if len(self.outcomes_before) < 3 or len(self.outcomes_after) < 3:
            return None

        avg_before = sum(self.outcomes_before) / len(self.outcomes_before)
        avg_after = sum(self.outcomes_after) / len(self.outcomes_after)

        if avg_before == 0:
            return None

        return (avg_after - avg_before) / avg_before

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "rule_id": self.rule_id,
            "rule_text": self.rule_text,
            "confidence_at_creation": self.confidence_at_creation,
            "outcomes_before": self.outcomes_before,
            "outcomes_after": self.outcomes_after,
            "impact_score": self.impact_score,
            "rule_type": self.rule_type,
            "created_at": self.created_at,
        }


@dataclass
class ReflectionQuality:
    """Tracks whether a reflection produced useful rules."""

    reflection_id: str
    rules_suggested: int
    rules_adopted: int  # Rules that were actually added
    rules_with_positive_impact: int  # Rules that improved outcomes
    rules_with_negative_impact: int  # Rules that made things worse
    id: str = field(default_factory=_new_id)
    created_at: str = field(default_factory=_now)

    @property
    def quality_score(self) -> float:
        """How useful was this reflection? 0.0 to 1.0."""
        if self.rules_suggested == 0:
            return 0.0

        adoption_rate = self.rules_adopted / self.rules_suggested
        if self.rules_adopted == 0:
            return adoption_rate * 0.5  # Penalize but don't zero out

        positive_rate = self.rules_with_positive_impact / self.rules_adopted
        negative_rate = self.rules_with_negative_impact / self.rules_adopted

        return adoption_rate * 0.3 + positive_rate * 0.5 + (1 - negative_rate) * 0.2

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "reflection_id": self.reflection_id,
            "rules_suggested": self.rules_suggested,
            "rules_adopted": self.rules_adopted,
            "rules_with_positive_impact": self.rules_with_positive_impact,
            "rules_with_negative_impact": self.rules_with_negative_impact,
            "quality_score": self.quality_score,
            "created_at": self.created_at,
        }


class MetaLearner:
    """Learns how to learn better by tracking the effectiveness of the learning system itself.

    Tracks:
    1. Rule impact — did applying a rule actually improve outcomes?
    2. Reflection quality — did a reflection produce useful rules?
    3. Learning patterns — what characteristics of rules correlate with positive impact?

    Over time, this produces meta-rules like:
    - "Rules with specific evidence ('because 4/5 succeeded') are 2x more impactful than vague rules"
    - "Reflection after 8 runs produces better rules than after 5 for this agent type"
    - "Rules about what to AVOID are more impactful than rules about what to DO"
    """

    def __init__(self, storage: BaseStorage, agent_name: str) -> None:
        self._storage = storage
        self._agent_name = agent_name
        self._rule_impacts: dict[str, RuleImpact] = {}
        self._reflection_qualities: list[ReflectionQuality] = []

    def track_rule_created(self, rule: Rule, recent_outcomes: list[float]) -> None:
        """Record the baseline outcomes when a rule is created.

        Call this immediately after a new rule is generated, passing
        the recent outcome scores BEFORE the rule was applied.
        """
        self._rule_impacts[rule.id] = RuleImpact(
            rule_id=rule.id,
            rule_text=rule.text,
            confidence_at_creation=rule.confidence,
            outcomes_before=recent_outcomes[-10:],
            rule_type=getattr(rule, "rule_type", "if_then"),
        )

    def track_outcome_with_rule(self, rule_id: str, outcome_score: float) -> None:
        """Record an outcome achieved while a rule was active.

        Call this on every tracked run, for each active rule.
        """
        impact = self._rule_impacts.get(rule_id)
        if impact:
            impact.outcomes_after.append(outcome_score)

    def track_reflection_quality(
        self,
        reflection: Reflection,
        rules_adopted: int,
        rules_positive: int = 0,
        rules_negative: int = 0,
    ) -> ReflectionQuality:
        """Record how useful a reflection was.

        Call this after enough time has passed to assess whether
        the reflection's suggested rules had positive impact.
        """
        quality = ReflectionQuality(
            reflection_id=reflection.id,
            rules_suggested=len(reflection.suggested_rules),
            rules_adopted=rules_adopted,
            rules_with_positive_impact=rules_positive,
            rules_with_negative_impact=rules_negative,
        )
        self._reflection_qualities.append(quality)
        return quality

    def get_rule_impacts(self) -> list[RuleImpact]:
        """Get all tracked rule impacts, sorted by impact score."""
        impacts = list(self._rule_impacts.values())
        # Sort by impact score, putting None (not enough data) at the end
        return sorted(
            impacts,
            key=lambda i: (i.impact_score is not None, i.impact_score or 0),
            reverse=True,
        )

    def get_best_rule_patterns(self) -> dict[str, Any]:
        """Analyze what rule characteristics correlate with positive impact.

        Returns patterns the reflection engine can use to generate better rules.
        """
        impacts = [i for i in self._rule_impacts.values() if i.impact_score is not None]

        if len(impacts) < 5:
            return {"status": "not_enough_data", "min_needed": 5, "current": len(impacts)}

        positive = [i for i in impacts if (i.impact_score or 0) > 0]
        negative = [i for i in impacts if (i.impact_score or 0) <= 0]

        patterns: dict[str, Any] = {
            "total_rules_tracked": len(impacts),
            "positive_impact_rate": len(positive) / len(impacts),
            "avg_positive_impact": (
                sum(i.impact_score for i in positive) / len(positive)
                if positive else 0
            ),
        }

        # Analyze rule text patterns
        avoid_rules = [i for i in positive if any(
            kw in i.rule_text.lower() for kw in ("avoid", "never", "don't")
        )]
        do_rules = [i for i in positive if not any(
            kw in i.rule_text.lower() for kw in ("avoid", "never", "don't")
        )]

        patterns["avoid_rules_positive_rate"] = (
            len(avoid_rules) / len([
                i for i in impacts if any(
                    kw in i.rule_text.lower() for kw in ("avoid", "never", "don't")
                )
            ]) if any(
                any(kw in i.rule_text.lower() for kw in ("avoid", "never", "don't"))
                for i in impacts
            ) else None
        )

        # Evidence pattern
        evidence_rules = [i for i in positive if "because" in i.rule_text.lower()]
        patterns["rules_with_evidence_positive_rate"] = (
            len(evidence_rules) / len([
                i for i in impacts if "because" in i.rule_text.lower()
            ]) if any("because" in i.rule_text.lower() for i in impacts) else None
        )

        # Confidence correlation
        if positive:
            patterns["avg_confidence_positive_rules"] = (
                sum(i.confidence_at_creation for i in positive) / len(positive)
            )
        if negative:
            patterns["avg_confidence_negative_rules"] = (
                sum(i.confidence_at_creation for i in negative) / len(negative)
            )

        return patterns

    def get_best_rule_type(self) -> dict[str, Any]:
        """Compare impact across rule types (if_then, scoring, decision_table).

        Returns stats per type so the reflection engine knows which format works best.
        """
        impacts = [i for i in self._rule_impacts.values() if i.impact_score is not None]

        if len(impacts) < 5:
            return {"status": "not_enough_data"}

        by_type: dict[str, list[float]] = {}
        for i in impacts:
            rt = getattr(i, "rule_type", "if_then")
            by_type.setdefault(rt, []).append(i.impact_score)

        results: dict[str, Any] = {}
        for rtype, scores in by_type.items():
            if scores:
                results[rtype] = {
                    "count": len(scores),
                    "avg_impact": round(sum(scores) / len(scores), 4),
                    "positive_rate": round(
                        len([s for s in scores if s > 0]) / len(scores), 4
                    ),
                }

        return results

    def get_meta_rules(self) -> list[str]:
        """Generate meta-rules that can improve the reflection engine.

        These are injected into the reflection prompt to help the LLM
        generate better rules based on what's worked historically.
        """
        patterns = self.get_best_rule_patterns()

        if patterns.get("status") == "not_enough_data":
            return []

        meta_rules: list[str] = []

        # Evidence pattern
        evidence_rate = patterns.get("rules_with_evidence_positive_rate")
        if evidence_rate is not None and evidence_rate > 0.6:
            meta_rules.append(
                f"Rules with explicit evidence ('because X') have a {evidence_rate:.0%} "
                f"positive impact rate. Always include evidence."
            )

        # Avoid vs do pattern
        avoid_rate = patterns.get("avoid_rules_positive_rate")
        if avoid_rate is not None:
            if avoid_rate > 0.7:
                meta_rules.append(
                    f"Rules about what to AVOID have a {avoid_rate:.0%} positive impact rate. "
                    f"Prioritize 'avoid' rules when you see failure patterns."
                )
            elif avoid_rate < 0.3:
                meta_rules.append(
                    f"Rules about what to AVOID have only a {avoid_rate:.0%} positive impact rate. "
                    f"Focus on positive 'do this' rules instead."
                )

        # Confidence calibration
        avg_pos_conf = patterns.get("avg_confidence_positive_rules")
        avg_neg_conf = patterns.get("avg_confidence_negative_rules")
        if avg_pos_conf is not None and avg_neg_conf is not None:
            if avg_pos_conf > avg_neg_conf + 0.1:
                meta_rules.append(
                    f"Higher-confidence rules ({avg_pos_conf:.2f} avg) tend to have positive impact. "
                    f"Lower-confidence rules ({avg_neg_conf:.2f} avg) tend to have negative impact. "
                    f"Only suggest rules when you have strong evidence."
                )

        # Overall hit rate
        pos_rate = patterns.get("positive_impact_rate", 0)
        if pos_rate < 0.5:
            meta_rules.append(
                f"Only {pos_rate:.0%} of past rules had positive impact. "
                f"Be more selective — fewer, higher-quality rules are better."
            )

        # Rule type effectiveness
        type_stats = self.get_best_rule_type()
        if type_stats.get("status") != "not_enough_data":
            best_type = max(
                ((t, s) for t, s in type_stats.items() if isinstance(s, dict) and s.get("count", 0) >= 3),
                key=lambda x: x[1]["positive_rate"],
                default=None,
            )
            if best_type:
                t, s = best_type
                if t != "if_then" and s["positive_rate"] > 0.6:
                    meta_rules.append(
                        f"'{t}' rules have {s['positive_rate']:.0%} positive impact rate "
                        f"({s['count']} tracked). Consider using this format for multi-factor decisions."
                    )

        return meta_rules

    def get_optimal_threshold(self) -> int | None:
        """Analyze reflection quality to suggest the optimal reflection_threshold.

        Returns the number of runs that produces the best reflection quality,
        or None if not enough data.
        """
        if len(self._reflection_qualities) < 3:
            return None

        # This is a simplified version — in production, you'd correlate
        # reflection quality with the number of runs available at the time
        avg_quality = sum(
            r.quality_score for r in self._reflection_qualities
        ) / len(self._reflection_qualities)

        logger.debug(f"Average reflection quality: {avg_quality:.2f}")
        return None  # Need more sophisticated analysis with run counts
