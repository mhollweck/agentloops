# API Reference

Complete documentation for every public class and method in AgentLoops.

---

## AgentLoops

The main orchestrator. This is the single entry point for adding self-learning to any agent.

```python
from agentloops import AgentLoops
```

### Constructor

```python
AgentLoops(
    agent_name: str,
    storage: str | BaseStorage = "file",
    storage_path: str | Path | None = None,
    reflection_model: str = "claude-sonnet-4-6",
    api_key: str | None = None,
)
```

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `agent_name` | `str` | required | Unique name for this agent. Used as the storage namespace. |
| `storage` | `str \| BaseStorage` | `"file"` | Storage backend. `"file"` for JSON file storage, or pass a `BaseStorage` instance. |
| `storage_path` | `str \| Path \| None` | `".agentloops"` | Directory for file storage. |
| `reflection_model` | `str` | `"claude-sonnet-4-6"` | Anthropic model for reflection and rule generation. |
| `api_key` | `str \| None` | `None` | Anthropic API key. Falls back to `ANTHROPIC_API_KEY` env var. |

### Methods

#### `track()`

Log an agent run with its outcome.

```python
track(
    input: str,
    output: str,
    outcome: str,
    metadata: dict[str, Any] | None = None,
) -> Run
```

| Parameter | Type | Description |
|-----------|------|-------------|
| `input` | `str` | The prompt or input given to the agent. |
| `output` | `str` | The agent's response or output. |
| `outcome` | `str` | Result: `"success"`, `"failure"`, or a numeric score as string (e.g., `"0.85"`). |
| `metadata` | `dict[str, Any] \| None` | Optional key-value pairs (latency, tokens, model, etc.). |

**Returns:** `Run` -- the persisted run object with a generated ID and timestamp.

**Notes:** Automatically records which rules were active at the time of the run.

---

#### `reflect()`

Trigger an LLM-powered reflection on recent runs.

```python
reflect(last_n: int = 5) -> Reflection
```

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `last_n` | `int` | `5` | Number of recent runs to analyze. |

**Returns:** `Reflection` -- structured critique with suggested rules and confidence scores.

**Raises:** `ValueError` if there are no runs to reflect on.

---

#### `enhance_prompt()`

Inject active rules and conventions into a base prompt.

```python
enhance_prompt(base_prompt: str) -> str
```

| Parameter | Type | Description |
|-----------|------|-------------|
| `base_prompt` | `str` | The agent's base system prompt. |

**Returns:** `str` -- the enhanced prompt with rules and conventions appended. Returns the base prompt unchanged if there are no active rules or conventions.

**Output format:**
```
{base_prompt}

## Decision Rules (learned from past performance)
- IF condition THEN action [confidence: 0.90]

## Conventions (self-learned behavioral patterns)
- Convention text here
```

---

#### `forget()`

Prune stale entries from memory.

```python
forget(
    strategy: str = "decay",
    max_age_days: int = 21,
) -> dict[str, list[str]]
```

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `strategy` | `str` | `"decay"` | `"decay"` (age-based), `"importance"` (confidence-weighted), or `"hybrid"` (both). |
| `max_age_days` | `int` | `21` | Maximum age in days before pruning eligibility. |

**Returns:** `dict` with keys `"rules_pruned"` and `"conventions_pruned"`, each containing lists of pruned IDs.

---

### Properties

| Property | Type | Description |
|----------|------|-------------|
| `rules` | `RuleEngine` | Direct access to the rule engine. |
| `conventions` | `ConventionStore` | Direct access to the convention store. |
| `tracker` | `Tracker` | Direct access to the tracker. |
| `agent_name` | `str` | The name of the agent this instance manages. |

---

## Reflector

Evaluates agent runs and produces structured critiques using an LLM.

```python
from agentloops import Reflector
```

### Constructor

```python
Reflector(
    storage: BaseStorage,
    agent_name: str,
    model: str = "claude-sonnet-4-6",
    api_key: str | None = None,
)
```

### Methods

#### `reflect()`

```python
reflect(last_n: int = 5) -> Reflection
```

Analyzes the last N runs and produces a structured critique. Sends a prompt to the LLM that includes recent runs, active rules, and active conventions. The LLM returns a JSON response that is parsed into a `Reflection` object.

**Raises:** `ValueError` if no runs are found for the agent.

---

## RuleEngine

Discovers and manages IF/THEN decision rules from performance data.

```python
from agentloops import RuleEngine
```

### Constructor

```python
RuleEngine(
    storage: BaseStorage,
    agent_name: str,
    model: str = "claude-sonnet-4-6",
    api_key: str | None = None,
)
```

### Methods

#### `generate_rules()`

Analyze runs to discover patterns and generate new rules.

```python
generate_rules(runs: list[Run] | None = None) -> list[Rule]
```

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `runs` | `list[Run] \| None` | `None` | Runs to analyze. Uses the last 20 runs if not provided. |

