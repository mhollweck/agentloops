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
    agent_type: str | None = None,
    api_key: str | None = None,
    llm_provider: str = "anthropic",
    llm_fn: Callable[[str], str] | None = None,
    storage: str | BaseStorage = "file",
    storage_path: str | Path | None = None,
    reflection_model: str = "claude-sonnet-4-6",
    auto_learn: bool = True,
    reflection_threshold: int = 10,
    evolution_interval: int = 50,
    outcome: OutcomeConfig | None = None,
    supabase_url: str | None = None,
    supabase_key: str | None = None,
    user_id: str | None = None,
)
```

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `agent_name` | `str` | required | Unique name for this agent. Used as the storage namespace. |
| `agent_type` | `str \| None` | `None` | Agent type for pre-seeded rules and cross-customer intelligence. Examples: `"sales-sdr"`, `"support-agent"`, `"content-writer"`. When set, the agent starts with domain-specific rules instead of learning from scratch. See [Seed Rules](#seed-rules) for all available types. |
| `api_key` | `str \| None` | `None` | LLM provider API key. For Anthropic: your `ANTHROPIC_API_KEY` (sk-ant-...). For OpenAI: your `OPENAI_API_KEY` (sk-...). Falls back to the corresponding environment variable (`ANTHROPIC_API_KEY` or `OPENAI_API_KEY`) when not provided. Not needed when using `llm_provider="custom"` with `llm_fn`. |
| `llm_provider` | `str` | `"anthropic"` | Which LLM provider to use for reflection and rule generation. `"anthropic"` (default), `"openai"`, or `"custom"` (requires `llm_fn`). |
| `llm_fn` | `Callable[[str], str] \| None` | `None` | Custom LLM callable for `llm_provider="custom"`. Takes a prompt string and returns a response string. Use this for local models (Ollama), Groq, Mistral, or any other provider. |
| `storage` | `str \| BaseStorage` | `"file"` | Storage backend. `"file"` for JSON file storage, `"supabase"` for Supabase cloud storage, or pass a `BaseStorage` instance. |
| `storage_path` | `str \| Path \| None` | `".agentloops"` | Directory for file storage. |
| `reflection_model` | `str` | `"claude-sonnet-4-6"` | Anthropic model for reflection and rule generation. |
| `auto_learn` | `bool` | `True` | When `True` and `api_key` is set, automatically triggers `reflect()`, `evolve()`, and `forget()` based on the configured thresholds. When `False` or no `api_key`, you must call these methods manually. |
| `reflection_threshold` | `int` | `10` | Number of tracked runs before auto-reflection triggers. Only applies when `auto_learn=True`. After each reflection, the counter resets. Lower values mean faster learning but more LLM calls. |
| `evolution_interval` | `int` | `50` | Number of tracked runs between automatic convention evolution cycles. Only applies when `auto_learn=True`. Evolution promotes high-confidence rules to conventions, resolves contradictions, and merges overlapping patterns. |
| `outcome` | `OutcomeConfig \| None` | `None` | Outcome configuration defining what "good" means for this agent. Supports binary, categorical, numeric, duration, and multi-metric outcomes. When `None`, defaults to binary (success/failure). |
| `supabase_url` | `str \| None` | `None` | Supabase project URL. Required when `storage="supabase"`. Falls back to `AGENTLOOPS_SUPABASE_URL` env var. |
| `supabase_key` | `str \| None` | `None` | Supabase API key. Required when `storage="supabase"`. Falls back to `AGENTLOOPS_SUPABASE_KEY` env var. |
| `user_id` | `str \| None` | `None` | User ID for multi-tenant Supabase storage. Enables Row Level Security (RLS) so each user's data is isolated. |

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

#### `check()`

Pre-flight validation of agent output against learned rules and built-in checks.

```python
check(
    output: str,
    input: str | None = None,
    custom_checks: list[Callable] | None = None,
    pass_threshold: float = 0.7,
) -> GateResult
```

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `output` | `str` | required | The agent output to validate. |
| `input` | `str \| None` | `None` | The original input (used for context in rule-based checks). |
| `custom_checks` | `list[Callable] \| None` | `None` | Custom check functions. Each takes `(output, input)` and returns a dict with `passed`, `name`, and optional `message`. |
| `pass_threshold` | `float` | `0.7` | Minimum score to pass. Score is computed as the ratio of passed checks to total checks. |

**Returns:** `GateResult` -- result object with `passed`, `score`, `failures`, and `warnings`.

---

### Properties

| Property | Type | Description |
|----------|------|-------------|
| `rules` | `RuleEngine` | Direct access to the rule engine. |
| `conventions` | `ConventionStore` | Direct access to the convention store. |
| `tracker` | `Tracker` | Direct access to the tracker. |
| `quality_gate` | `QualityGate` | Direct access to the quality gate instance. |
| `meta_learner` | `MetaLearner` | Direct access to the meta-learner for learning quality insights. |
| `outcome` | `OutcomeConfig` | The outcome configuration for this agent. |
| `agent_name` | `str` | The name of the agent this instance manages. |

---

## MetaLearner

Tracks the quality of the learning process itself and generates meta-rules to improve future reflections.

```python
from agentloops import MetaLearner
```

### Constructor

```python
MetaLearner(
    storage: BaseStorage,
    agent_name: str,
)
```

### Methods

#### `get_rule_impacts()`

Get impact data for rules, showing outcomes before vs after each rule was applied.

```python
get_rule_impacts() -> list[RuleImpact]
```

**Returns:** `list[RuleImpact]` -- impact records for rules that have enough data.

---

#### `get_best_rule_patterns()`

Analyze which rule characteristics correlate with positive outcomes.

```python
get_best_rule_patterns() -> dict[str, Any]
```

**Returns:** Dict with pattern analysis, including:
- `"evidence_vs_no_evidence"` -- impact comparison of rules with vs without evidence
- `"avoid_vs_do"` -- impact comparison of "avoid" rules vs "do" rules
- `"confidence_correlation"` -- how confidence level correlates with actual impact

---

#### `get_meta_rules()`

Get generated meta-rules that guide future reflections.

```python
get_meta_rules() -> list[str]
```

**Returns:** `list[str]` -- meta-guidance strings injected into reflection prompts (e.g., "Rules with specific evidence outperform abstract rules by 2x -- always cite run IDs").

---

#### `track_reflection_quality()`

Score a reflection's quality based on adoption rate and downstream impact of its suggested rules.

```python
track_reflection_quality(reflection_id: str) -> ReflectionQuality
```

| Parameter | Type | Description |
|-----------|------|-------------|
| `reflection_id` | `str` | ID of the reflection to evaluate. |

**Returns:** `ReflectionQuality` -- quality score with adoption and impact breakdown.

---

## RuleImpact

Impact data for a single rule, comparing outcomes before and after application.

```python
from agentloops import RuleImpact
```

| Field | Type | Description |
|-------|------|-------------|
| `rule_id` | `str` | The rule being measured. |
| `rule_text` | `str` | The IF/THEN rule text. |
| `outcomes_before` | `dict[str, float]` | Success rate and run count before the rule was active. |
| `outcomes_after` | `dict[str, float]` | Success rate and run count after the rule was active. |
| `impact_score` | `float` | Net change in success rate (-1.0 to 1.0). |

Methods: `to_dict() -> dict`, `from_dict(d: dict) -> RuleImpact`

---

## ReflectionQuality

Quality score for a reflection pass, based on how its suggested rules performed.

```python
from agentloops import ReflectionQuality
```

| Field | Type | Description |
|-------|------|-------------|
| `reflection_id` | `str` | The reflection being evaluated. |
| `adoption_rate` | `float` | Fraction of suggested rules that were actually generated and activated (0.0-1.0). |
| `avg_impact` | `float` | Average impact score of adopted rules. |
| `quality_score` | `float` | Composite score combining adoption rate and impact. |

Methods: `to_dict() -> dict`, `from_dict(d: dict) -> ReflectionQuality`

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

---

## OutcomeConfig

Defines what "good" means for an agent. Used by the reflection and rule engines to optimize for the right goals.

```python
from agentloops import OutcomeConfig
```

### Factory Methods

```python
# Binary — success or failure
OutcomeConfig.binary()

