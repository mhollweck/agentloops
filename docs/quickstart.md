# Getting Started with AgentLoops

Get your first self-learning agent running in under 5 minutes.

## Installation

```bash
pip install agentloops
```

AgentLoops uses the Anthropic SDK for reflection and rule generation. Set your API key:

```bash
export ANTHROPIC_API_KEY=sk-ant-...
```

## Create Your First AgentLoops Instance

```python
from agentloops import AgentLoops

loops = AgentLoops("my-agent", agent_type="sales-sdr")
```

That's it. AgentLoops creates a `.agentloops/my-agent/` directory in your working folder to store runs, rules, conventions, and reflections as JSON files.

### Three Tiers

| Tier | Usage | What you get |
|------|-------|-------------|
| **Free** ($0) | `AgentLoops("my-agent")` | Local storage, 3 agent types, manual triggers for `reflect()`, `evolve()`, `forget()` |
| **Pro** ($99/mo) | `AgentLoops("my-agent", agent_type="sales-sdr", storage="supabase", supabase_url="...", supabase_key="...")` | Cloud storage, unlimited agent types, auto-learn, dashboard, live global rules |
| **Team** ($249/mo) | Same constructor + org config | Shared namespace across org's agents, team analytics |
| **Enterprise** | Contact us | Cross-customer intelligence, benchmarking, dedicated support |

**Free** is fully functional -- you call `reflect()`, `evolve()`, and `forget()` manually. **Pro** ($99/mo) adds automatic learning triggers (reflection after N outcomes, spike detection, evolution on schedule) plus a dashboard and live rules from the collective intelligence network. **Team** ($249/mo) adds shared memory across your org's agents. **Enterprise** adds cross-customer intelligence, benchmarking, and dedicated support.

### Configuration Options

```python
loops = AgentLoops(
    agent_name="my-agent",
    agent_type="sales-sdr",             # Agent type for pre-seeded rules and cross-customer intelligence.
    api_key=None,                       # LLM provider API key. Falls back to ANTHROPIC_API_KEY or OPENAI_API_KEY env var.
    llm_provider="anthropic",           # "anthropic" (default), "openai", or "custom" (requires llm_fn).
    llm_fn=None,                        # Custom LLM callable for llm_provider="custom". Takes str, returns str.
    storage="file",                     # Default. Pass a BaseStorage instance for custom backends.
    storage_path=".agentloops",         # Where to store data. Defaults to ".agentloops".
    reflection_model="claude-sonnet-4-6",  # Model for reflection and rule generation.
    auto_learn=True,                    # Auto-trigger reflect/evolve/forget.
    reflection_threshold=10,            # Number of runs before auto-reflection triggers.
    evolution_interval=50,              # Number of runs between auto-evolution cycles.
)
```

## Bring Your Own LLM

AgentLoops defaults to Anthropic for reflection and rule generation, but supports OpenAI and custom LLM providers too.

```python
# OpenAI
loops = AgentLoops("my-agent", llm_provider="openai", api_key="sk-...")

# Custom LLM (e.g., local Ollama, Groq, Mistral)
import requests

def my_llm(prompt: str) -> str:
    response = requests.post("http://localhost:11434/api/generate", json={"model": "llama3", "prompt": prompt})
    return response.json()["response"]

loops = AgentLoops("my-agent", llm_provider="custom", llm_fn=my_llm)
```

When using `llm_provider="openai"`, set `OPENAI_API_KEY` as an environment variable or pass `api_key` directly. When using `llm_provider="custom"`, no API key is needed -- just provide your `llm_fn` callable.

## Track Your First Run

Every time your agent processes something, tell AgentLoops about it:

```python
run = loops.track(
    input="Write a cold email to the VP of Engineering at Acme Corp",
    output="Subject: Quick question about your infrastructure...",
    outcome="success",  # or "failure", or a numeric score like "0.85"
    metadata={"latency_ms": 1200, "tokens": 450},
)

print(run.id)  # "a1b2c3d4e5f6"
```

