"""
Knowledge Graph Module for the Scientific Paper Knowledge Base System.

This module provides a configurable interface to knowledge graph operations for scientific papers.
It supports multiple backend implementations (LightRAG and Graphiti) through a factory pattern.
"""

import os
from typing import Optional, Literal

from src.core.config import (
    KNOWLEDGE_GRAPH_BACKEND,
    DEFAULT_LLM_MODEL,
)
from src.core.logger import logger
from src.core.models import (
    QueryResponse,
    InsertResponse,
)
from src.kb_service.base_knowledge_graph import BaseKnowledgeGraph
from src.kb_service.lightrag_backend import LightRAGKnowledgeGraph
from src.kb_service.graphiti_backend import GraphitiKnowledgeGraph

from tenacity import retry, stop_after_attempt, wait_fixed, retry_if_exception_type


class KnowledgeGraphModule:
    """
    Knowledge Graph Module for interacting with the knowledge graph backend for scientific papers.
    """

    def __init__(
        self,
        backend: Optional[str] = None,
        llm_model: Optional[str] = None,
        **backend_kwargs,
    ):
        """
        Initialize the Knowledge Graph Module with the specified backend.

        Args:
            backend: The backend to use ("light_rag" or "graphiti")
            llm_model: (Unused, kept for compatibility)
            **backend_kwargs: Additional keyword arguments for the backend
        """
        self.backend_name = backend or KNOWLEDGE_GRAPH_BACKEND
        self.llm_model = llm_model or DEFAULT_LLM_MODEL
        self.backend = self._create_backend(**backend_kwargs)
        logger.info(
            f"Initialized Knowledge Graph Module with {self.backend_name} backend"
        )

    def _create_backend(self, **kwargs) -> BaseKnowledgeGraph:
        if self.backend_name.lower() == "light_rag":
            return LightRAGKnowledgeGraph(**kwargs)
        elif self.backend_name.lower() == "graphiti":
            return GraphitiKnowledgeGraph(**kwargs)
        else:
            error_msg = f"Unsupported knowledge graph backend: {self.backend_name}"
            logger.error(error_msg)
            raise ValueError(error_msg)

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_fixed(2),
        retry=retry_if_exception_type(Exception),
    )
    def query(self, query_text: str, mode: str = "local", **kwargs) -> QueryResponse:
        """
        Query the knowledge graph for scientific paper information.

        Args:
            query_text: The query text
            mode: Query mode (local, hybrid, or semantic)
            **kwargs: Additional parameters for the query

        Returns:
            QueryResponse object containing the response from the knowledge graph
        """
        logger.debug(f"Querying knowledge graph with: {query_text}")
        return self.backend.query(query_text, mode, **kwargs)

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_fixed(2),
        retry=retry_if_exception_type(Exception),
    )
    async def async_query(self, query_text: str, mode: str = "hybrid", **kwargs) -> str:
        """
        Async implementation of the query method.

        Args:
            query_text: The query text
            mode: Query mode (local, global, hybrid, naive, mix, bypass) 
            **kwargs: Additional parameters for the query

        Returns:
            The response text from the knowledge graph
        """
        logger.debug(f"Async querying knowledge graph with: {query_text}")
        return await self.backend.async_query(query_text, mode, **kwargs)

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_fixed(2),
        retry=retry_if_exception_type(Exception),
    )
    def save(
        self,
        text: str,
        name: Optional[str] = None,
        domain: Literal["scientific_paper"] = "scientific_paper",
    ) -> InsertResponse:
        """
        Save the given scientific paper text to the knowledge graph.

        Args:
            text: The text to save
            name: Optional name for the episode
            domain: The domain of the knowledge ("scientific_paper")

        Returns:
            InsertResponse object indicating success or failure
        """
        logger.debug(
            f"Saving scientific paper text to knowledge graph: {text[:100]}..."
        )
        return self.backend.save(text, name, domain)

    async def async_save(
        self,
        text: str,
        name: Optional[str] = None,
        domain: Literal["scientific_paper"] = "scientific_paper",
    ) -> str:
        """
        Async implementation of the save method.

        Args:
            text: The text to save
            name: Optional name for the episode
            domain: The domain of the knowledge ("scientific_paper")

        Returns:
            The ID of the saved episode
        """
        logger.debug(
            f"Async saving scientific paper text to knowledge graph: {text[:100]}..."
        )
        return await self.backend.async_save(text, name, domain)
