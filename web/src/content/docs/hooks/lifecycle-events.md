---
title: Lifecycle Events
description: Built-in events fired for every CRUD operation
---

Cinder fires events before and after every database operation. Register handlers to run custom logic at each point.

## Collection events

For each collection named `{name}`:

| Event | Fires | Handler signature |
|-------|-------|-------------------|
| `{name}:before_create` | Before INSERT | `async def handler(data: dict, ctx: CinderContext) -> dict` |
| `{name}:after_create` | After INSERT | `async def handler(record: dict, ctx: CinderContext)` |
| `{name}:before_update` | Before UPDATE | `async def handler(data: dict, ctx: CinderContext) -> dict` |
| `{name}:after_update` | After UPDATE | `async def handler(record: dict, ctx: CinderContext)` |
| `{name}:before_delete` | Before DELETE | `async def handler(record: dict, ctx: CinderContext)` |
| `{name}:after_delete` | After DELETE | `async def handler(record: dict, ctx: CinderContext)` |

`before_*` handlers can modify and return data. `after_*` handlers are fire-and-forget.

## App lifecycle events

| Event | Fires | Payload |
|-------|-------|---------|
| `app:startup` | ASGI lifespan start | `None` |
| `app:shutdown` | ASGI lifespan stop | `None` |

## Auth events

See [Auth Hooks](/authentication/hooks/) for the full list of auth-specific events.

## Registering handlers

**On the collection** (namespacing is automatic):

```python
@posts.on("before_create")
async def set_defaults(data, ctx):
    data["status"] = "draft"
    return data

@posts.on("after_create")
async def notify(record, ctx):
    print(f"Created: {record['id']}")
```

**On the app** (use the full event name):

```python
@app.on("posts:before_create")
async def set_defaults(data, ctx):
    data["status"] = "draft"
    return data
```

Both forms are equivalent.

## The `CinderContext` object

```python
from cinder.hooks.context import CinderContext

async def my_handler(data, ctx: CinderContext):
    ctx.user        # authenticated user dict, or None
    ctx.collection  # collection name (e.g. "posts")
    ctx.operation   # "create", "update", "delete"
    ctx.request_id  # correlation ID
    ctx.request     # Starlette Request object
    ctx.extra       # dict for passing data between hooks
```

## Modifying data in `before_*` hooks

Return the modified dict:

```python
@posts.on("before_create")
async def add_metadata(data, ctx):
    data["created_by"] = ctx.user["id"] if ctx.user else None
    data["ip_address"] = ctx.request.client.host
    return data
```

If you don't return anything, the original `data` is used unchanged.

## Aborting an operation

Raise `CinderError` from any hook to stop the operation and return an error response:

```python
from cinder.errors import CinderError

@posts.on("before_delete")
async def prevent_published_delete(record, ctx):
    if record.get("status") == "published":
        raise CinderError(403, "Cannot delete a published post")
```

## Multiple handlers

Multiple handlers on the same event run in registration order. Each receives the data returned by the previous:

```python
@posts.on("before_create")
async def step_one(data, ctx):
    data["step"] = 1
    return data

@posts.on("before_create")
async def step_two(data, ctx):
    data["step"] += 1  # receives data from step_one
    return data
```