**Returns:** `list[Rule]` -- newly generated rules (already persisted). Only rules with confidence >= 0.5 are generated.

---

#### `active()`

Return currently active rules sorted by confidence (highest first).

```python
active() -> list[Rule]
```

**Returns:** `list[Rule]` -- active rules sorted by confidence descending.

---

#### `add_rule()`

Manually add a rule.

```python
add_rule(
    text: str,
    evidence: list[str] | None = None,
    confidence: float = 0.7,
) -> Rule
```

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `text` | `str` | required | The IF/THEN rule text. |
| `evidence` | `list[str] \| None` | `None` | Supporting evidence strings. |
| `confidence` | `float` | `0.7` | Confidence score (0.0-1.0). |

**Returns:** `Rule` -- the created and persisted rule.

---

#### `deactivate_rule()`

Soft-delete a rule by setting it inactive.

```python
deactivate_rule(rule_id: str) -> bool
```

**Returns:** `True` if the rule was found and deactivated, `False` otherwise.

---

## ConventionStore

Manages evolving behavioral conventions with contradiction detection.

```python
from agentloops import ConventionStore
```

### Constructor

```python
ConventionStore(
    storage: BaseStorage,
    agent_name: str,
    model: str = "claude-sonnet-4-6",
    api_key: str | None = None,
)
```

### Methods

#### `evolve()`

Trigger convention evolution: compare rules, detect contradictions, merge, and update.

```python
evolve() -> dict[str, Any]
```

**Returns:** Dict with keys:
- `"new"` -- list of newly created convention dicts
- `"removed"` -- list of removed convention IDs
- `"merged"` -- list of merged convention dicts
- `"contradictions"` -- list of contradiction dicts with `convention_ids`, `description`, and `suggested_resolution`

---

#### `get_conventions()`

Return all active conventions.

```python
get_conventions() -> list[Convention]
```

---

#### `add()`

Manually add a convention.

```python
add(text: str, source: str = "manual") -> Convention
```

---

#### `detect_contradictions()`

Find conflicting conventions using LLM analysis.

```python
detect_contradictions() -> list[dict[str, Any]]
```

**Returns:** List of dicts, each with:
- `convention_ids` -- IDs of the conflicting conventions
- `description` -- what the contradiction is
- `suggested_resolution` -- which to keep and why

Returns an empty list if fewer than 2 conventions exist.

---

#### `resolve_contradiction()`

Resolve a conflict between conventions.

```python
resolve_contradiction(
    convention_ids: list[str],
    resolution: str,
) -> Convention
```

Marks conflicting conventions as `"contradicted"` and creates a new convention with the resolution text.

**Returns:** The new `Convention` representing the resolution.

---

## Forgetter

Time-decay and importance-weighted memory pruning.

```python
from agentloops import Forgetter
```

### Constructor

```python
Forgetter(storage: BaseStorage)
```

### Methods

#### `prune()`

Remove stale entries based on the chosen strategy.

```python
prune(
    strategy: str = "hybrid",
    max_age_days: int = 21,
    min_confidence: float = 0.3,
) -> dict[str, list[str]]
```

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `strategy` | `str` | `"hybrid"` | `"decay"`, `"importance"`, or `"hybrid"`. |
| `max_age_days` | `int` | `21` | Maximum age before pruning eligibility. |
| `min_confidence` | `float` | `0.3` | Minimum confidence to keep (importance/hybrid strategies). |

**Returns:** Dict with `"rules_pruned"` and `"conventions_pruned"` lists of IDs.

**Protection rules:**
- Rules with confidence >= 0.8 are never pruned
- Rules validated within `max_age_days` are never pruned
- Conventions updated within `max_age_days` are never pruned

---

## Tracker

Tracks agent runs and correlates performance with applied rules.

```python
from agentloops import Tracker
```

### Constructor

```python
Tracker(storage: BaseStorage, agent_name: str)
```

### Methods

#### `log_run()`

Log a completed agent run.

```python
log_run(
    input: str,
    output: str,
    outcome: str,
    metadata: dict[str, Any] | None = None,
    rules_applied: list[str] | None = None,
) -> Run
```

---

#### `get_runs()`

Retrieve runs with optional filters.

```python
get_runs(
    last_n: int | None = None,
    agent_name: str | None = None,
    outcome_filter: str | None = None,
) -> list[Run]
```

---

#### `correlate()`

Show performance before and after a rule was applied.

```python
correlate(rule_id: str) -> dict[str, Any]
```

**Returns:** Dict with:
- `"rule_id"` -- the rule ID
- `"with_rule"` -- `{"count": int, "success_rate": float, "avg_score"?: float}`
- `"without_rule"` -- same structure

---

#### `improvement_curve()`

Calculate improvement over time using a sliding window.

```python
improvement_curve(
    metric: str = "success_rate",
    window_days: int = 7,
) -> list[dict[str, Any]]
```

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `metric` | `str` | `"success_rate"` | `"success_rate"` or `"avg_score"`. |
| `window_days` | `int` | `7` | Size of the sliding window in days. |

