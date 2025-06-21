"""
Graphiti Knowledge Graph backend for the AI-Powered Knowledge Base System.

This module provides an implementation of the BaseKnowledgeGraph interface using Graphiti.
"""

import asyncio
from typing import Literal, Optional
from datetime import datetime

from src.core.config import (
    NEO4J_URI,
    NEO4J_USER,
    NEO4J_PASSWORD,
    OPENAI_API_KEY,
    GOOGLE_API_KEY,
    GRAPHITI_LLM_PROVIDER,
    GRAPHITI_OPENAI_LLM_MODEL,
    GRAPHITI_OPENAI_EMBEDDING_MODEL,
    GRAPHITI_GEMINI_LLM_MODEL,
    GRAPHITI_GEMINI_EMBEDDING_MODEL,
    GRAPHITI_SEARCH_LIMIT,
    GRAPHITI_SEARCH_MIN_SCORE,
    GRAPHITI_OPENAI_SMALL_LLM_MODEL,
    GRAPHITY_SEARCH_CONFIG,
)
from src.core.logger import logger
from src.core.models import (
    QueryResponse,
    InsertResponse,
)
from src.kb_service.base_knowledge_graph import BaseKnowledgeGraph
from src.kb_service.entities import (
    ScientificPaper,
    Author,
    Affiliation,
    PaperSection,
    Citation,
    Reference,
    Keyword,
    ResearchField,
    ConferenceOrJournal,
)

# Import Graphiti
from graphiti_core import Graphiti
from graphiti_core.llm_client.openai_client import OpenAIClient
from graphiti_core.embedder.openai import OpenAIEmbedder, OpenAIEmbedderConfig
from openai import AsyncOpenAI  # Added for OpenAI client instantiation
from graphiti_core.llm_client.gemini_client import GeminiClient
from graphiti_core.llm_client.config import (
    LLMConfig as GeminiLLMConfig,
)  # Corrected import
from graphiti_core.llm_client.config import (
    LLMConfig as OpenAILLMConfig,
)  # Corrected import
from graphiti_core.embedder.gemini import GeminiEmbedder, GeminiEmbedderConfig
from graphiti_core.nodes import EpisodeType, CommunityNode
from graphiti_core.cross_encoder.openai_reranker_client import OpenAIRerankerClient
from graphiti_core.search.search_config_recipes import (
    COMBINED_HYBRID_SEARCH_RRF,
    COMBINED_HYBRID_SEARCH_MMR,
    COMBINED_HYBRID_SEARCH_CROSS_ENCODER,
    NODE_HYBRID_SEARCH_NODE_DISTANCE,
    NODE_HYBRID_SEARCH_RRF,
)


