#!/bin/bash

# Docker build and run script for central-knowledge-base FastMCP server

set -e

# Get the project root directory (two levels up from this script)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

# Change to project root directory
cd "$PROJECT_ROOT"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Default values
IMAGE_NAME="central-knowledge-base"
TAG="latest"
CONTAINER_NAME="fastmcp-server"
PORT="8000"
DOCKERFILE_PATH="docker/mcp/Dockerfile"
NETWORK_MODE=""
AGENT_URL=""

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to show usage
show_usage() {
    echo "Usage: $0 [build|rebuild|fast-rebuild|dev|run|run-host|stop|logs|clean] [options]"
    echo ""
    echo "Commands:"
    echo "  build        Build the Docker image from scratch"
    echo "  rebuild      Rebuild only the application code (faster, uses cache for dependencies)"
    echo "  fast-rebuild Fast rebuild using BuildKit cache mount (fastest)"
    echo "  dev          Run in development mode with volume mount (no rebuild needed)"
    echo "  run          Run the FastMCP server container (uses host.docker.internal)"
    echo "  run-host     Run with host network mode (Linux only)"
    echo "  stop         Stop the running container"
    echo "  logs         Show container logs"
    echo "  clean        Remove container and image"
    echo ""
    echo "Options:"
    echo "  -p, --port PORT     Port to expose (default: 8000)"
    echo "  -t, --tag TAG       Docker image tag (default: latest)"
    echo "  -n, --name NAME     Container name (default: fastmcp-server)"
    echo "  --agent-url URL     Custom agent server URL (e.g., http://192.168.1.100:8000)"
    echo "  -h, --help          Show this help message"
    echo ""
    echo "Networking Information:"
    echo "  • 'run' uses host.docker.internal (works on Docker Desktop)"
    echo "  • 'run-host' uses host network mode (Linux only, allows localhost access)"
    echo "  • Use --agent-url for custom agent server locations"
    echo ""
    echo "Build Performance Tips:"
    echo "  • Use 'rebuild' for quick code changes (dependencies cached)"
    echo "  • Use 'fast-rebuild' for maximum speed with BuildKit"
    echo "  • Use 'dev' for development with live code reload"
    echo ""
    echo "Note: This script automatically changes to the project root directory before building."
}

# Parse command line arguments
COMMAND=""
while [[ $# -gt 0 ]]; do
    case $1 in
        build|rebuild|fast-rebuild|dev|run|run-host|stop|logs|clean)
            COMMAND="$1"
            shift
            ;;
        -p|--port)
            PORT="$2"
            shift 2
            ;;
        -t|--tag)
            TAG="$2"
            shift 2
            ;;
        -n|--name)
            CONTAINER_NAME="$2"
            shift 2
            ;;
        --agent-url)
            AGENT_URL="$2"
            shift 2
            ;;
        -h|--help)
            show_usage
            exit 0
            ;;
        *)
            print_error "Unknown option: $1"
            show_usage
            exit 1
            ;;
    esac
done

# Check if command is provided
if [[ -z "$COMMAND" ]]; then
    print_error "No command provided"
    show_usage
    exit 1
fi

# Function to time command execution
time_command() {
    local start_time=$(date +%s)
    eval "$@"
    local end_time=$(date +%s)
    local duration=$((end_time - start_time))
    print_status "Build completed in ${duration} seconds"
}

