---
title: "Docker"
description: "Deploy your Zeno app with Docker and docker-compose"
sidebar:
  order: 2
---

Docker is the most portable deployment option. Use it for self-hosted servers, VMs, or as the base for any container platform.

---

## Generate the files

```bash
zork deploy --platform docker --app main.py
```

This creates:

- `Dockerfile` — multi-stage production image
- `docker-compose.yml` — local and production orchestration
- `.dockerignore` — keeps the image lean
- `zork.toml` — deployment record

---

## Dockerfile

The generated Dockerfile uses a multi-stage build with [uv](https://docs.astral.sh/uv/) for fast, reproducible installs:

```dockerfile
# --- Build stage ---
FROM python:3.12-slim AS builder

COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

WORKDIR /app
COPY pyproject.toml uv.lock* ./
RUN uv sync --frozen --no-dev

COPY . .

# --- Runtime stage ---
FROM python:3.12-slim

RUN groupadd -r zork && useradd -r -g zork -u 1001 zork

WORKDIR /app
COPY --from=builder /app /app

ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONUNBUFFERED=1

USER zork
EXPOSE 8000

CMD ["sh", "-c", "zork migrate run --app main.py && gunicorn -k uvicorn.workers.UvicornWorker main:app --bind 0.0.0.0:8000"]
```

Key decisions:

- **Multi-stage build** — dependencies are installed in the builder stage; the runtime stage copies only the result, keeping the final image small
- **uv** — significantly faster than pip for resolving and installing packages; uses `uv.lock` for reproducibility
- **Non-root user** — the app runs as UID 1001 (`zork`) for security
- **Migrations on startup** — `zork migrate run` runs before gunicorn starts, ensuring the schema is always up to date
- **Gunicorn + UvicornWorker** — production-grade process management with async ASGI support

---

## docker-compose.yml

The generated compose file wires your app with the services it needs. If your app uses PostgreSQL and Redis, it looks like this:

```yaml
services:
  myapp:
    build: .
    ports:
      - "8000:8000"
    environment:
      - ZENO_SECRET=${ZENO_SECRET:-changeme}
      - DATABASE_URL=postgresql://zork:zork@postgres:5432/zork
      - ZENO_REDIS_URL=redis://redis:6379/0
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
    restart: unless-stopped

  postgres:
    image: postgres:16-alpine
    environment:
      - POSTGRES_USER=zork
      - POSTGRES_PASSWORD=zork
      - POSTGRES_DB=zork
    volumes:
      - pgdata:/var/lib/postgresql/data
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U zork"]
      interval: 5s
      timeout: 3s
      retries: 5

  redis:
    image: redis:7-alpine
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 5s
      timeout: 3s
      retries: 5

volumes:
  pgdata:
```

If your app only uses SQLite, no Postgres or Redis services are added.

---

## Build and run

```bash
# Build the image
docker build -t myapp .

# Run with docker compose (starts all services)
docker compose up

# Run in the background
docker compose up -d

# View logs
docker compose logs -f myapp
```

---

## Environment variables

Set your environment variables in a `.env` file at the project root. Docker Compose automatically reads it:

```env
ZENO_SECRET=your-secret-key-here
```

For production, prefer injecting secrets via your hosting environment rather than committing a `.env` file.

---

## Customising

**Change the number of workers:**

Edit the `CMD` in the Dockerfile:

```dockerfile
CMD ["sh", "-c", "zork migrate run --app main.py && gunicorn -k uvicorn.workers.UvicornWorker main:app --bind 0.0.0.0:8000 --workers 4"]
```

A good starting point is `(2 × CPU cores) + 1`.

**Change the port:**

Update `EXPOSE` and the `--bind` flag in the CMD, then update the `ports` mapping in `docker-compose.yml`.

---

## .dockerignore

The generated `.dockerignore` excludes files that should not be in the image:

```
.venv/
__pycache__/
*.pyc
.git/
.env
*.db
tests/
```

This keeps the image size down and prevents local environment files from leaking into the build.
