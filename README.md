# Central Knowledge Base

AI-Powered Knowledge Base System with FastMCP integration.

## Quick Start

### Docker Setup

All Docker-related files are organized in the `docker/mcp/` directory:

```bash
# Build and run FastMCP server
./docker/mcp/docker-build.sh build
./docker/mcp/docker-build.sh run

# Development mode with live reload
./docker/mcp/docker-build.sh dev
```

See [docker/mcp/README-Docker.md](docker/mcp/README-Docker.md) for detailed Docker documentation.

### Local Development

```bash
# Install dependencies
uv sync

# Run the application
# (Add specific run commands here)
```

## Project Structure

```
.
├── docker/mcp/           # Docker configurations and scripts
├── src/                  # Source code
├── docs/                 # Documentation
├── tests/                # Test files
└── examples/             # Example code
```

## Documentation

- [Docker Setup](docker/mcp/README-Docker.md) - Complete Docker guide
- [Architecture](docs/) - System architecture documentation

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests
5. Submit a pull request
