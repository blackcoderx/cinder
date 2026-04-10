---
title: Rate Limit Headers
description: Response headers reference for rate limiting
---

Every response includes rate limit information to help clients manage their requests.

## Allowed Responses (200-299)

These headers appear on successful requests:

```http
HTTP/1.1 200 OK
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 97
X-RateLimit-Reset: 1744300800
Content-Type: application/json
```

| Header | Example | Description |
|--------|---------|-------------|
| `X-RateLimit-Limit` | `100` | Maximum requests allowed in window |
| `X-RateLimit-Remaining` | `97` | Requests remaining in current window |
| `X-RateLimit-Reset` | `1744300800` | Unix timestamp when window resets |

## Rejected Responses (429)

When rate limit is exceeded:

```http
HTTP/1.1 429 Too Many Requests
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 0
X-RateLimit-Reset: 1744300800
Retry-After: 42
Content-Type: application/json

{"status": 429, "error": "Rate limit exceeded"}
```

| Header | Example | Description |
|--------|---------|-------------|
| `Retry-After` | `42` | Seconds until window resets and client can retry |

## Header Reference

### X-RateLimit-Limit

**Always present** on rate-limited endpoints.

```
X-RateLimit-Limit: 100
```

The maximum number of requests allowed in the current window.

### X-RateLimit-Remaining

**Always present** on rate-limited endpoints.

```
X-RateLimit-Remaining: 97
```

Requests remaining in the current window. When `0`, the next request will be rejected.

### X-RateLimit-Reset

**Always present** on rate-limited endpoints.

```
X-RateLimit-Reset: 1744300800
```

Unix timestamp (seconds since epoch) when the oldest request in the window will expire.

```python
from datetime import datetime

reset_timestamp = 1744300800
reset_time = datetime.fromtimestamp(reset_timestamp)
print(reset_time)  # 2026-04-10 12:00:00
```

### Retry-After

**Only present** when rate limit is exceeded (429 response).

```
Retry-After: 42
```

Seconds the client should wait before retrying. Calculated as:

```
ceil(X-RateLimit-Reset - current_time)
```

## Response Body on 429

```json
{
  "status": 429,
  "error": "Rate limit exceeded"
}
```

## Client Implementation Example

```javascript
async function apiRequest(url, options) {
  const response = await fetch(url, options);
  
  // Check rate limit headers
  const limit = response.headers.get('X-RateLimit-Limit');
  const remaining = response.headers.get('X-RateLimit-Remaining');
  const reset = response.headers.get('X-RateLimit-Reset');
  
  console.log(`Rate limit: ${remaining}/${limit}`);
  console.log(`Resets at: ${new Date(reset * 1000)}`);
  
  if (response.status === 429) {
    const retryAfter = response.headers.get('Retry-After');
    console.log(`Retrying in ${retryAfter} seconds...`);
    await sleep(retryAfter * 1000);
    return apiRequest(url, options); // Retry
  }
  
  return response;
}

function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}
```

## Server Implementation (Custom Backend)

If implementing a custom rate limit backend:

```python
from cinder.ratelimit import RateLimitBackend, RateLimitResult

class CustomRateLimitBackend(RateLimitBackend):
    async def check(self, key: str, limit: int, window: int) -> RateLimitResult:
        import time
        
        now = time.time()
        reset_at = now + window
        
        # Your rate limiting logic here
        allowed = True
        remaining = limit - 1
        
        return RateLimitResult(
            allowed=allowed,
            remaining=max(0, remaining),
            reset_at=reset_at
        )
```

The headers are automatically added by the middleware based on the `RateLimitResult`.

## IP Extraction

The rate limiter extracts client IP in this order:

1. `scope["client"][0]` — Direct ASGI connection
2. `X-Forwarded-For` header — First IP in list
3. Fallback: `"unknown"`

```
X-Forwarded-For: 192.168.1.1, 10.0.0.1, 172.16.0.1
                          ↑
                    This IP is used (first one)
```

## Headers by Scenario

| Scenario | Status | Headers Present |
|----------|---------|----------------|
| Normal request, under limit | 200 | `X-RateLimit-*` |
| Normal request, at limit | 429 | `X-RateLimit-*` + `Retry-After` |
| Rate limiting disabled | 200 | No rate limit headers |
| Rate limit backend error | 200 | No rate limit headers (fail-open) |

## Next Steps

- [Rate Limiting Overview](/rate-limiting/) — Quick start
- [Algorithm](/rate-limiting/algorithm/) — How it works
- [Configuration](/rate-limiting/configuration/) — Customize limits