# Categorical — multiple possible outcome values
OutcomeConfig.categorical(["booked", "replied", "ignored"])

# Numeric — scored outcomes with a goal direction
OutcomeConfig.numeric(goal="minimize")  # or goal="maximize"
```

### Constructor (Multi-Metric)

```python
OutcomeConfig(
    metrics: list[MetricDef],
)
```

| Parameter | Type | Description |
|-----------|------|-------------|
| `metrics` | `list[MetricDef]` | List of metric definitions with weights. |

### Methods

| Method | Signature | Description |
|--------|-----------|-------------|
| `score` | `(values: dict[str, Any]) -> float` | Compute a weighted composite score from metric values. |
| `describe` | `() -> str` | Generate a human-readable description of what "good" means. |

---

## MetricDef

Defines an individual metric within a multi-metric outcome configuration.

```python
from agentloops import MetricDef
```

```python
MetricDef(
    name: str,
    type: str,
    weight: float = 1.0,
    success_values: list[str] | None = None,
    target_value: float | None = None,
    goal: str | None = None,
)
```

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `name` | `str` | required | Metric name (e.g., `"booking_rate"`, `"latency"`). |
| `type` | `str` | required | One of `"binary"`, `"categorical"`, `"numeric"`, `"duration"`. |
| `weight` | `float` | `1.0` | Weight in composite scoring. Higher = more important. |
| `success_values` | `list[str] \| None` | `None` | For categorical metrics: which values count as success. |
| `target_value` | `float \| None` | `None` | For numeric/duration metrics: the target to optimize toward. |
| `goal` | `str \| None` | `None` | For numeric metrics: `"minimize"` or `"maximize"`. |

---

## QualityGate

Pre-flight validation engine. Runs built-in checks, rule-based checks, and custom checks against agent output.

```python
from agentloops.quality_gate import QualityGate
```

### Constructor

```python
QualityGate(
    rules: RuleEngine,
    pass_threshold: float = 0.7,
)
```

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `rules` | `RuleEngine` | required | Rule engine for rule-based validation. |
| `pass_threshold` | `float` | `0.7` | Minimum score to pass validation. |

### Methods

#### `check()`

```python
check(
    output: str,
    input: str | None = None,
    custom_checks: list[Callable] | None = None,
) -> GateResult
```

Runs all checks and returns a `GateResult`.

**Built-in checks:**
- Empty output detection
- Minimum/maximum length validation
- Hallucination marker detection (e.g., "I don't have access to", "As an AI")

**Rule-based checks:**
- Validates output against learned "avoid" rules from the rule engine

**Custom checks:**
- Each function takes `(output, input)` and returns `{"passed": bool, "name": str, "message": str}`

---

## GateResult

Result of a quality gate check.

```python
from agentloops.quality_gate import GateResult
```

| Field | Type | Description |
|-------|------|-------------|
| `passed` | `bool` | Whether the output passed all checks above the threshold. |
| `score` | `float` | Ratio of passed checks to total checks (0.0-1.0). |
| `failures` | `list[str]` | Descriptions of failed checks. |
| `warnings` | `list[str]` | Non-blocking warnings. |

---

## Seed Rules

Pre-seeded IF/THEN rules for common agent types. When you pass `agent_type` to the `AgentLoops` constructor, rules for that type are loaded automatically on first init.

```python
from agentloops import get_seed_rules, list_agent_types
```

### `list_agent_types()`

Returns all available agent types.

```python
list_agent_types() -> list[str]
```

**Returns:** `["sales-sdr", "customer-support", "help-desk", "content-creator", "code-generator", "recruiting", "legal-review", "insurance-claims", "devops-incident", "ecommerce-rec"]`

### `get_seed_rules()`

Get the starter rules for a specific agent type.

```python
get_seed_rules(agent_type: str) -> list[Rule]
```

| Parameter | Type | Description |
|-----------|------|-------------|
| `agent_type` | `str` | One of the supported agent types. |

**Returns:** `list[Rule]` -- pre-configured IF/THEN rules with default confidence scores.

**Raises:** `ValueError` if the agent type is not recognized.

---

## Framework Adapters

### AgentLoopsCallback (LangChain)

Drop-in LangChain callback handler that auto-tracks chain runs and errors.

```python
from agentloops.adapters.langchain import AgentLoopsCallback
```

```python
AgentLoopsCallback(
    loops: AgentLoops,
    outcome_fn: Callable | None = None,
)
```

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `loops` | `AgentLoops` | required | The AgentLoops instance to track to. |
| `outcome_fn` | `Callable \| None` | `None` | Custom function to determine outcome from a chain run. Receives the run result, returns an outcome string. Defaults to `"success"` for completed runs, `"failure"` for errors. |

**Usage:**

```python
handler = AgentLoopsCallback(loops, outcome_fn=lambda run: "success" if run.success else "failure")
result = chain.invoke(prompt, config={"callbacks": [handler]})
```

---

### AgentLoopsCrewCallback (CrewAI)

CrewAI callback that tracks task and crew completions.

```python
from agentloops.adapters.crewai import AgentLoopsCrewCallback
```

```python
AgentLoopsCrewCallback(
    loops: AgentLoops,
    outcome_fn: Callable | None = None,
)
```

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `loops` | `AgentLoops` | required | The AgentLoops instance to track to. |
| `outcome_fn` | `Callable \| None` | `None` | Custom function to determine outcome from a task result. Receives the task output, returns an outcome string. |

**Usage:**

```python
callback = AgentLoopsCrewCallback(loops, outcome_fn=lambda task: task.output.quality_score)
crew = Crew(agents=[agent], tasks=[task], callbacks=[callback])
```

---

## SupabaseStorage

Cloud storage backend using Supabase. Supports multi-tenant isolation via Row Level Security.

```python
from agentloops.storage import SupabaseStorage
```

### Constructor

```python
SupabaseStorage(
    supabase_url: str,
    supabase_key: str,
    agent_name: str,
    user_id: str | None = None,
)
```

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `supabase_url` | `str` | required | Supabase project URL. |
| `supabase_key` | `str` | required | Supabase API key (anon or service role). |
| `agent_name` | `str` | required | Agent name for namespacing. |
| `user_id` | `str \| None` | `None` | User ID for multi-tenant RLS. When set, all reads and writes are scoped to this user. |

**Installation:** `pip install agentloops[supabase]`

**Migration:** Apply `supabase/migrations/001_initial_schema.sql` to your Supabase project before first use.

Implements the full `BaseStorage` interface.
