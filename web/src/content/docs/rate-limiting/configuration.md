---
title: Rate Limiting Configuration
description: Customize rate limits for your API
---

## Per-Route Rules

Override default limits for specific paths:

```python
from cinder import Cinder

app = Cinder(database="app.db")

# Stricter limit for auth endpoints
app.rate_limit.rule("/api/auth/login", limit=10, window=60)

# Stricter limit for write operations
app.rate_limit.rule("/api/posts", limit=50, window=60)

# Generous limit for read-heavy endpoints
app.rate_limit.rule("/api/public", limit=500, window=60)
```

### Rule Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `path_prefix` | `str` | Yes | Path to apply rule to (uses `startswith`) |
| `limit` | `int` | Yes | Maximum requests in window |
| `window` | `int` | No | Window in seconds (default: 60) |
| `scope` | `str` | No | `ip`, `user`, or `both` (default: `ip`) |

### Path Matching

Rules match by prefix:

```python
app.rate_limit.rule("/api/auth", limit=10, window=60)

# Matches:
#   /api/auth/login    ✓
#   /api/auth/register ✓
#   /api/auth/logout   ✓

# Does not match:
#   /api/posts         ✗
#   /api/users         ✗
```

### Rule Priority

First matching rule wins:

```python
# Specific rule first
app.rate_limit.rule("/api/auth/login", limit=5, window=60)
# Generic rule second
app.rate_limit.rule("/api/auth", limit=10, window=60)
```

## Scope Options

Control what identifies the client:

### `ip` — By IP Address

```python
app.rate_limit.rule("/api/public", limit=100, window=60, scope="ip")
```

Rate limit applies per IP address. Good for anonymous endpoints.

### `user` — By User ID

```python
app.rate_limit.rule("/api/write", limit=50, window=60, scope="user")
```

Rate limit applies per authenticated user. Falls back to IP if not authenticated.

### `both` — User or IP

```python
app.rate_limit.rule("/api/data", limit=100, window=60, scope="both")
```

Authenticated users are limited by user ID. Anonymous users are limited by IP.

## Default Limits

### Anonymous (No Token)

```python
app.rate_limit.rule("/", limit=100, window=60, scope="ip")
```

### Authenticated

```python
app.rate_limit.rule("/", limit=1000, window=60, scope="user")
```

Higher limits for authenticated users who are trusted.

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `CINDER_RATE_LIMIT_ENABLED` | `true` | Enable/disable rate limiting |
| `CINDER_RATE_LIMIT_ANON` | `100/60` | Anonymous limit |
| `CINDER_RATE_LIMIT_USER` | `1000/60` | User limit |

### Format

```
CINDER_RATE_LIMIT_ANON=100/60
CINDER_RATE_LIMIT_USER=1000/60
```

Format: `{limit}/{window_seconds}`

## Custom Backend

```python
from cinder.ratelimit import RateLimitBackend, RateLimitResult

class MyRateLimitBackend(RateLimitBackend):
    async def check(self, key: str, limit: int, window: int) -> RateLimitResult:
        # Your implementation
        return RateLimitResult(allowed=True, remaining=limit-1, reset_at=time.time() + window)
    
    async def close(self) -> None:
        pass

app.rate_limit.use(MyRateLimitBackend())
```

## Complete Example

```python
from cinder import Cinder

app = Cinder(database="app.db")
app.configure_redis(url="redis://localhost:6379/0")

# Strict limits for auth endpoints
app.rate_limit.rule("/api/auth/login", limit=5, window=60, scope="ip")
app.rate_limit.rule("/api/auth/register", limit=10, window=60, scope="ip")

# Write limits for authenticated users
app.rate_limit.rule("/api/posts", limit=50, window=60, scope="user")
app.rate_limit.rule("/api/comments", limit=50, window=60, scope="user")

# Generous limits for public read endpoints
app.rate_limit.rule("/api/public", limit=500, window=60, scope="ip")

# All other endpoints use defaults
# (100/60 for anonymous, 1000/60 for authenticated)

app.serve()
```

## Disable Rate Limiting

```python
# Via code
app.rate_limit.enable(False)

# Via environment
# CINDER_RATE_LIMIT_ENABLED=false
```

## Chaining Rules

```python
app = Cinder(database="app.db")

# Chain multiple rules
app.rate_limit \
    .rule("/api/auth/login", limit=5, window=60) \
    .rule("/api/auth/register", limit=10, window=60) \
    .rule("/api/write", limit=100, window=60, scope="user")
```

## Common Patterns

### Pattern 1: Auth Protection

```python
# Prevent brute force on login
app.rate_limit.rule("/api/auth/login", limit=5, window=60, scope="ip")

# Limit registration spam
app.rate_limit.rule("/api/auth/register", limit=3, window=3600, scope="ip")
```

### Pattern 2: Tiered Access

```python
# Free tier: strict limits
app.rate_limit.rule("/api/", limit=100, window=60, scope="user")

# Premium tier: generous limits
app.rate_limit.rule("/api/", limit=10000, window=60, scope="user")
# (Enforced by checking user's plan in custom backend)
```

### Pattern 3: Write Protection

```python
# Limit write operations
app.rate_limit.rule("/api/", limit=10, window=60, scope="user")
```

## Next Steps

- [Algorithm](/rate-limiting/algorithm/) — How rate limiting works
- [Headers](/rate-limiting/headers/) — Response header reference
