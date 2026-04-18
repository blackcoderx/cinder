---
title: Render Deployment
description: Deploy Zork to Render
---

# Render Deployment

Render is a managed hosting platform that supports Python with automatic scaling, PostgreSQL, and Redis.

## Quick Start

Generate the Render configuration:

```bash
zork deploy render --app main.py
```

This creates a `render.yaml` file that Render uses to provision and deploy your app.

## Configuration

The generated `render.yaml`:

```yaml
services:
  - type: web
    name: myapp
    runtime: python
    buildCommand: pip install uv && uv sync --frozen --no-dev
    startCommand: zork migrate run && uvicorn main:app --host 0.0.0.0 --port $PORT
    healthCheckPath: /api/health
    envVars:
      - key: ZORK_SECRET
        generateValue: true
      - key: PYTHON_VERSION
        value: "3.12"
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

### 2. Create Render Project

1. Go to [Render Dashboard](https://dashboard.render.com)
2. Click **New** → **Web Service**
3. Select your GitHub repository

### 3. Configure

Render automatically detects Python. Verify the settings:

| Setting | Value |
|---------|-------|
| Build Command | `pip install uv && uv sync --frozen --no-dev` |
| Start Command | `zork migrate run && uvicorn main:app --host 0.0.0.0 --port $PORT` |
| Health Check | `/api/health` |

### 4. Add Environment Variables

The `render.yaml` generates these automatically:

| Variable | Description |
|----------|-------------|
| `ZORK_SECRET` | Auto-generated JWT secret |
| `PYTHON_VERSION` | Python version (default: 3.12) |

### 5. Add PostgreSQL (Optional)

If your app needs a database:

1. In the `render.yaml`, add:

```yaml
databases:
  - name: myapp-db
    plan: free
```

2. PostgreSQL is auto-provisioned and connected via `DATABASE_URL`.

### 6. Add Redis (Optional)

If your app uses caching or rate-limiting:

1. In the `render.yaml`, add:

```yaml
keyvalues:
  - name: myapp-redis
    plan: free
```

2. Redis is auto-provisioned and connected via `ZORK_REDIS_URL`.

## Update main.py

```python
from zork import Zork

app = Zork(
    # Uses DATABASE_URL from Render environment
)

app.serve()
```

## Deployment

After connecting to GitHub:

1. Render automatically builds and deploys
2. Check the **Logs** tab for build progress
3. Once deployed, your app is available at `https://your-app.onrender.com`

## Health Check

The `render.yaml` configures health checking:

```yaml
healthCheckPath: /api/health
```

Zork automatically provides this endpoint.

## Troubleshooting

### Build Fails

Check the **Logs** tab in Render dashboard. Common issues:

- Missing `uv.lock` — Run `uv sync` locally and commit
- Python version mismatch — Specify in `render.yaml`:

```yaml
- key: PYTHON_VERSION
  value: "3.12"
```

### Database Connection Failed

Ensure `DATABASE_URL` is correctly referenced:

```yaml
- key: DATABASE_URL
  fromDatabase:
    name: myapp-db
    property: connectionString
```

### 503 Service Unavailable

Increase the health check timeout or add a startup command:

```yaml
startCommand: sleep 10 && zork migrate run && uvicorn main:app --host 0.0.0.0 --port $PORT
```

### Environment Variables Not Set

Check the **Environment** tab in Render dashboard. You can manually add variables there.

## Scaling

### Free Tier Limitations

| Resource | Free Tier Limit |
|----------|----------------|
| Web Service | 750 hours/month |
| PostgreSQL | 1GB storage |
| Redis | 30MB storage |
| Bandwidth | 100GB/month |

### Paid Scaling

For higher traffic:

1. Go to your web service **Settings**
2. Change the **Plan** to **Starter** or **Pro**
3. Configure auto-scaling rules

## Next Steps

- [Docker Deployment](/deployment/docker) — Containerized deployment
- [Railway Deployment](/deployment/railway) — Simple cloud deployment
- [Fly.io Deployment](/deployment/flyio) — Edge deployment