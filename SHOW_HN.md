# Show HN: AgentLoops -- Self-learning loops for AI agents (7 mechanisms, battle-tested)

**Repo:** https://github.com/mhollweck/agentloops
**Landing page:** https://agent-loops.com
**Install:** `pip install agentloops`

---

Here's something that's been bugging me: everyone's building AI agents, everyone's adding memory, but almost nobody's agents actually *learn*. Memory stores facts. Learning extracts patterns from those facts and changes behavior. Those are fundamentally different things.

I've been running 7 AI agents in production for months (content creation, analytics, strategy). Early on, I realized they kept making the same mistakes. They had memory -- they could recall past runs. But they never *improved*. I was manually rewriting prompts every week based on what I saw in the outputs. That felt wrong. The data was right there. The agent should be doing this itself.

So I built AgentLoops -- a Python library that adds self-learning to any AI agent. Add 2 lines of code. Your agent learns automatically.

```python
loops = AgentLoops("sales-outreach", agent_type="sales-sdr", api_key="al_xxx")
loops.track(input=task, output=result, outcome="meeting_booked")
```

That's the integration. Learning triggers automatically after enough outcomes -- reflection, rule extraction, convention evolution, contradiction resolution, and selective forgetting all happen behind the scenes. You call `enhance_prompt()` to inject what the system has learned into your agent's next run.

Under the hood it implements 7 learning mechanisms: self-reflection, spike detection for anomalies, quality gates, IF/THEN rule extraction, cross-evaluation, contradiction resolution, and selective forgetting. Agent types (like `sales-sdr`, `support-agent`, `content-writer`) come pre-seeded with rules from the domain so your agent doesn't start from zero. It's framework-agnostic -- works with LangChain, CrewAI, raw API calls, whatever. The mechanisms are inspired by Reflexion (Shinn et al.), cognitive memory architectures, and a lot of trial and error running this in production.

The key insight: there's a clear gap in the agent stack. Frameworks (LangChain, CrewAI) handle orchestration. Observability tools (LangSmith, Arize) handle monitoring. Memory systems (Mem0, Letta -- $140M+ in funding between them) handle storage. Evaluation tools (Braintrust, RAGAS) handle testing. But nothing sits between memory and evaluation to actually close the learning loop. AgentLoops fills that gap.

This is MIT licensed and I'd love feedback -- especially from people running agents in production who've felt the same pain. What learning mechanisms are you building manually today? What's missing from this approach?
