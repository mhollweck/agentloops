# MCP Server Integration

AgentLoops ships an MCP (Model Context Protocol) server that exposes memory + learning to any MCP-compatible agent — Claude Managed Agents, local claude CLI, or any framework that speaks MCP.

Same backend as the Python SDK. No code needed.

## Quick Setup

### 1. Install

```bash
pip install agentloops[mcp]
```

### 2. Add to your MCP config

**Claude Desktop / Claude Code (`~/.claude.json`):**

```json
{
  "mcpServers": {
    "agentloops": {
      "command": "python",
      "args": ["-m", "agentloops_mcp"],
      "env": {
        "ANTHROPIC_API_KEY": "sk-ant-...",
        "AGENTLOOPS_STORAGE_PATH": "/path/to/storage"
      }
    }
  }
}
```

**Claude Managed Agents (YAML):**

```yaml
name: support-agent
system_prompt: "You are a customer support agent..."
tools:
  - type: mcp
    command: python -m agentloops_mcp
    env:
      ANTHROPIC_API_KEY: sk-ant-...
```

That's it. Your agent now has access to self-learning.

## Available Tools

| Tool | Purpose | When to use |
|------|---------|-------------|
| `recall` | Get relevant rules for a situation | Before generating a response |
| `remember` | Store outcome and trigger learning | After completing a task |
| `reflect` | Analyze recent runs, extract patterns | Periodically or on-demand |
| `get_rules` | Get full ruleset for an agent | Bootstrapping or auditing |
| `check` | Quality gate on output | Before sending output to users |
| `enhance_prompt` | Inject rules into a prompt | When building system prompts |
| `list_agent_types` | Show available seed rule types | During setup |

## Tool Details

### recall

```
recall(query="customer asking about refund", agent_type="customer-support")
```

Returns IF/THEN rules relevant to the query. If no rules are learned yet, returns seed rules for the agent type.

### remember

```
remember(
  session_summary="Handled refund for new customer, escalated to billing",
  outcome="resolved",
  context="customer signed up 2 weeks ago, frustrated tone"
)
```

Tracks the outcome. When enough outcomes accumulate, auto-reflection triggers and extracts new rules.

### reflect

```
reflect(agent_name="support-agent", last_n=10)
```

Analyzes the last N runs and generates new IF/THEN rules. Requires an LLM API key (`ANTHROPIC_API_KEY` or `OPENAI_API_KEY`).

### get_rules

```
get_rules(agent_name="support-agent", agent_type="customer-support")
```

Returns all active rules sorted by confidence.

### check

```
check(output="Here's your refund...", agent_name="support-agent")
```

Validates output against quality gates and learned rules. Returns PASS/FAIL with details.

### enhance_prompt

```
enhance_prompt(base_prompt="You are a support agent.", agent_name="support-agent")
```

Returns the base prompt with all learned rules and conventions appended.

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `ANTHROPIC_API_KEY` | For reflection | Anthropic API key for LLM-powered learning |
| `OPENAI_API_KEY` | Alternative | OpenAI API key (if not using Anthropic) |
| `AGENTLOOPS_STORAGE_PATH` | No | Storage directory (defaults to system temp) |

## 10 Agent Types

Pre-seeded starter rules are available for:

- `sales-sdr` — Cold outreach, meeting booking
- `customer-support` — Ticket resolution, escalation
- `help-desk` — Guest services, upselling
- `content-creator` — Engagement, formats
- `code-generator` — Error handling, testing
- `recruiting` — Candidate outreach, screening
- `legal-review` — Contract analysis
- `insurance-claims` — Claims processing
- `devops-incident` — Incident response
- `ecommerce-rec` — Product recommendations

Pass `agent_type` to `recall()` or `get_rules()` to bootstrap with proven patterns.

## Namespaces

Use the `namespace` parameter to isolate agents:

```
recall(query="...", agent_name="support", namespace="acme-corp")
recall(query="...", agent_name="support", namespace="globex-inc")
```

Each namespace gets its own storage and rules. This maps to per-org isolation in the hosted version.

## SSE Transport (Remote)

For remote/web MCP clients, run with SSE transport:

```bash
python -m agentloops_mcp --transport sse --port 8080
```

## Pricing

The MCP server uses the same tiers as the Python SDK:

| Tier | Price | What you get |
|------|-------|-------------|
| Free | $0 | 3 agent types, static rules, local storage |
| Pro | $99/mo | Unlimited types, live rules from network, cloud storage |
| Team | $249/mo | Shared namespace across org's agents |
| Enterprise | Contact us | Benchmarking, dedicated support |
