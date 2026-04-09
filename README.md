<p align="center">
  <h1 align="center">AgentLoops</h1>
  <p align="center"><strong>Your agents have memory. Now give them a brain.</strong></p>
</p>

<p align="center">
  <a href="https://pypi.org/project/agentloops/"><img src="https://img.shields.io/pypi/v/agentloops?color=blue" alt="PyPI"></a>
  <a href="https://pypi.org/project/agentloops/"><img src="https://img.shields.io/pypi/dm/agentloops" alt="Downloads"></a>
  <a href="https://github.com/mhollweck/agentloops/stargazers"><img src="https://img.shields.io/github/stars/mhollweck/agentloops?style=social" alt="Stars"></a>
  <a href="https://github.com/mhollweck/agentloops/blob/main/LICENSE"><img src="https://img.shields.io/badge/license-MIT-green" alt="License"></a>
</p>

---

## The Missing Layer

Every AI agent stack has memory. None of them learn.

```
Frameworks    Observability    Memory          ???         Evaluation
(LangChain,   (LangSmith,     (Mem0, Letta)              (Braintrust,
 CrewAI)       Arize)          $140M+ funded               RAGAS)
    │              │               │             │              │
    ▼              ▼               ▼             ▼              ▼
 ┌──────┐    ┌──────────┐    ┌─────────┐   ┌─────────┐   ┌──────────┐
 │Build │───▶│ Observe  │───▶│Remember │───▶│ LEARN  │───▶│Evaluate │
 │agents│    │  runs    │    │  facts  │   │patterns │   │ quality │
 └──────┘    └──────────┘    └─────────┘   └─────────┘   └──────────┘
                                                 ▲
                                                 │
                                          AgentLoops fills
                                            this gap
```

Memory stores what happened. **AgentLoops extracts why it worked** and feeds that back into your agents automatically.

## See It Work (30 seconds, no API key needed)

```bash
pip install agentloops
python -c "import urllib.request; exec(urllib.request.urlopen('https://raw.githubusercontent.com/mhollweck/agentloops/main/examples/quickstart/main.py').read())"
```

<details>
<summary><strong>Output: watch your agent go from 62% → 100%</strong></summary>

```
  ╔══════════════════════════════════════════════════════════╗
  ║     AgentLoops — Watch Your Agent Learn in Real Time    ║
  ╚══════════════════════════════════════════════════════════╝

  PHASE 1: Agent runs without learning
  ──────────────────────────────────────────────────────
    ✓ meeting_booked       │ VP Eng at Stripe — personalized technical email
    ✓ replied              │ CTO at startup — case study approach
    ✗ no_reply             │ Director at Shopify — listicle subject
    ✓ meeting_booked       │ VP Eng at Datadog — question about their product
    ✓ meeting_booked       │ Head of Eng at SaaS — congratulated on launch
    ✗ unsubscribed         │ CIO at Wells Fargo — listicle subject
    ✓ meeting_booked       │ VP Eng at Notion — observed their API latency
    ✗ no_reply             │ CTO at tiny startup — generic advice

  Success rate: 62%       Active rules: 0

  LEARNING: Extracting rules from performance data...
  ──────────────────────────────────────────────────────
    [92%] IF prospect is VP Engineering THEN lead with technical observation
    [85%] IF subject is listicle style THEN avoid for enterprise
    [75%] IF prospect had a recent public event THEN reference it

  PHASE 2: Agent runs WITH learned rules
  ──────────────────────────────────────────────────────
    ✓ meeting_booked       │ VP Eng at Cloudflare — observed Workers API latency
    ✓ meeting_booked       │ VP Eng at Twilio — noted Voice API incidents
    ✓ replied              │ CTO at 30-person SaaS — ROI case study
    ✓ meeting_booked       │ VP Eng at Figma — praised real-time collab speed

  Success rate: 100%

  QUALITY GATE: Checking output before sending...
    Personalized email: PASS ✓ (score: 1.0)
    Listicle email:     FAIL ✗ ⚠ Output uses listicle pattern which rule says to avoid

  ╔══════════════════════════════════════════════════════════╗
  ║  RESULT: 62% → 100% success rate                       ║
  ║  Your agent just learned from its own performance.      ║
  ╚══════════════════════════════════════════════════════════╝
```

