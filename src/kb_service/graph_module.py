"""
Knowledge Graph Module for the AI-Powered Knowledge Base System.

This module provides a configurable interface to knowledge graph operations
and manages the features list stored in the mermaid diagram.

It supports multiple backend implementations (LightRAG and Graphiti) through a factory pattern.
"""

import os
from typing import Optional, Literal

from src.core.config import (
    KNOWLEDGE_GRAPH_BACKEND,
    FEATURES_LIST_PATH,
    DEFAULT_LLM_MODEL,
)
from src.core.logger import logger
from src.core.models import (
    QueryResponse,
    InsertResponse,
    FeatureUpdateResponse,
)
from src.kb_service.base_knowledge_graph import BaseKnowledgeGraph
from src.kb_service.lightrag_backend import LightRAGKnowledgeGraph
from src.kb_service.graphiti_backend import GraphitiKnowledgeGraph

from litellm import completion
from tenacity import retry, stop_after_attempt, wait_fixed, retry_if_exception_type


class KnowledgeGraphModule:
    """
    Knowledge Graph Module for interacting with the knowledge graph backend and managing the features list.
    """

    def __init__(
        self,
        backend: Optional[str] = None,
        features_path: Optional[str] = None,
        llm_model: Optional[str] = None,
        **backend_kwargs,
    ):
        """
        Initialize the Knowledge Graph Module with the specified backend.

        Args:
            backend: The backend to use ("light_rag" or "graphiti")
            features_path: The path to the features list mermaid diagram
            llm_model: The LLM model to use for updating the features list
            **backend_kwargs: Additional keyword arguments for the backend
        """
        self.backend_name = backend or KNOWLEDGE_GRAPH_BACKEND
        self.features_path = features_path or FEATURES_LIST_PATH
        self.llm_model = llm_model or DEFAULT_LLM_MODEL

        # Initialize the backend using the factory pattern
        self.backend = self._create_backend(**backend_kwargs)

        logger.info(
            f"Initialized Knowledge Graph Module with {self.backend_name} backend"
        )

    def _create_backend(self, **kwargs) -> BaseKnowledgeGraph:
        """
        Create and return the appropriate backend based on configuration.

        Args:
            **kwargs: Additional keyword arguments for the backend

        Returns:
            An instance of a BaseKnowledgeGraph implementation

        Raises:
            ValueError: If the specified backend is not supported
        """
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
        Query the knowledge graph with the given text.

        Args:
            query_text: The query text
            mode: Query mode (local, hybrid, or semantic)
            **kwargs: Additional parameters for the query

        Returns:
            QueryResponse object containing the response from the knowledge graph
        """
        logger.debug(f"Querying knowledge graph with: {query_text}")

        # Delegate to the selected backend
        return self.backend.query(query_text, mode, **kwargs)

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_fixed(2),
        retry=retry_if_exception_type(Exception),
    )
    async def async_query(self, query_text: str, mode: str = "global", **kwargs) -> str:
        """
        Async implementation of the query method.

        Args:
            query_text: The query text
            mode: Query mode (local, hybrid, or semantic)
            **kwargs: Additional parameters for the query

        Returns:
            The response text from the knowledge graph
        """
        logger.debug(f"Async querying knowledge graph with: {query_text}")

        # Delegate to the selected backend's async method
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
        domain: Literal["tech", "business"] = "business",
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
        logger.debug(f"Saving {domain} domain text to knowledge graph: {text[:100]}...")

        # Delegate to the selected backend with all parameters
        return self.backend.save(text, name, domain)

    # @retry(
    #     stop=stop_after_attempt(3),
    #     wait=wait_fixed(2),
    #     retry=retry_if_exception_type(Exception),
    # )
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
        logger.debug(
            f"Async saving {domain} domain text to knowledge graph: {text[:100]}..."
        )

        # Delegate to the selected backend's async method
        return await self.backend.async_save(text, name, domain)

    def get_features_list(self) -> str:
        """
        Get the features list from the mermaid diagram.

        Returns:
            The features list as a string
        """
        try:
            if not os.path.exists(self.features_path):
                logger.error(f"Features list file not found at {self.features_path}")
                return ""
            with open(self.features_path, "r", encoding="utf-8") as file:
                content = file.read()
                logger.debug(f"Read features list from {self.features_path}")
                return content
        except Exception as e:
            error_msg = f"Error reading features list: {str(e)}"
            logger.error(error_msg)
            return ""

    def update_features_list(
        self,
        feature_name: str,
        feature_description: str,
        parent_node: Optional[str] = None,
    ) -> FeatureUpdateResponse:
        """
        Update the features list in the mermaid diagram using LLM.

        Args:
            feature_name: The name of the feature to add or update
            feature_description: The description of the feature
            parent_node: The parent node ID in the mermaid diagram (optional)

        Returns:
            FeatureUpdateResponse object indicating success or failure
        """
        # Read the current mermaid diagram
        current_diagram = self.get_features_list()
        if not current_diagram:
            return FeatureUpdateResponse(
                status="error",
                message="Failed to read current features list",
                updated_diagram="",
            )

        # Prepare the prompt for the LLM
        prompt = self._prepare_update_prompt(
            current_diagram, feature_name, feature_description, parent_node
        )

        try:
            # Call LiteLLM to generate the updated diagram
            messages = [
                {
                    "role": "system",
                    "content": "You are a helpful assistant that specializes in updating mermaid diagrams. Your task is to update a mermaid diagram with a new feature or modify an existing one while maintaining the structure and style of the diagram.",
                },
                {"role": "user", "content": prompt},
            ]

            logger.debug(f"Calling LLM with model {self.llm_model}")
            response = completion(model=self.llm_model, messages=messages)

            # Extract the updated diagram from the LLM response
            content = ""
            try:
                # Handle different response formats from LiteLLM
                # Using type: ignore to bypass static type checking for LiteLLM response objects
                # which can have different structures based on the model and configuration
                if hasattr(response, "choices") and response.choices:  # type: ignore
                    if hasattr(response.choices[0], "message") and hasattr(
                        response.choices[0].message, "content"
                    ):  # type: ignore
                        content = response.choices[0].message.content or ""  # type: ignore
                    elif hasattr(response.choices[0], "text"):  # type: ignore
                        content = response.choices[0].text or ""  # type: ignore
                elif hasattr(response, "content"):  # type: ignore
                    content = response.content or ""  # type: ignore
                elif isinstance(response, dict) and "content" in response:
                    content = response["content"] or ""
                elif isinstance(response, str):
                    content = response
            except Exception as e:
                logger.error(f"Error extracting content from LLM response: {e}")
                content = str(response) if response else ""

            updated_diagram = self._extract_mermaid_from_response(content)

            if not updated_diagram:
                return FeatureUpdateResponse(
                    status="error",
                    message="Failed to extract updated diagram from LLM response",
                    updated_diagram="",
                )

            # Write the updated diagram back to the file
            if not os.path.exists(self.features_path):
                logger.error(f"Features list file not found at {self.features_path}")
                return FeatureUpdateResponse(
                    status="error",
                    message=f"Features list file not found at {self.features_path}",
                    updated_diagram="",
                )
            with open(self.features_path, "w", encoding="utf-8") as file:
                file.write(updated_diagram)
                logger.info(f"Updated features list in {self.features_path}")

            return FeatureUpdateResponse(
                status="success",
                message=f"Successfully updated features list with feature: {feature_name}",
                updated_diagram=updated_diagram,
            )

        except Exception as e:
            error_msg = f"Error updating features list: {str(e)}"
            logger.error(error_msg)
            return FeatureUpdateResponse(
                status="error", message=error_msg, updated_diagram=""
            )

    def _prepare_update_prompt(
        self,
        current_diagram: str,
        feature_name: str,
        feature_description: str,
        parent_node: Optional[str] = None,
    ) -> str:
        """
        Prepare the prompt for the LLM to update the mermaid diagram.

        Args:
            current_diagram: The current mermaid diagram
            feature_name: The name of the feature to add or update
            feature_description: The description of the feature
            parent_node: The parent node ID in the mermaid diagram (optional)

        Returns:
            The prompt for the LLM
        """
        prompt = f"""
