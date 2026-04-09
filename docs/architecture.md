# Technical Architecture

This document covers the system design, data flow, storage architecture, and scaling considerations for AgentLoops.

---

## System Design Overview

AgentLoops is a layered library with a single orchestrator entry point (`AgentLoops`) that coordinates five subsystems:

```
┌───────────────────────────────────────────────────────────┐
│                      Your Application                      │
│                                                           │
│   from agentloops import AgentLoops                       │
│   loops = AgentLoops("my-agent")                          │
└──────────────────────────┬────────────────────────────────┘
                           │
                           ▼
┌───────────────────────────────────────────────────────────┐
│                    AgentLoops (core.py)                    │
│                                                           │
│   The orchestrator. Owns all subsystems. Exposes 4        │
│   methods: track(), reflect(), enhance_prompt(), forget() │
│   Plus 3 property accessors: .rules, .conventions,        │
│   .tracker                                                │
└──────┬────────┬─────────┬──────────┬──────────┬──────────┘
       │        │         │          │          │
       ▼        ▼         ▼          ▼          ▼
  ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐
  │Tracker │ │Reflect-│ │Rule    │ │Conven- │ │Forget- │
  │        │ │or      │ │Engine  │ │tion    │ │ter     │
  │log_run │ │reflect │ │generate│ │Store   │ │prune   │
  │get_runs│ │        │ │active  │ │evolve  │ │        │
  │correla-│ │        │ │add_rule│ │detect  │ │        │
  │  te    │ │        │ │deactiv-│ │resolve │ │        │
  │improve-│ │        │ │  ate   │ │        │ │        │
  │  ment  │ │        │ │        │ │        │ │        │
  └───┬────┘ └───┬────┘ └───┬────┘ └───┬────┘ └───┬────┘
      │          │          │          │          │
      └──────────┴──────────┴──────────┴──────────┘
                            │
                            ▼
              ┌──────────────────────────┐
              │     Storage Backend      │
              │                          │
              │  BaseStorage (abstract)  │
              │  FileStorage (default)   │
              │  Custom (you implement)  │
              └──────────────────────────┘
```

### Design Principles

1. **Single entry point.** Everything goes through `AgentLoops`. You never need to instantiate subsystems directly (though you can via the property accessors).

2. **Storage-agnostic.** All subsystems depend on `BaseStorage`, not on a specific database. Swap file storage for Postgres, Redis, or S3 by implementing one interface.

3. **LLM-powered analysis, not LLM-dependent storage.** Tracking and storage are pure data operations -- no LLM calls. Only `reflect()`, `generate_rules()`, and `evolve()` call the LLM.

4. **Append-only runs, mutable rules.** Runs are immutable once logged (JSONL append). Rules and conventions have lifecycles (active/inactive/pruned/superseded).

5. **Zero config to start.** `AgentLoops("name")` works out of the box with file storage and environment variable API keys.

---

## Data Flow

### Write Path (tracking a run)

```
loops.track(input, output, outcome, metadata)
       │
       ▼
  AgentLoops.track()
       │
       ├── 1. Get active rule IDs from RuleEngine
       │
       ├── 2. Create Run object with:
       │      - input, output, outcome
       │      - agent_name
       │      - auto-generated id + timestamp
       │      - metadata dict
       │      - rules_applied = active rule IDs
       │
       └── 3. Tracker.log_run() → Storage.save_run()
                                        │
                                        ▼
                                   runs.jsonl (append)
```

**Key detail:** The `rules_applied` field captures which rules were active at the time of the run. This enables later correlation analysis ("did this rule help?").

### Read Path (enhancing a prompt)

```
loops.enhance_prompt(base_prompt)
       │
       ├── 1. RuleEngine.active() → Storage.get_rules(active_only=True)
       │      Sort by confidence descending
       │
       ├── 2. ConventionStore.get_conventions() → Storage.get_conventions(active_only=True)
       │
       └── 3. Build enhanced prompt:
              base_prompt
              + "## Decision Rules" section
              + "## Conventions" section
```

