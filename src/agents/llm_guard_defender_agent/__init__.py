"""
LLM Guard Defender Agent module for the AI-Powered Knowledge Base System.

This module contains the LLM Guard Defender Agent implementation for prompt injection defense.
"""

from .agent import (
    LlmGuardDefenderAgent,
    llm_guard_defender_agent,
    create_agent,
)

__all__ = [
    "LlmGuardDefenderAgent",
    "llm_guard_defender_agent",
    "create_agent",
]
