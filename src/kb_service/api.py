"""
DEPRECATED: Use src.kb_service.graph_module.KnowledgeGraphModule instead.

Knowledge Base Service API for the AI-Powered Knowledge Base System.

This module provides a simplified interface to the Knowledge Base Service,
abstracting the underlying storage mechanisms (Knowledge Graph and Markdown).
It supports multiple knowledge graph backends through a configurable interface.
"""

from typing import Dict, List, Optional, Union

from src.core.logger import logger
from src.kb_service.graph_module import KnowledgeGraphModule
from src.kb_service.markdown_module import MarkdownModule


class KnowledgeBaseService:
    """
    Knowledge Base Service for managing and accessing knowledge.

    This service provides a simplified interface to the knowledge base,
    abstracting the underlying storage mechanisms (Knowledge Graph and Markdown).
    """

    def __init__(self, backend: Optional[str] = None, **backend_kwargs):
        """
        Initialize the Knowledge Base Service.

        Args:
            backend: The knowledge graph backend to use ("light_rag" or "graphiti")
            **backend_kwargs: Additional keyword arguments for the backend
        """
        self.graph_module = KnowledgeGraphModule(backend=backend, **backend_kwargs)
        self.markdown_module = MarkdownModule()

        logger.info(
            f"Initialized Knowledge Base Service with {self.graph_module.backend_name} backend"
        )

    def query_knowledge(self, text: str) -> str:
        """
        Query the knowledge base with the given text.

        Args:
            text: The query text

        Returns:
            The response from the knowledge base
        """
        logger.info(f"Querying knowledge base with: {text[:50]}...")

        # Query the knowledge graph
        response = self.graph_module.query(text)

        if response.status == "error":
            logger.error(f"Error querying knowledge base: {response.error_message}")
            return f"Error: {response.error_message}"

        return response.response

    def save_knowledge(
        self,
        text: str,
        team_name: str = "default",
        feature_name: str = "general",
        knowledge_type: str = "business",
        source_id: str = "",
        is_save_to_markdown: bool = True,
        is_save_to_graph: bool = True,
    ) -> bool:
        """
        Save new knowledge to the knowledge base.

        Args:
            text: The text to save
            team_name: The name of the team
            feature_name: The name of the feature
            knowledge_type: The type of knowledge (business or technical)
            source_id: The ID of the source (e.g. Jira ticket ID)
            is_save_to_markdown: Whether to save to markdown files
            is_save_to_graph: Whether to save to the knowledge graph
        Returns:
            True if the text was saved successfully, False otherwise
        """
        logger.info(
            f"Saving knowledge {knowledge_type} to knowledge base {team_name}/{feature_name}: {text[:50]}..."
        )

        # Save to the knowledge graph
        response = self.graph_module.save(
            text=text, name=feature_name, domain=knowledge_type
        )

        # Also save to markdown files
        if is_save_to_markdown:
            markdown_result = self.markdown_module.save(
                text=text,
                team_name=team_name,
                feature_name=feature_name,
                knowledge_type=knowledge_type,
                source_id=source_id,
            )
            if not markdown_result:
                logger.error("Error saving to markdown files")
                return False

        return True

    def get_markdown_knowledge(
        self, team_name: str, feature_name: str, knowledge_type: str = "business"
    ) -> str:
        """
        Get knowledge from markdown files.

        Args:
            team_name: The name of the team
            feature_name: The name of the feature
            knowledge_type: The type of knowledge (business or technical)

        Returns:
            The content of the markdown file
        """
        logger.info(
            f"Getting {knowledge_type} knowledge for {feature_name} (team: {team_name})"
        )

        return self.markdown_module.get(
            team_name=team_name,
            feature_name=feature_name,
            knowledge_type=knowledge_type,
        )

    def list_markdown_features(
        self, team_name: Optional[str] = None
    ) -> List[Dict[str, Union[str, List[str]]]]:
        """
        List features from markdown files.

        Args:
            team_name: The name of the team (optional)

        Returns:
            A list of feature dictionaries
        """
        logger.info(
            f"Listing features from markdown files{f' for team: {team_name}' if team_name else ''}"
        )

        return self.markdown_module.list_features(team_name=team_name)

    def delete_markdown_knowledge(
        self, team_name: str, feature_name: str, knowledge_type: Optional[str] = None
    ) -> bool:
        """
        Delete knowledge from markdown files.

        Args:
            team_name: The name of the team
            feature_name: The name of the feature
            knowledge_type: The type of knowledge (business or technical)
                            If None, delete the entire feature

        Returns:
            True if the deletion was successful, False otherwise
        """
        logger.info(
            f"Deleting {'all' if knowledge_type is None else knowledge_type} knowledge for {feature_name} (team: {team_name})"
        )

        return self.markdown_module.delete(
            team_name=team_name,
            feature_name=feature_name,
            knowledge_type=knowledge_type,
        )

    def get_features_list(self) -> str:
        """
        Get the features list from the mermaid diagram.

        Returns:
            The features list as a string
        """
        logger.info("Getting features list")

        return self.graph_module.get_features_list()

    def update_features_list(
        self,
        feature_name: str,
        feature_description: str,
        parent_node: Optional[str] = None,
    ) -> bool:
        """
        Update the features list in the mermaid diagram.

        Args:
            feature_name: The name of the feature to add or update
            feature_description: The description of the feature
            parent_node: The parent node ID in the mermaid diagram (optional)

        Returns:
            True if the features list was updated successfully, False otherwise
        """
        logger.info(f"Updating features list with feature: {feature_name}")

        # Type safety: parent_node is Optional[str] but the method expects Optional[str] as well
        response = self.graph_module.update_features_list(
            feature_name=feature_name,
            feature_description=feature_description,
            parent_node=parent_node,  # type: ignore
        )

        if response.status == "error":
            logger.error(f"Error updating features list: {response.message}")
            return False

        # After updating the features list, we should also save this information to the knowledge graph
        # to make it queryable
        feature_info = f"""
Feature Name: {feature_name}
Description: {feature_description}
Parent: {parent_node if parent_node else 'Root level'}
        """

        self.save_knowledge(
            text=feature_info, feature_name=feature_name, knowledge_type="business"
        )

        return True


# Create a singleton instance of the Knowledge Base Service with the default backend
# from the environment configuration
kb_service = KnowledgeBaseService()
