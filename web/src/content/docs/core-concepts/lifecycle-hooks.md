---
title: Lifecycle Hooks
description: Execute custom logic around CRUD operations
---

Hooks let you inject custom code at specific points during request processing. Think of them as middleware that's specific to a collection or event.

## The Pipeline Concept

Every API request flows through a pipeline of hooks:

```
┌─────────────┐    ┌─────────────────┐    ┌──────────────┐    ┌───────────┐
│   Request   │ → │ before_* hooks  │ → │  DB Operation │ → │ after_*  │
│   arrives   │    │ (can mutate)    │    │               │    │ (observe) │
└─────────────┘    └─────────────────┘    └──────────────┘    └───────────┘
```

- **before_* hooks** run before the database operation and can modify data or abort the request
- **after_* hooks** run after the operation and can react to results (return values are ignored)

## Registering Hooks

### Method 1: Direct Call

```python
async def add_slug(data, ctx):
    data["slug"] = data["title"].lower().replace(" ", "-")
    return data

posts.on("before_create", add_slug)
```

### Method 2: Decorator

```python
@posts.on("before_create")
async def add_slug(data, ctx):
    data["slug"] = data["title"].lower().replace(" ", "-")
    return data
```

Both forms call the same underlying code — use whichever reads better.

## Handler Signature

Every hook receives two arguments:

```python
async def handler(payload, ctx):
    # payload - varies by event (see table below)
    # ctx     - CinderContext with request metadata
    
    return payload  # for before_* hooks
```

### The Context Object

```python
class CinderContext:
    user: dict | None      # Authenticated user (or None)
    request_id: str        # Unique request ID for tracing
    collection: str        # Collection name
    operation: str          # "create", "read", "update", "delete", "list"
    request: Request       # Starlette request object
    extra: dict            # Ad-hoc data storage
```

## Collection Events

### Create Events

| Event | Payload | Mutable? | Description |
|-------|---------|---------|-------------|
| `before_create` | `dict` of input data | Yes — return modified dict | Runs before INSERT |
| `after_create` | `dict` of saved record | No | Runs after INSERT |

### Read Events

| Event | Payload | Mutable? | Description |
|-------|---------|---------|-------------|
| `before_read` | record `id` (string) | Yes — modify ID to fetch | Runs before SELECT |
| `after_read` | `dict` of record | Yes — return modified dict | Runs after SELECT |

### List Events

| Event | Payload | Mutable? | Description |
|-------|---------|---------|-------------|
| `before_list` | `{"filters": {}, "order_by": "...", "limit": 20, "offset": 0}` | Yes | Runs before SELECT |
| `after_list` | `list[dict]` of records | Yes — return modified list | Runs after SELECT |

### Update Events

| Event | Payload | Mutable? | Description |
|-------|---------|---------|-------------|
| `before_update` | `dict` of input data | Yes | Runs before UPDATE |
| `after_update` | `(new_record, old_record)` tuple | No | Runs after UPDATE |

### Delete Events

| Event | Payload | Mutable? | Description |
|-------|---------|---------|-------------|
| `before_delete` | `dict` of record being deleted | Can cancel | Runs before DELETE |
| `after_delete` | `dict` of deleted record | No | Runs after DELETE |

## Aborting Operations

### Return an Error

Raise `CinderError` to stop the request and return an error response:

```python
from cinder.errors import CinderError

@posts.on("before_create")
async def validate_title(data, ctx):
    if len(data.get("title", "")) < 3:
        raise CinderError(400, "Title must be at least 3 characters")
    return data
```

### Cancel Delete (Soft Delete)

Use `CinderError.cancel_delete()` to stop deletion without returning an error:

```python
@messages.on("before_delete")
async def soft_delete(record, ctx):
    # Mark as deleted instead of actually deleting
    await ctx.request.app.db.execute(
        "UPDATE messages SET is_deleted = 1 WHERE id = ?",
        (record["id"],)
    )
    raise CinderError.cancel_delete()
```

The DELETE request returns `200 OK` but the record stays in the database.

## Common Patterns

### Pattern 1: Data Transformation

Transform data before saving:

```python
@posts.on("before_create")
async def slugify(data, ctx):
    data["slug"] = data.get("title", "").lower().replace(" ", "-")
    return data
```

### Pattern 2: Validation

Validate data and reject invalid input:

```python
@products.on("before_create")
async def validate_price(data, ctx):
    price = data.get("price", 0)
    if price < 0:
        raise CinderError(400, "Price cannot be negative")
    if price > 1000000:
        raise CinderError(400, "Price exceeds maximum allowed")
    return data
```

### Pattern 3: Audit Logging

Log changes for audit trails:

```python
@orders.on("after_update")
async def log_status_change(payload, ctx):
    new_record, old_record = payload
    if new_record["status"] != old_record["status"]:
        await audit_log.insert({
            "user_id": ctx.user["id"],
            "order_id": new_record["id"],
            "old_status": old_record["status"],
            "new_status": new_record["status"],
        })
```

### Pattern 4: Owner Tracking

Manually set the `created_by` field (or augment Cinder's automatic tracking):

```python
@documents.on("before_create")
async def set_owner(data, ctx):
    if ctx.user:
        data["owner_id"] = ctx.user["id"]
        data["owner_name"] = ctx.user.get("name", "Unknown")
    return data
```

### Pattern 5: Conditional Expansion

Modify list queries based on user context:

```python
@posts.on("before_list")
async def filter_by_user(payload, ctx):
    if ctx.user and ctx.user.get("role") != "admin":
        # Non-admins only see their own posts
        payload["filters"]["author"] = ctx.user["id"]
    return payload
```

## App-Level Hooks

Register hooks at the app level for cross-cutting concerns:

```python
@app.on("app:startup")
async def seed_data(_, ctx):
    await create_default_categories()

@app.on("app:shutdown")
async def cleanup(_, ctx):
    await close_connections()

@app.on("app:error")
async def log_errors(exc, ctx):
    await sentry.capture(exc, request_id=ctx.request_id)
```

## Auth Events

Auth has its own events, prefixed with `auth:`:

| Event | Description |
|-------|-------------|
| `auth:before_register` | Before user registration |
| `auth:after_register` | After user registration |
| `auth:before_login` | Before login (can reject) |
| `auth:after_login` | After successful login |
| `auth:before_logout` | Before token revocation |
| `auth:after_logout` | After token revocation |

## Rules of Thumb

1. **Mutate by returning** — `before_*` hooks modify data by returning it
2. **Return `None` for unchanged** — returning `None` keeps the original data
3. **Hooks run in registration order** — order matters for dependent operations
4. **After hooks can't abort** — their return values are ignored
5. **Use guard clauses** — prevent infinite loops with conditions like `if record.get("processed"): return`

## Next Steps

- [Access Control](/core-concepts/access-control/) — Combine hooks with permissions
- [Schema Auto-Sync](/core-concepts/schema-autosync/) — Database schema management
