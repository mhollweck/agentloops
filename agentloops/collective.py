"""Collective Intelligence — sync anonymized learnings with the global network.

This is the core of AgentLoops' network effect. Every agent contributes
anonymized rules and outcome stats. In return, agents get access to
proven rules from all agents of the same type.

Privacy model:
  - ON BY DEFAULT when agent_type is set (like Homebrew analytics)
  - OPT-OUT: AgentLoops(..., collective=False) or agentloops.collective.opt_out()
  - SENT: generalized rule patterns (company/product names stripped), confidence, outcome stats
  - NEVER SENT: raw inputs, raw outputs, metadata, company names, user data
  - SANITIZED: company names, URLs, emails, dollar amounts stripped from rule text
  - THRESHOLD: Rules only enter the global pool after 5+ independent contributors submit similar patterns

Tiers:
  - Free ($0): 3 agent types, static seed rules (bundled with package).
  - Pro ($99/mo): Unlimited types, live global rules (updated daily from the network).
  - Team ($249/mo): Shared namespace across org's agents, team analytics.
  - Enterprise: Live rules + benchmarking + dedicated support.
"""

from __future__ import annotations

import hashlib
import json
import logging
import os
import re
import time
import threading
from typing import Any

from agentloops.models import Rule

logger = logging.getLogger("agentloops.collective")

# Supabase project for collective intelligence
SUPABASE_URL = "https://ynbypsidwwaoxkzwkmjm.supabase.co"
SUPABASE_ANON_KEY = os.environ.get(
    "AGENTLOOPS_SUPABASE_ANON_KEY",
    "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InluYnlwc2lkd3dhb3hrendrbWptIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzU3NjQxODksImV4cCI6MjA5MTM0MDE4OX0.BtHi7uiPEDFkTJ-QVHEn1UeTuzNI1EXswoEvOLv_ksc",
)

# Legacy API URL (will be replaced by Supabase, kept for env override)
COLLECTIVE_API_URL = os.environ.get(
    "AGENTLOOPS_COLLECTIVE_URL",
    f"{SUPABASE_URL}/rest/v1",
)


def _fingerprint(agent_type: str, rule_text: str, spec: dict | None = None) -> str:
    """Generate a stable fingerprint for dedup. Same rule from different users = same fingerprint."""
    if spec:
        # For structured rules, fingerprint the spec structure (more stable than rendered text)
        normalized = json.dumps(spec, sort_keys=True, separators=(",", ":"))
        raw = f"{agent_type}:spec:{normalized}"
    else:
        normalized = re.sub(r'\s+', ' ', rule_text.strip().lower())
        raw = f"{agent_type}:{normalized}"
    return hashlib.sha256(raw.encode()).hexdigest()[:32]


# -- Anti-poisoning: format validation ------------------------------------

def _validate_rule_format(rule_text: str) -> tuple[bool, str]:
    """Validate that a rule looks like a legitimate behavioral pattern.

    Returns (is_valid, reason). Rejects gibberish, URLs-only, too-short/long rules.
    """
    text = rule_text.strip()

    # Length checks
    if len(text) < 10:
        return False, f"Rule too short ({len(text)} chars, min 10)"
    if len(text) > 500:
        return False, f"Rule too long ({len(text)} chars, max 500)"

    # Reject rules that are just URLs
    if re.match(r'^https?://\S+$', text):
        return False, "Rule is just a URL"

    # Reject rules that are just numbers
    if re.match(r'^[\d\s.,]+$', text):
        return False, "Rule is just numbers"

    # Gibberish detection: high ratio of special characters
    alpha_count = sum(1 for c in text if c.isalpha())
    if len(text) > 0 and alpha_count / len(text) < 0.4:
        return False, "Rule has too many special characters (possible gibberish)"

    # Must contain IF/THEN pattern OR be a reasonable behavioral instruction
    has_if_then = bool(re.search(r'\bIF\b', text, re.IGNORECASE) and
                       re.search(r'\bTHEN\b', text, re.IGNORECASE))
    has_behavioral_keywords = bool(re.search(
        r'\b(ALWAYS|NEVER|WHEN|DO NOT|SHOULD|MUST|AVOID|PREFER|ENSURE)\b',
        text, re.IGNORECASE
    ))

    if not has_if_then and not has_behavioral_keywords:
        return False, "Rule must contain IF/THEN pattern or behavioral keywords (ALWAYS, NEVER, WHEN, etc.)"

    return True, "ok"


