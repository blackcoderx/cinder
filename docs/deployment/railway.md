---
title: Railway Deployment
description: Deploy Zork to Railway
---

# Railway Deployment

Railway is a platform that simplifies deploying Python applications with automatic provisioning of PostgreSQL and Redis.

## Quick Start

Generate the Railway configuration:

```bash
zork deploy railway --app main.py
```

This creates a `railway.toml` file that Railway uses to build and deploy your app.

## Configuration

The generated `railway.toml`:

```toml
[build]
builder = "NIXPACKS"

[deploy]
startCommand = "zork migrate run && uvicorn main:app --host 0.0.0.0 --port $PORT"
healthcheckPath = "/api/health"
healthcheckTimeout = 5
restartPolicyType = "ON_FAILURE"
restartPolicyMaxRetries = 3
```

## Setup

### 1. Push to GitHub

Push your Zork project to a GitHub repository:

```bash
git init
git add .
git commit -m "Initial commit"
git branch -M main
git remote add origin https://github.com/yourusername/your-repo.git
git push -u origin main
```

### 2. Create Railway Project

1. Go to [Railway.app](https://railway.app)
2. Click **New Project**
3. Select **Deploy from GitHub repo**
4. Select your repository

### 3. Add Environment Variables

In the Railway dashboard, add these variables:

| Variable | Required | Description |
|----------|----------|-------------|
| `ZORK_SECRET` | Yes | JWT signing secret |

Generate a secure secret:

```bash
zork generate-secret
```

Set the secret in Railway:

```
ZORK_SECRET = <your-generated-secret>
```

### 4. Add Database (Optional)

If your app uses PostgreSQL:

1. In Railway dashboard, click **New** → **Database** → **PostgreSQL**
2. Add a reference variable:

```
DATABASE_URL = ${Postgres.DATABASE_URL}
```

### 5. Add Redis (Optional)

If your app uses Redis for caching/rate-limiting:

1. Click **New** → **Database** → **Redis**
2. Add a reference variable:

```
ZORK_REDIS_URL = ${Redis.REDIS_URL}
```

## Update main.py

```python
from zork import Zork

app = Zork(
    # Uses DATABASE_URL from Railway environment
)

app.serve()
```

Or explicitly:

```python
app = Zork(
    database="postgresql://user:pass@railway.host:5432/dbname"
)
```

## Deployment

After pushing to GitHub and connecting to Railway:

1. Railway automatically detects changes and deploys
2. Check the **Deployments** tab for build progress
3. Once deployed, your app is available at `https://your-project.railway.app`

## Health Check

The `railway.toml` configures a health check at `/api/health`:

```toml
healthcheckPath = "/api/health"
healthcheckTimeout = 5
```

This endpoint is automatically provided by Zork.

## Troubleshooting

### Build Fails

Check the **Deployments** logs in Railway dashboard. Common issues:

- Missing `uv.lock` file — Run `uv sync` locally and commit
- Import errors — Ensure all dependencies are in `pyproject.toml`

### Database Connection Failed

Ensure `DATABASE_URL` is set correctly:

1. Go to **Variables** tab
2. Verify `DATABASE_URL` exists and references `${Postgres.DATABASE_URL}`
3. Check the **Logs** tab for connection errors

### 502 Bad Gateway

The app may be starting slowly. Increase the health check timeout:

```toml
[deploy]
healthcheckTimeout = 30
```

### Environment Variables Not Set

Railway sets the `$PORT` variable automatically. Use it in your start command:

```toml
startCommand = "uvicorn main:app --host 0.0.0.0 --port $PORT"
```

## Next Steps

- [Docker Deployment](/deployment/docker) — Containerized deployment
- [Render Deployment](/deployment/render) — Managed hosting
- [Fly.io Deployment](/deployment/flyio) — Edge deployment