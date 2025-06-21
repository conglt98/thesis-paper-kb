"""
Context Analyzer Agent for the AI-Powered Knowledge Base System.

This agent analyzes the user's session context using ADK's InMemorySession and DatabaseSession.
"""

from typing import Optional, Tuple
from contextlib import AsyncExitStack

from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm

from src.core.config import DEFAULT_LLM_MODEL
from src.core.logger import logger


class ContextAnalyzerAgent:
    """
    Agent that analyzes the user's session context using ADK session services.
    """

    def __init__(self, model: Optional[str] = None):
        self.model = model or DEFAULT_LLM_MODEL
        logger.info(f"Initializing Context Analyzer Agent with model: {self.model}")

    async def create_agent(self) -> Tuple[Agent, AsyncExitStack]:
        instruction = """
        You are a context analysis agent. Your job is to examine the user's session context, including conversation history and any stored session data (using InMemorySession and DatabaseSession), to provide relevant context for downstream agents.
        - You must utilize all available information—including conversation history, session data (InMemorySession, DatabaseSession), user metadata, and any relevant system state—to thoroughly analyze and infer the user's true intent, goals, and context. Your analysis should be as comprehensive as possible to support downstream agents in fulfilling the user's request accurately.
        - Only respond if you detect important context, a user goal, or a warning that downstream agents need to know. If there is nothing important, do not return any message to the user and simply pass the context along.
        """
        agent = Agent(
            name="context_analyzer_agent",
            model=LiteLlm(model=self.model),
            description="Agent that analyzes the user's session context using ADK session services.",
            instruction=instruction,
            tools=[],
        )
        return agent, AsyncExitStack()


context_analyzer_agent = ContextAnalyzerAgent()


async def create_agent() -> Tuple[Agent, AsyncExitStack]:
    return await context_analyzer_agent.create_agent()
