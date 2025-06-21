"""
Base Knowledge Graph interface for Scientific Paper Knowledge Base System.

This module defines the abstract base class that all scientific paper knowledge graph implementations must follow.
"""

from abc import ABC, abstractmethod
from typing import Optional

from src.core.models import (
    QueryResponse,
    InsertResponse,
)


class BaseKnowledgeGraph(ABC):
    """
    Abstract base class for scientific paper knowledge graph implementations.

    This class defines the interface that all scientific paper knowledge graph backends must implement,
    ensuring a consistent API regardless of the underlying technology.
    """

    @abstractmethod
    def query(self, query_text: str, mode: str = "local", **kwargs) -> QueryResponse:
        """
        Query the knowledge graph for scientific papers with the given text.

        Args:
            query_text: The query text
            mode: Query mode (local, global, hybrid, naive, mix, bypass)
            **kwargs: Additional parameters for the query

        Returns:
            QueryResponse object containing the response from the knowledge graph
        """
        pass

    @abstractmethod
    async def async_query(self, query_text: str, mode: str = "local", **kwargs) -> str:
        """
        Async implementation of the query method for scientific papers.

        Args:
            query_text: The query text
            mode: Query mode (local, global, hybrid, naive, mix, bypass)
            **kwargs: Additional parameters for the query

        Returns:
            The response text from the knowledge graph
        """
        pass

    @abstractmethod
    def save(
        self, text: str, paper_title: Optional[str] = None, doi: str = ""
    ) -> InsertResponse:
        """
        Save the given scientific paper text to the knowledge graph.

        Args:
            text: The text to save
            paper_title: Optional title of the scientific paper
            doi: The DOI of the paper (optional)

        Returns:
            InsertResponse object indicating success or failure
        """
        pass

    @abstractmethod
    async def async_save(
        self,
        text: str,
        paper_title: Optional[str] = None,
        doi: str = "",
    ) -> str:
        """
        Async implementation of the save method for scientific papers.

        Args:
            text: The text to save
            paper_title: Optional title of the scientific paper
            doi: The DOI of the paper (optional)

        Returns:
            The ID of the saved paper or operation result
        """
        pass
