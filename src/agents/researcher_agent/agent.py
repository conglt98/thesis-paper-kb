"""
Researcher Agent for the AI-Powered Knowledge Base System.

This agent specializes in searching for scientific papers on the internet using MCP tools.
"""

from typing import Optional, Tuple
from contextlib import AsyncExitStack

from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm
from google.adk.tools import FunctionTool

from src.core.config import DEFAULT_LLM_MODEL
from src.core.logger import logger
from src.agents.knowledge_base_agent.tools import paper_search_mcp_tools


class ResearcherAgent:
    """
    Agent that searches for scientific papers on the internet using MCP tools.
    """

    def __init__(self, model: Optional[str] = None):
        self.model = model or DEFAULT_LLM_MODEL
        logger.info(f"Initializing Researcher Agent with model: {self.model}")

    async def create_agent(self) -> Tuple[Agent, AsyncExitStack]:
        local_tools = []
        paper_tools, paper_exit_stack = await paper_search_mcp_tools()
        if paper_tools:
            local_tools.extend(paper_tools)
        instruction = """
        You are a researcher agent. Your job is to search for scientific papers on the internet using MCP tools. 
        - Only return your findings as data for the synthesizer agent. Do not greet or instruct the user directly. Do not return any message to the user.
        - Always provide clear references to the source of each paper in your data output.
        """
        agent = Agent(
            name="researcher_agent",
            model=LiteLlm(model=self.model),
            description="Agent that searches for scientific papers on the internet using MCP tools.",
            instruction=instruction,
            tools=local_tools,
        )
        exit_stack = AsyncExitStack()
        if paper_exit_stack:
            await exit_stack.enter_async_context(paper_exit_stack)
        return agent, exit_stack


researcher_agent = ResearcherAgent()


async def create_agent() -> Tuple[Agent, AsyncExitStack]:
    return await researcher_agent.create_agent()
