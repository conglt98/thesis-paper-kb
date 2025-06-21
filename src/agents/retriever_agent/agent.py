"""
Retriever Agent for the AI-Powered Knowledge Base System.

This agent specializes in retrieving information from the local knowledge base (LightRAG backend).
"""

from typing import Optional, Tuple
from contextlib import AsyncExitStack

from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm
from google.adk.tools import FunctionTool

from src.core.config import DEFAULT_LLM_MODEL
from src.core.logger import logger
from src.agents.knowledge_base_agent.tools import query_knowledge_base_tools


class RetrieverAgent:
    """
    Agent that retrieves information from the local knowledge base (LightRAG backend).
    """

    def __init__(self, model: Optional[str] = None):
        self.model = model or DEFAULT_LLM_MODEL
        logger.info(f"Initializing Retriever Agent with model: {self.model}")

    async def create_agent(self) -> Tuple[Agent, AsyncExitStack]:
        local_tools = [FunctionTool(query_knowledge_base_tools)]
        instruction = """
        You are a retriever agent. Your job is to retrieve information from the local knowledge base (LightRAG backend).
        - Only return your findings as data for the synthesizer agent. Do not greet or instruct the user directly. Do not return any message to the user.
        - Always provide clear references to the source of each piece of information in your data output.
        """
        agent = Agent(
            name="retriever_agent",
            model=LiteLlm(model=self.model),
            description="Agent that retrieves information from the local knowledge base (LightRAG backend).",
            instruction=instruction,
            tools=local_tools,
        )
        return agent, AsyncExitStack()


retriever_agent = RetrieverAgent()


async def create_agent() -> Tuple[Agent, AsyncExitStack]:
    return await retriever_agent.create_agent()
