# Framework Integration Guide

AgentLoops works with any agent framework -- or no framework at all. This guide shows complete working examples for the most popular setups.

The pattern is always the same:
1. Create an `AgentLoops` instance
2. Enhance your prompt with `enhance_prompt()`
3. Run your agent
4. Track the outcome with `track()`
5. Periodically reflect, generate rules, and evolve

---

## Raw Anthropic SDK

```python
import anthropic
from agentloops import AgentLoops

# Initialize
client = anthropic.Anthropic()
loops = AgentLoops("support-agent")

def run_agent(user_message: str) -> str:
    # Enhance the system prompt with learned rules
    base_prompt = "You are a customer support agent. Resolve issues efficiently."
    system_prompt = loops.enhance_prompt(base_prompt)
    
    # Call Claude
    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1024,
        system=system_prompt,
        messages=[{"role": "user", "content": user_message}],
    )
    
    output = response.content[0].text
    return output

def process_ticket(ticket: str, resolved: bool):
    """Process a support ticket and track the outcome."""
    output = run_agent(ticket)
    
    # Track the run
    loops.track(
        input=ticket,
        output=output,
        outcome="success" if resolved else "failure",
        metadata={"channel": "email", "category": "billing"},
    )
    
    return output

# After processing many tickets, reflect and improve
def nightly_learning():
    # Reflect on recent performance
    reflection = loops.reflect(last_n=20)
    print(f"Analysis: {reflection.critique}")
    
    # Generate new rules from patterns
    new_rules = loops.rules.generate_rules()
    print(f"New rules discovered: {len(new_rules)}")
    
    # Evolve conventions
    changes = loops.conventions.evolve()
    
    # Prune stale patterns
    loops.forget(strategy="hybrid", max_age_days=21)
```

---

## Raw OpenAI SDK

AgentLoops supports OpenAI as a first-class LLM provider. You can use OpenAI for your agent's LLM calls AND for AgentLoops' reflection/rule generation:

```python
from openai import OpenAI
from agentloops import AgentLoops

# Initialize — use OpenAI for both the agent and AgentLoops reflection
client = OpenAI()
loops = AgentLoops("sales-agent", llm_provider="openai")

def run_agent(prospect_info: str) -> str:
    # Enhance with learned rules
    base_prompt = "You are an AI SDR. Write personalized outreach emails."
    system_prompt = loops.enhance_prompt(base_prompt)
    
    # Call GPT
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prospect_info},
        ],
    )
    
    output = response.choices[0].message.content
    return output

def send_outreach(prospect: dict) -> dict:
    """Send an outreach email and track the result."""
    prompt = f"Write a cold email to {prospect['name']}, {prospect['title']} at {prospect['company']}."
    email = run_agent(prompt)
    
    # Send email via your ESP...
    # Later, when you know the outcome:
    return {"email": email, "prospect": prospect}

def record_outcome(prospect: dict, email: str, replied: bool, booked: bool):
    """Called when we know the outcome (reply, meeting booked, etc.)."""
    if booked:
        outcome = "meeting_booked"
    elif replied:
        outcome = "replied"
    else:
        outcome = "no_reply"
    
    loops.track(
        input=f"Outreach to {prospect['name']} at {prospect['company']}",
        output=email,
        outcome=outcome,
        metadata={
            "title": prospect["title"],
            "company_size": prospect.get("company_size"),
            "industry": prospect.get("industry"),
        },
    )

# Weekly learning cycle
def weekly_review():
    reflection = loops.reflect(last_n=50)
    rules = loops.rules.generate_rules()
    loops.conventions.evolve()
    loops.forget(max_age_days=21)
```

---

## LangChain

AgentLoops ships a built-in LangChain callback adapter that auto-tracks chain runs and errors:

```python
from langchain_anthropic import ChatAnthropic
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from agentloops import AgentLoops
from agentloops.adapters.langchain import AgentLoopsCallback

# Initialize
loops = AgentLoops("research-agent")
llm = ChatAnthropic(model="claude-sonnet-4-6")

# Create callback — automatically tracks chain runs
callback = AgentLoopsCallback(loops, outcome_fn=lambda run: "success" if run.success else "failure")

def create_chain():
    """Create a LangChain chain with learned rules injected."""
    base_prompt = "You are a research analyst. Summarize market trends with data."
    enhanced = loops.enhance_prompt(base_prompt)
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", enhanced),
        ("user", "{query}"),
    ])
    
    chain = prompt | llm | StrOutputParser()
    return chain

# Usage — callback auto-tracks every invocation
chain = create_chain()
result = chain.invoke({"query": "AI agent market size 2025"}, config={"callbacks": [callback]})
```

Install the LangChain adapter: `pip install agentloops[langchain]`

You can still track manually if you need more control over outcomes:

