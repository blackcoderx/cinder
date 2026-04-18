---
title: Docker Deployment
description: Deploy Zork to Docker and Docker Compose
---

# Docker Deployment

Zork includes a built-in Docker deployment generator that creates a `Dockerfile`, `docker-compose.yml`, and `.dockerignore` files.

## Quick Start

Generate the Docker configuration:

```bash
zork deploy docker --app main.py
```

This creates:

- `Dockerfile` — Multi-stage build for smaller images
- `docker-compose.yml` — Local development with optional PostgreSQL/Redis
- `.dockerignore` — Excludes unnecessary files from build context

## Dockerfile

The generated Dockerfile uses a multi-stage build:

```dockerfile
# Build stage
FROM python:3.12-slim AS builder

# Install uv for fast dependency management
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

WORKDIR /app
COPY pyproject.toml uv.lock* ./
RUN uv sync --frozen --no-dev

COPY . .

# Runtime stage
FROM python:3.12-slim

RUN groupadd -r zork && useradd -r -g zork -u 1001 zork

WORKDIR /app
COPY --from=builder /app /app

ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONUNBUFFERED=1

USER zork
EXPOSE 8000

CMD ["sh", "-c", "zork migrate run && uvicorn main:app --host 0.0.0.0 --port 8000"]
```

## Docker Compose

The `docker-compose.yml` includes your app plus optional PostgreSQL and Redis services:

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop all services
docker-compose down
```

### Services

| Service | Description |
|---------|-------------|
| `app` | Your Zork application |
| `postgres` | PostgreSQL database (optional) |
| `redis` | Redis for caching/rate-limiting (optional) |

## Configuration

### Environment Variables

Set these in your environment or `.env` file:

| Variable | Required | Description |
|----------|----------|-------------|
| `ZORK_SECRET` | Yes | JWT signing secret. Generate with `zork generate-secret` |
| `DATABASE_URL` | No | PostgreSQL connection (auto-configured if using compose) |
| `ZORK_REDIS_URL` | No | Redis connection (auto-configured if using compose) |

### Example .env File

```bash
# Required
ZORK_SECRET=your-secure-secret-key-here

# Database (if not using postgres service)
DATABASE_URL=postgresql://zork:zork@postgres:5432/zork

# Redis (if not using redis service)
ZORK_REDIS_URL=redis://redis:6379/0
```

## Build and Run

### Development

```bash
# Build and start
docker-compose up --build

# With auto-reload (mounts your code)
docker-compose up -d
docker-compose exec app sh
```

### Production

```bash
# Build the image
docker build -t my-zork-app .

# Run the container
docker run -d \
  -p 8000:8000 \
  -e ZORK_SECRET=your-secret \
  -e DATABASE_URL=postgresql://... \
  my-zork-app
```

## Health Check

The generated Dockerfile runs migrations before starting the server. To add a health check endpoint:

```python
from zork import Zork

app = Zork()

# Health check is automatically available at /api/health
app.serve()
```

Configure your orchestrator to use `http://localhost:8000/api/health` as the health check endpoint.

## PostgreSQL Setup

If using the included PostgreSQL service:

```python
# In your main.py
from zork import Zork

app = Zork(
    database="postgresql://zork:zork@postgres:5432/zork"
)
app.serve()
```

The Docker generator automatically sets `DATABASE_URL` in the compose file when it detects PostgreSQL usage.

## Redis Setup

If using the included Redis service:

```python
app = Zork(redis_url="redis://redis:6379/0")
```

The Docker generator automatically sets `ZORK_REDIS_URL` when it detects Redis usage.

## Customization

### Custom Ports

Edit `docker-compose.yml`:

```yaml
services:
  app:
    ports:
      - "8080:8000"  # Host port : Container port
```

### Custom Python Version

The generator uses Python 3.12 by default. To use a different version:

```bash
# Set before generating
export PYTHON_VERSION=3.11
zork deploy docker --app main.py
```

### Multi-Stage Build

The Dockerfile uses two stages to keep the final image small:

1. **builder** — Installs all dependencies
2. **runtime** — Only copies the virtual environment

This reduces image size from ~1GB to ~150MB.

## Troubleshooting

### Build Fails

Ensure your `pyproject.toml` and `uv.lock` are up to date:

```bash
uv sync
zork deploy docker --app main.py
```

### Permission Errors

The Dockerfile creates a non-root user (`zork`) for security. If you need root access:

```dockerfile
# Remove these lines:
RUN groupadd -r zork && useradd -r -g zork -u 1001 zork
USER zork
```

### Database Connection Failed

Ensure PostgreSQL is healthy before the app starts:

```yaml
services:
  app:
    depends_on:
      postgres:
        condition: service_healthy
```

This is already configured in the generated `docker-compose.yml`.

## Next Steps

- [Railway Deployment](/deployment/railway) — Simple cloud deployment
- [Render Deployment](/deployment/render) — Managed hosting
- [Fly.io Deployment](/deployment/flyio) — Edge deployment