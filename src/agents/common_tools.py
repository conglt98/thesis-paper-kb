"""
Common tools for the AI-Powered Knowledge Base System agents.

This module contains tool implementations that may be shared across multiple agents.
"""

from typing import Dict, Any


from src.core.logger import logger
from src.kb_service.api import kb_service


def query_knowledge(text: str) -> str:
    """
    Query the knowledge base with the given text.

    Args:
        text: The query text

    Returns:
        The response from the knowledge base
    """
    logger.info(f"Common tool: Querying knowledge base with: {text[:50]}...")

    try:
        response = kb_service.query_knowledge(text)
        return response
    except Exception as e:
        error_msg = f"Error querying knowledge base: {str(e)}"
        logger.error(error_msg)
        return f"Error: {error_msg}"


def save_knowledge(
    text: str,
    team_name: str,
    feature_name: str,
    knowledge_type: str,
    source_id: str = "",
    is_save_to_markdown: bool = True,
    is_save_to_graph: bool = True,
) -> Dict[str, Any]:
    """
    Save knowledge to the knowledge base.

    Args:
        text: The text content to save
        team_name: The team this knowledge belongs to
        feature_name: The specific feature this knowledge relates to
        knowledge_type: Type of knowledge - must be either "business" or "technical"
        source_id: The ID of the source (e.g. Jira ticket ID)
        is_save_to_markdown: Whether to save to markdown files
        is_save_to_graph: Whether to save to the knowledge graph

    Returns:
        Dictionary with status and message
    """
    # Validate parameters
    if not text or not text.strip():
        return {"status": "error", "message": "Text content cannot be empty"}

    # Auto-set team_name to 'Project_Manager' if empty or only whitespace
    if not team_name or not team_name.strip():
        team_name = "Project_Manager"

    if not feature_name or not feature_name.strip():
        return {"status": "error", "message": "Feature name cannot be empty"}

    if knowledge_type not in ["business", "technical"]:
        return {
            "status": "error",
            "message": "Knowledge type must be either 'business' or 'technical'",
        }

    # Call the KB service API
    success = kb_service.save_knowledge(
        text=text,
        team_name=team_name,
        feature_name=feature_name,
        knowledge_type=knowledge_type,
        source_id=source_id,
        is_save_to_markdown=is_save_to_markdown,
        is_save_to_graph=is_save_to_graph,
    )

    if success:
        return {
            "status": "success",
            "message": f"Successfully saved {knowledge_type} knowledge for {team_name}/{feature_name}",
        }
    else:
        return {
            "status": "error",
            "message": f"Failed to save {knowledge_type} knowledge for {team_name}/{feature_name}",
        }