The `outcome` field is how AgentLoops knows what's working. Use:
- `"success"` / `"failure"` for binary outcomes
- A numeric string like `"0.85"` or `"4.2"` for scored outcomes

### Configuring Outcomes

For agents with complex success criteria, define an `OutcomeConfig`:

```python
from agentloops import AgentLoops, OutcomeConfig, MetricDef

# Binary (the default if you don't specify)
loops = AgentLoops("my-agent", outcome=OutcomeConfig.binary())

# Categorical — multiple possible outcomes
loops = AgentLoops("booking-agent", outcome=OutcomeConfig.categorical(["booked", "replied", "ignored"]))

# Numeric — scored outcomes with a direction
loops = AgentLoops("speed-agent", outcome=OutcomeConfig.numeric(goal="minimize"))

# Multi-metric — weighted composite scoring
loops = AgentLoops("sales-agent", outcome=OutcomeConfig(metrics=[
    MetricDef("booking_rate", "categorical", weight=3.0, success_values=["booked"]),
    MetricDef("latency", "duration", weight=1.0, target_value=500),
]))

# Track with multi-metric values
loops.track(
    input="...",
    output="...",
    outcome={"booking_rate": "booked", "latency": 320},
)

# Compute composite score programmatically
score = loops.outcome.score({"booking_rate": "booked", "latency": 320})

# Human-readable description of what "good" means
print(loops.outcome.describe())
```

The outcome config tells the reflection engine what "good" looks like, so rules and conventions optimize for your actual goals -- not just binary pass/fail.

## Trigger Reflection

After tracking several runs, ask AgentLoops to analyze what's working and what isn't:

```python
reflection = loops.reflect(last_n=5)

print(reflection.critique)
# "Emails with personalized subject lines had a 80% success rate,
#  while generic subjects had 20%. The agent consistently fails
#  when it doesn't reference the prospect's company by name."

print(reflection.suggested_rules)
# ["IF cold outreach THEN personalize the subject line with the prospect's name",
#  "IF writing to VP-level THEN keep email under 100 words"]

print(reflection.confidence_scores)
# {"IF cold outreach THEN personalize...": 0.90, "IF writing to VP-level...": 0.75}
```

## Generate Rules

Turn patterns into persistent IF/THEN rules that your agent can use:

```python
new_rules = loops.rules.generate_rules()

for rule in new_rules:
    print(f"[{rule.confidence:.2f}] {rule.text}")
# [0.90] IF cold outreach THEN personalize the subject line — because 4/5 personalized emails succeeded
# [0.75] IF writing to VP-level THEN keep under 100 words — because 3/4 short emails got replies
```

Rules are automatically persisted and can be queried later:

```python
active_rules = loops.rules.active()  # Returns rules sorted by confidence
```

## Quality Gate

Before delivering agent output, validate it against learned rules and built-in checks:

```python
result = loops.check(output=agent_response, input=user_query)

if result.passed:
    deliver(agent_response)
else:
    print(result.score)       # 0.4 (below pass threshold)
    print(result.failures)    # ["Output is empty", "Violates rule: IF pricing THEN include disclaimer"]
    print(result.warnings)    # ["Output is shorter than recommended minimum"]
    regenerate()
```

The quality gate runs built-in checks (empty output, hallucination markers, length), rule-based checks (validates against learned "avoid" rules), and any custom check functions you provide. See the [API Reference](api-reference.md) for full configuration.

## Enhance a Prompt

The real payoff: inject everything the system has learned directly into your agent's prompt:

```python
base_prompt = "You are a sales outreach agent. Write compelling cold emails."

enhanced = loops.enhance_prompt(base_prompt)
print(enhanced)
```