**No LLM call.** This is a pure data assembly operation, making it fast enough to call on every agent invocation.

### Reflection Path (learning from runs)

```
loops.reflect(last_n=5)
       │
       ▼
  Reflector.reflect()
       │
       ├── 1. Load last N runs from storage
       │
       ├── 2. Load active rules + conventions
       │
       ├── 3. Build prompt with runs, rules, conventions
       │
       ├── 4. Call Anthropic API (LLM)
       │      Model: reflection_model (default: claude-sonnet-4-6)
       │      Max tokens: 2000
       │      Expected output: JSON with critique, suggested_rules,
       │      confidence_scores, rules_to_reconsider
       │
       ├── 5. Parse JSON response (with markdown fence stripping)
       │
       ├── 6. Create Reflection object
       │
       └── 7. Save to storage → reflections.json
```

### Rule Generation Path

```
loops.rules.generate_rules()
       │
       ▼
  RuleEngine.generate_rules()
       │
       ├── 1. Load last 20 runs (or provided runs)
       │
       ├── 2. Load existing active rules (to avoid duplicates)
       │
       ├── 3. Build prompt asking for IF/THEN rules with evidence
       │
       ├── 4. Call Anthropic API (LLM)
       │
       ├── 5. Parse JSON: array of {text, confidence, evidence}
       │
       ├── 6. Filter: only confidence >= 0.5
       │
       └── 7. For each rule: create Rule object → save to storage
```

### Convention Evolution Path

```
loops.conventions.evolve()
       │
       ▼
  ConventionStore.evolve()
       │
       ├── 1. Load active conventions + active rules
       │
       ├── 2. Build prompt asking the LLM to:
       │      - Identify reinforced conventions
       │      - Detect contradictions
       │      - Suggest merges
       │      - Suggest removals
       │      - Promote high-confidence rules to conventions
       │
       ├── 3. Call Anthropic API (LLM)
       │
       ├── 4. Apply changes:
       │      - new_conventions → save with status "active"
       │      - to_remove → mark status "pruned"
       │      - to_merge → create merged convention, mark originals "superseded"
       │
       └── 5. Return changes summary
```

### Forgetting Path

```
loops.forget(strategy="hybrid", max_age_days=21)
       │
       ▼
  Forgetter.prune()
       │
       ├── 1. Calculate cutoff date: now - max_age_days
       │
       ├── 2. For each active rule:
       │      PROTECTED if:
       │      - confidence >= 0.8
       │      - last_validated after cutoff
       │      
       │      PRUNED if (by strategy):
       │      - "decay": created before cutoff
       │      - "importance": confidence < min_confidence
       │      - "hybrid": either condition
       │      
       │      Action: set rule.active = False → save
       │
       └── 3. For each active convention:
              PROTECTED if:
              - updated_at after cutoff
              
              PRUNED if (by strategy):
              - "decay"/"hybrid": created before cutoff
              - "importance": skip (no confidence score)
              
              Action: set conv.status = "pruned" → save
```

---

## Storage Architecture

### File Storage Layout

```
.agentloops/
└── {agent_name}/
    ├── runs.jsonl           # Append-only, one JSON object per line
    ├── rules.json           # Array of rule objects
    ├── conventions.json     # Array of convention objects
    └── reflections.json     # Array of reflection objects
```

**Why JSONL for runs?** Runs are append-only and high-volume. JSONL (one JSON object per line) allows efficient appending without reading/rewriting the entire file. Rules, conventions, and reflections use standard JSON arrays because they're lower volume and need in-place updates.

### Data Models on Disk

**Run (runs.jsonl):**
```json
{"id":"a1b2c3","agent_name":"sales","input":"...","output":"...","outcome":"success","metadata":{"latency_ms":800},"rules_applied":["r1","r2"],"created_at":"2026-04-08T10:30:00"}
```