I need to update a mermaid diagram that represents a feature hierarchy. Here's the current diagram:

{current_diagram}

I want to {"add a new feature" if not parent_node else f"add a new feature under {parent_node}"} with the following details:
- Feature name: {feature_name}
- Feature description: {feature_description}

Please update the mermaid diagram to include this new feature. Follow these guidelines:
1. Maintain the existing structure and style of the diagram
2. Use the same node ID naming convention as in the existing diagram
3. If a similar feature already exists, update it instead of adding a new one
4. Return ONLY the complete updated mermaid diagram, including the ```mermaid and ``` tags
5. Make sure the syntax is correct and the diagram will render properly

Updated mermaid diagram:
"""
        return prompt

    def _extract_mermaid_from_response(self, response_text: str) -> str:
        """
        Extract the mermaid diagram from the LLM response.

        Args:
            response_text: The LLM response text

        Returns:
            The extracted mermaid diagram
        """
        # Look for content between ```mermaid and ``` tags
        if not response_text or not isinstance(response_text, str):
            logger.error("Invalid response text")
            return ""

        start_marker = "```mermaid"
        end_marker = "```"

        start_index = response_text.find(start_marker)
        if start_index == -1:
            logger.error("Could not find start of mermaid diagram in LLM response")
            return ""

        # Find the end marker after the start marker
        end_index = response_text.find(end_marker, start_index + len(start_marker))
        if end_index == -1:
            logger.error("Could not find end of mermaid diagram in LLM response")
            return ""

        # Extract the diagram including the markers
        diagram = response_text[start_index : end_index + len(end_marker)]
        return diagram
