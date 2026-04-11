---
title: Configuration
description: Configure rate limiting backends, global defaults, and per-route rules
sidebar:
  order: 2
---

## Backends

### In-memory (default)

Works out of the box, no extra dependencies. Not shared across processes.

```python
from cinder.ratelimit.backends import MemoryRateLimitBackend

app.rate_limit.use(MemoryRateLimitBackend())
```

### Redis (multi-process / multi-server)

```python
from cinder.ratelimit.backends import RedisRateLimitBackend

app.rate_limit.use(RedisRateLimitBackend())
```

Requires `pip install "cinder[redis]"`. Uses `CINDER_REDIS_URL` automatically.

When `CINDER_REDIS_URL` is set, the Redis backend is selected automatically — you don't need to call `.use()`.

## Global defaults

```python
app.rate_limit.configure()  # no method for this — use env vars
```

Set via environment variables:

```dotenv
CINDER_RATE_LIMIT_ANON=100/60    # format: {requests}/{window_seconds}
CINDER_RATE_LIMIT_USER=1000/60
```

## Per-route rules

```python
app.rate_limit.rule(
    "/api/auth/register",
    limit=5,
    window=60,        # seconds
    scope="ip",       # "ip" or "user"
)
```

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `path_prefix` | `str` | — | Rule applies to all paths starting with this prefix |
| `limit` | `int` | — | Maximum requests in the window |
| `window` | `int` | `60` | Window duration in seconds |
| `scope` | `str` | `"ip"` | Rate limit by `"ip"` or `"user"` |

Multiple rules can be registered. The first matching rule (by path prefix) wins.

## 429 response

When a client exceeds the limit:

```
HTTP/1.1 429 Too Many Requests
Retry-After: 45

{"detail": "Rate limit exceeded"}
```

## Chaining configuration

```python
app.rate_limit \
    .use(RedisRateLimitBackend()) \
    .rule("/api/auth", limit=10, window=60) \
    .rule("/api/posts", limit=100, window=60) \
    .enable(True)
```
