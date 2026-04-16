# Lifecycle Hooks

Lifecycle hooks let you run custom code before and after operations on your collections. Use hooks for validation, data transformation, notifications, and more.

## How Hooks Work

Hooks are functions that run at specific points during request processing:

- **Before hooks** receive and can modify the input data
- **After hooks** receive the result of the operation
- Hooks can be sync or async

## Collection Hooks

Register hooks on a collection for CRUD operations:

```python
@posts.on("before_create")
async def validate_post(data, ctx):
    # Validate or transform data before creating
    if len(data.get("title", "")) < 5:
        raise ZorkError(400, "Title must be at least 5 characters")
    return data
```

### Available Events

| Event | When It Runs | Handler Receives |
|-------|--------------|------------------|
| `before_create` | Before creating a record | The input data dict |
| `after_create` | After creating a record | The created record |
| `before_read` | Before fetching a record | The record ID |
| `after_read` | After fetching a record | The record |
| `before_update` | Before updating a record | The update data dict |
| `after_update` | After updating a record | Tuple of (new_record, old_record) |
| `before_delete` | Before deleting a record | The record being deleted |
| `after_delete` | After deleting a record | The deleted record |
| `before_list` | Before listing records | Query parameters dict |
| `after_list` | After listing records | List of records |

## Hook Decorator

The `on` method works as a decorator:

```python
@posts.on("before_create")
async def my_hook(data, ctx):
    # Your code here
    return data
```

Or register directly:

```python
async def my_hook(data, ctx):
    return data

posts.on("before_create", my_hook)
```

## Context Object

Every hook receives a context object with useful information:

```python
@posts.on("before_create")
async def my_hook(data, ctx):
    # Access the current user (if authenticated)
    if ctx.user:
        print(f"Creating post for user: {ctx.user['email']}")
    
    # Access the request ID for logging
    print(f"Request ID: {ctx.request_id}")
    
    # Access the collection name
    print(f"Collection: {ctx.collection}")
    
    # Access the operation
    print(f"Operation: {ctx.operation}")
    
    # Add custom data to pass between hooks
    ctx.extra["my_data"] = "value"
    
    return data
```

### Context Properties

| Property | Type | Description |
|----------|------|-------------|
| `user` | dict or None | The authenticated user making the request |
| `request_id` | str | Unique ID for this request |
| `collection` | str | Name of the collection |
| `operation` | str | Type of operation (create, read, etc.) |
| `request` | Request | The Starlette request object |
| `extra` | dict | Custom data storage |

## Before Hooks

Before hooks receive the input data and can modify it:

### Transforming Data

```python
@posts.on("before_create")
async def add_slug(data, ctx):
    data["slug"] = data["title"].lower().replace(" ", "-")
    return data
```

### Adding User References

```python
@posts.on("before_create")
async def set_author(data, ctx):
    if ctx.user:
        data["author_id"] = ctx.user["id"]
    return data
```

### Validation

Raise `ZorkError` to reject the request:

```python
from zork.errors import ZorkError

@posts.on("before_create")
async def validate_content(data, ctx):
    if "body" in data and len(data["body"]) < 10:
        raise ZorkError(400, "Post body must be at least 10 characters")
    return data
```

## After Hooks

After hooks receive the result and can perform side effects:

### Sending Notifications

```python
@posts.on("after_create")
async def notify_new_post(post, ctx):
    await send_email(
        to="admin@example.com",
        subject=f"New post: {post['title']}"
    )
```

### Logging

```python
@posts.on("after_update")
async def log_changes(args, ctx):
    new_record, old_record = args
    print(f"Post {new_record['id']} updated by {ctx.user['email']}")
```

### Updating Related Data

```python
@comments.on("after_create")
async def update_comment_count(comment, ctx):
    post_id = comment["post_id"]
    # Update the post's comment count
    await update_post_comment_count(post_id)
```

## Before List Hooks

The before_list hook receives a query descriptor dict:

```python
@posts.on("before_list")
async def filter_by_user(query, ctx):
    # Modify the query parameters
    if ctx.user and not ctx.user.get("is_admin"):
        # Add a filter for user's own posts
        query["filters"] = query.get("filters", {})
        query["filters"]["author_id"] = ctx.user["id"]
    return query
```

## Preventing Deletes

Return a special error from before_delete to cancel the delete:

```python
from zork.errors import ZorkError

@posts.on("before_delete")
async def prevent_delete(post, ctx):
    if post.get("is_locked"):
        raise ZorkError(403, "Cannot delete locked posts")
    return post
```

## Soft Deletes

Implement soft deletes by raising the cancel sentinel:

```python
from zork.errors import ZorkError, CANCEL_DELETE_MESSAGE

@posts.on("before_delete")
async def soft_delete(post, ctx):
    # Mark as deleted instead of actually deleting
    post["is_deleted"] = True
    # Update the record
    # Raise the cancel sentinel to skip the actual delete
    raise ZorkError.cancel_delete()
```

## Custom Events

You can define and fire custom events:

```python
@posts.on("before_create")
async def check_spam(data, ctx):
    if is_spam(data):
        # Fire a custom event
        await posts.fire("spam_detected", {"data": data, "reason": "spam"})
    return data

# Register a handler for custom events
@posts.on("spam_detected")
async def handle_spam(payload, ctx):
    print(f"Spam detected: {payload}")
```

## App-Level Hooks

Register hooks that run for all collections:

```python
@app.on("app:startup")
async def on_startup(ctx):
    print("Application starting")

@app.on("app:shutdown")
async def on_shutdown(ctx):
    print("Application shutting down")

@app.on("app:error")
async def on_error(error, ctx):
    print(f"Error occurred: {error}")
```

## Auth Hooks

Authentication has its own hooks:

```python
@auth.on("before_register")
async def validate_registration(data, ctx):
    # Add custom validation
    return data

@auth.on("after_register")
async def welcome_user(user, ctx):
    # Send welcome email
    pass

@auth.on("after_login")
async def track_login(user, ctx):
    # Log login activity
    pass
```

### Auth Hook Events

| Event | Description |
|-------|-------------|
| `auth:before_register` | Before user registration |
| `auth:after_register` | After user registration |
| `auth:before_login` | Before user login |
| `auth:after_login` | After user login |
| `auth:before_logout` | Before user logout |
| `auth:after_logout` | After user logout |
| `auth:before_password_reset` | Before password reset |
| `auth:after_password_reset` | After password reset |
| `auth:after_verify_email` | After email verification |

## Hook Order

Hooks run in the order they are registered. Multiple hooks on the same event all run:

```python
@posts.on("before_create")
async def hook1(data, ctx):
    print("Hook 1")
    return data

@posts.on("before_create")
async def hook2(data, ctx):
    print("Hook 2")
    return data
```

Both hooks run in order.

## Next Steps

- [Error Handling](/core-concepts/errors) — Raising and handling errors
- [Authentication](/authentication/setup) — Auth hooks
- [Realtime](/realtime/overview) — Publishing events from hooks
