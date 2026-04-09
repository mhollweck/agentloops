# Show HN: AgentLoops – Self-learning for AI agents (pip install, works with anything)

I've been running 7 AI agents in production for months. Content strategy, analytics, opportunity research, performance tracking. They run every morning at 6:30am on a cron job on my MacBook. They have memory — they can recall past runs, read shared files, pass notes to each other in markdown. But for the longest time, they didn't learn. They'd make the same mistakes on run #200 that they made on run #1, and I'd manually rewrite prompts every week based on what I saw in the outputs. The data was right there. The pattern was obvious. The agent just couldn't see it.

So I built AgentLoops. It's a Python library that adds self-learning to any AI agent. Two lines of code:

```python
loops = AgentLoops("sales-outreach", agent_type="sales-sdr")
loops.track(input=task, output=result, outcome="meeting_booked")
```

That's the integration. Your agent now tracks its own outcomes, reflects on what worked, extracts IF/THEN rules from the data, and injects those rules into future prompts automatically. You never touch the prompt again.

**what it actually does under the hood**

There are 7 learning mechanisms and I'm not going to pretend I designed them from theory. I built them because I kept hitting the same problems running real agents:

1. Self-reflection — agent evaluates its own output after every run
2. Spike detection — catches anomalies (your agent suddenly went from 80% to 30%, what happened?)
3. Quality gates — validates output before it reaches users (caught my agent using a pattern its own rules said to avoid)
4. IF/THEN rule extraction — turns performance data into structured decision rules
5. Cross-evaluation — compares predictions vs actual outcomes
6. Contradiction resolution — two rules say opposite things, which one wins?
7. Selective forgetting — prunes stale patterns that stopped being true

The system also has a meta-learner that tracks which reflections produce impactful rules and adjusts its own reflection strategy over time. The learning gets sharper, not just the behavior.

**the part I'm most excited about**

Every agent on AgentLoops contributes anonymized rules back to a global pool. Company names, URLs, emails, dollar amounts — all stripped before anything leaves your machine. When 5+ independent agents discover the same pattern, it becomes available to everyone. A new user's sales agent on day 1 inherits proven rules from every sales agent on the platform. This is the Waze model — the free map is useful, the live traffic data is what makes it indispensable.

Right now the library ships with 10 pre-seeded agent types (sales, support, content, legal, recruiting, and more) so your agent starts smart instead of learning from scratch. The collective intelligence network is live and collecting data. The more people who use it, the better every agent gets.

**what it's not**

It's not a memory system. Mem0 and Letta (combined $140M+ in funding) store facts — "this user likes window seats." That's recall. AgentLoops sits on top of memory and extracts patterns — "guests who book suites AND request late checkout convert 3x on spa upsells." Memory gives you a notebook. Learning gives you judgment.

It's also not a framework. You don't rebuild your agent on AgentLoops. You add it to whatever you already have — LangChain, CrewAI, raw API calls, doesn't matter. `pip install agentloops`, add two lines, done.

Works with any LLM (Anthropic, OpenAI, or bring your own). MIT licensed. There's also an MCP server if you don't write Python.

Repo: https://github.com/mhollweck/agentloops
Install: `pip install agentloops`

Would love feedback from anyone running agents in production. What learning are you building manually today? What breaks when you try to make agents improve over time?