</details>

## Quick Start

```bash
pip install agentloops
```

```python
from agentloops import AgentLoops

# Uses ANTHROPIC_API_KEY env var for reflection
loops = AgentLoops("sales-outreach", agent_type="sales-sdr")

# Track every agent run — learning happens automatically
loops.track(input=task, output=result, outcome="meeting_booked")

# Inject learned rules into your prompt
enhanced_prompt = loops.enhance_prompt(base_prompt)
```

That's it. Two methods. Your agent now learns from every run.

When you pass `agent_type="sales-sdr"`, AgentLoops loads pre-seeded IF/THEN rules for that agent type -- so your agent starts smart on day one instead of learning from scratch. 10 agent types available out of the box (sales, support, content, code, recruiting, legal, and more).

Learning triggers automatically after enough outcomes. You can also call `reflect()`, `evolve()`, and `forget()` manually for fine-grained control.

### Multi-LLM Support

AgentLoops works with Anthropic (default), OpenAI, or any custom LLM:

```python
# OpenAI
loops = AgentLoops("my-agent", llm_provider="openai", api_key="sk-...")

# Custom LLM (local Ollama, Groq, Mistral, etc.)
loops = AgentLoops("my-agent", llm_provider="custom", llm_fn=my_llm_callable)
```

## Collective Intelligence — Your Agent Starts Smart

> **Shipping now:** Pre-seeded starter rules for 10 agent types. **Coming soon:** Live cross-customer intelligence network.

Every agent on AgentLoops learns from its own runs. The vision: aggregate anonymized learnings across ALL agents of the same type into a **global intelligence pool**. Today, your agent starts with curated starter rules for its type. Soon, it'll inherit live proven rules from every agent on the platform.

```
More customers → More outcome data → Better global rules
  → New customers start smarter → Better results → More customers
```

This is the Waze model. The free map is great. The live traffic data is what makes it indispensable.

**What's available now:** 10 agent types with curated starter rules (`sales-sdr`, `customer-support`, `content-creator`, and 7 more). Your agent starts smart on day 1 instead of learning from scratch.

## Meta-Learning — The Learning Engine Learns Too

AgentLoops doesn't just improve your agent's behavior -- it improves the quality of its own learning over time. The meta-learner tracks which reflections produce impactful rules, which rule formats (evidence-backed vs not, "avoid" vs "do", confidence levels) correlate with positive outcomes, and generates meta-rules that get injected into future reflection prompts. The result: your agent's learning gets sharper with every cycle, not just its behavior.

```python
# Access meta-learning insights
impacts = loops.meta_learner.get_rule_impacts()
patterns = loops.meta_learner.get_best_rule_patterns()
meta_rules = loops.meta_learner.get_meta_rules()
```

When collective intelligence is active, meta-learnings are shared too -- new customers don't just get starter rules, they get starter *learning strategies*.

**What's coming (the network):** Every user contributes anonymized learnings. You pay for freshness and depth:

| Tier | Contributes? | Intelligence |
|------|-------------|-------------|
| **Free** | Yes (anonymized) | Curated starter rules bundled with the package |
| **Pro** | Yes | Live global rules updated from the network |
| **Enterprise** | Yes | Live rules + benchmarking + custom filters |

No other tool does this. Mem0 stores facts. Letta learns inside their platform. **AgentLoops learns across the entire ecosystem.**

## Before vs After

**Without AgentLoops** -- your agent makes the same mistakes forever:

```python
# Day 1: Agent sends cold email, gets ignored
# Day 30: Agent sends the same cold email, gets ignored
# Day 90: Agent sends the same cold email, gets ignored
# You manually rewrite the prompt. Again.
```

**With AgentLoops** -- your agent evolves:

```python
# Day 1: Agent sends cold email, gets ignored
# Day 2-9: Agent keeps tracking outcomes...
# Day 10: Auto-reflection triggers → "Emails without personalization get 0% reply rate"
# Day 11: enhance_prompt() injects: "IF cold outreach THEN personalize first line"
# Day 50: Auto-evolution → Convention: "Always reference prospect's recent work"
# Day 51: Agent books meetings. You never touched the prompt.
```

