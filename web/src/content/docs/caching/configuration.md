---
title: Cache Configuration
description: All cache configuration options
---

## Programmatic Configuration

### Enable Cache

```python
from cinder import Cinder

app = Cinder(database="app.db")

# Enable with in-memory backend (default)
app.cache.enable()

# Disable cache entirely
app.cache.enable(False)
```

### Use Backend

```python
from cinder import Cinder
from cinder.cache import RedisCacheBackend, MemoryCacheBackend

app = Cinder(database="app.db")

# Use Redis backend
app.cache.use(RedisCacheBackend())

# Or use memory backend explicitly
app.cache.use(MemoryCacheBackend())
```

### Configure Options

```python
app.cache.configure(
    default_ttl=600,    # Cache TTL in seconds
    per_user=True,      # Separate cache per user
)
```

### Exclude Paths

```python
app.cache.exclude(
    "/api/feed",
    "/api/search",
    "/api/notifications",
)
```

## Configuration Options

| Method | Parameters | Default | Description |
|--------|------------|---------|-------------|
| `enable()` | `value=True` | Enabled when Redis configured | Enable/disable caching |
| `use()` | `backend` | Auto (Redis or Memory) | Set cache backend |
| `configure()` | `default_ttl`, `per_user` | 300s, True | Set cache options |
| `exclude()` | `*paths` | None | Paths to never cache |

### default_ttl

Time-to-live for cache entries in seconds:

```python
app.cache.configure(default_ttl=600)  # 10 minutes
```

### per_user

Separate cache entries per user:

```python
# Default: True (safer, prevents data leaks)
app.cache.configure(per_user=True)

# Faster, but only for fully public data
app.cache.configure(per_user=False)
```

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `CINDER_CACHE_ENABLED` | `auto` | `true`/`false`/`auto` |
| `CINDER_CACHE_TTL` | `300` | Default TTL in seconds |
| `CINDER_CACHE_PREFIX` | `cinder` | Redis key prefix |

### CINDER_CACHE_ENABLED

```bash
# Auto (enable if Redis configured)
CINDER_CACHE_ENABLED=auto

# Force enable
CINDER_CACHE_ENABLED=true

# Disable entirely
CINDER_CACHE_ENABLED=false
```

### CINDER_CACHE_TTL

```bash
# 5 minutes (default)
CINDER_CACHE_TTL=300

# 1 hour
CINDER_CACHE_TTL=3600
```

### CINDER_CACHE_PREFIX

```bash
# Custom prefix for Redis keys
CINDER_CACHE_PREFIX=myapp
```

## Complete Example

```python
from cinder import Cinder
from cinder.cache import RedisCacheBackend

app = Cinder(database="app.db")

# Configure Redis (enables Redis backend)
app.configure_redis(url="redis://localhost:6379/0")

# Fine-tune cache settings
app.cache.configure(
    default_ttl=600,    # 10 minutes
    per_user=True,       # Separate cache per user
)

# Exclude volatile endpoints
app.cache.exclude(
    "/api/feed",
    "/api/search",
    "/api/realtime",
)

# Register collections
app.register(posts)
app.register(comments)

# Start server
app.serve()
```

## Backend Auto-Detection

| Configuration | Backend Used |
|---------------|--------------|
| No Redis configured | `MemoryCacheBackend` |
| `CINDER_REDIS_URL` set | `RedisCacheBackend` |
| `app.cache.use(backend)` | Custom backend |
| `app.configure_redis()` | `RedisCacheBackend` |

## Combining Options

```python
# All options combined
app = Cinder(database="app.db")
app.configure_redis(url="redis://localhost:6379/0")

app.cache.configure(
    default_ttl=300,
    per_user=True,
)
app.cache.exclude("/api/volatile")

# Same as above, but with env vars
# CINDER_REDIS_URL=redis://localhost:6379/0
# CINDER_CACHE_TTL=300
```

## Next Steps

- [Cache-Aside](/caching/cache-aside/) — How caching works
- [Cache Invalidation](/caching/invalidation/) — Automatic invalidation
