---
title: "Railway"
description: "Deploy your Zeno app to Railway"
sidebar:
  order: 3
---

[Railway](https://railway.com) is a cloud platform that auto-detects your Python app, provisions databases and Redis, and deploys on every push. No Dockerfile needed.

---

## Generate the config

```bash
zork deploy --platform railway --app main.py
```

This creates:

- `railway.toml` — build and deploy configuration
- `zork.toml` — deployment record

---

## `railway.toml`

```toml
[build]
builder = "NIXPACKS"

[deploy]
startCommand = "zork migrate run --app main.py && gunicorn -k uvicorn.workers.UvicornWorker main:app --bind 0.0.0.0:$PORT"
healthcheckPath = "/api/health"
healthcheckTimeout = 5
restartPolicyType = "ON_FAILURE"
restartPolicyMaxRetries = 3
```

Railway uses [Nixpacks](https://nixpacks.com) to automatically detect your Python version and install dependencies from `pyproject.toml` or `requirements.txt`. No `Dockerfile` required.

The start command runs migrations first, then starts gunicorn. `$PORT` is injected by Railway at runtime.

---

## Deploy

1. **Push to GitHub** and connect the repo to a Railway project
2. **Add a PostgreSQL service** (if your app uses it):
   - Click **New** → **Database** → **Add PostgreSQL**
   - In your web service settings, add a reference variable:
     ```
     DATABASE_URL = ${{Postgres.DATABASE_URL}}
     ```
3. **Add a Redis service** (if your app uses it):
   - Click **New** → **Database** → **Add Redis**
   - Add a reference variable:
     ```
     ZENO_REDIS_URL = ${{Redis.REDIS_URL}}
     ```
4. **Set your secret key** in the web service environment variables:
   ```
   ZENO_SECRET = <output of zork generate-secret>
   ```
5. Railway deploys automatically on every push to your connected branch

---

## Health checks

Railway uses `healthcheckPath = "/api/health"` to verify your app is running before routing traffic to it. Zeno exposes this endpoint automatically at `GET /api/health`.

---

## Environment variables

Set these in the Railway dashboard under your web service → **Variables**:

| Variable | Value |
|----------|-------|
| `ZENO_SECRET` | Output of `zork generate-secret` |
| `DATABASE_URL` | `${{Postgres.DATABASE_URL}}` (reference variable) |
| `ZENO_REDIS_URL` | `${{Redis.REDIS_URL}}` (reference variable) |

Reference variables like `${{Postgres.DATABASE_URL}}` are Railway's way of wiring service URLs between services in the same project. They resolve at deploy time.

---

## SQLite on Railway

Railway's filesystem is ephemeral — data written to disk does not persist between deploys. Do not use SQLite in production on Railway. Add a PostgreSQL service instead and update your app:

```python
app = Zeno(database="postgresql://...")
```

Or set `DATABASE_URL` in the environment — Zeno picks it up automatically.
