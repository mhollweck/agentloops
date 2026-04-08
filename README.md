<p align="center">
  <h1 align="center">AgentLoops</h1>
  <p align="center"><strong>Your agents have memory. Now give them a brain.</strong></p>
</p>

<p align="center">
  <a href="https://pypi.org/project/agentloops/"><img src="https://img.shields.io/pypi/v/agentloops?color=blue" alt="PyPI"></a>
  <a href="https://pypi.org/project/agentloops/"><img src="https://img.shields.io/pypi/dm/agentloops" alt="Downloads"></a>
  <a href="https://github.com/asobi-labs/agentloops/stargazers"><img src="https://img.shields.io/github/stars/asobi-labs/agentloops?style=social" alt="Stars"></a>
  <a href="https://github.com/asobi-labs/agentloops/blob/main/LICENSE"><img src="https://img.shields.io/badge/license-MIT-green" alt="License"></a>
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

## Quick Start

```bash
pip install agentloops
```

```python
from agentloops import AgentLoops

loops = AgentLoops("sales-outreach")

# Track every agent run
loops.track(input=task, output=result, outcome="meeting_booked")

# Agent reflects on what's working
reflection = loops.reflect()

# Inject learned rules into your prompt
enhanced_prompt = loops.enhance_prompt(base_prompt)

# Evolve conventions weekly
loops.conventions.evolve()

# Forget stale patterns
loops.forget(max_age_days=21)
```

That's it. Five methods. Your agent now learns from every run.

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
# Day 2: reflect() → "Emails without personalization get 0% reply rate"
# Day 3: enhance_prompt() injects: "IF cold outreach THEN personalize first line"
# Day 7: evolve() → Convention: "Always reference prospect's recent work"
# Day 30: Agent books mass meetings. You didn't touch the prompt once.
```

## The 7 Mechanisms

AgentLoops implements seven learning mechanisms, inspired by [Reflexion](https://arxiv.org/abs/2303.11366), cognitive memory architectures, and months of production use.

| # | Mechanism | What it does | When it runs |
|---|-----------|-------------|--------------|
| 1 | **Self-Reflection** | Agent evaluates its own output, writes patterns to conventions | After every run |
| 2 | **Spike Detection** | Detects performance anomalies, triggers follow-up | Continuous |
| 3 | **Quality Gate** | Scores outputs on configurable criteria before approval | Before output |
| 4 | **Decision Rules** | Extracts IF/THEN rules from performance data | Weekly |
| 5 | **Cross-Evaluation** | Compares predictions vs actual outcomes | Weekly |
| 6 | **Contradiction Resolution** | Detects and resolves conflicting learned rules | Weekly |
| 7 | **Selective Forgetting** | Prunes stale patterns that no longer apply | Daily |

These aren't theoretical. They've been running in production across 7 agents processing real data for months.

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
# With LangChain
result = chain.invoke(loops.enhance_prompt(prompt))
loops.track(input=prompt, output=result, outcome=outcome)

# With CrewAI
agent = Agent(role="researcher", goal=loops.enhance_prompt(base_goal))

# With raw OpenAI/Anthropic calls
response = client.chat.completions.create(
    messages=[{"role": "system", "content": loops.enhance_prompt(system_prompt)}]
)
loops.track(input=user_msg, output=response, outcome=metric)
```

## Use Cases

- **Sales agents** that learn which outreach patterns book meetings
- **Support agents** that learn which responses resolve tickets faster
- **Content agents** that learn which formats drive engagement
- **Coding agents** that learn which patterns produce fewer bugs
- **Research agents** that learn which sources yield better insights

If your agent runs more than once, it should be learning.

## Documentation

- [Getting Started](https://agentloops.dev/docs/quickstart) -- up and running in 5 minutes
- [7 Mechanisms Deep Dive](https://agentloops.dev/docs/mechanisms) -- how each mechanism works
- [Examples](https://github.com/asobi-labs/agentloops/tree/main/examples) -- real-world usage patterns
- [API Reference](https://agentloops.dev/docs/api) -- full API documentation

## Community

- [Discord](https://discord.gg/agentloops) -- questions, showcase, feedback
- [GitHub Issues](https://github.com/asobi-labs/agentloops/issues) -- bugs and feature requests
- [Twitter/X](https://x.com/mariahollweck) -- updates and announcements

## Contributing

Contributions welcome. See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License

MIT

---

<p align="center">
  Built by <a href="https://x.com/mariahollweck">Maria Hollweck</a> at <a href="https://asobi-labs.com">Asobi Labs</a>
</p>
