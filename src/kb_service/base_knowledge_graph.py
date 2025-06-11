"""
Base Knowledge Graph interface for the AI-Powered Knowledge Base System.

This module defines the abstract base class that all knowledge graph implementations must follow.
"""

from abc import ABC, abstractmethod
from typing import Optional, Literal

from src.core.models import (
    QueryResponse,
    InsertResponse,
)


class BaseKnowledgeGraph(ABC):
    """
    Abstract base class for knowledge graph implementations.

    This class defines the interface that all knowledge graph backends must implement,
    ensuring a consistent API regardless of the underlying technology.
    """

    @abstractmethod
    def query(self, query_text: str, mode: str = "local", **kwargs) -> QueryResponse:
        """
        Query the knowledge graph with the given text.

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
        Async implementation of the query method.

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
        self, text: str, name: Optional[str] = None, domain: str = "tech"
    ) -> InsertResponse:
        """
        Save the given text to the knowledge graph.

        Args:
            text: The text to save
            name: Optional name for the episode
            domain: The domain of the knowledge ("tech" or "business")

        Returns:
            InsertResponse object indicating success or failure
        """
        pass

    @abstractmethod
    async def async_save(
        self,
        text: str,
        name: Optional[str] = None,
        domain: Literal["tech", "business"] = "tech",
    ) -> str:
        """
        Async implementation of the save method.

        Args:
            text: The text to save
            name: Optional name for the episode
            domain: The domain of the knowledge ("tech" or "business")

        Returns:
            The ID of the saved episode
        """
        pass
