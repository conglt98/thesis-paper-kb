"""
LightRAG Knowledge Graph backend for the AI-Powered Knowledge Base System.

This module provides an implementation of the BaseKnowledgeGraph interface using LightRAG.
"""

import requests
import aiohttp
from typing import Optional, Literal

from src.core.config import (
    LIGHT_RAG_SERVER_URL,
    LIGHT_RAG_API_KEY,
    FEATURES_LIST_PATH,
    DEFAULT_LLM_MODEL,
)
from src.core.logger import logger
from src.core.models import (
    QueryRequest,
    QueryResponse,
    InsertTextRequest,
    InsertResponse,
)
from src.kb_service.base_knowledge_graph import BaseKnowledgeGraph


class LightRAGKnowledgeGraph(BaseKnowledgeGraph):
    """
    LightRAG Knowledge Graph implementation for interacting with the LightRAG server and managing the features list.
    """

    def __init__(
        self,
        base_url: Optional[str] = None,
        api_key: Optional[str] = None,
        llm_model: Optional[str] = None,
    ):
        """
        Initialize the LightRAG Knowledge Graph.

        Args:
            base_url: The base URL of the LightRAG server
            api_key: The API key for the LightRAG server
            llm_model: The LLM model to use for feature list management
        """
        self.base_url = base_url or LIGHT_RAG_SERVER_URL
        self.api_key = api_key or LIGHT_RAG_API_KEY
        self.llm_model = llm_model or DEFAULT_LLM_MODEL
        self.features_path = FEATURES_LIST_PATH

        logger.info(
            f"Initialized LightRAG Knowledge Graph with server at {self.base_url}"
        )

        # Create headers with API key if provided
        self.headers = {}
        if self.api_key:
            self.headers["Authorization"] = f"Bearer {self.api_key}"

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
        endpoint = f"{self.base_url}/query"

        # Prepare request payload
        payload = QueryRequest(query=query_text, mode=mode, **kwargs).dict(
            exclude_none=True
        )

        logger.debug(f"Querying LightRAG knowledge graph with: {payload}")

        try:
            response = requests.post(endpoint, json=payload, headers=self.headers)
            response.raise_for_status()

            # Parse the response JSON
            data = response.json()

            return QueryResponse(
                response=data.get("response", ""), status="success", error_message=None
            )

        except requests.exceptions.RequestException as e:
            error_msg = f"Error querying LightRAG knowledge graph: {str(e)}"
            logger.error(error_msg)
            return QueryResponse(response="", status="error", error_message=error_msg)

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
        endpoint = f"{self.base_url}/query"

        # Prepare request payload
        payload = QueryRequest(query=query_text, mode=mode, **kwargs).dict(
            exclude_none=True
        )

        logger.debug(f"Async querying LightRAG knowledge graph with: {payload}")

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    endpoint, json=payload, headers=self.headers
                ) as response:
                    response.raise_for_status()
                    data = await response.json()

            # Return the response text
            return data.get("response", "")

        except (aiohttp.ClientError, ValueError) as e:
            error_msg = f"Error async querying LightRAG knowledge graph: {str(e)}"
            logger.error(error_msg)
            raise RuntimeError(error_msg)

    def save(
        self, text: str, name: Optional[str] = None, domain: str = "tech"
    ) -> InsertResponse:
        """
        Save the given text to the knowledge graph.

        Args:
            text: The text to save
            name: Optional name for the episode (not used in LightRAG implementation)
            domain: The domain of the knowledge ("tech" or "business") (not used in LightRAG implementation)

        Returns:
            InsertResponse object indicating success or failure
        """
        endpoint = f"{self.base_url}/documents/text"

        # Prepare request payload
        # Note: LightRAG doesn't support name and domain parameters, so we only use the text
        payload = InsertTextRequest(text=text).dict()

        # Log domain information even though it's not used in the API call
        logger.debug(
            f"Saving {domain} domain text to LightRAG knowledge graph: {text[:100]}..."
        )

        try:
            response = requests.post(endpoint, json=payload, headers=self.headers)
            response.raise_for_status()

            data = response.json()
            logger.debug(f"Received response: {data}")

            return InsertResponse(
                status=data.get("status", "error"), message=data.get("message", "")
            )

        except requests.exceptions.RequestException as e:
            error_msg = f"Error saving to LightRAG knowledge graph: {str(e)}"
            logger.error(error_msg)
            return InsertResponse(status="error", message=error_msg)

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
            name: Optional name for the episode (not used in LightRAG implementation)
            domain: The domain of the knowledge ("tech" or "business") (not used in LightRAG implementation)

        Returns:
            The ID of the saved episode
        """
        endpoint = f"{self.base_url}/documents/text"

        # Prepare request payload
        # Note: LightRAG doesn't support name and domain parameters, so we only use the text
        payload = InsertTextRequest(text=text).dict()

        # Log domain information even though it's not used in the API call
        logger.debug(
            f"Async saving {domain} domain text to LightRAG knowledge graph: {text[:100]}..."
        )

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    endpoint, json=payload, headers=self.headers
                ) as response:
                    response.raise_for_status()
                    data = await response.json()

            logger.debug(f"Received async response: {data}")

            # Return document ID or a status message
            return data.get("id", str(data.get("status", "success")))

        except (aiohttp.ClientError, ValueError) as e:
            error_msg = f"Error async saving to LightRAG knowledge graph: {str(e)}"
            logger.error(error_msg)
            raise RuntimeError(error_msg)
