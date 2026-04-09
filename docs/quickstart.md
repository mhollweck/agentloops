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

loops = AgentLoops("my-agent")
```

That's it. Zero config. AgentLoops creates a `.agentloops/my-agent/` directory in your working folder to store runs, rules, conventions, and reflections as JSON files.

### Configuration Options

```python
loops = AgentLoops(
    agent_name="my-agent",
    storage="file",                     # Default. Pass a BaseStorage instance for custom backends.
    storage_path=".agentloops",         # Where to store data. Defaults to ".agentloops".
    reflection_model="claude-sonnet-4-6",  # Model for reflection and rule generation.
    api_key=None,                       # Uses ANTHROPIC_API_KEY env var if not set.
)
```

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

# Initialize
loops = AgentLoops("sales-outreach")

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