# Execute commands
case $COMMAND in
    build)
        print_status "Building Docker image: ${IMAGE_NAME}:${TAG}"
        print_status "Working directory: $PROJECT_ROOT"
        time_command "DOCKER_BUILDKIT=1 docker build -f \"${DOCKERFILE_PATH}\" -t \"${IMAGE_NAME}:${TAG}\" ."
        print_status "Build completed successfully!"
        ;;

    rebuild)
        print_status "Rebuilding application code: ${IMAGE_NAME}:${TAG}"
        print_status "Using cache for dependencies, only rebuilding source code..."
        print_status "Working directory: $PROJECT_ROOT"

        # Use build argument with current timestamp to invalidate cache for app code
        BUILD_TIMESTAMP=$(date +%s)
        time_command "DOCKER_BUILDKIT=1 docker build \
            -f \"${DOCKERFILE_PATH}\" \
            --build-arg CACHE_BUST=\"$BUILD_TIMESTAMP\" \
            --build-arg REBUILD_MODE=true \
            -t \"${IMAGE_NAME}:${TAG}\" ."

        print_status "Rebuild completed successfully!"
        print_status "Dependencies cached, only application code rebuilt"
        ;;

    fast-rebuild)
        print_status "Fast rebuilding with BuildKit cache mount: ${IMAGE_NAME}:${TAG}"
        print_status "Using advanced caching for maximum speed..."
        print_status "Working directory: $PROJECT_ROOT"

        # Use BuildKit with cache mounts for fastest rebuild
        BUILD_TIMESTAMP=$(date +%s)
        time_command "DOCKER_BUILDKIT=1 docker build \
            -f \"${DOCKERFILE_PATH}\" \
            --build-arg CACHE_BUST=\"$BUILD_TIMESTAMP\" \
            --build-arg REBUILD_MODE=true \
            --cache-from=\"${IMAGE_NAME}:${TAG}\" \
            --cache-from=\"${IMAGE_NAME}:cache\" \
            -t \"${IMAGE_NAME}:${TAG}\" ."

        print_status "Fast rebuild completed successfully!"
        print_status "Maximum caching utilized for optimal build speed"
        ;;

    dev)
        print_status "Starting development mode container"
        print_status "Source code will be mounted as volume for live reload"

        # Stop existing container if running
        if docker ps -q -f name="${CONTAINER_NAME}-dev" | grep -q .; then
            print_warning "Stopping existing dev container: ${CONTAINER_NAME}-dev"
            docker stop "${CONTAINER_NAME}-dev"
            docker rm "${CONTAINER_NAME}-dev"
        fi

        # Determine agent URL
        local url_agent="${AGENT_URL:-http://host.docker.internal:8000}"
        print_status "Using agent URL: $url_agent"

        # Run container with volume mount for development
        docker run -d \
            --name "${CONTAINER_NAME}-dev" \
            -p "${PORT}:8000" \
            -e "URL_AGENT=$url_agent" \
            -v "$PROJECT_ROOT/src:/app/src" \
            "${IMAGE_NAME}:${TAG}"

        print_status "Development container started successfully!"
        print_status "FastMCP server is running on port $PORT"
        print_status "Source code changes will be reflected immediately"
        print_status "Container name: ${CONTAINER_NAME}-dev"
        ;;

    run)
        print_status "Running FastMCP server container"

        # Stop existing container if running
        if docker ps -q -f name="$CONTAINER_NAME" | grep -q .; then
            print_warning "Stopping existing container: $CONTAINER_NAME"
            docker stop "$CONTAINER_NAME"
            docker rm "$CONTAINER_NAME"
        fi

        # Determine agent URL
        local url_agent="${AGENT_URL:-http://host.docker.internal:8000}"
        print_status "Using agent URL: $url_agent"

        # Run new container
        docker run -d \
            --name "$CONTAINER_NAME" \
            -p "${PORT}:8000" \
            -e "URL_AGENT=$url_agent" \
            "${IMAGE_NAME}:${TAG}"

        print_status "Container started successfully!"
        print_status "FastMCP server is running on port $PORT"
        print_status "Container name: $CONTAINER_NAME"
        ;;

    run-host)
        print_status "Running FastMCP server container with host network mode"

        # Stop existing container if running
        if docker ps -q -f name="$CONTAINER_NAME" | grep -q .; then
            print_warning "Stopping existing container: $CONTAINER_NAME"
            docker stop "$CONTAINER_NAME"
            docker rm "$CONTAINER_NAME"
        fi

        # For host network mode, use localhost
        local url_agent="${AGENT_URL:-http://localhost:8000}"
        print_status "Using agent URL: $url_agent"

        # Run new container with host network mode
        docker run -d \
            --name "$CONTAINER_NAME" \
            --network host \
            -e "URL_AGENT=$url_agent" \
            "${IMAGE_NAME}:${TAG}"

        print_status "Container started successfully!"
        print_status "FastMCP server is running on port $PORT"
        print_status "Container name: $CONTAINER_NAME"
        print_status "Note: Using host network mode - container shares host network namespace"
        ;;

    stop)
        print_status "Stopping container: $CONTAINER_NAME"
        docker stop "$CONTAINER_NAME" 2>/dev/null || print_warning "Container not running"
        docker rm "$CONTAINER_NAME" 2>/dev/null || print_warning "Container not found"

        # Also stop dev container if exists
        docker stop "${CONTAINER_NAME}-dev" 2>/dev/null || true
        docker rm "${CONTAINER_NAME}-dev" 2>/dev/null || true

        print_status "Container stopped and removed"
        ;;

    logs)
        print_status "Showing logs for container: $CONTAINER_NAME"
        if docker ps -q -f name="${CONTAINER_NAME}-dev" | grep -q .; then
            print_status "Development container is running, showing dev logs"
            docker logs -f "${CONTAINER_NAME}-dev"
        else
            docker logs -f "$CONTAINER_NAME"
        fi
        ;;

    clean)
        print_status "Cleaning up Docker resources"
        docker stop "$CONTAINER_NAME" 2>/dev/null || true
        docker rm "$CONTAINER_NAME" 2>/dev/null || true
        docker stop "${CONTAINER_NAME}-dev" 2>/dev/null || true
        docker rm "${CONTAINER_NAME}-dev" 2>/dev/null || true
        docker rmi "${IMAGE_NAME}:${TAG}" 2>/dev/null || true
        docker rmi "${IMAGE_NAME}:cache" 2>/dev/null || true
        print_status "Cleanup completed"
        ;;
esac
