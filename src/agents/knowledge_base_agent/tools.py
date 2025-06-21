import os
from typing import Optional, Tuple
from contextlib import AsyncExitStack
from src.core.config import DOWNLOADS_DIR
from google.adk.agents import Agent
from google.adk.models.lite_llm import LiteLlm
from google.adk.tools import FunctionTool
from google.adk.tools.mcp_tool.mcp_toolset import MCPToolset, StdioServerParameters
from src.kb_service.graph_module import KnowledgeGraphModule
from src.core.logger import logger


async def query_knowledge_base_tools(query: str):
    """
    Query the scientific paper knowledge base (LightRAG backend) for the given query.

    Args:
        query: The query to search the knowledge base for

    Returns:
        The response from the knowledge base
    """
    os.environ["KNOWLEDGE_GRAPH_BACKEND"] = "light_rag"
    kb_service = KnowledgeGraphModule()

    logger.info(f"Querying Knowledge Base Service with LightRAG backend...")
    response = await kb_service.async_query(query)
    logger.info(f"Query response: {response}")
    return response


async def figma_mcp_tools():
    """
    Initialize MCP tools for Figma integration.

    Returns:
        Tuple of (list of MCP tools, exit stack) or ([], None) if initialization fails
    """
    try:
        # Get tools from Figma MCP Docker container
        server_params = StdioServerParameters(
            command="docker",
            args=[
                "run",
                "-i",
                "--rm",
                "--read-only",
                "-e",
                f"FIGMA_API_KEY={os.getenv('FIGMA_API_KEY')}",
                "docker.io/acuvity/mcp-server-figma:0.2.2",
            ],
        )
        tools, exit_stack = await MCPToolset.from_server(
            connection_params=server_params
        )
        logger.info("MCP Figma Toolset created successfully.")
        return tools, exit_stack
    except Exception as e:
        logger.warning(f"Failed to connect to MCP Figma server: {e}")
        return [], None


async def atlassian_mcp_tools():
    """
    Initialize MCP tools for Atlassian (Confluence/Jira) integration.

    Returns:
        Tuple of (list of MCP tools, exit stack) or ([], None) if initialization fails
    """
    try:
        # Determine ENABLED_TOOLS value (from env or default)
        enabled_tools = os.getenv(
            "ENABLED_TOOLS",
            "confluence_get_comments,jira_get_comments,jira_get_issue,jira_search,confluence_search,confluence_get_page,jira_get_user_profile,jira_get_project_versions,jira_get_issue_link_types,jira_get_sprint_issues,jira_get_sprints_from_board,jira_get_board_issues,jira_get_agile_boards,jira_get_transitions,jira_get_worklog,jira_get_project_issues",
        )
        # Get tools from Atlassian MCP Docker container
        server_params = StdioServerParameters(
            command="docker",
            args=[
                "run",
                "-i",
                "--rm",
                "-e",
                f"CONFLUENCE_URL={os.getenv('CONFLUENCE_URL')}",
                "-e",
                f"CONFLUENCE_USERNAME={os.getenv('CONFLUENCE_USERNAME')}",
                "-e",
                f"CONFLUENCE_API_TOKEN={os.getenv('CONFLUENCE_API_TOKEN')}",
                "-e",
                f"JIRA_URL={os.getenv('JIRA_URL')}",
                "-e",
                f"JIRA_USERNAME={os.getenv('JIRA_USERNAME')}",
                "-e",
                f"JIRA_API_TOKEN={os.getenv('JIRA_API_TOKEN')}",
                "-e",
                f"ENABLED_TOOLS={enabled_tools}",
                "mcp/atlassian",
            ],
        )
        tools, exit_stack = await MCPToolset.from_server(
            connection_params=server_params
        )
        logger.info(
            f"MCP Atlassian Toolset created successfully with ENABLED_TOOLS={enabled_tools}"
        )
        return tools, exit_stack
    except Exception as e:
        logger.warning(f"Failed to connect to MCP Atlassian server: {e}")
        return [], None


async def paper_search_mcp_tools():
    """
    Initialize MCP tools for Paper Search integration.

    This function starts the MCP Paper Search server using the uvicorn runner and initializes the toolset for use by the agent.

    Returns:
        Tuple of (list of MCP tools, exit stack) or ([], None) if initialization fails
    """
    try:
        # Use the project root as the working directory so imports and file paths resolve correctly
        server_params = StdioServerParameters(
            command="uv",
            args=[
                "run",
                "-m",
                "paper_search_mcp.server",
            ],
        )
        tools, exit_stack = await MCPToolset.from_server(
            connection_params=server_params
        )
        logger.info("MCP Paper Search Toolset created successfully.")
        return tools, exit_stack
    except Exception as e:
        logger.warning(f"Failed to connect to MCP Paper Search server: {e}")
        return [], None
