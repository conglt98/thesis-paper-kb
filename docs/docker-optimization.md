# Docker Build Optimization

This document explains the optimized Docker build process for the central-knowledge-base FastMCP server.

## Build Commands Overview

The `scripts/docker-build.sh` script provides several build modes optimized for different scenarios:

### 🔨 `build` - Full Build
```bash
./scripts/docker-build.sh build
```
- Builds the complete Docker image from scratch
- Use when: First build, dependency changes, system changes
- Time: ~2-3 minutes (depends on dependencies)

### ⚡ `rebuild` - Smart Rebuild
```bash
./scripts/docker-build.sh rebuild
```
- **Optimized for code changes only**
- Caches dependency installation layer
- Only rebuilds application source code
- Uses build arguments for cache invalidation
- Time: ~30-60 seconds

### 🚀 `fast-rebuild` - Maximum Speed
```bash
./scripts/docker-build.sh fast-rebuild
```
- **Fastest rebuild option**
- Uses Docker BuildKit advanced caching
- Leverages cache-from for maximum efficiency
- Time: ~15-30 seconds

### 💻 `dev` - Development Mode
```bash
./scripts/docker-build.sh dev
```
- **No rebuild needed during development**
- Mounts source code as volume
- Live code reload
- Time: ~5 seconds to start

## Optimization Techniques

### 1. Layer Caching Strategy
The Dockerfile is structured to maximize Docker layer caching:

```dockerfile
# Heavy dependencies cached separately
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen

# Source code in separate layer for fast rebuilds
ARG CACHE_BUST
COPY src/ ./src/
```

### 2. Build Arguments
- `CACHE_BUST`: Invalidates cache for source code layer only
- `REBUILD_MODE`: Indicates rebuild vs full build

### 3. Docker BuildKit
- Enables advanced caching features
- Parallel build steps
- Efficient layer management

### 4. .dockerignore Optimization
Excludes unnecessary files from build context:
- Development files (`.vscode/`, `.idea/`)
- Cache directories (`__pycache__/`, `.pytest_cache/`)
- Storage directories (`rag_storage/`, `kb_markdown_files/`)

## Performance Comparison

| Command | Time | Use Case |
|---------|------|----------|
| `build` | ~3 min | First build, dependency changes |
| `rebuild` | ~45 sec | Code changes |
| `fast-rebuild` | ~20 sec | Frequent code changes |
| `dev` | ~5 sec | Development with live reload |

## Best Practices

### During Development
1. **First time**: `./scripts/docker-build.sh build`
2. **Code changes**: `./scripts/docker-build.sh rebuild`
3. **Frequent changes**: `./scripts/docker-build.sh dev`

### For Production
1. **CI/CD pipelines**: Use `build` for clean builds
2. **Stage deployments**: Use `fast-rebuild` if base image exists

### Memory and Storage
- BuildKit caches are stored locally
- Use `clean` command to free up space
- Dev mode uses volume mounts (no image storage)

## Build Timing

The script automatically times build operations:
```bash
[INFO] Build completed in 45 seconds
```

## Environment Variables

Set these for optimal performance:
```bash
export DOCKER_BUILDKIT=1  # Enable BuildKit (automatically set by script)
```

## Troubleshooting

### Slow Builds
- Check if Docker BuildKit is enabled
- Verify .dockerignore excludes large files
- Use `fast-rebuild` for maximum caching

### Cache Issues
- Use `build` to rebuild completely
- Check build arguments are properly set
- Verify layer structure in Dockerfile

### Development Issues
- Use `dev` mode for live reload
- Check volume mounts are working
- Verify source code changes are reflected
