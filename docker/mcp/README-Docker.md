# Docker Setup for Scientific Paper Knowledge Base FastMCP Server

This document provides instructions for building and running the Scientific Paper Knowledge Base FastMCP server using Docker.

## ⚡ Optimized Build Commands (Recommended)

We've optimized the Docker build process for maximum development efficiency. Use the enhanced build script for faster builds:

```bash
# First build - installs all dependencies
./docker/mcp/docker-build.sh build

# Fast rebuilds - only recompiles code changes (30x faster!)
./docker/mcp/docker-build.sh rebuild

# Super fast rebuilds - with BuildKit caching (50x faster!)
./docker/mcp/docker-build.sh fast-rebuild

# Development mode - live code reload (instant!)
./docker/mcp/docker-build.sh dev
```

**Performance comparison:**
- `build`: ~3 minutes (first time, dependency changes)
- `rebuild`: ~45 seconds (code changes only)
- `fast-rebuild`: ~20 seconds (maximum caching)
- `dev`: ~5 seconds (live reload)

For detailed optimization information, see [docs/docker-optimization.md](docs/docker-optimization.md).

## Quick Start

### 1. Build the Docker Image

```bash
# Build the image (optimized)
./docker/mcp/docker-build.sh build

# Or traditional Docker build
docker build -f docker/mcp/Dockerfile -t central-knowledge-base .
```

### 2. Run the FastMCP Server

```bash
# Run with the optimized script
./docker/mcp/docker-build.sh run

# Or traditional Docker run
docker run -i --rm --name fastmcp-server -p 8000:8000 central-knowledge-base

# Run with agent interaction configuration
docker run -i --rm --name fastmcp-server -p 8000:8000 \
  -e URL_AGENT="http://0.0.0.0:8000" \
  -e USER_ID="u_123" \
  -e SESSION_ID="s_123" \
  -e AGENT_APPS="scientific_paper_knowledge_base_agent" \
  central-knowledge-base
```

### 3. Test the Server

The FastMCP server will be running and accessible. You can test it by connecting an MCP client to `stdio` transport or checking the server status.

## Docker Commands

### Enhanced Build Script Commands

```bash
# Show all available commands
./docker/mcp/docker-build.sh --help

# Build commands
./docker/mcp/docker-build.sh build        # Full build
./docker/mcp/docker-build.sh rebuild      # Smart rebuild (fast)
./docker/mcp/docker-build.sh fast-rebuild # Maximum speed rebuild

# Runtime commands
./docker/mcp/docker-build.sh run          # Production mode
./docker/mcp/docker-build.sh dev          # Development mode with live reload
./docker/mcp/docker-build.sh stop         # Stop containers
./docker/mcp/docker-build.sh logs         # View logs
./docker/mcp/docker-build.sh clean        # Clean up images

# Custom options
./docker/mcp/docker-build.sh run -p 9000  # Custom port
./docker/mcp/docker-build.sh run -n my-server  # Custom container name
```

### Basic Docker Commands

```bash
# Build the image
docker build -f docker/mcp/Dockerfile -t central-knowledge-base .

# Run the container (default: stdio transport)
docker run -i central-knowledge-base

# Run with custom command
docker run -i central-knowledge-base uv run fastmcp run src/mcp/greetings.py:mcp

# Run in background with port mapping
docker run -d --name fastmcp-server -p 8000:8000 central-knowledge-base

# Run with HTTP transport
docker run -d --name fastmcp-http -p 8001:8001 central-knowledge-base \
  uv run fastmcp run src/mcp/greetings.py:mcp --transport streamable-http --host 0.0.0.0 --port 8001

# View logs
docker logs -f fastmcp-server

# Stop and remove container
docker stop fastmcp-server
docker rm fastmcp-server
```

### Using Docker Compose

```bash
# Navigate to the docker/mcp directory
cd docker/mcp

# Start with default stdio transport
docker-compose up fastmcp-server

# Start with HTTP transport
docker-compose up fastmcp-server-http

# Run in background
docker-compose up -d fastmcp-server

# View logs
docker-compose logs -f fastmcp-server

# Stop services
docker-compose down
```

### Using the Build Script

The `docker/mcp/docker-build.sh` script provides convenient commands:

```bash
# Build the image
./docker/mcp/docker-build.sh build

# Run the server
./docker/mcp/docker-build.sh run

# Run on custom port
./docker/mcp/docker-build.sh run -p 8080

# View logs
./docker/mcp/docker-build.sh logs

# Stop the server
./docker/mcp/docker-build.sh stop

# Clean up (remove container and image)
./docker/mcp/docker-build.sh clean

# Help
./docker/mcp/docker-build.sh --help
```

## Transport Modes

The FastMCP server supports different transport modes:

### 1. STDIO Transport (Default)
```bash
docker run -i central-knowledge-base
```
- Interactive mode for direct client communication
- Use `-i` flag for interactive input/output

### 2. HTTP Transport
```bash
docker run -d -p 8001:8001 central-knowledge-base \
  uv run fastmcp run src/mcp/greetings.py:mcp --transport streamable-http --host 0.0.0.0 --port 8001
```
- Web-based transport for HTTP clients
- Accessible via HTTP endpoints

### 3. SSE Transport
```bash
docker run -d -p 8002:8002 central-knowledge-base \
  uv run fastmcp run src/mcp/greetings.py:mcp --transport sse --host 0.0.0.0 --port 8002
```
- Server-Sent Events for real-time communication

## Environment Variables

You can customize the container behavior using environment variables:

```bash
docker run -e PYTHONPATH=/app -e CUSTOM_VAR=value central-knowledge-base
```

