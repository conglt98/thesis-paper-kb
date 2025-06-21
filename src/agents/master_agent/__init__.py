"""
Master Agent module for the AI-Powered Knowledge Base System.

This module contains the Master Agent implementation for orchestrating all sub-agents.
"""

from .agent import (
    MasterAgent,
    master_agent,
    master_agent_instance,
    root_agent,
)

__all__ = [
    "MasterAgent",
    "master_agent",
    "master_agent_instance",
    "root_agent",
]
