# AgentLoops MCP Server — Evaluation

## What this is

An MCP (Model Context Protocol) server that exposes AgentLoops memory + learning to any agent runtime — Claude Managed Agents, local claude CLI, or any other MCP-compatible framework. Same backend, new entry point.

## Why it matters

Current SDK requires `pip install agentloops` — targets Python devs. MCP targets everyone:
- Claude Managed Agents users configure via YAML, never write Python
- No-code agent builders
- JS/TS agent developers

This expands TAM without changing the product.

---

## How it works — end to end

### 1. Customer adds AgentLoops to their Managed Agent config

```yaml
name: support-agent
system_prompt: "You are a customer support agent for Acme Corp..."
tools:
  - type: mcp
    server: https://mcp.agent-loops.com
    api_key: al_live_xxx
```

That's the entire integration. No code, no SDK, no pip install.

### 2. Agent calls AgentLoops at runtime

```
User: "I want a refund, I signed up 2 weeks ago"

Agent → agentloops.recall("refund request new customer")
AgentLoops → returns: "IF customer mentions refund AND account < 30 days → escalate immediately. 
                        IF tone is frustrated → open with empathy before policy."

Agent uses rules → handles ticket correctly
```

### 3. Agent writes back after session

```
Session ends →
Agent → agentloops.remember({
  outcome: "resolved",
  tactic: "escalated to billing team",
  context: "new customer refund request"
})

AgentLoops extracts new rule → adds to org memory
Pro/Enterprise: contributes anonymized rule to collective intelligence network
```

### 4. Network effect kicks in (Pro+)

Next support agent at a *different company* on Pro tier gets rules learned from every support agent on the platform — without any of the raw customer data.

---

## MCP tool surface (what to expose)

```
recall(query, agent_type?, namespace?)
  → returns: relevant IF/THEN rules + recent learnings

remember(session_summary, outcome, context)
  → stores: new memory entry, triggers rule extraction

reflect(session_output)
  → auto-extracts: learnings without caller doing any structuring

get_rules(agent_type)
  → returns: full ruleset for this agent type (for bootstrapping)
```

---

## Real examples by agent type

### Customer support agent (Intercom, Zendesk)

```
recall("customer asking about downgrade")
→ "IF customer mentions competitor → offer retention discount before discussing downgrade.
   IF account > 12 months → flag as high-value, loop in CSM."

remember({outcome: "retained", tactic: "offered 20% discount", context: "competitor mention"})
→ rule extracted: "20% discount offer has 73% retention rate on competitor-mention cases"
```

### Sales SDR agent (11x, Artisan)

```
recall("cold outreach fintech CTO")
→ "IF title=CTO AND industry=fintech → lead with compliance angle, not feature list.
   IF no reply after 2 touches → switch channel to LinkedIn, not more email."

remember({outcome: "booked_meeting", tactic: "compliance angle + LinkedIn follow-up"})
→ feeds win/loss pattern back to collective intelligence
```

### Legal research agent (Harvey AI)

```
recall("contract review SaaS vendor agreement")
→ "IF indemnification clause is uncapped → always flag, never approve silently.
   IF governing law is Delaware → standard boilerplate, low risk."

remember({outcome: "flagged_for_review", clause: "uncapped indemnification"})
```

### Code review agent

```
recall("PR review Python async code")
→ "IF async function has no error handling → always comment, not just suggest.
   IF test coverage < 80% → block merge, don't just warn."
```

---

## Pricing fit (no change to existing tiers)

| Tier | Price | MCP behavior | Why upgrade |
|------|-------|-------------|-------------|
| Free | $0 | Static snapshot rules, 3 agent types | Smart on day 1, frozen |
| Pro | $99/mo | Live global rules updated daily | Rules improve as network grows |
| Team | $249/mo | Shared namespace across org's agents | All your agents share memory |
| Enterprise | Contact us | Full collective intelligence + benchmarking | Full network participant |

MCP is just a new SDK — same API keys, same backend, same tiers.

---

## Build plan

### Phase 1 — MVP (1-2 days)
- [x] `mcp/` directory in agentloops repo
- [x] MCP server in Python (FastMCP)
- [x] Exposes: `recall`, `remember`, `reflect`, `get_rules`, `check`, `enhance_prompt`, `list_agent_types`
- [x] Auth: API key passed via MCP config, validated against existing FastAPI backend
- [x] Deploy to `mcp.agent-loops.com`

### Phase 2 — Distribution (launch week)
- [x] Publish to npm as `agentloops-mcp` (npm-package/ ready, `npm publish` after launch)
- [x] Publish to PyPI as `agentloops[mcp]` extra (added to pyproject.toml)
- [ ] Add to Claude MCP directory (submit PR to modelcontextprotocol/servers after repo is public)
- [x] One-page integration guide in docs (docs/mcp.md)
- [x] Smithery.ai config (smithery.yaml in repo root)
- [ ] Submit to Glama.ai and PulseMCP directories (after repo is public)

### Phase 3 — Intelligence (post-launch)
- [x] `reflect()` tool — auto-extract learnings without structured input
- [ ] Agent-type fingerprinting — detect agent type from conversation context
- [x] Usage analytics per API key (server/mcp_sse.py — JSONL logging + rate limiting)

---

## Competitive watch

- **Mem0 MCP** — exists, ships raw memory storage. Position: "Mem0 remembers. AgentLoops learns."
- **Letta MCP** — doesn't exist yet. If they ship one, same counter-position as their SDK.
- **LangMem** — Google-backed, no collective intelligence, no structured rules.

---

## Open questions (resolved)

1. ~~Should `reflect()` be a separate paid tier feature or available on Pro?~~ **Available on all tiers.** Gate the collective intelligence, not the learning itself.
2. Rate limits per API key: Free 100 ops/min, Pro 1000 ops/min, Team/Enterprise unlimited.
3. Namespace isolation: per API key (maps to org). Agents within an org share memory. Team tier adds cross-agent shared namespace.
