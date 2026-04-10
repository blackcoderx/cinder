---
title: Caching
description: Response caching for collection endpoints
---

Cinder caches GET responses to reduce database load and improve response times.

## Quick Start

### In-Memory (No Setup)

```python
from cinder import Cinder

app = Cinder(database="app.db")
app.cache.enable()  # Uses MemoryCacheBackend
```

### With Redis

```python
from cinder import Cinder

app = Cinder(database="app.db")
app.configure_redis(url="redis://localhost:6379/0")
# Cache auto-enables when Redis is configured
```

## What Gets Cached

| Endpoint | Cached | Key Type |
|----------|--------|----------|
| `GET /api/{collection}` | ✅ Yes | List |
| `GET /api/{collection}/{id}` | ✅ Yes | Single record |
| All other endpoints | ❌ No | — |

## X-Cache Header

Every cached response includes an `X-Cache` header:

```http
HTTP/1.1 200 OK
X-Cache: HIT
Content-Type: application/json

{"items": [...], "total": 42}
```

| Header | Meaning |
|--------|---------|
| `X-Cache: HIT` | Response served from cache |
| `X-Cache: MISS` | Response from database |

## What Never Gets Cached

- **4xx/5xx responses** — Errors are never cached
- **Responses with `Set-Cookie`** — Security
- **`POST/PATCH/DELETE` requests** — Not idempotent
- **Excluded paths** — See [Configuration](/caching/configuration/))

## Automatic Invalidation

When data changes, the cache is automatically cleared:

```bash
# These operations invalidate related cache:
POST /api/posts      → Invalidates "list" cache for posts
PATCH /api/posts/123 → Invalidates "get" and "list" cache for posts
DELETE /api/posts/123 → Invalidates "get" and "list" cache for posts
```

See [Cache Invalidation](/caching/invalidation/) for details.

## Fail-Open Design

If the cache backend fails, requests pass through to the database:

```
Cache Error → Log → Pass through to database → Response served
```

Your API never breaks because of cache issues.

## Next Steps

- [Cache-Aside](/caching/cache-aside/) — How caching works internally
- [Cache Invalidation](/caching/invalidation/) — Automatic invalidation
- [Configuration](/caching/configuration/) — All options
