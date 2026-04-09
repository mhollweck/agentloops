"""Tests for Supabase storage backend (mocked — no real Supabase needed)."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from agentloops.models import Convention, Reflection, Rule, Run
from agentloops.storage.base import BaseStorage


class MockSupabaseResponse:
    """Mock Supabase API response."""

    def __init__(self, data=None, count=None):
        self.data = data or []
        self.count = count


class MockQuery:
    """Mock Supabase query builder with chaining."""

    def __init__(self, data=None):
        self._data = data or []

    def select(self, *args, **kwargs):
        return self

    def eq(self, *args):
        return self

    def order(self, *args, **kwargs):
        return self

    def limit(self, *args):
        return self

    def range(self, *args):
        return self

    def upsert(self, data, **kwargs):
        self._data.append(data)
        return self

    def delete(self):
        return self

    def execute(self):
        return MockSupabaseResponse(data=self._data)


class MockSupabaseClient:
    """Mock Supabase client."""

    def __init__(self):
        self._tables: dict[str, MockQuery] = {}

    def table(self, name: str):
        if name not in self._tables:
            self._tables[name] = MockQuery()
        return self._tables[name]


def _make_storage(user_id=None):
    """Create a SupabaseStorage with mock client injected."""
    from agentloops.storage.supabase import SupabaseStorage

    # Bypass __init__'s import of supabase package by constructing manually
    storage = object.__new__(SupabaseStorage)
    storage._client = MockSupabaseClient()
    storage._agent_name = "test-agent"
    storage._user_id = user_id
    return storage


class TestSupabaseStorageInit:
    """Test Supabase storage initialization."""

    def test_missing_url_raises(self):
        from agentloops.core import AgentLoops
        with pytest.raises(ValueError, match="supabase_url"):
            AgentLoops("test", storage="supabase")

    def test_missing_key_raises(self):
        from agentloops.core import AgentLoops
        with pytest.raises(ValueError, match="supabase_url"):
            AgentLoops("test", storage="supabase", supabase_url="https://x.supabase.co")


class TestSupabaseStorageCRUD:
    """Test CRUD operations with mocked Supabase client."""

    @pytest.fixture
    def storage(self):
        return _make_storage(user_id="user-123")

    def test_save_run(self, storage):
        run = Run(input="test", output="result", outcome="success", agent_name="test-agent")
        storage.save_run(run)

    def test_save_rule(self, storage):
        rule = Rule(text="IF X THEN Y", confidence=0.8)
        storage.save_rule(rule)

    def test_save_convention(self, storage):
        conv = Convention(text="Be concise", source="manual")
        storage.save_convention(conv)

    def test_save_reflection(self, storage):
        ref = Reflection(
            agent_name="test-agent",
            critique="Looks good",
            suggested_rules=["IF A THEN B"],
            confidence_scores={"IF A THEN B": 0.8},
        )
        storage.save_reflection(ref)

    def test_row_base_includes_user_id(self, storage):
        base = storage._row_base()
        assert base["agent_name"] == "test-agent"
        assert base["user_id"] == "user-123"

    def test_row_base_without_user_id(self):
        storage = _make_storage(user_id=None)
        base = storage._row_base()
        assert base["agent_name"] == "test-agent"
        assert "user_id" not in base

    def test_get_runs_returns_list(self, storage):
        runs = storage.get_runs()
        assert isinstance(runs, list)

    def test_get_rules_returns_list(self, storage):
        rules = storage.get_rules()
        assert isinstance(rules, list)

    def test_get_conventions_returns_list(self, storage):
        convs = storage.get_conventions()
        assert isinstance(convs, list)

    def test_get_reflections_returns_list(self, storage):
        refs = storage.get_reflections()
        assert isinstance(refs, list)

    def test_delete_unknown_collection_returns_false(self, storage):
        assert storage.delete("unknown", "some-id") is False


class TestSupabaseIntegration:
    """Test Supabase storage through AgentLoops constructor."""

    def test_env_var_fallback(self):
        """Should read URL/key from env vars if not passed directly."""
        # Mock the entire supabase import inside SupabaseStorage.__init__
        mock_module = MagicMock()
        mock_module.create_client.return_value = MockSupabaseClient()

        with patch.dict("sys.modules", {"supabase": mock_module}):
            with patch.dict("os.environ", {
                "AGENTLOOPS_SUPABASE_URL": "https://env.supabase.co",
                "AGENTLOOPS_SUPABASE_KEY": "env-key",
            }):
                from agentloops.core import AgentLoops
                loops = AgentLoops("test-agent", storage="supabase")
                assert loops.agent_name == "test-agent"

    def test_supabase_string_accepted(self):
        """storage='supabase' should be accepted with valid config."""
        mock_module = MagicMock()
        mock_module.create_client.return_value = MockSupabaseClient()

        with patch.dict("sys.modules", {"supabase": mock_module}):
            from agentloops.core import AgentLoops
            loops = AgentLoops(
                "test-agent",
                storage="supabase",
                supabase_url="https://test.supabase.co",
                supabase_key="test-key",
            )
            assert loops.agent_name == "test-agent"
