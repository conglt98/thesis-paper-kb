#!/usr/bin/env python
"""
Test script for the Knowledge Base Service API with configurable backends.

This script demonstrates how to use the Knowledge Base Service with different backends.
"""

import os
import sys
import asyncio
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Add the project root to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.core.logger import logger
from src.kb_service.api import KnowledgeBaseService
from src.kb_service.graph_module import KnowledgeGraphModule

from src.core.config import (
    KNOWLEDGE_GRAPH_BACKEND,
    NEO4J_URI,
    NEO4J_USER,
    NEO4J_PASSWORD,
)

logger.info(f"KNOWLEDGE_GRAPH_BACKEND: {KNOWLEDGE_GRAPH_BACKEND}")
logger.info(f"NEO4J_URI: {NEO4J_URI}")
logger.info(f"NEO4J_USER: {NEO4J_USER}")
logger.info(f"NEO4J_PASSWORD: {NEO4J_PASSWORD}")

sample_paper = """
# Scientific Paper: Deep Learning for NLP

## Abstract
This paper explores the application of deep learning techniques to natural language processing tasks.

## Authors
- Alice Smith
- Bob Johnson

## Publication Year
2024

## DOI
10.1234/dlnlp.2024.001

## Keywords
- Deep Learning
- NLP
- Transformers

## Sections
### Introduction
Deep learning has revolutionized NLP in recent years...

### Methods
We use transformer-based models...

### Results
Our experiments show...

### Conclusion
Deep learning models achieve state-of-the-art results on many NLP tasks.
"""


def test_lightrag_backend():
    """Test the Knowledge Base Service with LightRAG backend."""
    # Override the environment variable to use LightRAG backend
    os.environ["KNOWLEDGE_GRAPH_BACKEND"] = "light_rag"

    # Initialize the Knowledge Base Service with LightRAG backend
    kb_service = KnowledgeBaseService()

    logger.info("Testing Knowledge Base Service with LightRAG backend...")

    # Test query
    response = kb_service.query_knowledge("What are the main features of our product?")
    logger.info(f"Query response: {response}")

    # Test save
    result = kb_service.save_knowledge(
        text="Our product includes a configurable knowledge graph module that supports both LightRAG and Graphiti backends.",
        team_name="core",
        feature_name="knowledge_graph",
        knowledge_type="technical",
    )
    logger.info(f"Save result: {result}")

    # Test features list
    features_list = kb_service.get_features_list()
    logger.info(f"Features list length: {len(features_list)} characters")

    # Test update features list
    update_result = kb_service.update_features_list(
        feature_name="Configurable Knowledge Graph",
        feature_description="A knowledge graph module that supports multiple backends",
    )
    logger.info(f"Update features list result: {update_result}")


async def test_graphiti_backend():
    """Test the Knowledge Base Service with Graphiti backend."""
    # Override the environment variable to use Graphiti backend
    os.environ["KNOWLEDGE_GRAPH_BACKEND"] = "graphiti"

    # Initialize the Knowledge Base Service with Graphiti backend
    kb_service = KnowledgeGraphModule()

    logger.info("Testing Knowledge Base Service with Graphiti backend...")
    # Test save
    # result = await kb_service.async_save(
    #     text=sample_docs,
    #     name="Test Knowledge Graph",
    #     domain="business",
    # )
    # logger.info(f"Save result: {result}")

    # Test query
    # response = await kb_service.async_query("How the auto submission feature works?")
    # response = await kb_service.async_query("What is Maestro?")
    # response = await kb_service.async_query("How matching score work?")
    response = await kb_service.async_query(
        "What candidate will see when they first login to the candidate portal?"
    )
    logger.info(f"Query response: {response}")


def main():
    """Main function to run the tests."""
    # Test LightRAG backend
    # test_lightrag_backend()

    # Test Graphiti backend
    asyncio.run(test_graphiti_backend())

    # Example usage of KnowledgeBaseService for scientific paper
    service = KnowledgeBaseService()
    # Save the sample paper
    result = service.markdown_module.save(
        text=sample_paper,
        paper_title="Deep Learning for NLP",
        doi="10.1234/dlnlp.2024.001",
    )
    print(f"Save result: {result}")
    # List papers
    papers = service.markdown_module.list_papers()
    print(f"Papers in knowledge base: {papers}")


if __name__ == "__main__":
    main()