**Rule (rules.json):**
```json
[
  {
    "id": "r1",
    "text": "IF cold outreach THEN personalize subject line",
    "confidence": 0.90,
    "evidence_count": 5,
    "evidence": ["run a1b2c3 had 3x reply rate with personalization"],
    "created_at": "2026-04-01T10:00:00",
    "last_validated": "2026-04-08T10:00:00",
    "active": true
  }
]
```

**Convention (conventions.json):**
```json
[
  {
    "id": "c1",
    "text": "Always reference the prospect's recent company news",
    "source": "evolved from rule: IF prospect has recent news THEN reference it",
    "created_at": "2026-04-01T10:00:00",
    "updated_at": "2026-04-08T10:00:00",
    "status": "active"
  }
]
```

**Reflection (reflections.json):**
```json
[
  {
    "id": "ref1",
    "agent_name": "sales",
    "critique": "Emails with personalized subject lines had 80% success...",
    "suggested_rules": ["IF cold outreach THEN personalize..."],
    "confidence_scores": {"IF cold outreach THEN personalize...": 0.90},
    "run_ids": ["a1b2c3", "d4e5f6"],
    "created_at": "2026-04-08T10:30:00"
  }
]
```

### Custom Storage Backends

Implement the `BaseStorage` abstract class:

```python
class BaseStorage(ABC):
    save_run(run: Run) -> None
    get_runs(agent_name, last_n, outcome_filter) -> list[Run]
    save_rule(rule: Rule) -> None
    get_rules(active_only: bool) -> list[Rule]
    save_convention(convention: Convention) -> None
    get_conventions(active_only: bool) -> list[Convention]
    save_reflection(reflection: Reflection) -> None
    get_reflections(last_n: int | None) -> list[Reflection]
    delete(collection: str, id: str) -> bool
```

All models have `to_dict()` and `from_dict()` methods, making serialization to any format straightforward.

---

## How Reflection Works Under the Hood

The reflection system sends a carefully structured prompt to an LLM. Here's the actual prompt template:

```
You are a self-reflection engine for an AI agent named "{agent_name}".

Analyze these recent runs and produce a structured critique...

## Recent Runs
### Run 1 (id: abc123)
**Input:** {truncated to 500 chars}
**Output:** {truncated to 500 chars}
**Outcome:** success
**Rules applied:** rule1, rule2

## Active Rules (currently applied)
- [rule1] IF condition THEN action (confidence: 0.85)

## Active Conventions
- Always do X when Y

## Your Task
1. Identify what worked well and what failed.
2. Look for patterns...
3. Suggest new IF/THEN rules...
4. Flag outdated rules...
5. Rate confidence...
```

The LLM returns JSON. AgentLoops strips markdown fences if present and parses the response. If parsing fails, the raw text becomes the critique with empty rule suggestions.

**Input truncation:** Inputs and outputs are truncated to 500 characters in the reflection prompt to stay within token limits while preserving the signal. The full data remains in storage.

---

## How Rules Propagate Across Agents

Rules are scoped per agent by default. To share rules across agents:

```
Agent A                    Agent B
  │                          │
  ▼                          ▼
┌──────────┐              ┌──────────┐
│ Storage A│              │ Storage B│
│ (isolated)              │ (isolated)
└──────────┘              └──────────┘

        vs.

Agent A ────┐    ┌──── Agent B
            │    │
            ▼    ▼
        ┌──────────┐
        │ Shared   │
        │ Storage  │
        └──────────┘
```

**Shared storage pattern:**
```python
from agentloops.storage import FileStorage

shared = FileStorage(".agentloops", "shared-team")
agent_a = AgentLoops("agent-a", storage=shared)
agent_b = AgentLoops("agent-b", storage=shared)
```

Both agents read the same rules and conventions via `enhance_prompt()`. Runs are tagged with `agent_name` so you can filter later.

