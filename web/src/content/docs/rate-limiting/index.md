---
title: Rate Limiting
description: Protect your API from abuse with request throttling
---

Rate limiting controls how many requests clients can make in a given time window.

## Quick Start

### Automatic with Redis

```python
from cinder import Cinder

app = Cinder(database="app.db")
app.configure_redis(url="redis://localhost:6379/0")
# Rate limiting auto-enables
```

### In-Memory (No Setup)

```python
from cinder import Cinder

app = Cinder(database="app.db")
# Rate limiting enabled by default with memory backend
```

## Default Limits

| Client Type | Limit | Window | Key |
|-------------|-------|--------|-----|
| Anonymous (no token) | 100 requests | 60 seconds | By IP |
| Authenticated | 1000 requests | 60 seconds | By user ID |

## On Limit Exceeded

When a client exceeds the limit, they receive:

```http
HTTP/1.1 429 Too Many Requests
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 0
X-RateLimit-Reset: 1744300800
Retry-After: 42
Content-Type: application/json

{"status": 429, "error": "Rate limit exceeded"}
```

See [Headers](/rate-limiting/headers/) for all response headers.

## Middleware Order

Rate limiting runs early in the middleware stack:

```
1. ErrorHandler  (outermost)
2. RequestID
3. CORS
4. RateLimit    ← Blocks abuse BEFORE cache
5. Cache
6. Auth
7. Routes       (innermost)
```

This ensures abusive requests are rejected before they hit the cache or database.

## Fail-Open Design

If the rate limit backend fails, requests are allowed through:

```
Rate Limit Error → Log → Allow request → Continue
```

Your API never blocks legitimate users because of rate limiting issues.

## Next Steps

- [Algorithm](/rate-limiting/algorithm/) — How rate limiting works
- [Configuration](/rate-limiting/configuration/) — Customize limits and rules
- [Headers](/rate-limiting/headers/) — Response header reference
