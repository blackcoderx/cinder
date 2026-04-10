---
title: Environment Variables
description: Complete reference of all environment variables
---

Cinder supports various environment variables for configuration.

## Required

| Variable | Description |
|----------|-------------|
| `CINDER_SECRET` | JWT signing secret. If not set, a random secret is generated on each startup. |

## Database

| Variable | Default | Description |
|----------|---------|-------------|
| `CINDER_DATABASE_URL` | — | Database URL (highest priority) |
| `DATABASE_URL` | — | Standard PaaS convention |
| `CINDER_DB_POOL_MIN` | `1` | Min pool connections (PostgreSQL/MySQL) |
| `CINDER_DB_POOL_MAX` | `10` | Max pool connections |
| `CINDER_DB_POOL_TIMEOUT` | `30` | Seconds to wait for connection |
| `CINDER_DB_CONNECT_TIMEOUT` | `10` | Seconds to open new connection |

## Redis

| Variable | Description |
|----------|-------------|
| `CINDER_REDIS_URL` | Redis connection string |

## Cache

| Variable | Default | Description |
|----------|---------|-------------|
| `CINDER_CACHE_ENABLED` | auto | `true`/`false` |
| `CINDER_CACHE_TTL` | `300` | Default cache TTL in seconds |
| `CINDER_CACHE_PREFIX` | `cinder` | Redis key namespace prefix |

## Rate Limiting

| Variable | Default | Description |
|----------|---------|-------------|
| `CINDER_RATE_LIMIT_ENABLED` | `true` | Enable/disable |
| `CINDER_RATE_LIMIT_ANON` | `100/60` | Anonymous limit |
| `CINDER_RATE_LIMIT_USER` | `1000/60` | Authenticated limit |

## Realtime

| Variable | Default | Description |
|----------|---------|-------------|
| `CINDER_REALTIME_BROKER` | `memory` | `memory` or `redis` |
| `CINDER_SSE_HEARTBEAT` | `15` | Seconds between SSE pings |

## Email

| Variable | Default | Description |
|----------|---------|-------------|
| `CINDER_EMAIL_FROM` | `noreply@localhost` | Default sender address |
| `CINDER_APP_NAME` | `Your App` | App name in templates |
| `CINDER_BASE_URL` | `http://localhost:8000` | Base URL for links |

## Example `.env` File

```sh
# Required
CINDER_SECRET=your-secret-key-here

# Database (PostgreSQL)
DATABASE_URL=postgresql://user:pass@localhost/mydb

# Redis
CINDER_REDIS_URL=redis://localhost:6379/0

# Email
CINDER_EMAIL_FROM=no-reply@myapp.com
CINDER_APP_NAME=MyApp
CINDER_BASE_URL=https://myapp.com
```

## Generate a Secret

```bash
cinder generate-secret
```

## Priority Chain

| Priority | Source |
|-----------|--------|
| 1 (highest) | `CINDER_DATABASE_URL` |
| 2 | `DATABASE_URL` |
| 3 | `database=` constructor arg |
| 4 (lowest) | `"app.db"` (SQLite default) |

## Next Steps

- [Database](/database/sqlite/) — Database backends
- [Caching](/caching/overview/) — Cache configuration
- [CLI](/cli/commands/) — Command reference