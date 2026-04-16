# Error Handling

Zork provides a consistent way to handle errors throughout your application. Errors raised anywhere in your code are caught and converted to appropriate HTTP responses.

## ZorkError

The main exception class for application errors:

```python
from zork.errors import ZorkError

raise ZorkError(400, "Invalid input data")
raise ZorkError(401, "Authentication required")
raise ZorkError(403, "Permission denied")
raise ZorkError(404, "Record not found")
```

### ZorkError Properties

| Property | Type | Description |
|----------|------|-------------|
| `status_code` | int | HTTP status code |
| `message` | str | Error description |

### Error Response Format

All ZorkError exceptions return JSON responses:

```json
{
  "status": 400,
  "error": "Invalid input data"
}
```

## HTTP Status Codes

Use appropriate status codes for different error types:

| Code | Meaning | When to Use |
|------|---------|-------------|
| 400 | Bad Request | Invalid input, validation failure |
| 401 | Unauthorized | Missing or invalid authentication |
| 403 | Forbidden | Authenticated but not permitted |
| 404 | Not Found | Resource does not exist |
| 409 | Conflict | Duplicate or conflicting data |
| 429 | Too Many Requests | Rate limit exceeded |
| 500 | Internal Server Error | Unexpected errors |

## Raising Errors

### In Hooks

```python
from zork.errors import ZorkError

@posts.on("before_create")
async def validate_post(data, ctx):
    if not data.get("title"):
        raise ZorkError(400, "Title is required")
    if len(data["title"]) > 200:
        raise ZorkError(400, "Title must be 200 characters or less")
    return data
```

### Checking User Permissions

```python
@posts.on("before_update")
async def check_owner(data, ctx):
    if ctx.user.get("role") != "admin":
        raise ZorkError(403, "Only admins can update posts")
    return data
```

### Record Not Found

```python
@posts.on("before_delete")
async def check_exists(data, ctx):
    # The before_delete hook receives the existing record
    if data.get("is_locked"):
        raise ZorkError(409, "Cannot delete locked records")
    return data
```

## Error Handling in Lifecycle Hooks

### Canceling Deletes

Use the special `cancel_delete` method for soft deletes:

```python
from zork.errors import ZorkError, CANCEL_DELETE_MESSAGE

@posts.on("before_delete")
async def soft_delete(post, ctx):
    # Mark as deleted instead of removing
    post["is_deleted"] = True
    # Raise the special cancel sentinel
    raise ZorkError.cancel_delete()
```

When you raise `cancel_delete`, Zork skips the actual database deletion but still runs the after_delete hook.

### After Hook Errors

After hooks can also raise errors, but note that the operation has already completed:

```python
@posts.on("after_create")
async def send_notification(post, ctx):
    # If this fails, the post was still created
    # Consider making this non-critical
    try:
        await send_email(post)
    except Exception:
        pass  # Log but don't fail the request
```

## Custom Error Pages

Zork always returns JSON errors. The format is consistent:

```json
{
  "status": 404,
  "error": "Record not found"
}
```

## Validation Errors

Zork validates request data using Pydantic. Validation errors are converted to ZorkError with status 400:

```json
{
  "status": 400,
  "error": "1 validation error"
}
```

### Field-Level Validation

Use before hooks for custom field validation:

```python
@posts.on("before_create")
async def validate_fields(data, ctx):
    errors = []
    
    if "email" in data and "@" not in data["email"]:
        errors.append("Invalid email format")
    
    if "age" in data and data["age"] < 0:
        errors.append("Age cannot be negative")
    
    if errors:
        raise ZorkError(400, "; ".join(errors))
    
    return data
```

## Async Error Handling

All hooks can be async or sync:

```python
# Sync hook
@posts.on("before_create")
def validate_sync(data, ctx):
    if not data.get("title"):
        raise ZorkError(400, "Title required")
    return data

# Async hook
@posts.on("before_create")
async def validate_async(data, ctx):
    # Can use await here
    result = await check_external_service()
    if not result:
        raise ZorkError(400, "External validation failed")
    return data
```

## Error Logging

Unhandled errors are logged by the ErrorHandlerMiddleware:

```
ERROR: Unhandled error: Record not found
Traceback (most recent call last):
...
```

Use the app:error hook to capture all errors:

```python
@app.on("app:error")
async def log_all_errors(error, ctx):
    import logging
    logging.error(f"Error: {error}", exc_info=True)
```

## Database Errors

Database constraint violations are caught and converted to ZorkError:

```python
# Unique constraint violation
raise ZorkError(400, "UNIQUE constraint failed: email already exists")

# Not null violation
raise ZorkError(400, "NOT NULL constraint failed: title is required")
```

## Rate Limit Errors

Rate limit exceeded returns 429:

```json
{
  "status": 429,
  "error": "Rate limit exceeded"
}
```

The response also includes headers:

```
Retry-After: 60
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 0
X-RateLimit-Reset: 1640995200
```

See the [Rate Limiting](/rate-limiting/setup) guide for configuration.

## Next Steps

- [Lifecycle Hooks](/core-concepts/lifecycle-hooks) — Using hooks for validation
- [Rate Limiting](/rate-limiting/setup) — Configuring rate limits
- [Authentication](/authentication/setup) — Authentication errors