**Cross-pollination pattern** (rules discovered by one agent, used by another):
```python
# Agent A discovers rules
rules_a = agent_a.rules.generate_rules()

# Manually add the best ones to Agent B
for rule in rules_a:
    if rule.confidence >= 0.8:
        agent_b.rules.add_rule(text=rule.text, confidence=rule.confidence)
```

---

## Scaling Considerations

### File Storage Limits

| Metric | Practical Limit | Mitigation |
|--------|----------------|------------|
| Runs | ~100K runs per agent | Archive old runs to cold storage |
| Rules | ~1,000 active rules | Forgetter prunes to keep count manageable |
| Conventions | ~100 active conventions | Evolution merges overlapping ones |
| Reflections | ~5,000 reflections | Append-only, archive old ones |
| Disk space | ~500MB per 100K runs | Runs are the growth driver |

**For production at scale:** Implement a database-backed `BaseStorage`:
- PostgreSQL for transactional workloads
- ClickHouse or BigQuery for high-volume analytics
- Redis for hot-path reads (active rules, conventions)

### LLM Call Budget

| Operation | LLM Calls | When |
|-----------|-----------|------|
| `track()` | 0 | Every run |
| `enhance_prompt()` | 0 | Every run |
| `reflect()` | 1 | Periodically (e.g., every 10 runs) |
| `generate_rules()` | 1 | Periodically (e.g., weekly) |
| `evolve()` | 1 | Periodically (e.g., weekly) |
| `detect_contradictions()` | 1 | On-demand |
| `forget()` | 0 | On schedule |

**Hot path (every run):** Zero LLM calls. `track()` and `enhance_prompt()` are pure data operations.

**Cold path (learning):** 2-3 LLM calls per learning cycle. At weekly cadence, this is negligible cost.

### Concurrency

The current `FileStorage` is not thread-safe. For concurrent access:
- Use a database backend with proper transactions
- Or use file locking (e.g., `fcntl.flock`) around storage operations
- JSONL appends are generally safe for concurrent writes on most filesystems, but JSON array updates are not

---

## Security Model

### What Data Lives Where

| Data | Location | Contains |
|------|----------|----------|
| Runs | `.agentloops/{agent}/runs.jsonl` | Agent inputs, outputs, outcomes |
| Rules | `.agentloops/{agent}/rules.json` | Learned decision rules |
| Conventions | `.agentloops/{agent}/conventions.json` | Behavioral patterns |
| Reflections | `.agentloops/{agent}/reflections.json` | LLM analysis of runs |

### What Gets Sent to LLMs

| Operation | Data Sent | Notes |
|-----------|-----------|-------|
| `reflect()` | Last N runs (truncated to 500 chars each), active rules, conventions | Full input/output is truncated |
| `generate_rules()` | Last 20 runs (truncated to 200 chars each), existing rules | More aggressive truncation |
| `evolve()` | Active conventions, active rules | No run data sent |
| `detect_contradictions()` | Active conventions only | No run data sent |

### Recommendations

1. **Sensitive data in inputs/outputs:** If your agent processes PII, PHI, or financial data, the reflection and rule generation prompts will include truncated versions. Either:
   - Implement a custom storage backend that redacts sensitive fields before they're read by the Reflector
   - Use `metadata` to store sensitive context (metadata is not sent to the LLM)
   - Run reflection with a self-hosted model

2. **API keys:** The Anthropic API key is passed via constructor or environment variable. It's never stored in the `.agentloops/` directory.

3. **Storage permissions:** The `.agentloops/` directory should have appropriate filesystem permissions. Add it to `.gitignore` to prevent accidental commits of run data.

4. **Network boundary:** All LLM calls go to the Anthropic API. No data is sent elsewhere. The storage layer is entirely local (file-based) unless you implement a remote backend.

---

## Module Dependency Graph

