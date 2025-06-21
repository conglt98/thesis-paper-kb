"""
Knowledge Base Service API for Scientific Papers.

This module provides an interface to the Knowledge Base Service for scientific papers,
abstracting the underlying storage mechanisms (Knowledge Graph and Markdown).
"""

from typing import Optional

from src.core.logger import logger
from src.kb_service.graph_module import KnowledgeGraphModule
from src.kb_service.markdown_module import MarkdownModule


class KnowledgeBaseService:
    """
    Knowledge Base Service for managing and accessing scientific paper knowledge.
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
        Query the knowledge base for scientific papers with the given text.

        Args:
            text: The query text

        Returns:
            The response from the knowledge base
        """
        logger.info(f"Querying knowledge base with: {text[:50]}...")
        response = self.graph_module.query(text)
        if response.status == "error":
            logger.error(f"Error querying knowledge base: {response.error_message}")
            return f"Error: {response.error_message}"
        return response.response

    def save_paper(
        self,
        text: str,
        paper_title: str,
        doi: str = "",
        is_save_to_markdown: bool = True,
        is_save_to_graph: bool = True,
    ) -> bool:
        """
        Save a scientific paper to the knowledge base.

        Args:
            text: The text to save
            paper_title: The title of the scientific paper
            doi: The DOI of the paper (optional)
            is_save_to_markdown: Whether to save to markdown files
            is_save_to_graph: Whether to save to the knowledge graph
        Returns:
            True if the text was saved successfully, False otherwise
        """
        logger.info(
            f"Saving scientific paper '{paper_title}' to knowledge base: {text[:50]}..."
        )
        if is_save_to_graph:
            response = self.graph_module.save(
                text=text, name=paper_title, domain="scientific_paper", doi=doi
            )
            if response.status == "error":
                logger.error(f"Error saving to knowledge graph: {response.message}")
                return False
        if is_save_to_markdown:
            markdown_result = self.markdown_module.save(
                text=text, paper_title=paper_title, doi=doi
            )
            if not markdown_result:
                logger.error("Error saving to markdown files")
                return False
        return True

    def get_paper(self, paper_title: str, doi: str = "") -> str:
        """
        Get a scientific paper from markdown files.

        Args:
            paper_title: The title of the scientific paper
            doi: The DOI of the paper (optional)
        Returns:
            The content of the markdown file
        """
        logger.info(f"Getting scientific paper '{paper_title}' (DOI: {doi})")
        return self.markdown_module.get_paper(paper_title=paper_title, doi=doi)

    def list_papers(self) -> list:
        """
        List all scientific papers stored in the markdown module.

        Returns:
            A list of paper titles
        """
        logger.info("Listing all scientific papers")
        return self.markdown_module.list_papers()

    def delete_paper(self, paper_title: str, doi: str = "") -> bool:
        """
        Delete a scientific paper knowledge file or directory.

        Args:
            paper_title: The title of the scientific paper
            doi: The DOI of the paper (optional)
        Returns:
            True if the deletion was successful, False otherwise
        """
        logger.info(f"Deleting scientific paper '{paper_title}' (DOI: {doi})")
        return self.markdown_module.delete(paper_title=paper_title, doi=doi)
