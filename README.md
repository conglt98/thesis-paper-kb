# Scientific Paper Knowledge Base

AI-Powered Knowledge Base System for managing, querying, and analyzing scientific papers. Built with LightRAG, FastMCP, and modern LLM integration.

## Prerequisites
- Python 3.10+
- [uv](https://github.com/astral-sh/uv) (for dependency management)
- Docker (for MCP server)

## Database Setup (Required for LightRAG)
LightRAG **requires a database backend** to store scientific paper data. You must run Postgres (and/or Neo4j) before starting LightRAG.

- **Postgres** (with pgvector) is recommended for vector storage and production use.
- **Neo4j** can be used for graph features if enabled in LightRAG.
- For quick demos, LightRAG can use SQLite, but this is not recommended for real workloads.

### 1. Start Postgres and Neo4j with Docker Compose
```bash
cd docker/database
docker-compose up -d
```
- **Postgres**: `localhost:5432` (user: `postgres`, password: `password`)
- **Neo4j**: `localhost:7474` (HTTP), `localhost:7687` (Bolt, user: `neo4j`, password: `password`)

<details>
<summary>Connection Info</summary>

**Neo4j**
```
NEO4J_URI=bolt://localhost:7687
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=password
```

**Postgres**
```
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_USER=postgres
POSTGRES_PASSWORD=password
POSTGRES_DATABASE=postgres
```
</details>

### 2. Configure LightRAG to Use Postgres
Set the following environment variables (in your shell or a `.env` file in the LightRAG directory):
```bash
export PGVECTOR_URL="postgresql://postgres:password@localhost:5432/postgres"
# Or in .env:
# PGVECTOR_URL=postgresql://postgres:password@localhost:5432/postgres
```
> See LightRAG documentation for all supported database configuration options.

## Quick Start

### 1. Start LightRAG Server (Knowledge Base Backend)

```bash
uv run lightrag-server
```
- By default, LightRAG runs at `http://localhost:9621`.
- You can configure the port and other settings via environment variables (see below).

### 2. Start MCP Server (Scientific Paper Agent)

#### a. Build and run with Docker
```bash
cd docker/mcp
./docker-build.sh build
./docker-build.sh run
```
- The MCP server will be available at `localhost:8000` (stdio) or `localhost:8001` (HTTP, if using the HTTP service).

#### b. Run both LightRAG and MCP with Docker Compose
```bash
cd docker/mcp
# (Make sure LightRAG is running separately, or add it to your own docker-compose)
docker-compose up sci-paper-kb-mcp sci-paper-kb-mcp-http
```

### 3. Example: Query Scientific Paper Knowledge (LightRAG)

```python
from src.kb_service.graph_module import KnowledgeGraphModule

graph_module = KnowledgeGraphModule(backend="light_rag")
query = "What are the main contributions of the paper 'Deep Learning for NLP'?"
result = graph_module.query(query)
print(result.response)
```

## Project Structure
```
.
├── docker/mcp/           # Docker configurations and scripts
├── src/                  # Source code (scientific paper entities, agent, LightRAG integration, etc.)
├── docs/                 # Documentation (usage, architecture, etc.)
├── tests/                # Test files
└── examples/             # Example code
```

## Environment Variables
| Variable           | Default Value                | Description                                 |
|--------------------|-----------------------------|---------------------------------------------|
| LIGHT_RAG_SERVER_URL | http://localhost:9621      | LightRAG server URL                         |
| LIGHT_RAG_API_KEY  | (empty)                     | API key for LightRAG (if enabled)           |
| PGVECTOR_URL       | postgresql://postgres:password@localhost:5432/postgres | Postgres connection for LightRAG |
| AGENT_APPS         | scientific_paper_knowledge_base_agent | Name of the agent app              |
| URL_AGENT          | http://host.docker.internal:8000 | MCP agent endpoint (for Docker)        |
| USER_ID            | u_123                       | User identifier for agent sessions          |
| SESSION_ID         | s_123                       | Session identifier for agent conversations  |

## Monitoring & Troubleshooting
- **Check MCP HTTP health:**
  ```bash
  curl http://localhost:8001/health
  ```
- **View MCP logs:**
  ```bash
  docker logs sci-paper-kb-mcp
  ```
- **Stop and remove containers:**
  ```bash
  docker-compose down
  ```
- **Check LightRAG logs:**
  - By default, logs are printed to the console where you run `uv run lightrag-server`.
- **Common issues:**
  - Ensure LightRAG is running before starting the agent/MCP.
  - Check environment variables if you change ports or hostnames.
  - Make sure the database (Postgres/Neo4j) is running and accessible before starting LightRAG.

## Documentation
- [Usage Guide](docs/usage.md) - How to use the scientific paper knowledge base
- [Architecture](docs/architecture.md) - System architecture documentation
- [Docker Setup](docker/mcp/README-Docker.md) - Complete Docker guide

## Contributing
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests
5. Submit a pull request
