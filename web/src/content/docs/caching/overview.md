---
title: Overview
description: Cache-aside response caching for collection endpoints
---

Cinder ships with a **cache-aside** response cache for collection GET endpoints.

## Install Redis

For production multi-process deployments:

```bash
pip install cinder[redis]
```

## Zero-Config (In-Memory)

The in-memory backend requires no configuration:

```python
app = Cinder("app.db")
app.cache.enable()            # use in-memory backend
app.cache.configure(default_ttl=60)
```

## Redis Backend

```python
app = Cinder("app.db")
app.configure_redis(url="redis://localhost:6379/0")
```

Or via environment variable:

```sh
CINDER_REDIS_URL=redis://localhost:6379/0
```

## How It Works

- **Cache-aside** — GET requests to `/api/{collection}` and `/api/{collection}/{id}` are cached
- **X-Cache header** — Responses include `X-Cache: HIT` or `X-Cache: MISS`
- **Per-user segmentation** — Cache keys include user ID by default
- **Automatic invalidation** — Any POST/PATCH/DELETE busts relevant cache keys
- **Fail-open** — If cache backend is down, requests pass through to database
- **Never cached** — 4xx/5xx responses, `Set-Cookie` responses

## Programmatic Configuration

```python
from cinder import Cinder, RedisCacheBackend

app = Cinder("app.db")

# Use a custom backend
app.cache.use(RedisCacheBackend())

# Configure TTL and per-user segmentation
app.cache.configure(default_ttl=600, per_user=True)

# Opt specific paths out of caching
app.cache.exclude("/api/feed", "/api/search")
```

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `CINDER_CACHE_ENABLED` | auto | `true`/`false` |
| `CINDER_CACHE_TTL` | `300` | Default TTL in seconds |
| `CINDER_CACHE_PREFIX` | `cinder` | Redis key namespace prefix |

## Example

```python
app = Cinder(database="app.db")
app.configure_redis(url="redis://localhost:6379/0")

# All GET /api/posts/* requests are cached
# POST/PATCH/DELETE automatically invalidates cache
```

## Next Steps

- [Rate Limiting](/rate-limiting/overview/) — Request throttling
- [Redis](/configuration/env-variables/) — Redis configuration