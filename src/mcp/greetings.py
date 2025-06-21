import os
import requests
from fastmcp import FastMCP

mcp = FastMCP("Scientific Paper MCP Server")

# Environment variables for agent configuration
URL_AGENT = os.getenv("URL_AGENT", "http://0.0.0.0:8000")
USER_ID = os.getenv("USER_ID", "u_123")
SESSION_ID = os.getenv("SESSION_ID", "s_123")
AGENT_APPS = os.getenv("AGENT_APPS", "knowledge_base_agent")


@mcp.tool()
def scientific_paper_query(query: str) -> str:
    """
    Query and synthesize information about scientific papers from the knowledge base agent.

    Args:
        query: The user's question or information need about scientific papers

    Returns:
        The agent's response with relevant scientific paper information, or an error message
    """
    try:
        # Step 1: Check/create session
        session_url = (
            f"{URL_AGENT}/apps/{AGENT_APPS}/users/{USER_ID}/sessions/{SESSION_ID}"
        )
        session_response = requests.post(session_url)

        # Log session response using loguru for better observability and production readiness
        from src.core.logger import logger

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


if __name__ == "__main__":
    mcp.run()
