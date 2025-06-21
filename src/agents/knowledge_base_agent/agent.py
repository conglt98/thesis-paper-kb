"""
Knowledge Base Agent implementation for the AI-Powered Knowledge Base System.

This module contains the implementation of the Knowledge Base Agent using the Google
Agent Development Kit (ADK). The Knowledge Base Agent is responsible for
retrieving and synthesizing information about scientific papers from the knowledge base (LightRAG backend).
"""

from typing import Optional, Tuple
from contextlib import AsyncExitStack

from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm
from google.adk.tools import FunctionTool

from src.core.config import DEFAULT_LLM_MODEL, DOWNLOADS_DIR
from src.core.logger import logger
from src.agents.knowledge_base_agent.tools import query_knowledge_base_tools
from src.agents.knowledge_base_agent.tools import paper_search_mcp_tools


class KnowledgeBaseAgent:
    """
    Knowledge Base Agent for retrieving and synthesizing information about scientific papers.

    This agent is responsible for:
    - Querying the scientific paper knowledge base (LightRAG backend) when requested.
    - Synthesizing and presenting scientific paper information to the user.
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
        # Only include the tool for querying scientific paper knowledge base
        local_tools = [FunctionTool(query_knowledge_base_tools)]

        combined_exit_stack = AsyncExitStack()

        # Add MCP Paper Search tools
        paper_tools, paper_exit_stack = await paper_search_mcp_tools()
        if paper_tools:
            local_tools.extend(paper_tools)
        if paper_exit_stack:
            await combined_exit_stack.enter_async_context(paper_exit_stack)

        instruction = """
        You are an expert agent for the Scientific Paper Knowledge Base System.

        For every user request about scientific papers, you MUST always:
        - Use BOTH the LightRAG backend (for local/private knowledge base) AND the MCP Paper Search tools (for public internet sources).
        - Query both sources, synthesize and compare the results, and present a comprehensive answer that integrates information from both.
        - Always provide clear, concise, and accurate information.
        - ALWAYS include full references to the source papers for every piece of information you provide, clearly indicating which source (local/private or internet) each reference comes from.

        If there are differences or conflicts between sources, explain them and provide references for each perspective.

        Your goal is to ensure the user receives the most complete, well-sourced, and reliable answer possible.
        """

        logger.info(
            f"Created Knowledge Base Agent with {len(local_tools)} scientific paper tools"
        )

        agent = Agent(
            name="scientific_paper_knowledge_base_agent",
            model=LiteLlm(model=self.model),
            description="You are the Knowledge Base Agent for the Scientific Paper Knowledge Base System. You retrieve and synthesize information about scientific papers from the knowledge base (LightRAG backend).",
            instruction=instruction,
            tools=local_tools,
        )
        return agent, combined_exit_stack


# Create a singleton instance of the Knowledge Base Agent
knowledge_base_agent = KnowledgeBaseAgent()


# Function for adk web - this is the pattern ADK expects
async def create_agent() -> Tuple[Agent, AsyncExitStack]:
    """
    Create the Knowledge Base Agent instance for ADK web interface.

    Returns:
        Tuple of (the configured ADK Agent instance, combined exit stack)
    """
    return await knowledge_base_agent.create_agent()


# agent instance for adk web
knowledge_base_agent_instance = knowledge_base_agent.create_agent()
root_agent = knowledge_base_agent_instance
logger.info("Scientific Paper Knowledge Base Agent initialized successfully")