class GraphitiKnowledgeGraph(BaseKnowledgeGraph):
    """
    Graphiti Knowledge Graph implementation for interacting with the Graphiti API, focused on scientific paper knowledge base.
    """

    def __init__(
        self,
        neo4j_uri: Optional[str] = None,
        neo4j_user: Optional[str] = None,
        neo4j_password: Optional[str] = None,
    ):
        """
        Initialize the Graphiti Knowledge Graph.

        Args:
            neo4j_uri: The URI of the Neo4j database
            neo4j_user: The Neo4j username
            neo4j_password: The Neo4j password
        """
        self.neo4j_uri = neo4j_uri or NEO4J_URI
        self.neo4j_user = neo4j_user or NEO4J_USER
        self.neo4j_password = neo4j_password or NEO4J_PASSWORD

        # Initialize the Graphiti client
        self.graphiti = None
        self.initialized = False

        logger.info(
            f"Initialized Graphiti Knowledge Graph with Neo4j at {self.neo4j_uri}"
        )

    async def _ensure_initialized(self):
        """
        Ensure that the Graphiti client is initialized.
        """
        if not self.initialized or not self.graphiti:
            try:
                llm_client = None
                embedder = None
                cross_encoder = None

                if GRAPHITI_LLM_PROVIDER.lower() == "openai":
                    if not OPENAI_API_KEY:
                        raise ValueError(
                            "OPENAI_API_KEY must be set for OpenAI provider."
                        )

                    async_openai_client = AsyncOpenAI(api_key=OPENAI_API_KEY)

                    llm_config = OpenAILLMConfig(
                        # api_key=OPENAI_API_KEY,
                        model=GRAPHITI_OPENAI_LLM_MODEL,
                        small_model=GRAPHITI_OPENAI_SMALL_LLM_MODEL,
                        # max_tokens=32768,
                    )

                    llm_client = OpenAIClient(
                        client=async_openai_client,
                        config=llm_config,
                    )
                    embedder = OpenAIEmbedder(
                        client=async_openai_client,
                        config=OpenAIEmbedderConfig(
                            embedding_model=GRAPHITI_OPENAI_EMBEDDING_MODEL
                            # api_key is handled by the async_openai_client
                        ),
                    )
                    cross_encoder = OpenAIRerankerClient(client=async_openai_client)
                    logger.info(
                        f"Using OpenAI provider for Graphiti with model {GRAPHITI_OPENAI_LLM_MODEL=}, {GRAPHITI_OPENAI_SMALL_LLM_MODEL=}, {GRAPHITI_OPENAI_EMBEDDING_MODEL=}"
                    )
                elif GRAPHITI_LLM_PROVIDER.lower() == "gemini":
                    if not GOOGLE_API_KEY:
                        raise ValueError(
                            "GOOGLE_API_KEY must be set for Gemini provider."
                        )
                    llm_client = GeminiClient(
                        config=GeminiLLMConfig(
                            api_key=GOOGLE_API_KEY, model=GRAPHITI_GEMINI_LLM_MODEL
                        )
                    )
                    embedder = GeminiEmbedder(
                        config=GeminiEmbedderConfig(
                            api_key=GOOGLE_API_KEY,
                            embedding_model=GRAPHITI_GEMINI_EMBEDDING_MODEL,
                        )
                    )
                    logger.info(
                        f"Using Gemini provider for Graphiti with model {GRAPHITI_GEMINI_LLM_MODEL=}, {GRAPHITI_GEMINI_EMBEDDING_MODEL=}"
                    )
                else:
                    logger.warning(
                        f"Unsupported GRAPHITI_LLM_PROVIDER: {GRAPHITI_LLM_PROVIDER}. "
                        f"Graphiti will use its default LLM and embedder configuration (OpenAI)."
                    )
                    # Optionally, ensure OPENAI_API_KEY is set for default Graphiti behavior or raise error
                    if not OPENAI_API_KEY and not (
                        llm_client and embedder
                    ):  # if not explicitly configured and defaults to OpenAI
                        logger.warning(
                            "OPENAI_API_KEY is not set. Graphiti might fail if it defaults to OpenAI without an API key."
                        )

                self.graphiti = Graphiti(
                    self.neo4j_uri,
                    self.neo4j_user,
                    self.neo4j_password,
                    llm_client=llm_client,  # Can be None, Graphiti defaults to OpenAI
                    embedder=embedder,  # Can be None, Graphiti defaults to OpenAI
                    cross_encoder=cross_encoder,  # Can be None
                )

                # Initialize the graph database with indices
                await self.graphiti.build_indices_and_constraints()

                self.initialized = True
                logger.info("Graphiti client initialized successfully")
            except Exception as e:
                error_msg = f"Error initializing Graphiti client: {str(e)}"
                logger.error(error_msg)
                raise RuntimeError(error_msg)

    def query(self, query_text: str, mode: str = "global", **kwargs) -> QueryResponse:
        """
        Query the knowledge graph with the given text.

        Args:
            query_text: The query text
            mode: Query mode (not used in Graphiti, kept for interface compatibility)
            **kwargs: Additional parameters for the query

        Returns:
            QueryResponse object containing the response from the knowledge graph
        """
        logger.debug(f"Querying Graphiti knowledge graph with: {query_text}")

        try:
            # Run the async query in a new event loop
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            response_text = loop.run_until_complete(
                self.async_query(query_text, **kwargs)
            )
            loop.close()

            return QueryResponse(
                response=response_text, status="success", error_message=None
            )

        except Exception as e:
            error_msg = f"Error querying Graphiti knowledge graph: {str(e)}"
            logger.error(error_msg)
            return QueryResponse(response="", status="error", error_message=error_msg)

    async def async_query(self, query_text: str, mode: str = "global", **kwargs) -> str:
        """
        Async implementation of the query method.

        Args:
            query_text: The query text
            **kwargs: Additional parameters for the query

        Returns:
            The response text from the knowledge graph
        """
        await self._ensure_initialized()

        mode = kwargs.get("mode", GRAPHITY_SEARCH_CONFIG)
        logger.info(f"Using mode: {mode}")

        if mode == "deep":
            node_search_config = COMBINED_HYBRID_SEARCH_RRF.model_copy()
        elif mode == "broad":
            node_search_config = COMBINED_HYBRID_SEARCH_MMR.model_copy()
        else:
            raise ValueError(f"Invalid mode: {mode}")

        # Set limit from environment config or kwargs if provided
        if "top_k" in kwargs and kwargs["top_k"]:
            node_search_config.limit = kwargs["top_k"]
        else:
            node_search_config.limit = GRAPHITI_SEARCH_LIMIT

        # Set reranker_min_score from environment config or kwargs if provided
        if "reranker_min_score" in kwargs and kwargs["reranker_min_score"]:
            node_search_config.reranker_min_score = kwargs["reranker_min_score"]
        else:
            node_search_config.reranker_min_score = GRAPHITI_SEARCH_MIN_SCORE

        # Use the search method from Graphiti based on the documentation
        if not self.graphiti or not self.initialized:
            error_msg = "Graphiti client not initialized"
            logger.error(error_msg)
            raise RuntimeError(error_msg)

        search_results = await self.graphiti._search(
            query=query_text, config=node_search_config
        )

        # Process and format the results
        response_parts = []

        # Process nodes
        if search_results and hasattr(search_results, "nodes") and search_results.nodes:
            response_parts.append(
                f"Found {len(search_results.nodes)} relevant entities with format: <node name>: <node summary> : <node attributes |>"
            )

            for i, node in enumerate(search_results.nodes, 1):
                # Get basic node information
                node_type = (
                    node.labels[0]
                    if hasattr(node, "labels") and node.labels
                    else "Entity"
                )
                name = node.name if hasattr(node, "name") else "Unnamed entity"

                # Get node description from summary or attributes
                description = ""
                if hasattr(node, "summary") and node.summary:
                    description = node.summary
                else:
                    logger.debug(f"Node {node.name} has no summary")

                # Format all attributes as additional context
                context_info = ""
                if hasattr(node, "attributes") and node.attributes:
                    # Add all other attributes as context
                    logger.debug(f"Node {node.name} has attributes: {node.attributes}")
                    for key, value in node.attributes.items():
                        if key == "description":
                            continue
                        context_info += f" | {key}: {value}"
                else:
                    logger.debug(f"Node {node.name} has no attributes")

                if not description:
                    description = "No description available"

                response_parts.append(f"{i}. {name}: {description}{context_info}")

        # Process edges
        if search_results and hasattr(search_results, "edges") and search_results.edges:
            response_parts.append(
                f"\nFound {len(search_results.edges)} relevant relationships with format: <edge name>: <edge fact> : "
            )

            for i, edge in enumerate(search_results.edges, 1):
                # Extract edge information using generic attribute access
                relationship = edge.fact

                response_parts.append(f"{i}. {edge.name}: {relationship}")

        # Process communities
        if (
            search_results
            and hasattr(search_results, "communities")
            and search_results.communities
        ):
            response_parts.append(
                f"\nFound {len(search_results.communities)} relevant communities nodes with format: <community name>: <community summary> :"
            )
            for i, community in enumerate(search_results.communities, 1):
                name = community.name if hasattr(community, "name") else ""
                summary = (
                    community.summary
                    if hasattr(community, "summary") and community.summary
                    else ""
                )
                response_parts.append(f"{i}. {name}: {summary}")

        return "\n\n".join(response_parts)

    async def async_save(
        self,
        text: str,
        name: str | None = None,
        domain: Literal["scientific_paper"] = "scientific_paper",
    ) -> str:
        """
        Async implementation of the save method. Routes to the appropriate domain-specific
        save method based on the domain parameter.

        Args:
            text: The text to save
            name: Optional name for the episode
            domain: The domain of the knowledge ("scientific_paper")

        Returns:
            The ID of the saved episode
        """
        # Route to the scientific paper save method
        return await self.save_scientific_paper(text, name)

    async def save_scientific_paper(self, text: str, name: str | None = None) -> str:
        """
        Save scientific paper knowledge to the graph. This method handles scientific paper entities.

        Args:
            text: The text containing scientific paper knowledge to save
            name: Optional name for the episode

        Returns:
            The ID of the saved episode
        """
        await self._ensure_initialized()
        episode_name = (
            name or f"scientific_paper_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        )

        logger.info(
            f"Adding episode to Graphiti with scientific paper entity types: {ScientificPaper}"
        )

        if self.graphiti and self.initialized:
            result = await self.graphiti.add_episode(
                name=episode_name,
                episode_body=text,
                source=EpisodeType.text,
                source_description="Scientific Paper Knowledge Entry",
                reference_time=datetime.now(),
                entity_types={
                    "ScientificPaper": ScientificPaper,
                    "Author": Author,
                    "Affiliation": Affiliation,
                    "PaperSection": PaperSection,
                    "Citation": Citation,
                    "Reference": Reference,
                    "Keyword": Keyword,
                    "ResearchField": ResearchField,
                    "ConferenceOrJournal": ConferenceOrJournal,
                },
            )
            logger.info(
                f"Added scientific paper episode to Graphiti with custom entity types: {episode_name}"
            )
            return episode_name
        else:
            error_msg = "Graphiti client not initialized"
            logger.error(error_msg)
            raise RuntimeError(error_msg)

    def save(
        self,
        text: str,
        name: str | None = None,
        domain: Literal["scientific_paper"] = "scientific_paper",
    ) -> InsertResponse:
        """
        Save the given text to the knowledge graph.

        Args:
            text: The text to save

        Returns:
            InsertResponse object indicating success or failure
        """
        logger.debug(f"Saving text to Graphiti knowledge graph: {text[:100]}...")

        try:
            # Run the async save in a new event loop
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            result = loop.run_until_complete(self.async_save(text, name, domain))
            loop.close()

            return InsertResponse(
                status="success",
                message=f"Successfully saved text to Graphiti knowledge graph with ID: {result}",
            )

        except Exception as e:
            error_msg = f"Error saving to Graphiti knowledge graph: {str(e)}"
            logger.error(error_msg)
            return InsertResponse(status="error", message=error_msg)
