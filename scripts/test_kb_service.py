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


sample_docs = """

# Feature Documentation: [Maestro: Aequor]: Auto Submission: Auto Submission flow Email

## 1. Feature Overview & Identification

*   **Feature Name:** [Maestro: Aequor]: Auto Submission: Auto Submission flow Email
*   **Status:** Released for UAT
*   **Product/Module:** maestro
*   **Brief Description:**
    *   Automates the job application process by allowing candidates to auto-submit applications for their top 3 matched jobs via email.
*   **Business Goal/Value Proposition:**
    *   Streamline and accelerate the application process for candidates, improving engagement and submission rates.
*   **Tags/Keywords:** Auto Submission, Email, Job Matching, Candidate Application

## 2. Business Context & User Focus

*   **Target User(s):**
    *   Candidates using the recruitment platform.
*   **User Problem/Need:**
    *   Want faster application process for best matched jobs.
*   **User Stories / Acceptance Criteria:**
    *   System sends email based on matching criteria (e.g., score ≥ 98%, open jobs, custom field set).
    *   Sends top 3 jobs ensuring different facilities or shifts.
    *   One email per job per day.
    *   Candidate responses trigger auto submission or feedback collection.
    *   Reminder emails sent if no response.
*   **User Journey / Workflow(s) Description:**
    1. System identifies matching jobs.
    2. Sends email to candidate.
    3. Candidate responds with Yes or No.
    4. System processes response and submits or collects feedback.
    5. Reminder sent if needed.
*   **Business Logic & Rules:**
    *   Matching score and candidate status criteria.
    *   Email and SMS templates used.
*   **Success Metrics:**
    *   Increased application submission rates.
    *   Improved feedback loop for matching algorithm.

## 3. User Guide: Using [Maestro: Aequor]: Auto Submission: Auto Submission flow Email

### 3.1. Purpose of this Feature
*   To automate application submissions via email interaction.

### 3.2. Before You Start (Pre-requisites)
*   Candidate must meet auto submission criteria.

### 3.3. Step-by-Step Instructions

*   No manual steps; automated email sending and response processing.

### 3.4. Troubleshooting / FAQs

*   No information provided.

## 4. Additional Information

*   **Training Points:**
    *   Emphasize automation flow and candidate interaction.
*   **Related Features:**
    *   Parent Epic: [Maestro: Aequor] Auto Submission (AHS-91)

## 5. Ownership & Stakeholders

*   **Product Owner:** No information provided.
*   **Tech Lead:** No information provided.
*   **Key Business Stakeholders:** No information provided.
*   **Development Team:** Project_Manager

## 6. Reference Links

*   **Product:** maestro
*   **Project Name:** AHS
*   **Epic ID:** AHS-91
*   **Epic Name:** [Maestro: Aequor] Auto Submission
*   **Epic Status:** Internal UAT
*   **Feature Name:** [Maestro: Aequor]: Auto Submission: Auto Submission flow Email
*   **Ticket ID:** AHS-92
*   **Figma Links:** No information provided.
*   **Docs Links:** No information provided.
*   **Confluence Links:** No information provided.
*   **Gitlab Links:** No information provided.
*   **Team:** Project_Manager

## 7. Actors

*   **Actor 1:**
    *   **Name:** Candidate
    *   **Description:** Recipient of auto submission emails and responder to engagement interactions.
""".strip()


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


if __name__ == "__main__":
    main()
