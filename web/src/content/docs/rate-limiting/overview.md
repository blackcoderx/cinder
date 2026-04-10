---
title: Overview
description: Protect your API from abuse with rate limiting
---

Cinder includes a configurable rate limiter that protects every endpoint.

## Quick Start

```python
app = Cinder("app.db")
app.configure_redis(url="redis://localhost:6379/0")
# Rate limiting is enabled automatically
```

## Default Limits

| Client type | Default limit |
|-------------|--------------|
| Anonymous (no token) | 100 requests / 60 seconds per IP |
| Authenticated | 1000 requests / 60 seconds per user |

## On Limit Exceeded

```http
HTTP/1.1 429 Too Many Requests
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 0
X-RateLimit-Reset: 1744147200
Retry-After: 42

{"status": 429, "error": "Rate limit exceeded"}
```

Every allowed response also carries rate-limit headers.

## Environment Variables

```sh
CINDER_RATE_LIMIT_ANON=200/60
CINDER_RATE_LIMIT_USER=5000/60
```

| Variable | Default | Description |
|----------|---------|-------------|
| `CINDER_RATE_LIMIT_ENABLED` | `true` | Set to `false` to disable |
| `CINDER_RATE_LIMIT_ANON` | `100/60` | Anonymous limit |
| `CINDER_RATE_LIMIT_USER` | `1000/60` | Authenticated limit |

## Per-Route Rules

Add tighter or looser limits for specific paths:

```python
from cinder import RateLimitRule

app.rate_limit.rule("/api/auth/login", limit=10, window=60, scope="ip")
app.rate_limit.rule("/api/posts", limit=50, window=60, scope="user")
```

| `scope` | Key used |
|---------|---------|
| `"ip"` | client IP address |
| `"user"` | authenticated user ID |
| `"both"` | user ID if authenticated, otherwise IP |

## Custom Backend

```python
from cinder import RateLimitBackend, RateLimitResult

class MyRateLimitBackend(RateLimitBackend):
    async def check(self, key: str, limit: int, window_seconds: int) -> RateLimitResult:
        # Return RateLimitResult(allowed, remaining, reset_at)
        ...
    async def close(self) -> None: ...

app.rate_limit.use(MyRateLimitBackend())
```

## Next Steps

- [Caching](/caching/overview/) — Response caching
- [Redis](/configuration/env-variables/) — Redis configuration