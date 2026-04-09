# Show HN: AgentLoops -- Self-learning loops for AI agents (7 mechanisms, battle-tested)

**Repo:** https://github.com/mhollweck/agentloops
**Landing page:** https://agentloops.dev
**Install:** `pip install agentloops`

---

Here's something that's been bugging me: everyone's building AI agents, everyone's adding memory, but almost nobody's agents actually *learn*. Memory stores facts. Learning extracts patterns from those facts and changes behavior. Those are fundamentally different things.

I've been running 7 AI agents in production for months (content creation, analytics, strategy). Early on, I realized they kept making the same mistakes. They had memory -- they could recall past runs. But they never *improved*. I was manually rewriting prompts every week based on what I saw in the outputs. That felt wrong. The data was right there. The agent should be doing this itself.

So I built AgentLoops -- a Python library that adds self-learning to any AI agent. It implements 7 learning mechanisms: self-reflection after every run, spike detection for anomalies, quality gates before output, IF/THEN rule extraction from performance data, cross-evaluation of predictions vs outcomes, contradiction resolution when learned rules conflict, and selective forgetting to prune stale patterns. You add ~5 lines of code: `track()` your runs, `reflect()` on performance, `enhance_prompt()` with learned conventions. It's framework-agnostic -- works with LangChain, CrewAI, raw API calls, whatever. The mechanisms are inspired by Reflexion (Shinn et al.), cognitive memory architectures, and a lot of trial and error running this in production.

The key insight: there's a clear gap in the agent stack. Frameworks (LangChain, CrewAI) handle orchestration. Observability tools (LangSmith, Arize) handle monitoring. Memory systems (Mem0, Letta -- $140M+ in funding between them) handle storage. Evaluation tools (Braintrust, RAGAS) handle testing. But nothing sits between memory and evaluation to actually close the learning loop. AgentLoops fills that gap.

This is MIT licensed and I'd love feedback -- especially from people running agents in production who've felt the same pain. What learning mechanisms are you building manually today? What's missing from this approach?
