# agentloops-mcp

npm wrapper for the [AgentLoops](https://agent-loops.com) MCP server. Self-learning for AI agents -- your agents have memory, now give them a brain.

## Prerequisites

```bash
pip install agentloops[mcp]
```

## Usage

```bash
npx agentloops-mcp
```

Or install globally:

```bash
npm install -g agentloops-mcp
agentloops-mcp
```

## Claude Desktop Configuration

Add this to your Claude Desktop MCP config (`claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "agentloops": {
      "command": "npx",
      "args": ["-y", "agentloops-mcp"],
      "env": {
        "AGENTLOOPS_API_KEY": "your-api-key"
      }
    }
  }
}
```

## Available Tools

| Tool | Description |
|------|-------------|
| `ingest_run` | Send an agent run (input/output/reflection) for learning |
| `get_rules` | Get learned IF/THEN rules for an agent type |
| `get_conventions` | Get self-learned conventions and patterns |
| `search_memory` | Semantic search across agent memories |
| `get_spike_alerts` | Get performance spike alerts for follow-up |
| `prune_stale` | Trigger selective forgetting of outdated learnings |
| `get_status` | Check learning system health and stats |

## Supported Agent Types

- `code-writer` -- generates and edits code
- `code-reviewer` -- reviews PRs and diffs
- `planner` -- breaks down tasks into steps
- `researcher` -- gathers and synthesizes information
- `qa-tester` -- writes and runs tests
- `devops` -- CI/CD, infra, deployments
- `data-analyst` -- queries data and builds reports
- `content-writer` -- writes articles, docs, copy
- `customer-support` -- handles tickets and questions
- `sdr` -- sales development outreach

## Links

- [Full documentation](https://agent-loops.com)
- [Python package on PyPI](https://pypi.org/project/agentloops/)
- [GitHub](https://github.com/mhollweck/agentloops)

## License

MIT
