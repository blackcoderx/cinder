# Rate Limiting Setup

Zork includes rate limiting to protect your API from abuse and ensure fair usage.

## Overview

Rate limiting controls how many requests a client can make in a given time window. When limits are exceeded, requests are rejected with a 429 status code.

## Enabling Rate Limiting

Rate limiting is enabled by default. Configure it explicitly:

```python
from zork import Zork
from zork.ratelimit import MemoryRateLimitBackend

app = Zork()
app.rate_limit.use(MemoryRateLimitBackend())
```

## Rate Limit Backends

### Memory Backend

In-memory rate limiting for single-process applications:

```python
from zork.ratelimit import MemoryRateLimitBackend

app.rate_limit.use(MemoryRateLimitBackend())
```

Best for:

- Development and testing
- Single-server deployments

Note: Memory backend is not shared between processes.

### Redis Backend

Redis-backed rate limiting for production:

```python
app.configure_redis(url="redis://localhost:6379/0")
```

Benefits:

- Shared across all server processes
- Accurate counting across requests
- High performance

## Default Limits

Default rate limits:

| Client Type | Limit | Window |
|-------------|-------|--------|
| Anonymous | 100 requests | Per minute |
| Authenticated | 1000 requests | Per minute |

Configure via environment variables:

```bash
ZORK_RATE_LIMIT_ANON=50/60        # 50 requests per minute
ZORK_RATE_LIMIT_USER=500/60      # 500 requests per minute
```

## Custom Rules

Add specific rules for certain paths:

```python
app.rate_limit.rule("/api/search", limit=10, window=60)    # 10 searches per minute
app.rate_limit.rule("/api/export", limit=5, window=3600)    # 5 exports per hour
```

Rule parameters:

- `path_prefix` — Path to limit (must start with `/`)
- `limit` — Maximum requests allowed
- `window` — Time window in seconds
- `scope` — `ip` (default), `user`, or `both`

## Scope Options

Rate limits can be applied per IP address or per user, or both:

### Per IP (Default)

```python
app.rate_limit.rule("/api/search", limit=10, scope="ip")
```

### Per User

Requires authentication:

```python
app.rate_limit.rule("/api/upload", limit=100, scope="user")
```

### Both (User or IP)

Uses user ID if authenticated, otherwise falls back to IP:

```python
app.rate_limit.rule("/api/posts", limit=50, scope="both")
```

## Response Headers

Rate-limited responses include headers:

```
Retry-After: 60
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 0
X-RateLimit-Reset: 1640995200
```

| Header | Description |
|--------|-------------|
| `Retry-After` | Seconds until the limit resets |
| `X-RateLimit-Limit` | Maximum requests allowed |
| `X-RateLimit-Remaining` | Requests remaining in window |
| `X-RateLimit-Reset` | Unix timestamp when window resets |

## Rate Limit Exceeded Response

When a client exceeds the rate limit:

```json
{
  "status": 429,
  "error": "Rate limit exceeded"
}
```

## Disabling Rate Limiting

Disable rate limiting:

```bash
ZORK_RATE_LIMIT_ENABLED=false
```

Or via configuration:

```python
app.rate_limit.enable(False)
```

## Trust Forwarded For

When running behind a reverse proxy, you may need to trust the `X-Forwarded-For` header to get the real client IP:

```python
app.build(middleware_stack=[
    # ... other middleware
    app.rate_limit.middleware(trust_forwarded_for=True)
])
```

Or in the configuration:

```python
app.rate_limit.configure(trust_forwarded_for=True)
```

**Security Note:** Only enable `trust_forwarded_for` when Zork is behind a trusted reverse proxy that always sets this header. Otherwise, attackers could spoof it to bypass rate limits.

## Custom Rate Limit Backend

Create a custom rate limit backend:

```python
from zork.ratelimit import RateLimitBackend, RateLimitResult

class MyRateLimitBackend(RateLimitBackend):
    async def check(self, key, limit, window_seconds):
        # Check if key is within limit
        # Return RateLimitResult
        return RateLimitResult(
            allowed=True,
            remaining=limit - 1,
            reset_at=time.time() + window_seconds
        )
    
    async def close(self):
        pass
```

Then use it:

```python
app.rate_limit.use(MyRateLimitBackend())
```

## Best Practices

### Set Reasonable Limits

Start with generous limits and tighten based on actual usage patterns.

### Different Limits for Different Operations

```python
# Heavy operations - stricter limits
app.rate_limit.rule("/api/generate-report", limit=5, window=3600)

# Light operations - looser limits
app.rate_limit.rule("/api/posts", limit=100, window=60)
```

### Combine with Authentication

Authenticated users typically get higher limits:

```bash
# Anonymous users
ZORK_RATE_LIMIT_ANON=50/60

# Authenticated users
ZORK_RATE_LIMIT_USER=500/60
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `ZORK_RATE_LIMIT_ENABLED` | Enable/disable | true |
| `ZORK_RATE_LIMIT_ANON` | Anonymous limit | 100/60 |
| `ZORK_RATE_LIMIT_USER` | Authenticated limit | 1000/60 |
| `ZORK_RATE_LIMIT_TRUST_FORWARDED_FOR` | Trust X-Forwarded-For header | false |

## Input Validation

The rate limiter validates inputs and raises `ValueError` for invalid values:

- `limit` must be positive (> 0)
- `window_seconds` must be positive (> 0)

This prevents unexpected behavior from misconfiguration.

## Next Steps

- [Authentication](/authentication/setup) — Combined with rate limiting
- [Deployment](/deployment/overview) — Production deployment
