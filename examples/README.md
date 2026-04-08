# AgentLoops Examples

10 complete, runnable examples showing how AgentLoops adds self-learning to AI agents across different industries. Each example demonstrates the full lifecycle: track runs, reflect, generate rules, evolve conventions, and forget stale patterns.

## How to Run

```bash
# Install agentloops first
pip install agentloops

# Run any example
python examples/sales_agent/main.py
```

Each example works out of the box with simulated data. For production use with automatic reflection and rule generation, set your `ANTHROPIC_API_KEY` environment variable.

## Examples

| # | Example | Industry | Description |
|---|---------|----------|-------------|
| 1 | [`sales_agent/main.py`](sales_agent/main.py) | B2B SaaS Sales | AI SDR that learns which subject lines and messaging convert for enterprise vs SMB prospects. |
| 2 | [`support_agent/main.py`](support_agent/main.py) | Customer Service | Support agent that learns SSO issues need different handling than password resets for enterprise customers. |
| 3 | [`content_agent/main.py`](content_agent/main.py) | Creator Economy | Content agent that learns which hooks, formats, and posting times drive engagement. |
| 4 | [`insurance_agent/main.py`](insurance_agent/main.py) | Insurance | Claims processor that learns fraud patterns like body shop claim clustering and evolving schemes. |
| 5 | [`coding_agent/main.py`](coding_agent/main.py) | Developer Tools | Code assistant that learns project-specific patterns (Zustand not Redux, Tailwind not styled-components). |
| 6 | [`recruiting_agent/main.py`](recruiting_agent/main.py) | HR / Recruiting | Candidate screener that learns what hiring managers actually care about vs stated job requirements. |
| 7 | [`legal_agent/main.py`](legal_agent/main.py) | Legal Tech | Contract reviewer that learns clause enforceability by jurisdiction and propagates attorney corrections. |
| 8 | [`devops_agent/main.py`](devops_agent/main.py) | SRE / DevOps | Incident responder that learns alert-to-root-cause mappings to reduce MTTR from 45 min to 5 min. |
| 9 | [`ecommerce_agent/main.py`](ecommerce_agent/main.py) | E-Commerce | Product recommender that learns seasonal patterns and which recs lead to returns (negative signal). |
| 10 | [`compliance_agent/main.py`](compliance_agent/main.py) | Financial Services | Compliance monitor that reduces false positive rate from 95% to 20% while catching real violations. |

## What Each Example Demonstrates

Every example follows the same lifecycle:

1. **Track** -- Log agent runs with realistic inputs, outputs, and outcomes
2. **Reflect** -- Analyze patterns in the tracked runs (simulated; uses Claude API in production)
3. **Rules** -- Generate IF/THEN decision rules from performance data
4. **Conventions** -- Build higher-level behavioral patterns the agent follows
5. **Enhance** -- Inject learned rules and conventions into the agent's prompt
6. **Forget** -- Prune stale rules and conventions to keep memory fresh

## Adapting for Your Use Case

Each example is designed to be copy-pasted and modified:

1. Change the `agent_name` to match your agent
2. Replace the sample runs with your agent's actual inputs/outputs/outcomes
3. Replace `loops.rules.add_rule()` calls with `loops.reflect()` and `loops.rules.generate_rules()` for automatic rule discovery
4. Replace `loops.conventions.add()` with `loops.conventions.evolve()` for automatic convention evolution
5. Call `loops.enhance_prompt(base_prompt)` before every agent invocation to inject learned rules

```python
from agentloops import AgentLoops

loops = AgentLoops("my-agent")

# In your agent loop:
enhanced_prompt = loops.enhance_prompt(base_prompt)  # Inject learned rules
result = call_your_agent(enhanced_prompt, user_input)  # Your agent runs
loops.track(input=user_input, output=result, outcome=measure_outcome(result))  # Track

# Periodically:
reflection = loops.reflect(last_n=10)       # Analyze recent performance
new_rules = loops.rules.generate_rules()    # Discover new rules
changes = loops.conventions.evolve()        # Evolve conventions
loops.forget(strategy="hybrid")             # Prune stale memory
```
