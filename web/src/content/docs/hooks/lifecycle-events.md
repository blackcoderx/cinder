---
title: Lifecycle Events
description: Built-in events fired for every CRUD operation
---

Cinder fires events before and after every database operation. Register handlers to run custom logic at each point.

## Collection events

For each collection named `{name}`:

| Event | Fires | Payload type | Can modify |
|-------|-------|-------------|------------|
| `{name}:before_create` | Before INSERT | `dict` (input data) | Yes — return modified dict |
| `{name}:after_create` | After INSERT | `dict` (saved record) | No |
| `{name}:before_update` | Before UPDATE | `dict` (patch data) | Yes — return modified dict |
| `{name}:after_update` | After UPDATE | `tuple[dict, dict]` (updated, previous) | No |
| `{name}:before_delete` | Before DELETE | `dict` (record to delete) | No |
| `{name}:after_delete` | After DELETE | `dict` (deleted record) | No |
| `{name}:before_read` | Before single GET | `str` (record ID) | Yes — return modified ID |
| `{name}:after_read` | After single GET | `dict` (record) | Yes — return modified dict |
| `{name}:before_list` | Before list GET | `dict` (query descriptor) | Yes — return modified descriptor |
| `{name}:after_list` | After list GET | `list[dict]` (records) | Yes — return modified list |

### List query descriptor

The `before_list` hook receives a dict you can modify to alter the query:

```python
@posts.on("before_list")
async def restrict_to_published(query, ctx):
    query["filters"]["status"] = "published"
    return query
```

The descriptor has these keys: `filters` (dict), `order_by` (str), `limit` (int), `offset` (int).

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
