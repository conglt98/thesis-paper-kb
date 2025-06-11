# Testing Docker Networking Configuration

This guide helps you test the Docker networking fixes for MCP to communicate with the host agent server.

## Prerequisites

1. Make sure you have an agent server running on the host machine:
   ```bash
   # Start the agent server (should be running on port 8000)
   cd /path/to/your/project
   export PYTHONPATH=.
   source .env
   uv run adk web src/agents
   ```

2. The agent server should be accessible at `http://localhost:8000` on your host machine.

## Test Scenarios

### Scenario 1: Docker Desktop (Mac/Windows) - Default Configuration

```bash
# Build the MCP server image
./docker/mcp/docker-build.sh build

# Run with default host.docker.internal configuration
./docker/mcp/docker-build.sh run

# Check logs to see if it starts correctly
./docker/mcp/docker-build.sh logs
```

Expected output: Container should start without connection errors.

### Scenario 2: Linux with Host Network Mode

```bash
# Build the MCP server image
./docker/mcp/docker-build.sh build

# Run with host network mode (Linux only)
./docker/mcp/docker-build.sh run-host

# Check logs
./docker/mcp/docker-build.sh logs
```

Expected output: Container uses host network and can access localhost:8000.

### Scenario 3: Custom Agent Server URL

```bash
# If your agent server runs on a different machine or port
./docker/mcp/docker-build.sh run --agent-url "http://192.168.1.100:9000"

# Or using environment variable
export URL_AGENT="http://192.168.1.100:9000"
docker-compose up fastmcp-server
```

### Scenario 4: Using Docker Compose

```bash
# Default configuration (host.docker.internal)
docker-compose up fastmcp-server

# Custom agent URL
URL_AGENT="http://192.168.1.100:8000" docker-compose up fastmcp-server

# Host network mode (Linux)
docker-compose up fastmcp-server-host-network
```

## Testing the interact_agent Tool

Once your MCP server is running, test the `interact_agent` tool:

1. **Connect to the MCP server** (method depends on your setup):
   - Using ADK with MCP integration
   - Using Claude Desktop with MCP server configuration
   - Using FastMCP client

2. **Test the tool**:
   ```
   Use the interact_agent tool with message: "hello"
   ```

3. **Expected behavior**:
   - Tool should successfully connect to the agent server
   - You should receive a response from the agent
   - No "Connection refused" errors

## Troubleshooting

### Connection Refused Error

**Symptom**: `Connection refused` or `Max retries exceeded`

**Solutions**:
1. **Verify agent server is running**:
   ```bash
   curl http://localhost:8000/health
   ```

2. **For Docker Desktop users**:
   ```bash
   # Try connecting from within the container
   docker exec -it fastmcp-server curl http://host.docker.internal:8000/health
   ```

3. **For Linux users**:
   ```bash
   # Use host network mode
   ./docker/mcp/docker-build.sh run-host
   ```

4. **For remote agent servers**:
   ```bash
   # Use specific IP address
   ./docker/mcp/docker-build.sh run --agent-url "http://YOUR_MACHINE_IP:8000"
   ```

### Network Mode Issues

**Docker Desktop (Mac/Windows)**:
- Use default `run` command
- `host.docker.internal` should work automatically

**Linux**:
- Use `run-host` command for host network mode
- Or use your machine's IP address instead of localhost

**WSL2 (Windows)**:
- May need to use WSL2 IP address
- Check with: `ip addr show eth0`

### Container Logs Show Wrong URL

**Check environment variables**:
```bash
docker exec -it fastmcp-server env | grep URL_AGENT
```

**Expected values**:
- Default: `http://host.docker.internal:8000`
- Host network: `http://localhost:8000`
- Custom: Your specified URL

## Verification Commands

```bash
# Check if agent server is accessible from host
curl http://localhost:8000/health

# Check if agent server is accessible from container (Docker Desktop)
docker exec -it fastmcp-server curl http://host.docker.internal:8000/health

# Check if agent server is accessible from container (Host network)
docker exec -it fastmcp-server curl http://localhost:8000/health

# Check environment variables in container
docker exec -it fastmcp-server env | grep -E "(URL_AGENT|USER_ID|SESSION_ID|AGENT_APPS)"

# Test MCP tool directly
# (This depends on your MCP client setup)
```

## Success Indicators

1. **Container starts without errors**
2. **No connection refused messages in logs**
3. **interact_agent tool returns agent responses instead of network errors**
4. **Health check commands succeed from within container**

## Common Configuration Examples

### Local Development (Docker Desktop)
```bash
# Agent server on host:8000, MCP in Docker
./docker/mcp/docker-build.sh run
```

### Local Development (Linux)
```bash
# Agent server on host:8000, MCP in Docker with host network
./docker/mcp/docker-build.sh run-host
```

### Remote Agent Server
```bash
# Agent server on different machine
./docker/mcp/docker-build.sh run --agent-url "http://10.0.1.100:8000"
```

### Custom Port
```bash
# Agent server on different port
./docker/mcp/docker-build.sh run --agent-url "http://host.docker.internal:9000"
```
