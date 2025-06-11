"""
Logging configuration for the AI-Powered Knowledge Base System.
"""

import sys
from loguru import logger
from src.core.config import LOG_LEVEL

# Remove default logger
logger.remove()

# Add stderr handler with the configured log level
logger.add(sys.stderr, level=LOG_LEVEL)

# Optionally add file logging for production environments
# logger.add("logs/kb_system_{time}.log", rotation="10 MB", level=LOG_LEVEL)

# Export the configured logger
__all__ = ["logger"]
