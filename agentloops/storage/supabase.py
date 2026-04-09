"""Supabase cloud storage backend for AgentLoops (Pro tier).

Stores runs, rules, conventions, and reflections in Supabase Postgres,
enabling persistent cloud storage, cross-device access, and the
dashboard. Uses Supabase's Python client for auth and real-time sync.

Required tables (auto-created via migration):
    agentloops_runs
    agentloops_rules
    agentloops_conventions
    agentloops_reflections

Usage:
    from agentloops.storage.supabase import SupabaseStorage

    storage = SupabaseStorage(
        url="https://xxx.supabase.co",
        key="your-service-role-key",
        agent_name="sales-sdr",
    )
    loops = AgentLoops("sales-sdr", storage=storage)
"""

from __future__ import annotations

from typing import Any

from agentloops.models import Convention, Reflection, Rule, Run
from agentloops.storage.base import BaseStorage


class SupabaseStorage(BaseStorage):
    """Supabase-backed storage for AgentLoops cloud tier.

    All data is scoped to the agent_name, so multiple agents can share
    the same Supabase project. Row-level security should be configured
    to scope data per user_id (set via JWT claims).
    """

    def __init__(
        self,
        url: str,
        key: str,
        agent_name: str,
        user_id: str | None = None,
    ) -> None:
        """Initialize Supabase storage.

        Args:
            url: Supabase project URL (https://xxx.supabase.co).
            key: Supabase API key (service role for server, anon for client).
            agent_name: Name of the agent (used to scope all queries).
            user_id: Optional user ID for multi-tenant scoping.
        """
        try:
            from supabase import create_client
        except ImportError:
            raise ImportError(
                "Supabase storage requires the 'supabase' package. "
                "Install it with: pip install agentloops[supabase]"
            )

        self._client = create_client(url, key)
        self._agent_name = agent_name
        self._user_id = user_id

    def _row_base(self) -> dict[str, Any]:
        """Base fields for every row (agent scoping + optional user scoping)."""
        base = {"agent_name": self._agent_name}
        if self._user_id:
            base["user_id"] = self._user_id
        return base

    # -- runs ----------------------------------------------------------------

    def save_run(self, run: Run) -> None:
        data = {**self._row_base(), **run.to_dict()}
        self._client.table("agentloops_runs").upsert(data).execute()

    def get_runs(
        self,
        agent_name: str | None = None,
        last_n: int | None = None,
        outcome_filter: str | None = None,
    ) -> list[Run]:
        name = agent_name or self._agent_name
        query = (
            self._client.table("agentloops_runs")
            .select("*")
            .eq("agent_name", name)
        )
        if self._user_id:
            query = query.eq("user_id", self._user_id)
        if outcome_filter:
            query = query.eq("outcome", outcome_filter)

        query = query.order("created_at", desc=False)

        if last_n:
            # Get total count, then offset to last N
            count_resp = (
                self._client.table("agentloops_runs")
                .select("id", count="exact")
                .eq("agent_name", name)
            )
            if self._user_id:
                count_resp = count_resp.eq("user_id", self._user_id)
            count_result = count_resp.execute()
            total = count_result.count or 0
            if total > last_n:
                query = query.range(total - last_n, total - 1)

        result = query.execute()
        return [Run.from_dict(r) for r in (result.data or [])]

    # -- rules ---------------------------------------------------------------

    def save_rule(self, rule: Rule) -> None:
        data = {**self._row_base(), **rule.to_dict()}
        self._client.table("agentloops_rules").upsert(
            data, on_conflict="id"
        ).execute()

    def get_rules(self, active_only: bool = True) -> list[Rule]:
        query = (
            self._client.table("agentloops_rules")
            .select("*")
            .eq("agent_name", self._agent_name)
        )
        if self._user_id:
            query = query.eq("user_id", self._user_id)
        if active_only:
            query = query.eq("active", True)

        result = query.execute()
        return [Rule.from_dict(r) for r in (result.data or [])]

    # -- conventions ---------------------------------------------------------

    def save_convention(self, convention: Convention) -> None:
        data = {**self._row_base(), **convention.to_dict()}
        self._client.table("agentloops_conventions").upsert(
            data, on_conflict="id"
        ).execute()

    def get_conventions(self, active_only: bool = True) -> list[Convention]:
        query = (
            self._client.table("agentloops_conventions")
            .select("*")
            .eq("agent_name", self._agent_name)
        )
        if self._user_id:
            query = query.eq("user_id", self._user_id)
        if active_only:
            query = query.eq("status", "active")

        result = query.execute()
        return [Convention.from_dict(r) for r in (result.data or [])]

    # -- reflections ---------------------------------------------------------

    def save_reflection(self, reflection: Reflection) -> None:
        data = {**self._row_base(), **reflection.to_dict()}
        self._client.table("agentloops_reflections").upsert(
            data, on_conflict="id"
        ).execute()

    def get_reflections(self, last_n: int | None = None) -> list[Reflection]:
        query = (
            self._client.table("agentloops_reflections")
            .select("*")
            .eq("agent_name", self._agent_name)
            .order("created_at", desc=False)
        )
        if self._user_id:
            query = query.eq("user_id", self._user_id)
        if last_n:
            query = query.limit(last_n).order("created_at", desc=True)

        result = query.execute()
        rows = result.data or []
        if last_n:
            rows = list(reversed(rows))  # Restore chronological order
        return [Reflection.from_dict(r) for r in rows]

    # -- delete --------------------------------------------------------------

    def delete(self, collection: str, id: str) -> bool:
        table_map = {
            "runs": "agentloops_runs",
            "rules": "agentloops_rules",
            "conventions": "agentloops_conventions",
            "reflections": "agentloops_reflections",
        }
        table = table_map.get(collection)
        if not table:
            return False

        result = self._client.table(table).delete().eq("id", id).execute()
        return len(result.data or []) > 0