**Returns:** List of dicts with `"window_start"`, `"window_end"`, the metric value, and `"run_count"`.

---

## Storage Backends

### BaseStorage (Abstract)

The interface all storage backends must implement.

```python
from agentloops.storage import BaseStorage
```

| Method | Signature |
|--------|-----------|
| `save_run` | `(run: Run) -> None` |
| `get_runs` | `(agent_name: str \| None, last_n: int \| None, outcome_filter: str \| None) -> list[Run]` |
| `save_rule` | `(rule: Rule) -> None` |
| `get_rules` | `(active_only: bool = True) -> list[Rule]` |
| `save_convention` | `(convention: Convention) -> None` |
| `get_conventions` | `(active_only: bool = True) -> list[Convention]` |
| `save_reflection` | `(reflection: Reflection) -> None` |
| `get_reflections` | `(last_n: int \| None = None) -> list[Reflection]` |
| `delete` | `(collection: str, id: str) -> bool` |

### FileStorage

JSON file storage -- the default backend.

```python
from agentloops.storage import FileStorage
```

```python
FileStorage(base_path: str | Path, agent_name: str)
```

Creates this directory structure:
```
{base_path}/{agent_name}/
    runs.jsonl       # Append-only run log
    rules.json       # Active and inactive rules
    conventions.json # Convention lifecycle
    reflections.json # Reflection history
```

### Custom Storage Backend

Implement `BaseStorage` to use any datastore:

```python
from agentloops.storage import BaseStorage
from agentloops.models import Run, Rule, Convention, Reflection

class PostgresStorage(BaseStorage):
    def __init__(self, connection_string: str):
        self._conn = connect(connection_string)
    
    def save_run(self, run: Run) -> None:
        self._conn.execute("INSERT INTO runs ...", run.to_dict())
    
    # ... implement all abstract methods
```

Then pass it to AgentLoops:

```python
storage = PostgresStorage("postgresql://...")
loops = AgentLoops("my-agent", storage=storage)
```

---

## Data Models

### Run

A single agent run with its input, output, and outcome.

```python
from agentloops import Run
```

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `input` | `str` | required | The prompt or input given to the agent. |
| `output` | `str` | required | The agent's response. |
| `outcome` | `str` | required | `"success"`, `"failure"`, or a numeric score. |
| `agent_name` | `str` | required | Which agent produced this run. |
| `id` | `str` | auto-generated | 12-character hex UUID. |
| `metadata` | `dict[str, Any]` | `{}` | Arbitrary key-value pairs. |
| `rules_applied` | `list[str]` | `[]` | IDs of rules active during this run. |
| `created_at` | `str` | auto-generated | ISO 8601 timestamp. |

Methods: `to_dict() -> dict`, `from_dict(d: dict) -> Run`

### Rule

An IF/THEN decision rule derived from performance data.

```python
from agentloops import Rule
```

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `text` | `str` | required | The IF/THEN rule text. |
| `confidence` | `float` | required | 0.0 to 1.0. |
| `evidence_count` | `int` | `1` | Number of supporting data points. |
| `id` | `str` | auto-generated | 12-character hex UUID. |
| `evidence` | `list[str]` | `[]` | Supporting evidence strings. |
| `created_at` | `str` | auto-generated | ISO 8601 timestamp. |
| `last_validated` | `str` | auto-generated | Last time this rule was confirmed. |
| `active` | `bool` | `True` | Whether the rule is currently applied. |

Methods: `to_dict() -> dict`, `from_dict(d: dict) -> Rule`

### Convention

A behavioral pattern that evolves over time.

```python
from agentloops import Convention
```

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `text` | `str` | required | The convention text. |
| `source` | `str` | required | What produced this convention. |
| `id` | `str` | auto-generated | 12-character hex UUID. |
| `created_at` | `str` | auto-generated | ISO 8601 timestamp. |
| `updated_at` | `str` | auto-generated | Last modification time. |
| `status` | `str` | `"active"` | `"active"`, `"superseded"`, `"contradicted"`, or `"pruned"`. |

Methods: `to_dict() -> dict`, `from_dict(d: dict) -> Convention`

### Reflection

Structured output from a reflection pass.

```python
from agentloops import Reflection
```

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `agent_name` | `str` | required | Which agent was reflected on. |
| `critique` | `str` | required | 2-3 paragraph analysis. |
| `suggested_rules` | `list[str]` | required | Suggested IF/THEN rules. |
| `confidence_scores` | `dict[str, float]` | required | Confidence per suggested rule. |
| `id` | `str` | auto-generated | 12-character hex UUID. |
| `run_ids` | `list[str]` | `[]` | IDs of runs that were analyzed. |
| `created_at` | `str` | auto-generated | ISO 8601 timestamp. |

Methods: `to_dict() -> dict`, `from_dict(d: dict) -> Reflection`