```
agentloops/__init__.py
       │
       ├── core.py (AgentLoops)
       │      │
       │      ├── tracker.py (Tracker)
       │      ├── reflector.py (Reflector)
       │      ├── rule_engine.py (RuleEngine)
       │      ├── convention_store.py (ConventionStore)
       │      └── forgetter.py (Forgetter)
       │
       ├── models.py (Run, Rule, Convention, Reflection)
       │      └── (no dependencies beyond stdlib)
       │
       └── storage/
              ├── base.py (BaseStorage - abstract)
              │      └── depends on models.py
              └── file.py (FileStorage)
                     └── depends on base.py, models.py
```

**External dependencies:**
- `anthropic` -- used by Reflector, RuleEngine, and ConventionStore for LLM calls (default provider)
- `openai` (optional) -- alternative LLM provider, install with `pip install agentloops[openai]`
- Standard library only for everything else (json, pathlib, uuid, datetime, dataclasses, abc)

The LLM imports are deferred (inside methods, not at module level) so you can use AgentLoops for tracking and prompt enhancement without having any LLM SDK installed, as long as you don't call `reflect()`, `generate_rules()`, or `evolve()`.

### Multi-LLM Support

AgentLoops supports three LLM providers for reflection, rule generation, and convention evolution:

| Provider | `llm_provider` | API Key | Notes |
|----------|----------------|---------|-------|
| Anthropic | `"anthropic"` (default) | `ANTHROPIC_API_KEY` env var or `api_key` param | Uses Claude models |
| OpenAI | `"openai"` | `OPENAI_API_KEY` env var or `api_key` param | Uses GPT models |
| Custom | `"custom"` | Not needed | Pass `llm_fn` -- any callable that takes a prompt string and returns a response string |

The custom provider enables local models (Ollama), Groq, Mistral, or any other LLM endpoint. The `llm_fn` callable is passed the same structured prompts that would go to Anthropic/OpenAI, and must return the response text.

---

## Server Architecture (FastAPI)

AgentLoops includes a FastAPI server (`server/app.py`) for hosted deployments:

```
┌──────────────────────────────────────────────────────────┐
│                    FastAPI Server                          │
│                   (server/app.py)                          │
│                                                          │
│  15 REST endpoints:                                       │
│  - POST /track          - GET  /runs                     │
│  - POST /reflect        - GET  /rules                    │
│  - POST /evolve         - GET  /conventions              │
│  - POST /forget         - GET  /reflections              │
│  - POST /check          - GET  /improvement-curve        │
│  - POST /enhance-prompt - GET  /correlate/{rule_id}      │
│  - POST /agents         - GET  /agents                   │
│  - GET  /health                                          │
│                                                          │
│  Authentication:                                          │
│  - JWT tokens (user sessions)                            │
│  - API keys (server-to-server, al_xxx format)            │
│  Both managed in server/auth.py                          │
│                                                          │
│  Storage: Supabase (with Row Level Security)             │
└──────────────────────┬───────────────────────────────────┘
                       │
                       ▼
              ┌─────────────────┐
              │    Supabase     │
              │  (PostgreSQL +  │
              │   RLS + Auth)   │
              └─────────────────┘
```

**Note:** The `al_xxx` API key format is used for authenticating with the hosted API server (server/auth.py). When using the library directly, the `api_key` parameter is the LLM provider's API key (Anthropic or OpenAI).

## Dashboard Architecture (Next.js)

The dashboard (`dashboard/`) provides a visual interface for monitoring agent learning, following the maria-os design system (white background, black borders, no colored backgrounds).

```
┌──────────────────────────────────────────────────────────┐
│                  Next.js Dashboard                         │
│                  (dashboard/)                              │
│                                                          │
│  Pages:                                                   │
│  - Overview      — agent list, health status             │
│  - Agent Detail  — runs, rules, conventions, reflections │
│  - Learning      — improvement curves, rule correlation  │
│  - Quality       — gate results, failure analysis        │
│                                                          │
│  Data source: FastAPI server OR direct Supabase queries  │
└──────────────────────────────────────────────────────────┘
```