## The 7 Mechanisms

AgentLoops implements seven learning mechanisms, inspired by [Reflexion](https://arxiv.org/abs/2303.11366), cognitive memory architectures, and months of production use.

| # | Mechanism | What it does | When it runs |
|---|-----------|-------------|--------------|
| 1 | **Self-Reflection** | Agent evaluates its own output, writes patterns to conventions | After every run |
| 2 | **Spike Detection** | Detects performance anomalies, triggers follow-up | Continuous |
| 3 | **Quality Gate** | Pre-flight validation via `loops.check()` — built-in + rule-based + custom checks | Before output |
| 4 | **Decision Rules** | Extracts IF/THEN rules from performance data | Weekly |
| 5 | **Cross-Evaluation** | Compares predictions vs actual outcomes | Weekly |
| 6 | **Contradiction Resolution** | Detects and resolves conflicting learned rules | Weekly |
| 7 | **Selective Forgetting** | Prunes stale patterns that no longer apply | Daily |

These aren't theoretical. They've been running in production across 7 agents processing real data for months.

## Multi-Outcome System

Not every agent has a simple pass/fail outcome. AgentLoops supports rich outcome definitions so learning works for any metric:

```python
from agentloops import AgentLoops, OutcomeConfig, MetricDef

# Binary (default) — success or failure
loops = AgentLoops("my-agent", outcome=OutcomeConfig.binary())

# Categorical — multiple outcome values
loops = AgentLoops("my-agent", outcome=OutcomeConfig.categorical(["booked", "replied", "ignored"]))

# Numeric — scored outcomes with a goal direction
loops = AgentLoops("my-agent", outcome=OutcomeConfig.numeric(goal="minimize"))

# Multi-metric — weighted composite scoring
loops = AgentLoops("my-agent", outcome=OutcomeConfig(metrics=[
    MetricDef("booking_rate", "categorical", weight=3.0, success_values=["booked"]),
    MetricDef("latency", "duration", weight=1.0, target_value=500),
]))

# Score a run with multiple metrics
score = loops.outcome.score({"booking_rate": "booked", "latency": 320})
```

The outcome config tells the reflection and rule engines what "good" looks like, so they generate rules that actually optimize for your goals.

## Quality Gates

Validate agent output before it reaches users:

```python
result = loops.check(output=agent_response, input=user_query)

if result.passed:
    deliver(agent_response)
else:
    print(result.failures)  # ["Output contains hallucination markers", "Violates rule: IF pricing question THEN include disclaimer"]
    regenerate()
```

Built-in checks catch empty outputs, hallucination markers, and length violations. Rule-based checks validate output against learned "avoid" rules. You can also pass custom check functions. See the [API Reference](https://agent-loops.com/docs/api) for full configuration.

## How It Works

```
                    ┌─────────────────┐
                    │   Your Agent    │
                    └────────┬────────┘
                             │
                    loops.track(input, output, outcome)
                             │
                             ▼
              ┌──────────────────────────────┐
              │        AgentLoops Core       │
              │                              │
              │  ┌────────┐  ┌────────────┐  │
              │  │Reflect │  │Quality Gate│  │
              │  └───┬────┘  └─────┬──────┘  │
              │      │             │         │
              │      ▼             ▼         │
              │  ┌─────────────────────┐     │
              │  │    Conventions DB   │     │
              │  │  (IF/THEN rules,   │     │
              │  │   patterns, spikes) │     │
              │  └─────────┬───────────┘     │
              │            │                 │
              │  ┌─────────▼───────────┐     │
              │  │ Evolve / Forget /   │     │
              │  │ Resolve Conflicts   │     │
              │  └─────────────────────┘     │
              └──────────────┬───────────────┘
                             │
                    loops.enhance_prompt(base)
                             │
                             ▼
                    ┌─────────────────┐
                    │  Enhanced Agent  │
                    │  (with learned   │
                    │   conventions)   │
                    └─────────────────┘
```

## Comparison

| Feature | AgentLoops | Mem0 | Letta | DIY |
|---------|-----------|------|-------|-----|
| Memory storage | -- | Yes | Yes | Yes |
| Self-reflection | Yes | -- | -- | Manual |
| Automatic rule extraction | Yes | -- | -- | Manual |
| Spike detection | Yes | -- | -- | Manual |
| Contradiction resolution | Yes | -- | -- | No |
| Selective forgetting | Yes | -- | Partial | No |
| Prompt enhancement | Yes | -- | -- | Manual |
| Convention evolution | Yes | -- | -- | No |
| Framework-agnostic | Yes | Yes | No | Yes |
| Lines of code to add | ~5 | ~10 | ~50 | ~500 |
| Focus | **Learning** | Storage | Stateful agents | -- |

AgentLoops is not a replacement for memory systems. It's the layer that sits on top of them and actually *learns*.

## Framework Agnostic

Works with any agent framework. Or no framework at all.

```python
# With LangChain — drop-in callback handler
from agentloops.adapters.langchain import AgentLoopsCallback

handler = AgentLoopsCallback(loops, outcome_fn=lambda run: "success" if run.success else "failure")
result = chain.invoke(prompt, config={"callbacks": [handler]})
# Automatically tracks chain runs, errors, and outcomes

# With CrewAI — callback for tasks and crews
from agentloops.adapters.crewai import AgentLoopsCrewCallback

callback = AgentLoopsCrewCallback(loops, outcome_fn=lambda task: task.output.quality_score)
crew = Crew(agents=[agent], tasks=[task], callbacks=[callback])
# Automatically tracks task completions and crew results

# With raw OpenAI/Anthropic calls
response = client.chat.completions.create(
    messages=[{"role": "system", "content": loops.enhance_prompt(system_prompt)}]
)
loops.track(input=user_msg, output=response, outcome=metric)
```

## Use Cases

- **Sales agents** that learn which outreach patterns book meetings
- **Support agents** that learn which responses resolve tickets faster
- **Help desk agents** that learn guest preferences, upsell timing, and escalation patterns (hotels, airlines, SaaS)
- **Content agents** that learn which formats drive engagement
- **Coding agents** that learn which patterns produce fewer bugs
- **Research agents** that learn which sources yield better insights

If your agent runs more than once, it should be learning.

### Why Self-Learning Matters (Not Just Memory)

Memory systems (Mem0, Letta, Zep) store facts: *"this user prefers window seats"* or *"last order was a latte."* That's recall — the agent remembers what happened.

**Learning is fundamentally different.** Learning means the agent changes its *behavior* based on outcomes:

| | Memory | Learning |
|---|--------|---------|
| Hotel help desk | "Guest in 412 asked for extra towels last time" | "Guests who book suites AND request late checkout convert 3x on spa upsells — offer proactively" |
| Sales outreach | "Last email to this prospect was June 3" | "CTOs at Series B companies respond 4x more to technical deep-dives than ROI pitches" |
| Support tickets | "Customer had billing issue last month" | "Billing tickets mentioning 'cancel' resolve 60% faster when you lead with empathy + immediate credit" |

Memory gives you a notebook. Learning gives you judgment.

Without learning, your agent makes the same mistakes on run #1,000 as run #1. It remembers more *facts* but never gets *smarter*. It's the difference between a new hire who takes great notes and a senior employee who has developed intuition from thousands of reps.

AgentLoops doesn't replace memory — it sits on top of it. Memory stores what happened. **AgentLoops learns what to do about it.**

## Documentation

- [Getting Started](https://agent-loops.com/docs/quickstart) -- up and running in 5 minutes
- [7 Mechanisms Deep Dive](https://agent-loops.com/docs/mechanisms) -- how each mechanism works
- [Examples](https://github.com/mhollweck/agentloops/tree/main/examples) -- real-world usage patterns
- [API Reference](https://agent-loops.com/docs/api) -- full API documentation

## Community

- [Discord](https://discord.gg/mwQZQCRp) -- questions, showcase, feedback
- [GitHub Issues](https://github.com/mhollweck/agentloops/issues) -- bugs and feature requests
- [Twitter/X](https://x.com/mariahollweck) -- updates and announcements

## Contributing

Contributions welcome. See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License

MIT

---

<p align="center">
  Built by <a href="https://x.com/mariahollweck">Maria Hollweck</a> at <a href="https://asobi-labs.com">Asobi Labs</a>
</p>
