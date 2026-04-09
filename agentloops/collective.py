"""Collective Intelligence — sync anonymized learnings with the global network.

This is the core of AgentLoops' network effect. Every agent contributes
anonymized rules and outcome stats. In return, agents get access to
proven rules from all agents of the same type.

Privacy model:
  - SENT: rule text, confidence, evidence count, outcome stats (success rate + sample size)
  - NEVER SENT: raw inputs, raw outputs, metadata, agent names, user data

Tiers:
  - Free: Contributes anonymized rules. Gets static seed rules (bundled with package).
  - Pro: Contributes + gets LIVE global rules on every enhance_prompt() call.
  - Enterprise: Contributes + live rules + benchmarking + custom filters.
"""

from __future__ import annotations

import json
import logging
import os
import threading
from typing import Any

from agentloops.models import Rule

logger = logging.getLogger("agentloops.collective")

COLLECTIVE_API_URL = "https://api.agent-loops.com/v1/collective"


class CollectiveClient:
    """Syncs anonymized learnings with the AgentLoops global network.

    Operates in two modes:
    - Background sync (free): periodically sends anonymized rules, non-blocking
    - Active sync (pro/enterprise): pulls live global rules on demand

    All network calls are fire-and-forget on a background thread.
    The library NEVER blocks your agent waiting for a network response.
    """

    def __init__(
        self,
        agent_type: str,
        api_key: str | None = None,
        api_url: str | None = None,
        enabled: bool = True,
    ) -> None:
        self._agent_type = agent_type
        self._api_key = api_key
        self._api_url = api_url or os.environ.get(
            "AGENTLOOPS_COLLECTIVE_URL", COLLECTIVE_API_URL
        )
        self._enabled = enabled and agent_type is not None
        self._tier = self._resolve_tier()

    def _resolve_tier(self) -> str:
        if not self._enabled:
            return "disabled"
        if self._api_key:
            # Could check key format for enterprise vs pro
            return "pro"
        return "free"

    # -- Contributing rules to the network ---------------------------------

    def contribute_rules(self, rules: list[Rule]) -> None:
        """Send anonymized rules to the global network (non-blocking).

        Only sends: rule text, confidence, evidence count, agent_type.
        Never sends: raw inputs, outputs, metadata, or user data.
        """
        if not self._enabled or not rules:
            return

        anonymized = [
            {
                "agent_type": self._agent_type,
                "rule_text": rule.text,
                "confidence": rule.confidence,
                "evidence_count": rule.evidence_count,
            }
            for rule in rules
            if rule.active and rule.confidence >= 0.6  # Only contribute validated rules
        ]

        if not anonymized:
            return

        # Fire-and-forget on background thread — never block the agent
        thread = threading.Thread(
            target=self._send_contribution,
            args=(anonymized,),
            daemon=True,
        )
        thread.start()

    def contribute_outcome_stats(
        self,
        success_rate: float,
        sample_size: int,
    ) -> None:
        """Send anonymized outcome stats (non-blocking).

        Only sends: agent_type, success rate, sample size.
        """
        if not self._enabled:
            return

        stats = {
            "agent_type": self._agent_type,
            "success_rate": round(success_rate, 4),
            "sample_size": sample_size,
        }

        thread = threading.Thread(
            target=self._send_stats,
            args=(stats,),
            daemon=True,
        )
        thread.start()

    # -- Pulling global rules from the network -----------------------------

    def pull_global_rules(self) -> list[Rule]:
        """Pull live global rules for this agent type from the network.

        Only available for Pro/Enterprise tiers (requires api_key).
        Free tier uses static seed rules bundled with the package.

        Returns:
            List of Rule objects from the global network.
            Empty list if disabled, no api_key, or network error.
        """
        if self._tier not in ("pro", "enterprise"):
            return []

        try:
            import urllib.request

            req = urllib.request.Request(
                f"{self._api_url}/rules/{self._agent_type}",
                headers={
                    "Authorization": f"Bearer {self._api_key}",
                    "Content-Type": "application/json",
                },
            )
            with urllib.request.urlopen(req, timeout=5) as resp:
                data = json.loads(resp.read().decode())

            return [
                Rule(
                    text=r["rule_text"],
                    confidence=r["confidence"],
                    evidence_count=r.get("evidence_count", 1),
                    evidence=[f"global:{self._agent_type}"],
                )
                for r in data.get("rules", [])
            ]
        except Exception as e:
            logger.debug(f"Failed to pull global rules: {e}")
            return []

    # -- Benchmarking (Enterprise only) ------------------------------------

    def get_benchmark(self) -> dict[str, Any] | None:
        """Get benchmarking data for this agent type (Enterprise only).

        Returns percentile ranking compared to all agents of the same type.
        """
        if self._tier != "enterprise":
            return None

        try:
            import urllib.request

            req = urllib.request.Request(
                f"{self._api_url}/benchmark/{self._agent_type}",
                headers={
                    "Authorization": f"Bearer {self._api_key}",
                    "Content-Type": "application/json",
                },
            )
            with urllib.request.urlopen(req, timeout=5) as resp:
                return json.loads(resp.read().decode())
        except Exception as e:
            logger.debug(f"Failed to get benchmark: {e}")
            return None

    # -- Internal network helpers ------------------------------------------

    def _send_contribution(self, anonymized_rules: list[dict]) -> None:
        """Send anonymized rules to the collective API."""
        try:
            import urllib.request

            data = json.dumps({
                "agent_type": self._agent_type,
                "rules": anonymized_rules,
            }).encode()

            req = urllib.request.Request(
                f"{self._api_url}/contribute",
                data=data,
                headers={"Content-Type": "application/json"},
                method="POST",
            )
            if self._api_key:
                req.add_header("Authorization", f"Bearer {self._api_key}")

            with urllib.request.urlopen(req, timeout=5) as resp:
                logger.debug(f"Contributed {len(anonymized_rules)} rules")
        except Exception as e:
            # Never crash the agent for a network error
            logger.debug(f"Contribution failed (non-blocking): {e}")

    def _send_stats(self, stats: dict) -> None:
        """Send anonymized outcome stats."""
        try:
            import urllib.request

            data = json.dumps(stats).encode()
            req = urllib.request.Request(
                f"{self._api_url}/stats",
                data=data,
                headers={"Content-Type": "application/json"},
                method="POST",
            )
            if self._api_key:
                req.add_header("Authorization", f"Bearer {self._api_key}")

            with urllib.request.urlopen(req, timeout=5) as resp:
                logger.debug("Stats contributed")
        except Exception as e:
            logger.debug(f"Stats contribution failed (non-blocking): {e}")

    @property
    def enabled(self) -> bool:
        return self._enabled

    @property
    def tier(self) -> str:
        return self._tier


def opt_out():
    """Globally disable collective intelligence contribution.

    Call this if you don't want any data sent to the network.

    Usage:
        import agentloops.collective
        agentloops.collective.opt_out()
    """
    os.environ["AGENTLOOPS_COLLECTIVE_DISABLED"] = "1"


def is_opted_out() -> bool:
    """Check if collective intelligence is disabled."""
    return os.environ.get("AGENTLOOPS_COLLECTIVE_DISABLED", "").lower() in ("1", "true", "yes")
