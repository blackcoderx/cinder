---
title: Redis Backends
description: How Cinder uses Redis across its subsystems
---

Cinder uses Redis differently depending on the subsystem. All subsystems share the same connection.

## Shared Connection

```
┌─────────────────────────────────────────────────────────┐
│                   redis_client.py                        │
├─────────────────────────────────────────────────────────┤
│  configure(url)  →  set URL                            │
│  get_client()    →  return singleton (lazy init)        │
│  close()        →  cleanup on shutdown                 │
└─────────────────────────────────────────────────────────┘
           │
           │  .get_client()
           ↓
  ┌─────────────────────────────────┐
  │  redis.asyncio.Redis singleton   │
  └─────────────────────────────────┘
           │
           ├──→ RedisCacheBackend.get(key)
           ├──→ RedisCacheBackend.set(key, value)
           ├──→ RedisRateLimitBackend.check(key)
           └──→ RedisBroker.publish(channel)
```

## Cache Backend

### Key Format

```
{cinder}:{response}:{collection}:{type}:{fingerprint}
```

Examples:
- `cinder:response:posts:list:a1b2c3d4...` — List endpoint cache
- `cinder:response:posts:get:550e8400...` — Single record cache

### Operations Used

| Operation | Purpose |
|-----------|---------|
| `GET` | Read from cache |
| `SET` / `SETEX` | Write to cache with optional TTL |
| `DEL` | Delete specific keys |
| `SCAN` + `DEL` | Pattern-based deletion |
| `SADD` / `SMEMBERS` / `DEL` | Tag-based invalidation tracking |

### Tag Sets

Cache keys are grouped by collection using Redis sets:

```
Tag: "cinder:tag:collection:posts"
Members: ["cinder:response:posts:list:a1b2...", "cinder:response:posts:list:c3d4..."]
```

When a POST/PATCH/DELETE happens, the tag is queried and all related cache keys are deleted.

## Rate Limit Backend

### Key Format

```
ratelimit:{path}:{scope}:{identifier}
```

Examples:
- `ratelimit:/api/posts:ip:192.168.1.1`
- `ratelimit:/api/posts:user:user-uuid-123`

### Operations Used

| Operation | Purpose |
|-----------|---------|
| `ZREMRANGEBYSCORE` | Remove expired entries (window sliding) |
| `ZCARD` | Count entries in current window |
| `ZADD` | Add new request timestamp |
| `ZRANGE` | Get oldest entry (for reset time) |
| `PEXPIRE` | Auto-expire key after window |

### Why Sorted Sets?

The sliding window algorithm needs to:
1. Remove old entries (outside the window)
2. Count current entries
3. Add new entry
4. All atomically to prevent race conditions

Sorted sets with timestamps as scores make this efficient and atomic.

## Realtime Broker

### Channel Format

Channels are arbitrary strings:

```
collection:{collection_name}   # e.g., "collection:posts"
notifications:user-{id}        # e.g., "notifications:user-123"
system:alerts
```

### Operations Used

| Operation | Purpose |
|-----------|---------|
| `PUBLISH` | Send message to channel |
| `SUBSCRIBE` | Listen to channel (background task) |

### Architecture

```
Server 1 ──PUBLISH──→ Channel ──→ Server 2 (via SUBSCRIBE)
                      │
                      └──→ Server 3 (via SUBSCRIBE)
```

Messages fan out to all subscribed processes, enabling horizontal scaling.

## Memory Backends

When Redis is unavailable, Cinder uses in-memory alternatives:

### Cache Fallback

```python
# MemoryCacheBackend
class MemoryCacheBackend:
    _store: dict[str, bytes]      # Simple dict
    _timers: dict[str, asyncio.TimerHandle]  # TTL handling
    _tags: dict[str, set[str]]    # Tag tracking
```

### Rate Limit Fallback

```python
# MemoryRateLimitBackend
class MemoryRateLimitBackend:
    _windows: dict[str, deque[float]]  # key → timestamps
```

### Realtime Fallback

```python
# RealtimeBroker (in-process)
class RealtimeBroker:
    _subscribers: dict[str, asyncio.Queue]  # channel → queues
```

## Key Differences

| Feature | Redis Backend | Memory Backend |
|---------|--------------|---------------|
| Multi-process | ✅ Safe | ❌ Per-process |
| Survives restart | ✅ Persistent | ❌ Lost |
| Cross-instance | ✅ Shared | ❌ Isolated |
| Performance | Fast | Fast (single-process) |
| Setup required | Redis server | None |

## When to Use Each

| Scenario | Recommended Backend |
|----------|-------------------|
| Development | Memory (no setup) |
| Testing | Memory |
| Single gunicorn worker | Either works |
| Multiple gunicorn workers | Redis required |
| Kubernetes replicas | Redis required |
| Horizontal scaling | Redis required |

## Custom Backends

Override any backend with your own implementation:

```python
from cinder.cache import CacheBackend
from cinder.ratelimit import RateLimitBackend

# Custom cache backend
class MyCacheBackend(CacheBackend):
    async def get(self, key: str) -> bytes | None: ...
    async def set(self, key: str, value: bytes, ttl: int | None = None) -> None: ...
    async def delete(self, *keys: str) -> None: ...

app.cache.use(MyCacheBackend())

# Custom rate limit backend
class MyRateLimitBackend(RateLimitBackend):
    async def check(self, key: str, limit: int, window: int) -> RateLimitResult: ...

app.rate_limit.use(MyRateLimitBackend())
```

## Next Steps

- [Redis Overview](/redis/) — Shared infrastructure
- [Caching](/caching/) — Response caching
- [Rate Limiting](/rate-limiting/) — Request throttling
