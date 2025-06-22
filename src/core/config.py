"""
Configuration module for the AI-Powered Knowledge Base System.
"""

import os
from pathlib import Path

# Base paths
PROJECT_ROOT = Path(__file__).parent.parent.parent.absolute()
INPUTS_DIR = os.path.join(PROJECT_ROOT, "inputs")
CACHE_DIR = os.path.join(PROJECT_ROOT, ".cache")
DOWNLOADS_DIR = os.path.join(
    PROJECT_ROOT, "downloads"
)  # Directory for all downloaded files

# Ensure cache and downloads directories exist
Path(CACHE_DIR).mkdir(exist_ok=True, parents=True)
Path(DOWNLOADS_DIR).mkdir(exist_ok=True, parents=True)

# Knowledge Graph Backend Configuration
# Options: "light_rag" or "graphiti"
KNOWLEDGE_GRAPH_BACKEND = os.getenv("KNOWLEDGE_GRAPH_BACKEND", "light_rag")

# LightRAG Server Configuration
# Construct the URL from HOST and PORT environment variables
LIGHT_RAG_HOST = os.getenv("LIGHT_RAG_HOST", "localhost")
LIGHT_RAG_PORT = os.getenv("PORT", "8000")
# LIGHT_RAG_SERVER_URL = f"http://{LIGHT_RAG_HOST}:{LIGHT_RAG_PORT}"
LIGHT_RAG_SERVER_URL = "http://localhost:9621"
LIGHT_RAG_API_KEY = os.getenv("LIGHT_RAG_API_KEY", "")

# Graphiti/Neo4j Configuration
NEO4J_URI = os.getenv("NEO4J_URI", "bolt://localhost:7687")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "password").replace(" ", "=")
GRAPHITI_SEARCH_LIMIT = int(os.getenv("GRAPHITI_SEARCH_LIMIT", "50"))
GRAPHITI_SEARCH_MIN_SCORE = float(os.getenv("GRAPHITI_SEARCH_MIN_SCORE", "0.2"))
GRAPHITY_SEARCH_CONFIG = os.getenv(
    "GRAPHITY_SEARCH_CONFIG", "broad"
)  # Options: "deep" or "broad"

# Features List Configuration
FEATURES_LIST_PATH = os.path.join(INPUTS_DIR, "mermaid_list_features.md")

# LLM Configuration
DEFAULT_LLM_MODEL = os.getenv("DEFAULT_LLM_MODEL", "openai/gpt-4.1-mini")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "")

# Graphiti LLM Configuration
GRAPHITI_LLM_PROVIDER = os.getenv(
    "GRAPHITI_LLM_PROVIDER", "openai"
)  # "openai" or "gemini"
GRAPHITI_OPENAI_LLM_MODEL = os.getenv("GRAPHITI_OPENAI_LLM_MODEL", "gpt-4.1-mini")
GRAPHITI_OPENAI_SMALL_LLM_MODEL = os.getenv(
    "GRAPHITI_OPENAI_SMALL_LLM_MODEL", "gpt-4.1-nano"
)
GRAPHITI_OPENAI_EMBEDDING_MODEL = os.getenv(
    "GRAPHITI_OPENAI_EMBEDDING_MODEL", "text-embedding-3-small"
)
GRAPHITI_GEMINI_LLM_MODEL = os.getenv(
    "GRAPHITI_GEMINI_LLM_MODEL", "gemini-2.5-flash-latest"
)  # Changed from gemini-2.0-flash as per common model names
GRAPHITI_GEMINI_EMBEDDING_MODEL = os.getenv(
    "GRAPHITI_GEMINI_EMBEDDING_MODEL", "embedding-001"
)

# Markdown Storage Configuration
MARKDOWN_ROOT_PATH = os.getenv(
    "MARKDOWN_ROOT_PATH", os.path.join(PROJECT_ROOT, "kb_markdown_files")
)

# Logging Configuration
LOG_LEVEL = os.getenv("LOG_LEVEL", "DEBUG")
