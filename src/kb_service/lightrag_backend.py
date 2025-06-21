"""
LightRAG Knowledge Graph backend for the Scientific Paper Knowledge Base System.

This module provides an implementation of the BaseKnowledgeGraph interface using LightRAG for scientific paper knowledge.
"""

import requests
import aiohttp
from typing import Optional, Literal
import lightrag.utils

from src.core.config import (
    LIGHT_RAG_SERVER_URL,
    LIGHT_RAG_API_KEY,
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


def my_process_combine_contexts(hl_context, ll_context):
    if isinstance(hl_context, str):
        hl_context = []
    if isinstance(ll_context, str):
        ll_context = []
    seen_content = {}
    combined_data = []
    for item in hl_context + ll_context:
        content_dict = {k: v for k, v in item.items() if k != "id"}
        content_key = tuple(sorted(content_dict.items()))
        if content_key not in seen_content:
            seen_content[content_key] = item
            combined_data.append(item)
    for i, item in enumerate(combined_data):
        item["id"] = str(i)
    return combined_data


lightrag.utils.process_combine_contexts = my_process_combine_contexts


class LightRAGKnowledgeGraph(BaseKnowledgeGraph):
    """
    LightRAG Knowledge Graph implementation for interacting with the LightRAG server for scientific paper knowledge.
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
            llm_model: (Unused, kept for compatibility)
        """
        self.base_url = base_url or LIGHT_RAG_SERVER_URL
        self.api_key = api_key or LIGHT_RAG_API_KEY
        self.llm_model = llm_model or DEFAULT_LLM_MODEL

        logger.info(
            f"Initialized LightRAG Knowledge Graph with server at {self.base_url}"
        )

        # Create headers with API key if provided
        self.headers = {}
        if self.api_key:
            self.headers["Authorization"] = f"Bearer {self.api_key}"

    def query(self, query_text: str, mode: str = "local", **kwargs) -> QueryResponse:
        """
        Query the scientific paper knowledge base (LightRAG) with the given text.

        Args:
            query_text: The query text
            mode: Query mode (local, global, hybrid, naive, mix, bypass)
            **kwargs: Additional parameters for the query

        Returns:
            QueryResponse object containing the response from the knowledge base
        """
        endpoint = f"{self.base_url}/query"
        payload = QueryRequest(query=query_text, mode=mode, **kwargs).dict(
            exclude_none=True
        )
        logger.debug(f"Querying LightRAG knowledge graph with: {payload}")
        try:
            response = requests.post(endpoint, json=payload, headers=self.headers)
            response.raise_for_status()
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
        Async implementation of the query method for scientific paper knowledge.

        Args:
            query_text: The query text
            mode: Query mode (local, global, hybrid, naive, mix, bypass)
            **kwargs: Additional parameters for the query

        Returns:
            The response text from the knowledge base
        """
        endpoint = f"{self.base_url}/query"
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
            return data.get("response", "")
        except (aiohttp.ClientError, ValueError) as e:
            error_msg = f"Error async querying LightRAG knowledge graph: {str(e)}"
            logger.error(error_msg)
            raise RuntimeError(error_msg)

    def save(
        self, text: str, name: Optional[str] = None, domain: str = "scientific_paper"
    ) -> InsertResponse:
        """
        Save the given scientific paper text to the knowledge base (LightRAG).

        Args:
            text: The text to save
            name: (Unused in LightRAG API)
            domain: (Unused in LightRAG API, always "scientific_paper")

        Returns:
            InsertResponse object indicating success or failure
        """
        endpoint = f"{self.base_url}/documents/text"
        payload = InsertTextRequest(text=text).dict()
        logger.debug(
            f"Saving scientific paper text to LightRAG knowledge graph: {text[:100]}..."
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
        domain: Literal["scientific_paper"] = "scientific_paper",
    ) -> str:
        """
        Async implementation of the save method for scientific paper knowledge.

        Args:
            text: The text to save
            name: (Unused in LightRAG API)
            domain: (Unused in LightRAG API, always "scientific_paper")

        Returns:
            The ID of the saved episode or a status message
        """
        endpoint = f"{self.base_url}/documents/text"
        payload = InsertTextRequest(text=text).dict()
        logger.debug(
            f"Async saving scientific paper text to LightRAG knowledge graph: {text[:100]}..."
        )
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    endpoint, json=payload, headers=self.headers
                ) as response:
                    response.raise_for_status()
                    data = await response.json()
            logger.debug(f"Received async response: {data}")
            return data.get("id", str(data.get("status", "success")))
        except (aiohttp.ClientError, ValueError) as e:
            error_msg = f"Error async saving to LightRAG knowledge graph: {str(e)}"
            logger.error(error_msg)
            raise RuntimeError(error_msg)
