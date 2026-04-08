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

```python
from openai import OpenAI
from agentloops import AgentLoops

# Initialize
client = OpenAI()
loops = AgentLoops("sales-agent")

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

```python
from langchain_anthropic import ChatAnthropic
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from agentloops import AgentLoops

# Initialize
loops = AgentLoops("research-agent")
llm = ChatAnthropic(model="claude-sonnet-4-6")

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

def research(query: str) -> str:
    """Run a research query through the learning-enhanced chain."""
    chain = create_chain()
    result = chain.invoke({"query": query})
    return result

def track_research(query: str, result: str, quality_score: float):
    """Track the research output quality."""
    loops.track(
        input=query,
        output=result,
        outcome=str(quality_score),  # e.g., "4.5" out of 5
        metadata={"source": "langchain", "model": "claude-sonnet-4-6"},
    )

# With LangChain callbacks for automatic tracking
from langchain_core.callbacks import BaseCallbackHandler

class AgentLoopsCallback(BaseCallbackHandler):
    """LangChain callback that auto-tracks runs."""
    
    def __init__(self, loops: AgentLoops):
        self.loops = loops
        self._current_input = None
    
    def on_chain_start(self, serialized, inputs, **kwargs):
        self._current_input = str(inputs)
    
    def on_chain_end(self, outputs, **kwargs):
        if self._current_input:
            self.loops.track(
                input=self._current_input,
                output=str(outputs),
                outcome="success",  # Override with actual outcome later
            )

# Usage with callback
callback = AgentLoopsCallback(loops)
chain = create_chain()
result = chain.invoke({"query": "AI agent market size 2025"}, config={"callbacks": [callback]})
```

---

## CrewAI

```python
from crewai import Agent, Task, Crew
from agentloops import AgentLoops

# Initialize AgentLoops for each crew member
sales_loops = AgentLoops("crew-sales-researcher")
writer_loops = AgentLoops("crew-email-writer")

# Create agents with enhanced prompts
researcher = Agent(
    role="Sales Researcher",
    goal=sales_loops.enhance_prompt(
        "Find detailed information about prospects including recent news, "
        "company updates, and personal interests."
    ),
    backstory="You are an expert at finding actionable intelligence on sales prospects.",
    verbose=True,
)

writer = Agent(
    role="Email Writer",
    goal=writer_loops.enhance_prompt(
        "Write personalized cold emails that get replies. "
        "Every email must feel hand-written, not templated."
    ),
    backstory="You are a master copywriter specializing in B2B outreach.",
    verbose=True,
)

def run_outreach_crew(prospect: dict) -> str:
    """Run the full outreach crew for a prospect."""
    research_task = Task(
        description=f"Research {prospect['name']} at {prospect['company']}. "
                    f"Find recent news, blog posts, and social media activity.",
        agent=researcher,
        expected_output="A research brief with 3-5 actionable talking points.",
    )
    
    email_task = Task(
        description="Using the research brief, write a personalized cold email "
                    "that references specific details about the prospect.",
        agent=writer,
        expected_output="A ready-to-send cold email.",
    )
    
    crew = Crew(
        agents=[researcher, writer],
        tasks=[research_task, email_task],
        verbose=True,
    )
    
    result = crew.kickoff()
    
    # Track both agents' contributions
    sales_loops.track(
        input=f"Research {prospect['name']} at {prospect['company']}",
        output=str(research_task.output) if research_task.output else "",
        outcome="success",
        metadata={"prospect": prospect["name"]},
    )
    
    writer_loops.track(
        input=f"Write email for {prospect['name']}",
        output=str(result),
        outcome="success",  # Update later with actual outcome
        metadata={"prospect": prospect["name"]},
    )
    
    return str(result)

# Weekly learning for the whole crew
def crew_learning_cycle():
    for loops in [sales_loops, writer_loops]:
        loops.reflect(last_n=20)
        loops.rules.generate_rules()
        loops.conventions.evolve()
        loops.forget(max_age_days=21)
```

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
