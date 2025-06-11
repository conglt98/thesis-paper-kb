# Use Python 3.12 slim image as base
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install uv package manager
RUN pip install uv

# Copy only dependency files first (for better caching)
COPY pyproject.toml uv.lock ./

# Install Python dependencies using uv (this layer will be cached)
RUN uv sync --frozen

# Build argument for cache busting (used by rebuild command)
ARG CACHE_BUST
ARG REBUILD_MODE=false

# Copy source code (this layer will be invalidated during rebuild)
COPY src/ ./src/

# Set environment variables
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# Expose default FastMCP port (can be overridden)
EXPOSE 8000

# Default command - can be overridden when running the container
CMD ["uv", "run", "fastmcp", "run", "src/mcp/greetings.py:mcp"]
