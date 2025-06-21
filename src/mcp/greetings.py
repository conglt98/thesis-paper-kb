import os
import requests
from fastmcp import FastMCP
from src.core.logger import logger

mcp = FastMCP("Scientific Paper MCP Server")

# Environment variables for agent configuration
URL_AGENT = os.getenv("URL_AGENT", "http://0.0.0.0:8000")
USER_ID = os.getenv("USER_ID", "u_123")
SESSION_ID = os.getenv("SESSION_ID", "s_123")
AGENT_APPS = os.getenv("AGENT_APPS", "knowledge_base_agent")


def _query_scientific_paper_agent(raw_query: str, mode: str) -> str:
    """
    Internal helper to query the scientific paper agent with a specific mode.
    Args:
        raw_query: The user's original query.
        mode: The query mode, one of 'local', 'internet', or 'hybrid'.
    Returns:
        The agent's response or an error message.
    """
    mode_instructions = {
        "local": "Query using only internal knowledge. ",
        "internet": "Search for information on the internet about this topic. ",
        "hybrid": "Combine internal knowledge and internet search. ",
    }
    query = mode_instructions.get(mode, "") + raw_query
    try:
        # Step 1: Check/create session
        session_url = (
            f"{URL_AGENT}/apps/{AGENT_APPS}/users/{USER_ID}/sessions/{SESSION_ID}"
        )
        session_response = requests.post(session_url)
        logger.info(
            f"Session response: {session_response.status_code} - {session_response.text}"
        )
        # Step 2: Send query to agent
        run_url = f"{URL_AGENT}/run"
        payload = {
            "app_name": AGENT_APPS,
            "user_id": USER_ID,
            "session_id": SESSION_ID,
            "new_message": {"role": "user", "parts": [{"text": query}]},
        }
        headers = {"Content-Type": "application/json"}
        run_response = requests.post(run_url, json=payload, headers=headers)
        if run_response.status_code == 200:
            return run_response.text
        else:
            return f"Error calling scientific paper agent: {run_response.status_code} - {run_response.text}"
    except requests.exceptions.RequestException as e:
        return f"Network error: {str(e)}"
    except Exception as e:
        return f"Unexpected error: {str(e)}"


@mcp.tool()
def local_scientific_paper_knowledge(raw_query: str) -> str:
    """
    Query and synthesize information about scientific papers using only the local/internal knowledge base.

    Args:
        raw_query: The user's question or information need about scientific papers.

    Returns:
        The agent's response with relevant scientific paper information from the local knowledge base, or an error message.
    """
    return _query_scientific_paper_agent(raw_query, mode="local")


@mcp.tool()
def internet_scientific_paper_search(raw_query: str) -> str:
    """
    Search for and synthesize information about scientific papers using internet sources only (ignoring local/internal knowledge).

    Args:
        raw_query: The user's question or information need about scientific papers.

    Returns:
        The agent's response with relevant scientific paper information from internet sources, or an error message.
    """
    return _query_scientific_paper_agent(raw_query, mode="internet")


@mcp.tool()
def hybrid_scientific_paper_query(raw_query: str) -> str:
    """
    Query and synthesize information about scientific papers using both the local/internal knowledge base and internet sources (hybrid approach).

    Args:
        raw_query: The user's question or information need about scientific papers.

    Returns:
        The agent's response with relevant scientific paper information from both local and internet sources, or an error message.
    """
    return _query_scientific_paper_agent(raw_query, mode="hybrid")


if __name__ == "__main__":
    mcp.run()
