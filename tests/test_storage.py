"""Tests for FileStorage backend."""

from __future__ import annotations

from agentloops.models import Convention, Reflection, Rule, Run
from agentloops.storage.file import FileStorage


class TestRunStorage:
    def test_save_and_get_run(self, storage):
        run = Run(
            input="hello",
            output="world",
            outcome="success",
            agent_name="test-agent",
        )
        storage.save_run(run)

        runs = storage.get_runs(agent_name="test-agent")
        assert len(runs) == 1
        assert runs[0].id == run.id
        assert runs[0].input == "hello"

    def test_multiple_runs(self, storage):
        for i in range(5):
            storage.save_run(Run(
                input=f"in-{i}",
                output=f"out-{i}",
                outcome="success",
                agent_name="test-agent",
            ))
        assert len(storage.get_runs(agent_name="test-agent")) == 5

    def test_get_runs_last_n(self, storage):
        for i in range(10):
            storage.save_run(Run(
                input=f"in-{i}",
                output=f"out-{i}",
                outcome="success",
                agent_name="test-agent",
            ))
        runs = storage.get_runs(agent_name="test-agent", last_n=3)
        assert len(runs) == 3

    def test_get_runs_outcome_filter(self, storage):
        storage.save_run(Run(input="a", output="b", outcome="success", agent_name="test-agent"))
        storage.save_run(Run(input="c", output="d", outcome="failure", agent_name="test-agent"))
        storage.save_run(Run(input="e", output="f", outcome="success", agent_name="test-agent"))

        successes = storage.get_runs(outcome_filter="success")
        assert len(successes) == 2

    def test_delete_run(self, storage):
        run = Run(input="a", output="b", outcome="success", agent_name="test-agent")
        storage.save_run(run)
        assert storage.delete("runs", run.id) is True
        assert len(storage.get_runs()) == 0

    def test_delete_nonexistent_run(self, storage):
        assert storage.delete("runs", "nonexistent") is False


class TestRuleStorage:
    def test_save_and_get_rule(self, storage):
        rule = Rule(text="IF X THEN Y", confidence=0.8)
        storage.save_rule(rule)

        rules = storage.get_rules()
        assert len(rules) == 1
        assert rules[0].text == "IF X THEN Y"

    def test_update_existing_rule(self, storage):
        rule = Rule(text="IF X THEN Y", confidence=0.5)
        storage.save_rule(rule)

        rule.confidence = 0.9
        storage.save_rule(rule)

        rules = storage.get_rules()
        assert len(rules) == 1
        assert rules[0].confidence == 0.9

    def test_active_only_filter(self, storage):
        r1 = Rule(text="Active rule", confidence=0.8)
        r2 = Rule(text="Inactive rule", confidence=0.5, active=False)
        storage.save_rule(r1)
        storage.save_rule(r2)

        active = storage.get_rules(active_only=True)
        all_rules = storage.get_rules(active_only=False)
        assert len(active) == 1
        assert len(all_rules) == 2

    def test_delete_rule(self, storage):
        rule = Rule(text="To delete", confidence=0.5)
        storage.save_rule(rule)
        assert storage.delete("rules", rule.id) is True
        assert len(storage.get_rules(active_only=False)) == 0


class TestConventionStorage:
    def test_save_and_get_convention(self, storage):
        conv = Convention(text="Be helpful", source="manual")
        storage.save_convention(conv)

        convs = storage.get_conventions()
        assert len(convs) == 1
        assert convs[0].text == "Be helpful"

    def test_update_existing_convention(self, storage):
        conv = Convention(text="Original", source="manual")
        storage.save_convention(conv)

        conv.text = "Updated"
        storage.save_convention(conv)

        convs = storage.get_conventions()
        assert len(convs) == 1
        assert convs[0].text == "Updated"

    def test_active_only_filter(self, storage):
        c1 = Convention(text="Active", source="manual")
        c2 = Convention(text="Pruned", source="manual", status="pruned")
        storage.save_convention(c1)
        storage.save_convention(c2)

        active = storage.get_conventions(active_only=True)
        all_convs = storage.get_conventions(active_only=False)
        assert len(active) == 1
        assert len(all_convs) == 2


class TestPersistenceAcrossInstances:
    def test_runs_persist(self, tmp_path):
        s1 = FileStorage(tmp_path / ".agentloops", "test-agent")
        s1.save_run(Run(input="a", output="b", outcome="success", agent_name="test-agent"))

        s2 = FileStorage(tmp_path / ".agentloops", "test-agent")
        runs = s2.get_runs()
        assert len(runs) == 1
        assert runs[0].input == "a"

    def test_rules_persist(self, tmp_path):
        s1 = FileStorage(tmp_path / ".agentloops", "test-agent")
        s1.save_rule(Rule(text="IF X THEN Y", confidence=0.8))

        s2 = FileStorage(tmp_path / ".agentloops", "test-agent")
        rules = s2.get_rules()
        assert len(rules) == 1

    def test_conventions_persist(self, tmp_path):
        s1 = FileStorage(tmp_path / ".agentloops", "test-agent")
        s1.save_convention(Convention(text="Be helpful", source="manual"))

        s2 = FileStorage(tmp_path / ".agentloops", "test-agent")
        convs = s2.get_conventions()
        assert len(convs) == 1


class TestReflectionStorage:
    def test_save_and_get_reflection(self, storage):
        ref = Reflection(
            agent_name="test-agent",
            critique="Good work overall",
            suggested_rules=["IF X THEN Y"],
            confidence_scores={"rule1": 0.8},
            run_ids=["run-1", "run-2"],
        )
        storage.save_reflection(ref)

        refs = storage.get_reflections()
        assert len(refs) == 1
        assert refs[0].critique == "Good work overall"

    def test_get_reflections_last_n(self, storage):
        for i in range(5):
            storage.save_reflection(Reflection(
                agent_name="test-agent",
                critique=f"Reflection {i}",
                suggested_rules=[],
                confidence_scores={},
            ))
        refs = storage.get_reflections(last_n=2)
        assert len(refs) == 2


class TestCleanup:
    def test_delete_unknown_collection(self, storage):
        assert storage.delete("unknown", "some-id") is False

    def test_delete_from_empty_collection(self, storage):
        assert storage.delete("rules", "nonexistent") is False
        assert storage.delete("conventions", "nonexistent") is False
        assert storage.delete("runs", "nonexistent") is False
