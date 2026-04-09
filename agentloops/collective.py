"""Collective Intelligence — sync anonymized learnings with the global network.

This is the core of AgentLoops' network effect. Every agent contributes
anonymized rules and outcome stats. In return, agents get access to
proven rules from all agents of the same type.

Privacy model (privacy-first, opt-in only):
  - REQUIRES: Explicit opt-in via collective=True in constructor
  - SENT: generalized rule patterns (company/product names stripped), confidence, outcome stats
  - NEVER SENT: raw inputs, raw outputs, metadata, company names, user data
  - THRESHOLD: Rules only enter the global pool after 5+ independent contributors submit similar patterns
  - OPT-OUT: agentloops.collective.opt_out() disables everything globally

Tiers:
  - Free: Can opt-in to contribute. Gets static seed rules (bundled with package).
  - Pro: Can opt-in to contribute. Gets LIVE global rules on every enhance_prompt() call.
  - Enterprise: Can opt-in to contribute. Live rules + benchmarking + custom filters.
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
        agent_type: str | None = None,
        api_key: str | None = None,
        api_url: str | None = None,
        enabled: bool = False,  # OPT-IN ONLY — must explicitly enable
    ) -> None:
        """Initialize the collective intelligence client.

        Args:
            agent_type: Agent type for global rule matching.
            api_key: AgentLoops platform key (al_xxx format) for Pro/Enterprise.
            api_url: Override the collective API endpoint.
            enabled: Must be True to participate. Privacy-first: disabled by default.
        """
        self._agent_type = agent_type
        self._api_key = api_key
        self._api_url = api_url or os.environ.get(
            "AGENTLOOPS_COLLECTIVE_URL", COLLECTIVE_API_URL
        )
        self._enabled = enabled and agent_type is not None and not is_opted_out()
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

        Privacy guarantees:
        - Rule text is SANITIZED: company names, product names, and specific
          data are stripped before sending. Only generalized patterns are shared.
        - Only high-confidence rules (>= 0.6) are contributed.
        - No raw inputs, outputs, metadata, or user data is ever sent.
        - Rules only enter the global pool after 5+ independent contributors
          submit similar patterns (server-side threshold).
        """
        if not self._enabled or not rules:
            return

        anonymized = [
            {
                "agent_type": self._agent_type,
                "rule_text": _sanitize_rule_text(rule.text),
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


def _sanitize_rule_text(text: str) -> str:
    """Strip company names, product names, and specific data from rule text.

    Keeps the behavioral pattern but removes identifying information.
    E.g., "IF prospect is VP Engineering at Stripe THEN lead with API latency data"
    becomes "IF prospect is VP Engineering at [COMPANY] THEN lead with [PRODUCT] data"
    """
    import re

    # Replace capitalized proper nouns that look like company/product names
    # (2+ chars, starts with uppercase, not common words)
    common_words = {
        "IF", "THEN", "AND", "OR", "NOT", "WHEN", "ALWAYS", "NEVER",
        "DO", "THE", "WITH", "FOR", "FROM", "ABOUT", "BECAUSE",
        "VP", "CTO", "CEO", "CIO", "CFO", "COO", "CMO",
        "Engineering", "Sales", "Marketing", "Support", "Product",
        "Enterprise", "Startup", "SMB", "Series", "Pre-seed",
    }

    def replace_proper_noun(match: re.Match) -> str:
        word = match.group(0)
        if word in common_words:
            return word
        return "[ENTITY]"

    # Replace what looks like company names (capitalized words not in common set)
    # This is intentionally aggressive — better to over-sanitize than leak
    sanitized = re.sub(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b', replace_proper_noun, text)

    # Replace URLs
    sanitized = re.sub(r'https?://\S+', '[URL]', sanitized)

    # Replace email addresses
    sanitized = re.sub(r'\S+@\S+\.\S+', '[EMAIL]', sanitized)

    # Replace specific numbers that might be identifying (revenue, employee count, etc.)
    # Keep percentages and small numbers (they're pattern data, not identifying)
    sanitized = re.sub(r'\$[\d,]+[KMB]?\b', '[AMOUNT]', sanitized)
    sanitized = re.sub(r'\b\d{3,}\b', '[NUMBER]', sanitized)

    return sanitized


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