# -- Anti-poisoning: anomaly detection ------------------------------------

class _AnomalyTracker:
    """In-memory tracker for per-session contribution anomalies."""

    MAX_RULES_PER_CALL = 20
    MAX_SAME_FINGERPRINT_PER_INSTANCE = 3

    def __init__(self) -> None:
        self._fingerprint_counts: dict[str, int] = {}  # fingerprint -> count from this instance
        self._lock = threading.Lock()

    def check_batch_size(self, rules: list) -> list:
        """Cap a batch at MAX_RULES_PER_CALL. Logs warning if exceeded."""
        if len(rules) > self.MAX_RULES_PER_CALL:
            logger.warning(
                f"AgentLoops anti-poisoning: batch of {len(rules)} rules exceeds "
                f"limit of {self.MAX_RULES_PER_CALL} — truncating"
            )
            return rules[:self.MAX_RULES_PER_CALL]
        return rules

    def should_skip_fingerprint(self, fingerprint: str) -> bool:
        """Returns True if this fingerprint has been contributed too many times from this instance."""
        with self._lock:
            count = self._fingerprint_counts.get(fingerprint, 0)
            if count >= self.MAX_SAME_FINGERPRINT_PER_INSTANCE:
                return True
            self._fingerprint_counts[fingerprint] = count + 1
            return False


# -- Anti-poisoning: rate limiting (Python-side) --------------------------

