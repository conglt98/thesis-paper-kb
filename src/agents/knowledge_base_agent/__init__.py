"""
Knowledge Base Agent module for the AI-Powered Knowledge Base System.

This module contains the Knowledge Base Agent implementation and its associated tools
for handling knowledge base retrieval.
"""

from .agent import (
    KnowledgeBaseAgent,
    knowledge_base_agent,
    knowledge_base_agent_instance,
)

__all__ = [
    "KnowledgeBaseAgent",
    "knowledge_base_agent",
    "knowledge_base_agent_instance",
]