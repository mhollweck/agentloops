# AgentLoops Integration Guide (for AI coding assistants)

This file helps AI coding assistants (Claude Code, Cursor, Copilot, etc.) integrate AgentLoops correctly.

## What AgentLoops Does

AgentLoops adds self-learning to AI agents. It tracks outcomes, extracts IF/THEN rules from performance data, and injects those rules back into agent prompts automatically. Agents improve without manual prompt rewriting.

## Installation

```bash
pip install agentloops
```

## Integration Pattern (3 lines)

```python
from agentloops import AgentLoops

# Initialize with an agent type for starter rules
loops = AgentLoops("agent-name", agent_type="sales-sdr")

# Track every run
loops.track(input=user_input, output=agent_output, outcome="success")

# Enhance prompts with learned rules
enhanced_prompt = loops.enhance_prompt(base_system_prompt)
```

## Available Agent Types

`sales-sdr`, `customer-support`, `help-desk`, `content-creator`, `code-generator`, `recruiting`, `legal-review`, `insurance-claims`, `devops-incident`, `ecommerce-rec`

## Key Methods

- `loops.track(input, output, outcome)` — Log a run. Outcome is any string: "success", "failure", "meeting_booked", "resolved", etc.
- `loops.enhance_prompt(base_prompt)` — Returns the prompt with learned IF/THEN rules appended.
- `loops.reflect(last_n=10)` — Manually trigger reflection on recent runs. Requires ANTHROPIC_API_KEY or OPENAI_API_KEY env var.
- `loops.check(output=text)` — Quality gate: validates output before sending to users.
- `loops.forget()` — Prune stale rules older than 21 days.
- `loops.rules.active()` — Get all active IF/THEN rules.
- `loops.conventions.get_conventions()` — Get behavioral conventions.

## Integration Examples

### With a LangChain chain
```python
from agentloops.adapters.langchain import AgentLoopsCallback

handler = AgentLoopsCallback(loops, outcome_fn=lambda run: "success" if run.success else "failure")
result = chain.invoke(prompt, config={"callbacks": [handler]})
```

### With a CrewAI crew
```python
from agentloops.adapters.crewai import AgentLoopsCrewCallback

callback = AgentLoopsCrewCallback(loops, outcome_fn=lambda task: task.output.quality_score)
crew = Crew(agents=[agent], tasks=[task], callbacks=[callback])
```

### With raw API calls
```python
response = client.chat.completions.create(
    messages=[{"role": "system", "content": loops.enhance_prompt(system_prompt)}]
)
loops.track(input=user_msg, output=response.choices[0].message.content, outcome=metric)
```

## Multi-LLM Support

```python
# OpenAI
loops = AgentLoops("my-agent", llm_provider="openai")

# Custom LLM (Ollama, Groq, etc.)
loops = AgentLoops("my-agent", llm_provider="custom", llm_fn=my_callable)
```

## Outcome Configuration

```python
from agentloops import OutcomeConfig

# Binary (default)
loops = AgentLoops("my-agent", outcome=OutcomeConfig.binary())

# Categorical
loops = AgentLoops("my-agent", outcome=OutcomeConfig.categorical(["booked", "replied", "ignored"]))

# Numeric
loops = AgentLoops("my-agent", outcome=OutcomeConfig.numeric(goal="minimize"))
```

## MCP Server (no code needed)

```bash
pip install agentloops[mcp]
```

Add to Claude Desktop config:
```json
{
  "mcpServers": {
    "agentloops": {
      "command": "python",
      "args": ["-m", "agentloops_mcp"],
      "env": { "ANTHROPIC_API_KEY": "sk-ant-..." }
    }
  }
}
```

## Common Mistakes to Avoid

- Don't call `reflect()` without an LLM API key set — it needs ANTHROPIC_API_KEY or OPENAI_API_KEY
- Don't skip `agent_type` — without it, the agent starts with zero rules instead of proven seed rules
- Don't forget to call `enhance_prompt()` — tracking alone doesn't change behavior, you need to inject the rules
- Storage defaults to `.agentloops/` in the current directory — add it to .gitignore
