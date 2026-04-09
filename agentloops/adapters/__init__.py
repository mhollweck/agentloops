"""Framework adapters for LangChain, CrewAI, and other agent frameworks.

Adapters wrap AgentLoops functionality into framework-native patterns
so users don't need to manually call track() and enhance_prompt().
"""

from agentloops.adapters.langchain import AgentLoopsCallback
from agentloops.adapters.crewai import AgentLoopsCrewCallback

__all__ = ["AgentLoopsCallback", "AgentLoopsCrewCallback"]
