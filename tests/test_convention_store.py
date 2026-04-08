"""Tests for the ConventionStore module."""

from __future__ import annotations

from unittest.mock import patch

from agentloops.convention_store import ConventionStore
from agentloops.models import Convention


class TestAddConvention:
    def test_add_convention_basic(self, storage):
        store = ConventionStore(storage, "test-agent")
        conv = store.add("Always greet the user by name")
        assert isinstance(conv, Convention)
        assert conv.text == "Always greet the user by name"
        assert conv.source == "manual"
        assert conv.status == "active"

    def test_add_convention_with_source(self, storage):
        store = ConventionStore(storage, "test-agent")
        conv = store.add("Use bullet points for lists", source="reflection-123")
        assert conv.source == "reflection-123"

    def test_add_multiple_conventions(self, storage):
        store = ConventionStore(storage, "test-agent")
        store.add("Convention 1")
        store.add("Convention 2")
        store.add("Convention 3")
        assert len(store.get_conventions()) == 3


class TestGetConventions:
    def test_get_conventions_returns_active_only(self, storage):
        store = ConventionStore(storage, "test-agent")
        c1 = store.add("Active convention")
        c2 = store.add("Will be pruned")

        # Manually mark c2 as pruned
        c2.status = "pruned"
        storage.save_convention(c2)

        convs = store.get_conventions()
        assert len(convs) == 1
        assert convs[0].text == "Active convention"

    def test_get_conventions_empty(self, storage):
        store = ConventionStore(storage, "test-agent")
        assert store.get_conventions() == []


class TestContradictionDetection:
    def test_detect_contradictions_with_llm_mock(self, storage):
        store = ConventionStore(storage, "test-agent")
        store.add("Always use formal language")
        store.add("Always use casual, friendly language")

        mock_response = {
            "contradictions": [
                {
                    "convention_ids": ["id1", "id2"],
                    "description": "Formal vs casual language conflict",
                    "suggested_resolution": "Use formal by default, casual for returning users",
                }
            ]
        }

        with patch.object(store, "_call_llm", return_value=mock_response):
            contradictions = store.detect_contradictions()

        assert len(contradictions) == 1
        assert "formal" in contradictions[0]["description"].lower() or "casual" in contradictions[0]["description"].lower()

    def test_detect_contradictions_needs_at_least_two(self, storage):
        store = ConventionStore(storage, "test-agent")
        store.add("Only one convention")
        assert store.detect_contradictions() == []

    def test_detect_contradictions_none_found(self, storage):
        store = ConventionStore(storage, "test-agent")
        store.add("Always be helpful")
        store.add("Always be accurate")

        mock_response = {"contradictions": []}
        with patch.object(store, "_call_llm", return_value=mock_response):
            contradictions = store.detect_contradictions()
        assert contradictions == []


class TestResolveContradiction:
    def test_resolve_marks_originals_contradicted(self, storage):
        store = ConventionStore(storage, "test-agent")
        c1 = store.add("Always use formal language")
        c2 = store.add("Always use casual language")

        resolved = store.resolve_contradiction(
            convention_ids=[c1.id, c2.id],
            resolution="Use formal language by default, casual for returning users",
        )

        assert resolved.status == "active"
        assert "resolved contradiction" in resolved.source

        # Original conventions should be marked contradicted
        all_convs = storage.get_conventions(active_only=False)
        for conv in all_convs:
            if conv.id == c1.id or conv.id == c2.id:
                assert conv.status == "contradicted"

    def test_resolve_creates_new_convention(self, storage):
        store = ConventionStore(storage, "test-agent")
        c1 = store.add("A")
        c2 = store.add("B")

        resolved = store.resolve_contradiction(
            convention_ids=[c1.id, c2.id],
            resolution="A and B combined",
        )

        active = store.get_conventions()
        # Only the resolved one should be active
        assert len(active) == 1
        assert active[0].id == resolved.id


class TestEvolve:
    def test_evolve_with_mocked_llm(self, storage, sample_rules):
        store = ConventionStore(storage, "test-agent")
        store.add("Existing convention")

        mock_response = {
            "new_conventions": [
                {"text": "New convention from rules", "source": "derived from rule analysis"}
            ],
            "contradictions": [],
            "to_remove": [],
            "to_merge": [],
        }

        with patch.object(store, "_call_llm", return_value=mock_response):
            changes = store.evolve()

        assert len(changes["new"]) == 1
        assert changes["new"][0]["text"] == "New convention from rules"

    def test_evolve_empty_system(self, storage):
        store = ConventionStore(storage, "test-agent")
        changes = store.evolve()
        assert changes == {"new": [], "removed": [], "merged": [], "contradictions": []}
