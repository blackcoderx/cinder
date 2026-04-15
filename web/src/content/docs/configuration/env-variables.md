---
title: Environment Variables
description: All environment variables recognised by Zeno
---

Zeno reads configuration from environment variables. Set them in a `.env` file (loaded by your process manager) or export them in your shell.

## Core

| Variable | Default | Description |
|----------|---------|-------------|
| `ZORK_SECRET` | _(random, not stable)_ | Secret key used to sign JWT tokens. **Must be set in production** — without it, tokens are invalidated on every restart. Generate one with `zork generate-secret`. |
| `ZORK_DATABASE_URL` | — | Database connection URL. Takes precedence over `DATABASE_URL` and the `database=` constructor argument. |
| `DATABASE_URL` | — | Fallback database URL (checked if `ZORK_DATABASE_URL` is not set). |

## Application metadata

| Variable | Default | Description |
|----------|---------|-------------|
| `ZORK_APP_NAME` | `"Your App"` | App name used in email templates and OpenAPI docs. |
| `ZORK_BASE_URL` | `"http://localhost:8000"` | Base URL used to generate links in email templates (e.g. verification and password reset links). |

## Email

| Variable | Default | Description |
|----------|---------|-------------|
| `ZORK_EMAIL_FROM` | `"noreply@localhost"` | Default sender address for all outgoing emails. |

## Caching

| Variable | Default | Description |
|----------|---------|-------------|
| `ZORK_CACHE_ENABLED` | _(auto)_ | Set to `true` or `false` to explicitly enable or disable caching. By default, caching is enabled when `ZORK_REDIS_URL` is set. |
| `ZORK_CACHE_TTL` | `300` | Default cache TTL in seconds. |
| `ZORK_CACHE_PREFIX` | `"zork"` | Key prefix used for all Redis cache entries. |

## Rate limiting

| Variable | Default | Description |
|----------|---------|-------------|
| `ZORK_RATE_LIMIT_ENABLED` | `true` | Set to `false` to disable rate limiting globally. |
| `ZORK_RATE_LIMIT_ANON` | `"100/60"` | Default limit for unauthenticated requests: `{requests}/{window_seconds}`. |
| `ZORK_RATE_LIMIT_USER` | `"1000/60"` | Default limit for authenticated requests. |

## Redis

| Variable | Default | Description |
|----------|---------|-------------|
| `ZORK_REDIS_URL` | — | Redis connection URL (e.g. `redis://localhost:6379`). When set, all subsystems that support Redis (cache, rate limiting, realtime broker) automatically use it. |

## Realtime

| Variable | Default | Description |
|----------|---------|-------------|
| `ZORK_REALTIME_BROKER` | _(auto)_ | Force a specific broker: `"redis"` or `"memory"`. By default, the Redis broker is used when `ZORK_REDIS_URL` is set. |

## Example `.env` file

```dotenv
ZORK_SECRET=your-64-char-hex-secret-here
DATABASE_URL=postgresql://user:pass@localhost/mydb
ZORK_REDIS_URL=redis://localhost:6379
ZORK_APP_NAME=My App
ZORK_BASE_URL=https://myapp.com
ZORK_EMAIL_FROM=no-reply@myapp.com
```

Generate a secret:

```bash
zork generate-secret
```