Common environment variables:
- `PYTHONPATH`: Python module search path (default: `/app`)
- `PYTHONUNBUFFERED`: Disable Python output buffering (default: `1`)

### Agent Interaction Configuration

For the `interact_agent` tool, you can configure the following environment variables:

```bash
# Default configuration (Docker Desktop - Mac/Windows)
docker run -i --rm --name fastmcp-server -p 8000:8000 \
  -e URL_AGENT="http://host.docker.internal:8000" \
  -e USER_ID="u_123" \
  -e SESSION_ID="s_123" \
  -e AGENT_APPS="scientific_paper_knowledge_base_agent" \
  central-knowledge-base

# For Linux systems using host network
docker run -i --rm --name fastmcp-server --network host \
  -e URL_AGENT="http://localhost:8000" \
  -e USER_ID="u_123" \
  -e SESSION_ID="s_123" \
  -e AGENT_APPS="scientific_paper_knowledge_base_agent" \
  central-knowledge-base

# For remote agent server
docker run -i --rm --name fastmcp-server -p 8000:8000 \
  -e URL_AGENT="http://192.168.1.100:8000" \
  -e USER_ID="u_123" \
  -e SESSION_ID="s_123" \
  -e AGENT_APPS="scientific_paper_knowledge_base_agent" \
  central-knowledge-base
```

Agent interaction environment variables:
- `URL_AGENT`: Base URL of the agent server
  - Default: `http://host.docker.internal:8000` (for Docker Desktop)
  - Use `http://localhost:8000` with host network mode on Linux
  - Use specific IP for remote agent servers
- `USER_ID`: User identifier for agent sessions (default: `u_123`)
- `SESSION_ID`: Session identifier for agent conversations (default: `s_123`)
- `AGENT_APPS`: Agent application name to interact with (default: `scientific_paper_knowledge_base_agent`)

## Development Mode

For development, you can mount the source code as a volume:

```bash
docker run -d \
  --name fastmcp-dev \
  -p 8000:8000 \
  -v $(pwd)/src:/app/src:ro \
  central-knowledge-base
```

Or use the enhanced script:
```bash
./docker/mcp/docker-build.sh dev
```

This allows you to modify the source code without rebuilding the image.

## Troubleshooting

### Container Won't Start
```bash
# Check container logs
docker logs fastmcp-server

# Run in interactive mode to see errors
docker run -it central-knowledge-base /bin/bash
```

### Port Already in Use
```bash
# Use a different port
docker run -d -p 8080:8000 central-knowledge-base

# Or stop the conflicting container
docker ps
docker stop <container-id>
```

### Permission Issues
```bash
# Make sure the build script is executable
chmod +x docker/mcp/docker-build.sh
```

## Advanced Usage

### Custom FastMCP Server

To run a different FastMCP server file:

```bash
# Run a custom MCP server
docker run -i central-knowledge-base uv run fastmcp run src/mcp/custom_server.py:mcp

# With additional arguments
docker run -i central-knowledge-base uv run fastmcp run src/mcp/custom_server.py:mcp --debug
```

### Multi-Stage Builds

The Dockerfile uses a single-stage build for simplicity. For production, consider:

1. Multi-stage builds to reduce image size
2. Non-root user for security
3. Health checks for monitoring

### Production Deployment

For production deployment:

1. Use specific version tags instead of `latest`
2. Set up proper logging and monitoring
3. Configure resource limits
4. Use orchestration tools like Kubernetes or Docker Swarm

## File Structure

```
.
├── docker/
│   └── mcp/
│       ├── Dockerfile              # Main Docker configuration
│       ├── docker-compose.yml      # Docker Compose configuration
│       ├── docker-build.sh         # Build and management script
│       └── README-Docker.md        # This documentation file
├── .dockerignore                   # Files to exclude from build context
└── src/
    └── mcp/
        └── greetings.py            # FastMCP server implementation
```

## Next Steps

1. Customize the `src/mcp/greetings.py` file to add your own tools and functionality
2. Modify the Dockerfile for your specific requirements
3. Set up CI/CD pipelines for automated building and deployment
4. Configure monitoring and logging for production use

## Docker Networking for Host Communication

When MCP runs in Docker and needs to connect to an agent server running on the host machine, the default `localhost:8000` won't work because Docker containers have their own network namespace.

### Option 1: Using host.docker.internal (Recommended for Docker Desktop)

The default configuration uses `host.docker.internal` which allows containers to reach the host machine:

```bash
# This is the default service - works on Docker Desktop (Mac/Windows)
docker-compose up fastmcp-server

# Or set explicitly:
docker-compose up -e URL_AGENT="http://host.docker.internal:8000" fastmcp-server
```

### Option 2: Using Host Network Mode (Linux)

For Linux systems, you can use host network mode:

```bash
# Use the host network service
docker-compose up fastmcp-server-host-network
```

This allows the container to use the host's network directly, so `localhost:8000` will work.

### Option 3: Custom Agent Server URL

If your agent server runs on a different host or port:

```bash
# Connect to agent server on a different machine
docker-compose up -e URL_AGENT="http://192.168.1.100:8000" fastmcp-server

# Connect to agent server on different port
docker-compose up -e URL_AGENT="http://host.docker.internal:9000" fastmcp-server
```

### Troubleshooting Network Issues

1. **Connection refused error**:
   - Make sure your agent server is running on the host machine
   - Verify the correct port (default: 8000)
   - Try `host.docker.internal` instead of `localhost`

2. **For Linux users**:
   - Use the `fastmcp-server-host-network` service
   - Or set `URL_AGENT`