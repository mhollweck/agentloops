# Core Concepts

AgentLoops implements seven learning mechanisms that work together to make agents smarter over time. These mechanisms are inspired by [Reflexion](https://arxiv.org/abs/2303.11366) (self-reflection), cognitive memory architectures (encode/consolidate/forget), and months of production use across 7 real agents.

This document explains each mechanism in depth: what it does, how it works internally, and when to use it.

---

## The Learning Loop

Before diving into individual mechanisms, here's how they fit together:

```
     ┌──────────────────────────────────────────────────────────────────┐
     │                        EVERY RUN                                 │
     │                                                                  │
     │   Your Agent ──track()──> Tracker ──> runs.jsonl                 │
     │       ^                                    │                     │
     │       │                                    ▼                     │
     │   enhance_prompt()              reflect() (after N runs)         │
     │       ^                                    │                     │
     │       │                                    ▼                     │
     │   ┌───┴────┐                     ┌─────────────────┐            │
     │   │ Active │<────────────────────│   Reflector     │            │
     │   │ Rules  │                     │ (LLM critique)  │            │
     │   │   +    │                     └────────┬────────┘            │
     │   │Convns  │                              │                     │
     │   └───┬────┘                              ▼                     │
     │       ^                         generate_rules()                │
     │       │                                    │                     │
     │       │              ┌─────────────────────┼───────────┐        │
     │       │              ▼                     ▼            ▼        │
     │       │         Rule Engine          Convention     Forgetter   │
     │       │         (IF/THEN)            Store           (prune)    │
     │       │              │               (evolve)           │        │
     │       └──────────────┴───────────────────┘              │        │
     │                                                         │        │
     │                      ◄──── prune stale entries ─────────┘        │
     └──────────────────────────────────────────────────────────────────┘
```

**The cycle:**
1. Your agent runs. You call `track()` with the input, output, and outcome.
2. After several runs, you call `reflect()`. The Reflector sends recent runs to an LLM for analysis.
3. The reflection suggests new IF/THEN rules. You call `generate_rules()` to persist them.
4. Next time your agent runs, `enhance_prompt()` injects those rules into the prompt.
5. Periodically, `evolve()` promotes high-confidence rules to conventions and resolves contradictions.
6. `forget()` prunes stale patterns that no longer apply.
7. Repeat. The agent gets better every cycle.

---

## 1. Self-Reflection

**What it does:** After a batch of runs, an LLM analyzes what worked, what failed, and why.

**How it works:**

```
  Recent Runs (last N)
  + Active Rules
  + Active Conventions
         │
         ▼
  ┌──────────────────┐
  │  Reflection LLM  │
  │                  │
  │  "Analyze these  │
  │   runs. What     │
  │   patterns do    │
  │   you see?"      │
  └────────┬─────────┘
           │
           ▼
  ┌──────────────────┐
  │   Reflection     │
  │                  │
  │  - critique      │
  │  - suggested_    │
  │    rules[]       │
  │  - confidence_   │
  │    scores{}      │
  └──────────────────┘
```

The Reflector builds a prompt that includes:
- The last N runs with their inputs, outputs, and outcomes
- All currently active rules (so the LLM can evaluate whether they're working)
- All current conventions (so the LLM has full context)

The LLM returns a structured JSON response with:
- **critique**: A 2-3 paragraph analysis of what's working and what isn't
- **suggested_rules**: New IF/THEN rules based on observed patterns
- **confidence_scores**: A confidence rating (0.0-1.0) for each suggestion
- **rules_to_reconsider**: IDs of existing rules that may be outdated

**When to use:** Call `reflect()` after every 5-10 runs, or on a schedule (daily, hourly, etc. depending on volume).

```python
# Basic reflection
reflection = loops.reflect(last_n=5)

# Access the structured output
print(reflection.critique)
print(reflection.suggested_rules)
print(reflection.confidence_scores)
```

---

## 2. Rule Generation

**What it does:** Converts observed performance patterns into explicit IF/THEN decision rules with evidence.

**How it works:**

```
  All Recent Runs (last 20)
  + Existing Rules (to avoid duplicates)
         │
         ▼
  ┌──────────────────┐
  │ Rule Generation  │
  │      LLM        │
  │                  │
  │  "Find IF/THEN  │
  │   patterns with  │
  │   evidence"      │
  └────────┬─────────┘
           │
           ▼
  ┌──────────────────┐
  │   New Rules      │
  │                  │
  │  - text          │
  │  - confidence    │
  │  - evidence[]    │
  │  - evidence_     │
  │    count         │
  └──────────────────┘
```

A good rule looks like:
```
IF the user asks about pricing THEN include the comparison table
  -- because runs with tables had 90% success vs 45% without
```

Rules have:
- **text**: The IF/THEN rule itself
- **confidence**: 0.0-1.0 based on evidence strength (only rules >= 0.5 are generated)
- **evidence**: List of supporting observations from specific runs
- **evidence_count**: Number of supporting data points
- **active**: Whether the rule is currently applied

**When to use:** Run `generate_rules()` after accumulating meaningful data -- typically weekly or after significant outcome changes.

```python
# Generate from last 20 runs (default)
new_rules = loops.rules.generate_rules()

# Generate from specific runs
new_rules = loops.rules.generate_rules(runs=my_runs)

# Manually add a rule you've observed
loops.rules.add_rule(
    text="IF customer mentions competitor THEN highlight our unique differentiator",
    evidence=["ticket-123 resolved faster with this approach"],
    confidence=0.8,
)
```

---

## 3. Convention Evolution

**What it does:** Promotes high-confidence rules to long-lived conventions, detects contradictions between them, and merges overlapping patterns.

**How it works:**

```
  Active Conventions     Active Rules
         │                    │
         └────────┬───────────┘
                  │
                  ▼
         ┌────────────────┐
         │ Evolution LLM  │
         │                │
         │ "Compare rules │
         │  to conventions.│
         │  Find conflicts,│
         │  merges, new   │
         │  promotions."  │
         └───────┬────────┘
                 │
                 ▼
         ┌────────────────┐
         │   Changes      │
         │                │
         │ - new[]        │ ──> New conventions added
         │ - removed[]    │ ──> Stale ones pruned
         │ - merged[]     │ ──> Overlapping ones combined
         │ - contradictions│ ──> Conflicts flagged
         └────────────────┘
```

The evolution engine performs four operations:

1. **Promotion**: High-confidence rules with strong evidence become conventions -- behavioral patterns the agent always follows.

2. **Contradiction Detection**: Finds conventions that give opposite advice. Example:
   - Convention A: "Always include pricing in first email"
   - Convention B: "Never mention pricing before qualification call"
   
   These contradict each other and need resolution.

3. **Merging**: Combines overlapping conventions. Two conventions that say similar things become one cleaner version.

4. **Removal**: Flags conventions with no supporting evidence in current rules.

Convention statuses:
- `active` -- currently applied to agent prompts
- `superseded` -- replaced by a merged convention
- `contradicted` -- part of a resolved conflict
- `pruned` -- removed by the forgetter

**When to use:** Run `evolve()` weekly, after rule generation.

```python
# Trigger evolution
changes = loops.conventions.evolve()
print(f"Added: {len(changes['new'])}")
print(f"Removed: {len(changes['removed'])}")
print(f"Merged: {len(changes['merged'])}")
print(f"Contradictions found: {len(changes['contradictions'])}")

# Detect contradictions without resolving them
contradictions = loops.conventions.detect_contradictions()

# Manually resolve a contradiction
resolved = loops.conventions.resolve_contradiction(
    convention_ids=["abc123", "def456"],
    resolution="Include pricing only after the prospect has been qualified via at least one interaction",
)
```

---

## 4. Selective Forgetting

**What it does:** Prunes stale rules and conventions so the agent's learned knowledge stays current and relevant.

**How it works:**

```
  All Active Rules + Conventions
         │
         ▼
  ┌──────────────────────────────────────────┐
  │              Forgetter                    │
  │                                          │
  │  For each item, check:                   │
  │                                          │
  │  PROTECTED (never pruned):               │
  │  - Rules with confidence >= 0.8          │
  │  - Rules validated within max_age_days   │
  │  - Conventions updated within max_age_days│
  │                                          │
  │  PRUNED if:                              │
  │  - "decay": older than max_age_days      │
  │  - "importance": confidence < threshold  │
  │  - "hybrid": either condition met        │
  └──────────────────────────────────────────┘
```

Three strategies:

| Strategy | Prunes when | Best for |
|----------|------------|----------|
| `decay` | Item is older than `max_age_days` | Fast-changing domains where old patterns become irrelevant |
| `importance` | Rule confidence is below `min_confidence` | Domains where weak signals are noise |
| `hybrid` | Either age or confidence threshold is met | General use (the default) |

**Protection rules** (these items are NEVER pruned):
- Rules with confidence >= 0.8 (strong evidence)
- Rules that have been validated recently (within `max_age_days`)
- Conventions that were updated recently

**When to use:** Run daily or weekly to keep memory lean.

```python
# Default: hybrid strategy, 21-day max age
pruned = loops.forget()
print(f"Rules pruned: {pruned['rules_pruned']}")
print(f"Conventions pruned: {pruned['conventions_pruned']}")

# Aggressive pruning for fast-moving domains
pruned = loops.forget(strategy="decay", max_age_days=7)

# Conservative: only remove low-confidence items
pruned = loops.forget(strategy="importance")
```

---

## 5. Performance Tracking

**What it does:** Logs every agent run with its outcome, correlates performance with applied rules, and computes improvement curves over time.

**How it works:**

```
  track() ──> Run stored in runs.jsonl
                    │
                    ├──> correlate(rule_id)
                    │         │
                    │         ▼
                    │    "Runs WITH this rule: 85% success"
                    │    "Runs WITHOUT: 45% success"
                    │
                    └──> improvement_curve()
                              │
                              ▼
                         ┌──────────────────────────┐
                         │ Window 1: 60% success     │
                         │ Window 2: 72% success     │
                         │ Window 3: 85% success     │
                         │ (agent is improving!)     │
                         └──────────────────────────┘
```

Key features:

- **Run logging**: Every call to `track()` records the input, output, outcome, metadata, and which rules were active at the time.

- **Rule correlation**: `correlate(rule_id)` splits all runs into two groups (with vs. without the rule) and computes success rates. This tells you whether a rule is actually helping.

- **Improvement curves**: `improvement_curve()` computes a sliding-window metric over time, so you can see whether your agent is getting better.

```python
# Track with metadata
run = loops.track(
    input="...",
    output="...",
    outcome="success",
    metadata={"latency_ms": 800, "model": "claude-sonnet-4-6", "tokens": 320},
)

# See if a rule is helping
correlation = loops.tracker.correlate("rule-id-here")
print(correlation["with_rule"])     # {"count": 50, "success_rate": 0.85}
print(correlation["without_rule"])  # {"count": 30, "success_rate": 0.45}

# Track improvement over time
curve = loops.tracker.improvement_curve(metric="success_rate", window_days=7)
for point in curve:
    print(f"{point['window_start']}: {point['success_rate']:.1%} ({point['run_count']} runs)")
```

---

## 6. Quality Gates

**What it does:** Uses active rules as pre-flight checks before agent output is delivered. If the output violates known rules, you can flag it for review or regeneration.

**How it works:**

Quality gates are not a separate component -- they're a pattern built on top of `enhance_prompt()` and `rules.active()`. The idea: before your agent's output reaches the user, check it against what the system has learned.

```
  Agent Output
       │
       ▼
  ┌──────────────────────┐
  │  Quality Gate Check  │
  │                      │
  │  For each active rule:│
  │  Does the output     │
  │  violate this rule?  │
  └──────────┬───────────┘
             │
        ┌────┴────┐
        │         │
     PASS      FAIL
        │         │
        ▼         ▼
    Deliver    Regenerate
    output     or flag for
               human review
```

Implementation pattern:

```python
# Get active rules
rules = loops.rules.active()

# Build a quality check prompt
check_prompt = f"""Check this agent output against these rules:

Rules:
{chr(10).join(f'- {r.text}' for r in rules)}

Output to check:
{agent_output}

Does the output violate any rules? Return JSON:
{{"passes": true/false, "violations": ["rule text that was violated"]}}
"""

# Send to LLM for evaluation
result = check_with_llm(check_prompt)

if not result["passes"]:
    # Regenerate with violations flagged, or route to human
    regenerate_with_feedback(result["violations"])
```

---

## 7. Spike Response

**What it does:** Detects performance anomalies -- sudden drops or jumps in success rate -- and triggers focused learning on what changed.

**How it works:**

Spike detection is a pattern built on top of the Tracker's `improvement_curve()` method. When a metric deviates significantly from recent averages, you trigger a focused reflection.

```
  improvement_curve()
       │
       ▼
  ┌────────────────────────────────┐
  │  Compare latest window to      │
  │  running average               │
  │                                │
  │  If |current - avg| > threshold│
  │     → SPIKE DETECTED           │
  └────────────┬───────────────────┘
               │
               ▼
  ┌────────────────────────────────┐
  │  Focused reflection on runs    │
  │  in the spike window           │
  │                                │
  │  "What changed? What's new?    │
  │   What rule started/stopped?"  │
  └────────────────────────────────┘
```

Implementation pattern:

```python
curve = loops.tracker.improvement_curve(metric="success_rate", window_days=3)

if len(curve) >= 2:
    current = curve[-1]["success_rate"]
    previous = curve[-2]["success_rate"]
    
    # Detect significant drop
    if previous - current > 0.15:  # 15% drop
        print(f"SPIKE: Success rate dropped from {previous:.1%} to {current:.1%}")
        
        # Trigger focused reflection on recent runs
        reflection = loops.reflect(last_n=10)
        print(f"Analysis: {reflection.critique}")
        
        # Generate rules from the anomaly period
        new_rules = loops.rules.generate_rules()
```

---

## Data Flow Summary

```
┌─────────────────────────────────────────────────────────────────┐
│                    .agentloops/{agent}/                          │
│                                                                 │
│  runs.jsonl ─────────────> Tracker                              │
│  (append-only log)         - log_run()                          │
│                            - correlate()                        │
│                            - improvement_curve()                │
│                                    │                            │
│                                    ▼                            │
│  reflections.json <─────── Reflector                            │
│  (analysis history)        - reflect()                          │
│                                    │                            │
│                                    ▼                            │
│  rules.json <──────────── RuleEngine                            │
│  (IF/THEN rules)           - generate_rules()                   │
│  (active/inactive)         - active()                           │
│                            - add_rule()                         │
│                            - deactivate_rule()                  │
│                                    │                            │
│                                    ▼                            │
│  conventions.json <─────── ConventionStore                      │
│  (behavioral patterns)     - evolve()                           │
│  (status lifecycle)        - detect_contradictions()            │
│                            - resolve_contradiction()            │
│                                    │                            │
│                                    ▼                            │
│                            Forgetter                            │
│                            - prune() ──> marks rules inactive   │
│                                      ──> marks conventions      │
│                                          "pruned"               │
└─────────────────────────────────────────────────────────────────┘
```

## Storage

All data lives locally by default in `.agentloops/{agent_name}/`:
- `runs.jsonl` -- append-only log of all runs (JSONL format for streaming efficiency)
- `rules.json` -- current rules with active/inactive status
- `conventions.json` -- conventions with full lifecycle status
- `reflections.json` -- history of all reflections

You can implement a custom storage backend by subclassing `BaseStorage` for databases, cloud storage, or shared state across agent fleets.

## Next Steps

- **[API Reference](api-reference.md)** -- every method, parameter, and return type
- **[Integration Guide](integrations.md)** -- use with LangChain, CrewAI, OpenAI, Anthropic
- **[Architecture](architecture.md)** -- system design and scaling considerations