```python
def track_research(query: str, result: str, quality_score: float):
    loops.track(
        input=query,
        output=result,
        outcome=str(quality_score),  # e.g., "4.5" out of 5
        metadata={"source": "langchain", "model": "claude-sonnet-4-6"},
    )
```

---

## CrewAI

AgentLoops ships a built-in CrewAI callback adapter that tracks task and crew completions:

```python
from crewai import Agent, Task, Crew
from agentloops import AgentLoops
from agentloops.adapters.crewai import AgentLoopsCrewCallback

# Initialize AgentLoops
loops = AgentLoops("crew-outreach")

# Create callback — automatically tracks task completions
callback = AgentLoopsCrewCallback(loops, outcome_fn=lambda task: task.output.quality_score)

# Create agents with enhanced prompts
researcher = Agent(
    role="Sales Researcher",
    goal=loops.enhance_prompt(
        "Find detailed information about prospects including recent news, "
        "company updates, and personal interests."
    ),
    backstory="You are an expert at finding actionable intelligence on sales prospects.",
    verbose=True,
)

writer = Agent(
    role="Email Writer",
    goal=loops.enhance_prompt(
        "Write personalized cold emails that get replies. "
        "Every email must feel hand-written, not templated."
    ),
    backstory="You are a master copywriter specializing in B2B outreach.",
    verbose=True,
)

def run_outreach_crew(prospect: dict) -> str:
    research_task = Task(
        description=f"Research {prospect['name']} at {prospect['company']}.",
        agent=researcher,
        expected_output="A research brief with 3-5 actionable talking points.",
    )
    
    email_task = Task(
        description="Write a personalized cold email using the research brief.",
        agent=writer,
        expected_output="A ready-to-send cold email.",
    )
    
    crew = Crew(
        agents=[researcher, writer],
        tasks=[research_task, email_task],
        callbacks=[callback],  # Auto-tracks task completions
        verbose=True,
    )
    
    return str(crew.kickoff())
```

Install the CrewAI adapter: `pip install agentloops[crewai]`

---

## Any Custom Agent (Generic Pattern)

AgentLoops doesn't care how your agent works. Here's the universal pattern:

```python
from agentloops import AgentLoops

loops = AgentLoops("my-custom-agent")

class MyAgent:
    def __init__(self):
        self.base_prompt = "You are a helpful assistant."
    
    def run(self, user_input: str) -> str:
        # 1. Enhance prompt with learned rules
        prompt = loops.enhance_prompt(self.base_prompt)
        
        # 2. Run your agent however you want
        output = self._call_llm(prompt, user_input)
        
        # 3. Determine the outcome (your logic)
        outcome = self._evaluate(user_input, output)
        
        # 4. Track it
        loops.track(
            input=user_input,
            output=output,
            outcome=outcome,
        )
        
        return output
    
    def _call_llm(self, system: str, user: str) -> str:
        # Your LLM call here -- any provider, any framework
        ...
    
    def _evaluate(self, input: str, output: str) -> str:
        # Your evaluation logic -- could be:
        # - User feedback ("thumbs up" / "thumbs down")
        # - Automated scoring
        # - Business metric (conversion, resolution, etc.)
        # - LLM-as-judge
        ...

# Learning cycle -- run on a schedule
def learn():
    loops.reflect(last_n=10)
    loops.rules.generate_rules()
    loops.conventions.evolve()
    loops.forget(strategy="hybrid", max_age_days=21)
```

### Outcome Evaluation Strategies

The `outcome` parameter is the most important signal. Here are common patterns:

```python
# Binary: success/failure
outcome = "success" if user_liked_it else "failure"

# Numeric score (0-1)
outcome = str(quality_score)  # e.g., "0.85"

# Business metric
outcome = "meeting_booked"  # or "no_reply", "replied", "unsubscribed"

# LLM-as-judge
judge_response = judge_llm("Rate this output 1-5: ...")
outcome = str(judge_response)

# Composite score
score = (relevance * 0.4) + (accuracy * 0.3) + (tone * 0.3)
outcome = str(round(score, 2))
```

---

## Multi-Agent Systems

When running multiple agents that should share learning:

```python
from agentloops import AgentLoops
from agentloops.storage import FileStorage

# Shared storage -- all agents read from the same convention pool
shared_storage = FileStorage(".agentloops", "shared-pool")

# Individual agents with their own tracking
researcher = AgentLoops("researcher", storage=shared_storage)
writer = AgentLoops("writer", storage=shared_storage)
reviewer = AgentLoops("reviewer", storage=shared_storage)

# Each agent tracks independently but conventions are shared
researcher.track(input="...", output="...", outcome="success")
writer.track(input="...", output="...", outcome="failure")

# Conventions evolve based on ALL agents' data
researcher.conventions.evolve()
```

For isolated agents that learn independently:

```python
# Separate storage per agent (default behavior)
agent_a = AgentLoops("agent-a")  # stores in .agentloops/agent-a/
agent_b = AgentLoops("agent-b")  # stores in .agentloops/agent-b/
```
