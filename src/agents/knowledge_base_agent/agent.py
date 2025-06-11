"""
Processor Agent implementation for the AI-Powered Knowledge Base System.

This module contains the implementation of the Processor Agent using the Google
Agent Development Kit (ADK). The Processor Agent is responsible for handling
Figma design extraction, Atlassian (Confluence/Jira) integration, and local file processing.
"""

from typing import Optional, Tuple
from contextlib import AsyncExitStack

from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm
from google.adk.tools import FunctionTool

from src.core.config import DEFAULT_LLM_MODEL
from src.core.logger import logger
from src.agents.knowledge_base_agent.tools import (
    figma_mcp_tools,
    atlassian_mcp_tools,
    query_knowledge_base_tools,
)


class KnowledgeBaseAgent:
    """
    Knowledge Base Agent for handling Figma design extraction, Atlassian integration, and comprehensive knowledge retrieval.

    This agent is responsible for:
    - Retrieving information from the knowledge base Graphiti / LightRAG if user asks.
    """

    def __init__(self, model: Optional[str] = None):
        """
        Initialize the Knowledge Base Agent.

        Args:
            model: The LLM model to use (defaults to the configured DEFAULT_LLM_MODEL)
        """
        self.model = model or DEFAULT_LLM_MODEL
        logger.info(f"Initializing Knowledge Base Agent with model: {self.model}")

    async def create_agent(self) -> Tuple[Agent, AsyncExitStack]:
        """
        Create the ADK Agent instance for the Knowledge Base Agent.

        Returns:
            Tuple of (the configured ADK Agent instance, combined exit stack)
        """
        # Initialize MCP tool sets
        figma_tools, figma_exit_stack = await figma_mcp_tools()
        atlassian_tools, atlassian_exit_stack = await atlassian_mcp_tools()

        local_tools = [
            FunctionTool(query_knowledge_base_tools)
        ]

        # Combine all tools
        all_tools = figma_tools + atlassian_tools + local_tools

        # Create a combined exit stack
        combined_exit_stack = AsyncExitStack()
        if figma_exit_stack:
            await combined_exit_stack.enter_async_context(figma_exit_stack)
        if atlassian_exit_stack:
            await combined_exit_stack.enter_async_context(atlassian_exit_stack)

        instruction = """
        You are an expert knowledge synthesis agent for the AI-Powered Knowledge Base System.
        You are responsible for retrieving information from the knowledge base Graphiti / LightRAG if user asks.
        """

        logger.info(
            f"Created Knowledge Base Agent with {len(all_tools)} tools total ({len(local_tools)} essential processing tools)"
        )

        agent = Agent(
            name="knowledge_base_agent",
            model=LiteLlm(model=self.model),
            description="You are the Knowledge Base Agent for AI-Powered Knowledge Base System. You are responsible for retrieving information from the knowledge base Graphiti.",
            instruction=instruction,
            tools=all_tools,
        )
        return agent, combined_exit_stack


# Create a singleton instance of the Processor Agent
knowledge_base_agent = KnowledgeBaseAgent()


# Function for adk web - this is the pattern ADK expects
async def create_agent() -> Tuple[Agent, AsyncExitStack]:
    """
    Create the Processor Agent instance for ADK web interface.

    Returns:
        Tuple of (the configured ADK Agent instance, combined exit stack)
    """
    return await knowledge_base_agent.create_agent()


# root_agent = create_agent

# agent instance for adk web
knowledge_base_agent_instance = knowledge_base_agent.create_agent()
root_agent = knowledge_base_agent_instance
logger.info("Knowledge Base Agent initialized successfully")
