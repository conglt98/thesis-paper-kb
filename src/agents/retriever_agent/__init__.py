"""
Retriever Agent module for the AI-Powered Knowledge Base System.

This module contains the Retriever Agent implementation for local knowledge base retrieval.
"""

from .agent import (
    RetrieverAgent,
    retriever_agent,
    create_agent,
)

__all__ = [
    "RetrieverAgent",
    "retriever_agent",
    "create_agent",
]
