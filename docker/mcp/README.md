# Docker MCP Server Setup

This directory contains Docker configurations for running the FastMCP server.

## Quick Start

```bash
# Build and run FastMCP server
./docker-build.sh build
./docker-build.sh run

# Development mode with live reload
./docker-build.sh dev

# View logs
./docker-build.sh logs

# Stop and cleanup
./docker-build.sh stop
```

## Files

- `Dockerfile` - Docker image configuration
- `docker-compose.yml` - Docker Compose setup
- `docker-build.sh` - Enhanced build and management script
- `README-Docker.md` - Detailed documentation

## Cursor MCP

- Run server api agent
adk api_server ./src/agents

- Add MCP config
```json
"central-knowledge-base": {
      "command": "docker",
      "args": [
        "run",
        "-i",
        "--rm",
        "--name", "fastmcp-server",
        "-p", "8001:8001",
        "-e", "URL_AGENT=http://host.docker.internal:8000",
        "-e", "USER_ID=u_123",
        "-e", "SESSION_ID=s_123",
        "-e", "AGENT_APPS=business_agent",
        "central-knowledge-base"
      ]
    }
```

## Documentation

See [README-Docker.md](README-Docker.md) for complete documentation and advanced usage.