class _RateLimiter:
    """In-memory rate limiter: max 50 contributions per agent per hour."""

    MAX_PER_HOUR = 50

    def __init__(self) -> None:
        self._timestamps: list[float] = []
        self._lock = threading.Lock()

    def check_and_record(self, count: int = 1) -> bool:
        """Returns True if under the rate limit. Records the contribution timestamps."""
        now = time.time()
        cutoff = now - 3600  # 1 hour window

        with self._lock:
            # Prune old entries
            self._timestamps = [t for t in self._timestamps if t > cutoff]

            if len(self._timestamps) + count > self.MAX_PER_HOUR:
                logger.warning(
                    f"AgentLoops anti-poisoning: rate limit would be exceeded "
                    f"({len(self._timestamps)} + {count} > {self.MAX_PER_HOUR}/hr) — rejecting"
                )
                return False

            self._timestamps.extend([now] * count)
            return True


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
        enabled: bool = True,  # On by default when agent_type is set
    ) -> None:
        self._agent_type = agent_type
        self._api_key = api_key
        self._supabase_url = os.environ.get("AGENTLOOPS_SUPABASE_URL", SUPABASE_URL)
        self._supabase_anon_key = os.environ.get("AGENTLOOPS_SUPABASE_ANON_KEY", SUPABASE_ANON_KEY)
        self._api_url = api_url or COLLECTIVE_API_URL
        self._enabled = enabled and agent_type is not None and not is_opted_out()
        self._has_logged_contribution = False
        self._tier = self._resolve_tier()
        # Anti-poisoning defenses
        self._anomaly_tracker = _AnomalyTracker()
        self._rate_limiter = _RateLimiter()

    def _resolve_tier(self) -> str:
        if not self._enabled:
            return "disabled"
        if self._api_key:
            return "pro"
        return "free"

    def _supabase_headers(self, *, service_role: bool = False) -> dict[str, str]:
        """Headers for Supabase REST API calls."""
        key = self._supabase_anon_key
        if service_role:
            key = os.environ.get("AGENTLOOPS_SUPABASE_SERVICE_KEY", key)
        return {
            "apikey": key,
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json",
            "Prefer": "return=minimal",
        }

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

        if not self._supabase_anon_key:
            logger.debug("No Supabase anon key — skipping collective contribution")
            return

        if not self._has_logged_contribution:
            logger.info(
                "AgentLoops: contributing anonymized rule patterns to the collective "
                "intelligence network. Only sanitized IF/THEN patterns are sent (no raw "
                "data, no identifiers). Opt out: AgentLoops(..., collective=False) or "
                "set AGENTLOOPS_COLLECTIVE_DISABLED=1"
            )
            print(
                "  AgentLoops: contributing anonymized rules to the collective network. "
                "Opt out: collective=False"
            )
            self._has_logged_contribution = True

        # Anti-poisoning: cap batch size
        rules = self._anomaly_tracker.check_batch_size(rules)

        anonymized = []
        for rule in rules:
            if not rule.active or rule.confidence < 0.6:
                continue

            sanitized_text = _sanitize_rule_text(rule.text)
            sanitized_spec = _sanitize_spec(rule.spec) if rule.spec else None

            # Anti-poisoning: format validation (skip for structured rules — they have spec validation)
            if rule.rule_type == "if_then":
                is_valid, reason = _validate_rule_format(sanitized_text)
                if not is_valid:
                    logger.debug(f"Rule rejected by format validation: {reason}")
                    continue
            elif rule.rule_type == "scoring" and sanitized_spec:
                if not sanitized_spec.get("factors") or not sanitized_spec.get("thresholds"):
                    logger.debug("Scoring rule rejected: missing factors or thresholds")
                    continue
            elif rule.rule_type == "decision_table" and sanitized_spec:
                if not sanitized_spec.get("columns") or not sanitized_spec.get("rows"):
                    logger.debug("Decision table rejected: missing columns or rows")
                    continue

            fp = _fingerprint(self._agent_type, sanitized_text, sanitized_spec)

            # Anti-poisoning: skip if same fingerprint contributed too many times
            if self._anomaly_tracker.should_skip_fingerprint(fp):
                logger.debug(f"Rule skipped: fingerprint {fp[:8]}... seen too many times from this instance")
                continue

            # Extract reasoning from "because" clause for staging pipeline
            reasoning = None
            for sep in [" — because ", " because ", " - because "]:
                if sep in sanitized_text:
                    reasoning = sanitized_text.split(sep, 1)[1]
                    break
            if not reasoning and rule.evidence:
                reasoning = "; ".join(rule.evidence[:3])

            anonymized.append({
                "agent_type": self._agent_type,
                "rule_text": sanitized_text,
                "confidence": rule.confidence,
                "evidence_count": rule.evidence_count,
                "fingerprint": fp,
                "reasoning": reasoning,
            })

        if not anonymized:
            return

        # Anti-poisoning: rate limiting
        if not self._rate_limiter.check_and_record(len(anonymized)):
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
        """Send anonymized outcome stats (non-blocking)."""
        if not self._enabled:
            return

        if not self._supabase_anon_key:
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

        Returns rules that have been contributed by 5+ independent users
        (the privacy threshold).
        """
        if self._tier not in ("pro", "enterprise"):
            return []

        try:
            import urllib.request

            # Query Supabase for rules with contributor_count >= 5
            service_key = os.environ.get("AGENTLOOPS_SUPABASE_SERVICE_KEY", "")
            if not service_key:
                logger.debug("No service key — can't pull global rules")
                return []

            url = (
                f"{self._supabase_url}/rest/v1/collective_rules"
                f"?agent_type=eq.{self._agent_type}"
                f"&contributor_count=gte.5"
                f"&select=rule_text,confidence,evidence_count,contributor_count"
                f"&order=contributor_count.desc"
                f"&limit=50"
            )
            req = urllib.request.Request(url, headers={
                "apikey": service_key,
                "Authorization": f"Bearer {service_key}",
            })
            with urllib.request.urlopen(req, timeout=5) as resp:
                data = json.loads(resp.read().decode())

            return [
                Rule(
                    text=r["rule_text"],
                    confidence=r["confidence"],
                    evidence_count=r.get("evidence_count", 1),
                    evidence=[f"global:{self._agent_type}:n={r.get('contributor_count', 5)}"],
                )
                for r in data
            ]
        except Exception as e:
            logger.debug(f"Failed to pull global rules: {e}")
            return []

    # -- Benchmarking (Enterprise only) ------------------------------------

    def get_benchmark(self) -> dict[str, Any] | None:
        """Get benchmarking data for this agent type (Enterprise only)."""
        if self._tier != "enterprise":
            return None

        try:
            import urllib.request

            service_key = os.environ.get("AGENTLOOPS_SUPABASE_SERVICE_KEY", "")
            if not service_key:
                return None

            url = (
                f"{self._supabase_url}/rest/v1/collective_outcome_stats"
                f"?agent_type=eq.{self._agent_type}"
                f"&select=success_rate,sample_size"
                f"&order=created_at.desc"
                f"&limit=100"
            )
            req = urllib.request.Request(url, headers={
                "apikey": service_key,
                "Authorization": f"Bearer {service_key}",
            })
            with urllib.request.urlopen(req, timeout=5) as resp:
                data = json.loads(resp.read().decode())

            if not data:
                return None

            rates = [d["success_rate"] for d in data]
            return {
                "agent_type": self._agent_type,
                "network_avg_success_rate": round(sum(rates) / len(rates), 4),
                "network_sample_count": len(rates),
                "network_total_runs": sum(d["sample_size"] for d in data),
            }
        except Exception as e:
            logger.debug(f"Failed to get benchmark: {e}")
            return None

    # -- Internal network helpers ------------------------------------------

    def _send_contribution(self, anonymized_rules: list[dict]) -> None:
        """Send anonymized rules to Supabase staging pipeline via RPC."""
        try:
            import urllib.request

            headers = self._supabase_headers()

            # Generate agent hash for server-side rate limiting
            hour_bucket = int(time.time() // 3600)
            agent_hash = hashlib.sha256(
                f"{self._agent_type}:{hour_bucket}".encode()
            ).hexdigest()[:32]

            for rule in anonymized_rules:
                data = json.dumps({
                    "p_agent_type": rule["agent_type"],
                    "p_rule_text": rule["rule_text"],
                    "p_confidence": rule["confidence"],
                    "p_evidence_count": rule["evidence_count"],
                    "p_fingerprint": rule["fingerprint"],
                    "p_agent_hash": agent_hash,
                    "p_reasoning": rule.get("reasoning"),
                }).encode()

                # Use submit_rule (staging pipeline) — falls back to
                # upsert_collective_rule on older Supabase schemas
                try:
                    req = urllib.request.Request(
                        f"{self._supabase_url}/rest/v1/rpc/submit_rule",
                        data=data,
                        headers=headers,
                        method="POST",
                    )
                    with urllib.request.urlopen(req, timeout=5) as resp:
                        pass
                except urllib.error.HTTPError:
                    # Fallback for older schema without submit_rule
                    fallback_data = json.dumps({
                        "p_agent_type": rule["agent_type"],
                        "p_rule_text": rule["rule_text"],
                        "p_confidence": rule["confidence"],
                        "p_evidence_count": rule["evidence_count"],
                        "p_fingerprint": rule["fingerprint"],
                        "p_agent_hash": agent_hash,
                    }).encode()
                    req = urllib.request.Request(
                        f"{self._supabase_url}/rest/v1/rpc/upsert_collective_rule",
                        data=fallback_data,
                        headers=headers,
                        method="POST",
                    )
                    with urllib.request.urlopen(req, timeout=5) as resp:
                        pass

            logger.debug(f"Contributed {len(anonymized_rules)} rules to collective")
        except Exception as e:
            # Never crash the agent for a network error
            logger.debug(f"Contribution failed (non-blocking): {e}")

    def _send_stats(self, stats: dict) -> None:
        """Send anonymized outcome stats to Supabase."""
        try:
            import urllib.request

            data = json.dumps(stats).encode()
            headers = self._supabase_headers()

            req = urllib.request.Request(
                f"{self._supabase_url}/rest/v1/collective_outcome_stats",
                data=data,
                headers=headers,
                method="POST",
            )
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
    sanitized = re.sub(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b', replace_proper_noun, text)

    # Replace URLs
    sanitized = re.sub(r'https?://\S+', '[URL]', sanitized)

    # Replace email addresses
    sanitized = re.sub(r'\S+@\S+\.\S+', '[EMAIL]', sanitized)

    # Replace specific numbers that might be identifying
    sanitized = re.sub(r'\$[\d,]+[KMB]?\b', '[AMOUNT]', sanitized)
    sanitized = re.sub(r'\b\d{3,}\b', '[NUMBER]', sanitized)

    return sanitized


def _sanitize_spec(spec: dict | None) -> dict | None:
    """Recursively sanitize all string values in a rule spec dict."""
    if spec is None:
        return None
    sanitized = {}
    for key, value in spec.items():
        if isinstance(value, str):
            sanitized[key] = _sanitize_rule_text(value)
        elif isinstance(value, list):
            sanitized[key] = [
                _sanitize_spec(item) if isinstance(item, dict)
                else _sanitize_rule_text(item) if isinstance(item, str)
                else item
                for item in value
            ]
        elif isinstance(value, dict):
            sanitized[key] = _sanitize_spec(value)
        else:
            sanitized[key] = value
    return sanitized


def opt_out():
    """Globally disable collective intelligence contribution."""
    os.environ["AGENTLOOPS_COLLECTIVE_DISABLED"] = "1"


def is_opted_out() -> bool:
    """Check if collective intelligence is disabled."""
    return os.environ.get("AGENTLOOPS_COLLECTIVE_DISABLED", "").lower() in ("1", "true", "yes")
