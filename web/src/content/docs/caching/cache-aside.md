---
title: Cache-Aside
description: How Cinder's cache-aside pattern works
---

The cache-aside pattern caches data only when needed, keeping the cache fresh with writes.

## How It Works

```
┌─────────────────────────────────────────────────────────────┐
│                    GET Request                               │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
                    ┌─────────────────┐
                    │  Check Cache    │
                    └────────┬────────┘
                             │
              ┌──────────────┴──────────────┐
              ▼                             ▼
        ┌───────────┐               ┌───────────┐
        │  HIT      │               │  MISS     │
        └─────┬─────┘               └─────┬─────┘
              │                             │
              ▼                             ▼
    ┌─────────────────┐           ┌─────────────────┐
    │ Return Cached   │           │ Query Database  │
    │ Response        │           └────────┬────────┘
    └─────────────────┘                    │
                                           ▼
                                 ┌─────────────────┐
                                 │ Store Response  │
                                 │ in Cache        │
                                 └────────┬────────┘
                                          │
                                          ▼
                                 ┌─────────────────┐
                                 │ Return Response │
                                 └─────────────────┘
```

## Cache Keys

### List Endpoints

```
response:{collection}:list:{fingerprint}
```

The fingerprint is a hash of:
- Request path
- Query string (normalized, sorted)
- User segment (if per-user caching enabled)

Example:
```
response:posts:list:a1b2c3d4e5f6g7h8
```

### Get Endpoints

```
response:{collection}:get:{id}
```

Example:
```
response:posts:get:550e8400-e29b-41d4-a716-446655440000
```

## Per-User Segmentation

By default, cache keys include the user ID to prevent data leaking between users:

```python
app.cache.configure(per_user=True)
```

| User | Cache Key |
|------|-----------|
| Alice | `response:posts:list:...:alice-id` |
| Bob | `response:posts:list:...:bob-id` |
| Anonymous | `response:posts:list:...:anon` |

This ensures:
- Alice never sees Bob's private posts
- Owner-rule filtered results don't leak
- User-specific data stays isolated

### When Disabled

```python
app.cache.configure(per_user=False)
```

All users share the same cache for public endpoints. Useful for read-heavy public data.

## Cache Flow Details

### On Cache HIT

```
1. Extract path, query string, user segment
2. Build cache key
3. GET from cache backend
4. Return cached response with X-Cache: HIT
```

### On Cache MISS

```
1. Extract path, query string, user segment
2. Build cache key
3. GET from cache backend → None
4. Pass through to route handler
5. Capture response
6. If 200-299 status and no Set-Cookie:
   a. Store in cache with TTL
   b. Add key to collection tag set
7. Return response with X-Cache: MISS
```

### Response Filtering

Only successful responses are cached:

| Response | Cached? |
|----------|---------|
| 200 OK | ✅ Yes |
| 201 Created | ✅ Yes |
| 4xx errors | ❌ No |
| 5xx errors | ❌ No |
| Set-Cookie header | ❌ No |
| Authenticated user | Depends on `per_user` setting |

## TTL (Time-To-Live)

The cache entry expires after `TTL` seconds:

```python
app.cache.configure(default_ttl=300)  # 5 minutes
```

After TTL expires:
- Next request triggers a fresh database query
- Old entry is automatically evicted

Benefits:
- Fresh data eventually appears
- Stale data auto-expires
- No manual cache clearing needed

## Excluded Paths

Prevent specific paths from being cached:

```python
app.cache.exclude("/api/feed", "/api/search", "/api/notifications")
```

These requests always hit the database.

## Middleware Order

Cache middleware sits in the middleware stack:

```
1. ErrorHandler  (outermost)
2. RequestID
3. CORS
4. RateLimit     ← Before cache (blocks abuse)
5. Cache         ← Cache lookup here
6. Auth          ← User resolved here
7. Routes        (innermost)
```

Cache middleware runs **above** auth, so it has access to the authenticated user for per-user segmentation.

## Headers Summary

| Header | Value | When |
|--------|-------|------|
| `X-Cache` | `HIT` | Response from cache |
| `X-Cache` | `MISS` | Fresh response from database |

## Next Steps

- [Cache Invalidation](/caching/invalidation/) — How writes clear the cache
- [Configuration](/caching/configuration/) — All cache options
