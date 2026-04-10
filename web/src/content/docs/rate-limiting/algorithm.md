---
title: Rate Limiting Algorithm
description: How Cinder's sliding window rate limiter works
---

Cinder uses a sliding window algorithm to track and limit request rates.

## Sliding Window Concept

The sliding window tracks requests within a time window:

```
Time ──────────────────────────────────────────────────────→

◄────────────────── window (60s) ──────────────────────────►
        │                                           │
        ▼                                           ▼
   oldest                                    newest
   request                                  request
        │                                           │
        └─── ✗ ─ ✗ ─ ✓ ─ ✓ ─ ✓ ─ ✗ ─ ✓ ─ ✓ ────┘
           ▲   ▲       ▲       ▲   ▲
         outside                           inside
         window                            window
           
   Requests inside window: 5
   If limit = 5: NEXT REQUEST REJECTED
```

As time passes, old requests slide out of the window, making room for new ones.

## How Requests Are Tracked

### Key Components

| Component | Description |
|-----------|-------------|
| Window | Fixed time period (e.g., 60 seconds) |
| Limit | Maximum requests allowed in window |
| Counter | Current request count in window |
| Key | Identifier (IP, user ID, or both) |

### Request Flow

```
1. Request arrives
         │
         ▼
2. Determine rate limit key
   - Anonymous: client IP
   - Authenticated: user ID
         │
         ▼
3. Look up request timestamps in window
         │
         ├─── Within limit? ──→ Allow request, record timestamp
         │
         └─── Over limit? ────→ Reject with 429
```

## Redis Backend: Sorted Sets

The Redis backend uses sorted sets for atomic operations:

```
Key: "ratelimit:/api/posts:ip:192.168.1.1"
Members: {timestamp: "request-id"}

Sorted by timestamp (score = time request was made)

Example sorted set:
  {
    1744300740: "req-001",
    1744300752: "req-002",
    1744300768: "req-003"
  }
```

### Operations

| Step | Redis Command | Description |
|------|---------------|-------------|
| 1 | `ZREMRANGEBYSCORE key -inf (now - window)` | Remove old entries |
| 2 | `ZCARD key` | Count remaining entries |
| 3 | If under limit: `ZADD key now request-id` | Add new request |
| 4 | If under limit: `PEXPIRE key window` | Auto-expire key |

### Why Atomic?

Using sorted sets and atomic operations prevents race conditions:

```
Without atomicity (BAD):

Worker 1: ZCARD → 99 requests
Worker 2: ZCARD → 99 requests
Worker 1: ZADD → 100 requests (allowed)
Worker 2: ZADD → 101 requests (allowed) ❌

With atomicity (GOOD):

Worker 1: Atomic check → reject at 100
Worker 2: Atomic check → reject at 100
Worker 1: 100th request → allowed
Worker 2: 100th request → rejected ✓
```

## Memory Backend: Deques

The memory backend uses Python deques:

```python
# Simplified concept
class MemoryRateLimitBackend:
    _windows: dict[str, deque[float]]  # key → timestamps
    
    async def check(self, key, limit, window):
        now = time.monotonic()
        timestamps = self._windows.get(key, deque())
        
        # Remove expired
        cutoff = now - window
        while timestamps and timestamps[0] < cutoff:
            timestamps.popleft()
        
        # Check limit
        if len(timestamps) >= limit:
            return RateLimitResult(
                allowed=False,
                remaining=0,
                reset_at=now + window
            )
        
        # Add new timestamp
        timestamps.append(now)
        self._windows[key] = timestamps
        
        return RateLimitResult(
            allowed=True,
            remaining=limit - len(timestamps),
            reset_at=now + window
        )
```

### Limitation

Memory rate limiting is **per-process**. With multiple workers:

```
Worker 1: tracks requests separately
Worker 2: tracks requests separately
Worker 3: tracks requests separately

User makes 100 requests
  → Worker 1 handles 34 requests (allowed)
  → Worker 2 handles 33 requests (allowed)
  → Worker 3 handles 33 requests (allowed)
  
Total: 100 requests (should be limited to 100)
Each worker thinks: 33-34 requests (under 100)
```

This is why Redis is recommended for production with multiple workers.

## Key Format

```
ratelimit:{path}:{scope}:{identifier}
```

| Scope | Identifier | Example |
|-------|------------|---------|
| `ip` | Client IP | `ratelimit:/api/posts:ip:192.168.1.1` |
| `user` | User ID | `ratelimit:/api/posts:user:abc123` |
| `both` | User ID or IP | `ratelimit:/api/posts:both:abc123` |

## Window Reset

The window slides continuously. The `X-RateLimit-Reset` header shows when enough old requests expire:

```
Current time: 10:00
Window: 60 seconds
Limit: 100

Requests in window:
  09:59:30 ────────────────── 10:00:00
  ◄──────── 30 seconds ───────►
  
Oldest request expires at: 09:59:30 + 60s = 10:00:30
X-RateLimit-Reset: 10:00:30
```

## Fail-Open

Both backends fail open:

```python
try:
    result = await backend.check(key, limit, window)
except Exception:
    logger.exception("Rate-limit backend error")
    # Allow request through
    return await self.app(scope, receive, send)
```

Errors are logged but never block legitimate users.

## Next Steps

- [Configuration](/rate-limiting/configuration/) — Set custom limits
- [Headers](/rate-limiting/headers/) — Response headers reference
