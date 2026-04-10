---
title: Redis
description: Shared Redis infrastructure for Cinder's optional subsystems
---

Redis powers Cinder's optional subsystems: caching, rate limiting, and realtime. Configure it once, use it everywhere.

## Overview

```
┌─────────────────────────────────────────────────────────┐
│              app.configure_redis(url="...")              │
│                     OR CINDER_REDIS_URL                   │
└─────────────────────────┬───────────────────────────────┘
                          │
           ┌──────────────┼──────────────┐
           ↓              ↓              ↓
      ┌─────────┐   ┌───────────┐  ┌─────────┐
      │  Cache  │   │Rate Limit │  │ Realtime│
      └─────────┘   └───────────┘  └─────────┘
```

When Redis is configured:
- **Cache** uses `RedisCacheBackend` (shared storage)
- **Rate Limiting** uses `RedisRateLimitBackend` (multi-process safe)
- **Realtime** uses `RedisBroker` (fan-out pub/sub)

When Redis is not configured, all subsystems fall back to in-memory alternatives.

## Configuration

### Environment Variable

```bash
CINDER_REDIS_URL=redis://localhost:6379/0
```

### Programmatic

```python
from cinder import Cinder

app = Cinder(database="app.db")

# Configure Redis for all subsystems
app.configure_redis(url="redis://localhost:6379/0")

# Or with authentication
app.configure_redis(url="redis://user:password@redis.example.com:6379/0")
```

### URL Formats Supported

| URL | Description |
|-----|-------------|
| `redis://localhost:6379/0` | Local Redis, database 0 |
| `redis://localhost:6379/` | Local Redis, default database |
| `rediss://host:6379` | Redis with TLS |
| `redis://password@host:6379` | Password authentication |
| `redis://user:password@host:6379` | User + password auth |

## The Shared Client

Cinder uses a single Redis connection shared across all subsystems:

```
┌─────────────────────────────────────────┐
│           redis_client (singleton)       │
├─────────────────────────────────────────┤
│  _url: str | None                       │
│  _client: redis.asyncio.Redis | None    │
└─────────────────────────────────────────┘
                      ↑
        ┌─────────────┼─────────────┐
        ↓             ↓             ↓
   ┌─────────┐   ┌─────────┐   ┌─────────┐
   │  Cache  │   │  Rate   │   │ Realtime│
   │Backend  │   │  Limit  │   │ Broker  │
   └─────────┘   └─────────┘   └─────────┘
```

Benefits:
- **Single connection pool** for all Redis operations
- **Lazy initialization** — client created on first use
- **Proper cleanup** — closed during app shutdown

## Graceful Degradation

Each subsystem falls back independently when Redis is unavailable:

| Subsystem | Redis Available | Redis Unavailable |
|-----------|-----------------|-------------------|
| Cache | `RedisCacheBackend` | `MemoryCacheBackend` |
| Rate Limiting | `RedisRateLimitBackend` | `MemoryRateLimitBackend` |
| Realtime | `RedisBroker` | `RealtimeBroker` (single-process) |

This means:
- **Dev mode**: No Redis needed, everything works with in-memory backends
- **Production**: Configure Redis for multi-process safety and shared state

## Installation

```bash
pip install cinder[redis]
```

This installs the `redis` package. Without it, Redis features are unavailable but in-memory fallbacks work fine.

## Shared Infrastructure Diagram

```
                    Your App
                        │
                        ▼
              ┌─────────────────┐
              │ Cinder (build)  │
              └────────┬────────┘
                       │
          ┌────────────┼────────────┐
          ↓            ↓            ↓
   ┌────────────┐ ┌───────────┐ ┌──────────┐
   │   Cache    │ │Rate Limit │ │ Realtime │
   │            │ │           │ │          │
   │ GET cache  │ │ 429 check │ │ Pub/Sub  │
   └────────────┘ └───────────┘ └──────────┘
          │            │            │
          └────────────┼────────────┘
                       │
                       ▼
              ┌─────────────────┐
              │ Redis Client    │
              │ (singleton)     │
              └─────────────────┘
```

## When to Use Redis

### Use Redis For:

- **Production deployments** with multiple workers
- **Multi-instance deployments** (horizontal scaling)
- **Persistent caching** across restarts
- **Accurate rate limiting** across all workers
- **Realtime** with multiple server instances

### Skip Redis For:

- **Local development**
- **Single-worker deployments**
- **Testing**

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `CINDER_REDIS_URL` | — | Redis connection URL |
| `REDIS_URL` | — | Fallback Redis URL |

## Health Checks

Verify Redis connectivity:

```bash
cinder doctor --app app.py
```

Output:
```
[OK] Database: postgres://...
[OK] Redis: redis://localhost:6379/0
```

## Next Steps

- [Redis Backends](/redis/backends/) — Backend implementations
- [Caching](/caching/) — Response caching
- [Rate Limiting](/rate-limiting/) — Request throttling
- [Realtime](/realtime/overview/) — Real-time updates
