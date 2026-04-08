"""File-based JSON storage backend for AgentLoops.

Directory layout per agent:
    .agentloops/{agent_name}/
        runs.jsonl
        rules.json
        conventions.json
        reflections.json
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from agentloops.models import Convention, Reflection, Rule, Run
from agentloops.storage.base import BaseStorage


class FileStorage(BaseStorage):
    """JSON file storage — the default backend for local development."""

    def __init__(self, base_path: str | Path, agent_name: str) -> None:
        self._dir = Path(base_path) / agent_name
        self._dir.mkdir(parents=True, exist_ok=True)

    # -- paths ---------------------------------------------------------------

    @property
    def _runs_path(self) -> Path:
        return self._dir / "runs.jsonl"

    @property
    def _rules_path(self) -> Path:
        return self._dir / "rules.json"

    @property
    def _conventions_path(self) -> Path:
        return self._dir / "conventions.json"

    @property
    def _reflections_path(self) -> Path:
        return self._dir / "reflections.json"

    # -- helpers -------------------------------------------------------------

    def _read_json(self, path: Path) -> list[dict[str, Any]]:
        if not path.exists():
            return []
        text = path.read_text().strip()
        if not text:
            return []
        return json.loads(text)

    def _write_json(self, path: Path, data: list[dict[str, Any]]) -> None:
        path.write_text(json.dumps(data, indent=2) + "\n")

    def _append_jsonl(self, path: Path, record: dict[str, Any]) -> None:
        with open(path, "a") as f:
            f.write(json.dumps(record) + "\n")

    def _read_jsonl(self, path: Path) -> list[dict[str, Any]]:
        if not path.exists():
            return []
        records: list[dict[str, Any]] = []
        for line in path.read_text().strip().splitlines():
            line = line.strip()
            if line:
                records.append(json.loads(line))
        return records

    # -- runs ----------------------------------------------------------------

    def save_run(self, run: Run) -> None:
        self._append_jsonl(self._runs_path, run.to_dict())

    def get_runs(
        self,
        agent_name: str | None = None,
        last_n: int | None = None,
        outcome_filter: str | None = None,
    ) -> list[Run]:
        records = self._read_jsonl(self._runs_path)
        if agent_name:
            records = [r for r in records if r.get("agent_name") == agent_name]
        if outcome_filter:
            records = [r for r in records if r.get("outcome") == outcome_filter]
        if last_n:
            records = records[-last_n:]
        return [Run.from_dict(r) for r in records]

    # -- rules ---------------------------------------------------------------

    def save_rule(self, rule: Rule) -> None:
        rules = self._read_json(self._rules_path)
        # Update existing or append
        for i, r in enumerate(rules):
            if r["id"] == rule.id:
                rules[i] = rule.to_dict()
                self._write_json(self._rules_path, rules)
                return
        rules.append(rule.to_dict())
        self._write_json(self._rules_path, rules)

    def get_rules(self, active_only: bool = True) -> list[Rule]:
        rules = self._read_json(self._rules_path)
        if active_only:
            rules = [r for r in rules if r.get("active", True)]
        return [Rule.from_dict(r) for r in rules]

    # -- conventions ---------------------------------------------------------

    def save_convention(self, convention: Convention) -> None:
        conventions = self._read_json(self._conventions_path)
        for i, c in enumerate(conventions):
            if c["id"] == convention.id:
                conventions[i] = convention.to_dict()
                self._write_json(self._conventions_path, conventions)
                return
        conventions.append(convention.to_dict())
        self._write_json(self._conventions_path, conventions)

    def get_conventions(self, active_only: bool = True) -> list[Convention]:
        conventions = self._read_json(self._conventions_path)
        if active_only:
            conventions = [c for c in conventions if c.get("status") == "active"]
        return [Convention.from_dict(c) for c in conventions]

    # -- reflections ---------------------------------------------------------

    def save_reflection(self, reflection: Reflection) -> None:
        reflections = self._read_json(self._reflections_path)
        reflections.append(reflection.to_dict())
        self._write_json(self._reflections_path, reflections)

    def get_reflections(self, last_n: int | None = None) -> list[Reflection]:
        reflections = self._read_json(self._reflections_path)
        if last_n:
            reflections = reflections[-last_n:]
        return [Reflection.from_dict(r) for r in reflections]

    # -- delete --------------------------------------------------------------

    def delete(self, collection: str, id: str) -> bool:
        path_map = {
            "runs": self._runs_path,
            "rules": self._rules_path,
            "conventions": self._conventions_path,
            "reflections": self._reflections_path,
        }
        path = path_map.get(collection)
        if not path:
            return False

        if collection == "runs":
            records = self._read_jsonl(path)
            filtered = [r for r in records if r.get("id") != id]
            if len(filtered) == len(records):
                return False
            path.write_text("".join(json.dumps(r) + "\n" for r in filtered))
            return True
        else:
            records = self._read_json(path)
            filtered = [r for r in records if r.get("id") != id]
            if len(filtered) == len(records):
                return False
            self._write_json(path, filtered)
            return True
