---
title: Cache Invalidation
description: How Cinder automatically invalidates cached responses
---

Cache invalidation ensures clients always see fresh data after writes.

## The Problem

```
User A reads post 123 → Cache stores response
User B updates post 123 → Database updated
User A reads post 123 → Still returns cached (stale) data ❌
```

Cinder solves this by invalidating cache on every write.

## Tag-Based Invalidation

Cinder uses tags to track which cache entries belong to which collection:

```
Tag: "tag:collection:posts"
  └── Contains: [key1, key2, key3, ...]
```

When a write happens, Cinder:
1. Finds all cache keys for that collection
2. Deletes them all
3. Next read fetches fresh data

## How It Works

### Automatic Hook Registration

When you configure caching, Cinder registers hooks on all collections:

```python
install_invalidation(registry, cache_backend, collections)
```

This registers three hooks per collection:

| Hook | Action |
|------|--------|
| `{collection}:after_create` | Invalidate list cache |
| `{collection}:after_update` | Invalidate list + get cache |
| `{collection}:after_delete` | Invalidate list + get cache |

### Invalidation Flow

```
POST /api/posts {title: "New Post"}
        │
        ▼
┌───────────────────────────────────┐
│ 1. Insert into database           │
│ 2. Fire after_create hook         │
└───────────────────────────────────┘
        │
        ▼
┌───────────────────────────────────┐
│ 3. Query tag set                  │
│    SMEMBERS "tag:collection:posts"│
│    → [key1, key2, key3, ...]     │
└───────────────────────────────────┘
        │
        ▼
┌───────────────────────────────────┐
│ 4. Delete all cached list entries │
│    DEL key1 key2 key3 ...         │
└───────────────────────────────────┘
        │
        ▼
┌───────────────────────────────────┐
│ 5. Delete the tag set             │
│    DEL "tag:collection:posts"     │
└───────────────────────────────────┘
```

### For Update and Delete

```
PATCH /api/posts/123 {title: "Updated"}
        │
        ▼
┌───────────────────────────────────┐
│ 1. Update in database             │
│ 2. Fire after_update hook         │
└───────────────────────────────────┘
        │
        ├──→ Invalidate list cache (same as create)
        │
        └──→ Invalidate single record cache
              DEL "response:posts:get:123"
```

## Tag Structure

```
┌─────────────────────────────────────────────────────┐
│                    Redis / Memory                    │
├─────────────────────────────────────────────────────┤
│                                                      │
│  Tag Set: "tag:collection:posts"                    │
│  Members: [                                          │
│    "response:posts:list:a1b2...",                   │
│    "response:posts:list:c3d4...",                   │
│    "response:posts:list:e5f6..."                    │
│  ]                                                   │
│                                                      │
│  Cache Entry: "response:posts:list:a1b2..."         │
│  Value: [                                            │
│    200,                                              │
│    {"Content-Type": "application/json"},             │
│    b'{"items": [...], "total": 42}'                 │
│  ]                                                   │
│                                                      │
└─────────────────────────────────────────────────────┘
```

## What Gets Invalidated

| Operation | List Cache | Get Cache |
|-----------|------------|-----------|
| POST (create) | ✅ Invalidated | ❌ No get cache |
| PATCH (update) | ✅ Invalidated | ✅ Invalidated |
| DELETE | ✅ Invalidated | ✅ Invalidated |

## Example Scenarios

### Scenario 1: New Post Created

```bash
POST /api/posts {"title": "Hello"}

# Result:
# - List cache for "posts" is deleted
# - Next GET /api/posts fetches fresh data including the new post
```

### Scenario 2: Post Updated

```bash
PATCH /api/posts/123 {"title": "Updated Title"}

# Result:
# - List cache for "posts" is deleted
# - Get cache for post 123 is deleted
# - Next requests get fresh data
```

### Scenario 3: Post Deleted

```bash
DELETE /api/posts/123

# Result:
# - List cache for "posts" is deleted
# - Get cache for post 123 is deleted
```

## Manual Invalidation

### Delete by Pattern

```python
# Delete all cache entries for posts
await app.cache.backend.delete_pattern("response:posts:*")
```

### Clear Everything

```python
# Clear all cache
await app.cache.backend.clear()
```

### Delete by Key

```python
# Delete specific cache entry
await app.cache.backend.delete("response:posts:get:123")
```

## Invalidation + Realtime

When realtime is configured, the flow is:

```
POST /api/posts
        │
        ├──→ 1. Insert into database
        ├──→ 2. Invalidate cache
        ├──→ 3. Publish event to "collection:posts"
        │
        ▼
Connected clients receive push notification:
        │
        └──→ "collection:posts" event
              │
              └──→ Client refetches data
                    (cache miss → fresh data)
```

This ensures clients stay synchronized without polling.

## Best Practices

1. **Keep TTL reasonable** — Long TTL + frequent updates = stale reads
2. **Use per_user=True for private data** — Prevents cross-user leaks
3. **Exclude volatile endpoints** — `/api/search`, `/api/feed`, etc.
4. **Monitor hit rate** — `X-Cache: HIT` / `MISS` ratio

## Troubleshooting

### Stale Data

If you see stale data:

1. Check if TTL is too long
2. Verify invalidation hooks are registered
3. Check for cache backend errors in logs

### Cache Never Hits

Possible causes:
- Different query parameters (each is a separate cache key)
- Per-user enabled and testing as different users
- 4xx/5xx responses (never cached)

## Next Steps

- [Cache-Aside](/caching/cache-aside/) — How caching works
- [Configuration](/caching/configuration/) — Cache options