Output:
```
You are a sales outreach agent. Write compelling cold emails.

## Decision Rules (learned from past performance)
- IF cold outreach THEN personalize the subject line [confidence: 0.90]
- IF writing to VP-level THEN keep under 100 words [confidence: 0.75]

## Conventions (self-learned behavioral patterns)
- Always reference the prospect's recent company news
- Use question-based subject lines for higher open rates
```

Your agent now benefits from everything it has learned, without you manually rewriting prompts.

## Full Working Example (20 Lines)

```python
from agentloops import AgentLoops

# Initialize (uses ANTHROPIC_API_KEY env var for reflection)
loops = AgentLoops("sales-outreach", agent_type="sales-sdr")

# Simulate a few agent runs
loops.track(
    input="Email the CTO at Stripe about our API monitoring tool",
    output="Subject: Your API latency numbers are impressive...",
    outcome="success",
)
loops.track(
    input="Email the VP Eng at Notion about our API monitoring tool",
    output="Subject: Check out our product...",
    outcome="failure",
)
loops.track(
    input="Email the Head of Platform at Figma about our API monitoring tool",
    output="Subject: Loved your talk at Config about plugin APIs...",
    outcome="success",
)

# Reflect on what's working
reflection = loops.reflect(last_n=3)
print(reflection.critique)

# Generate rules from patterns
rules = loops.rules.generate_rules()

# Enhance your agent's prompt with learned rules
enhanced = loops.enhance_prompt("You are a sales outreach agent.")
print(enhanced)

# Evolve conventions over time
changes = loops.conventions.evolve()

# Prune stale patterns
pruned = loops.forget(strategy="hybrid", max_age_days=21)
```

## Supabase Cloud Storage

For production deployments, use Supabase as the storage backend:

```bash
pip install agentloops[supabase]
```

```python
loops = AgentLoops(
    "my-agent",
    storage="supabase",
    supabase_url="https://your-project.supabase.co",
    supabase_key="your-anon-key",
    user_id="user-123",  # Optional: enables multi-tenant RLS
)
```

You can also set `AGENTLOOPS_SUPABASE_URL` and `AGENTLOOPS_SUPABASE_KEY` as environment variables instead of passing them directly. The database migration is included at `supabase/migrations/001_initial_schema.sql` in the repo.

## Framework Adapters

Drop-in callbacks for popular frameworks:

```python
# LangChain
from agentloops.adapters.langchain import AgentLoopsCallback

handler = AgentLoopsCallback(loops, outcome_fn=lambda run: "success" if run.success else "failure")
result = chain.invoke(prompt, config={"callbacks": [handler]})

# CrewAI
from agentloops.adapters.crewai import AgentLoopsCrewCallback

callback = AgentLoopsCrewCallback(loops, outcome_fn=lambda task: task.output.quality_score)
crew = Crew(agents=[agent], tasks=[task], callbacks=[callback])
```

Both adapters auto-track runs and errors. Pass a custom `outcome_fn` to define what "success" means for your agent.

## What Happens Under the Hood

When you call `track()`, AgentLoops:
1. Logs the run with its input, output, outcome, and any active rules that were applied
2. Stores it in `.agentloops/{agent_name}/runs.jsonl`

When you call `reflect()`:
1. Loads the last N runs
2. Sends them to Claude with the current rules and conventions
3. Gets back a structured critique with suggested new rules
4. Persists the reflection for historical tracking

When you call `enhance_prompt()`:
1. Loads all active rules (sorted by confidence)
2. Loads all active conventions
3. Appends them to your base prompt in a structured format

## Next Steps

- **[Core Concepts](concepts.md)** -- understand the 7 learning mechanisms in depth
- **[API Reference](api-reference.md)** -- every class and method documented
- **[Integration Guide](integrations.md)** -- use with LangChain, CrewAI, OpenAI, Anthropic
- **[Industry Use Cases](verticals.md)** -- see how AgentLoops applies to your domain
- **[Examples](https://github.com/mhollweck/agentloops/tree/main/examples)** -- working code for 10 verticals
