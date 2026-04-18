---
title: Fly.io Deployment
description: Deploy Zork to Fly.io edge network
---

# Fly.io Deployment

Fly.io is an edge platform that deploys your app close to users globally with automatic scaling and low latency.

## Quick Start

Generate the Fly.io configuration:

```bash
zork deploy fly --app main.py
```

This creates:

- `fly.toml` — Fly.io configuration
- `Dockerfile` — Container build definition
- `.dockerignore` — Build context exclusions

## Configuration

The generated `fly.toml`:

```toml
app = "myapp"
primary_region = "iad"

[build]

[deploy]
  release_command = "zork migrate run"

[http_service]
  internal_port = 8000
  force_https = true
  auto_stop_machines = "stop"
  auto_start_machines = true
  min_machines_running = 1

  [http_service.concurrency]
    type = "connections"
    hard_limit = 250
    soft_limit = 200

  [[http_service.checks]]
    grace_period = "10s"
    interval = "15s"
    method = "GET"
    path = "/api/health"
    timeout = "2s"

[[vm]]
  memory = "512mb"
  cpu_kind = "shared"
  cpus = 1
```

## Setup

### 1. Install Fly CLI

```bash
# macOS
brew install flyctl

# Linux
curl -L https://flyctl.io/install.sh | sh

# Windows (PowerShell)
irm https://flyctl.io/install.ps1 | iex
```

### 2. Authenticate

```bash
fly auth login
```

### 3. Launch Your App

```bash
cd your-project
fly launch --no-deploy
```

This creates the Fly.io app without deploying. Follow the prompts to:

- Choose your organization
- Select a primary region
- Set up PostgreSQL (optional)

### 4. Add Environment Variables

```bash
# Set the JWT secret
fly secrets set ZORK_SECRET=$(zork generate-secret)

# Set additional secrets as needed
fly secrets set SOME_OTHER_SECRET=value
```

### 5. Deploy

```bash
fly deploy
```

## Health Check

The `fly.toml` configures health checking:

```toml
[[http_service.checks]]
  grace_period = "10s"
  interval = "15s"
  method = "GET"
  path = "/api/health"
  timeout = "2s"
```

Zork automatically provides this endpoint at `/api/health`.

## PostgreSQL Setup

### Create Database

```bash
fly postgres create --name myapp-db
fly postgres attach myapp-db
```

This automatically sets the `DATABASE_URL` environment variable.

### Update main.py

```python
from zork import Zork

# DATABASE_URL is automatically set by fly postgres attach
app = Zork()

app.serve()
```

## Redis Setup

Fly.io recommends Upstash for Redis:

### 1. Create Redis

```bash
fly redis create
```

### 2. Get Connection URL

```bash
fly redis list
```

### 3. Set Environment Variable

```bash
fly secrets set ZORK_REDIS_URL=<your-redis-url>
```

## Regions

### Add Regions

```bash
# Add a region
fly regions add fra

# Set preferred regions
fly launch --hae-primary-region iad --hae-regions fra,sin
```

### View Regions

```bash
fly status
```

## Scaling

### Free Tier

| Resource | Free Tier Limit |
|----------|----------------|
| VMs | 3 shared-CPU |
| Volume | 3GB |
| Bandwidth | 160GB/month |

### Auto-Scaling

Configure in `fly.toml`:

```toml
[http_service]
  auto_stop_machines = "stop"
  auto_start_machines = true
  min_machines_running = 0  # Scale to zero when idle
```

## Troubleshooting

### Build Fails

Check the build logs:

```bash
fly logs
```

Common issues:

- Missing `uv.lock` — Run `uv sync` locally and commit
- Import errors — Verify all dependencies in `pyproject.toml`

### Database Connection Failed

Ensure PostgreSQL is attached:

```bash
fly postgres attach myapp-db
```

Check the environment:

```bash
fly secrets list
```

### Health Check Failed

The health check requires `/api/health`. Verify it's responding:

```bash
curl https://yourapp.fly.dev/api/health
```

If needed, increase the timeout in `fly.toml`:

```toml
[[http_service.checks]]
  timeout = "10s"
```

### Deployment Stuck

Force a new deployment:

```bash
fly deploy --force-nomad
```

## Customization

### Custom Port

Edit `fly.toml`:

```toml
[http_service]
  internal_port = 8080
```

### Custom VM Size

```toml
[[vm]]
  memory = "1gb"
  cpu_kind = "dedicated"
  cpus = 2
```

### Custom Domain

```bash
fly certs add yourdomain.com
```

Then configure DNS with your provider.

## Commands Reference

| Command | Description |
|---------|-------------|
| `fly launch` | Create and configure app |
| `fly deploy` | Deploy app |
| `fly status` | View app status |
| `fly logs` | View logs |
| `fly redis create` | Create Redis |
| `fly postgres create` | Create PostgreSQL |
| `fly secrets set` | Set secrets |
| `fly regions add` | Add region |

## Next Steps

- [Docker Deployment](/deployment/docker) — Containerized deployment
- [Railway Deployment](/deployment/railway) — Simple cloud deployment
- [Render Deployment](/deployment/render) — Managed hosting