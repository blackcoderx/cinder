# Middleware Stack

This guide explains how requests flow through Zork and the middleware that processes them.

## Request Flow

When a request arrives at your Zork application, it passes through several layers:

```
Client Request
     │
     ▼
┌─────────────────────────┐
│  ErrorHandlerMiddleware  │  Catches all exceptions, returns JSON errors
└─────────────────────────┘
     │
     ▼
┌─────────────────────────┐
│   RequestIDMiddleware    │  Adds X-Request-ID header to responses
└─────────────────────────┘
     │
     ▼
┌─────────────────────────┐
│     CORSMiddleware      │  Handles Cross-Origin Resource Sharing
└─────────────────────────┘
     │
     ▼
┌─────────────────────────┐
│  RateLimitMiddleware    │  Enforces request rate limits
└─────────────────────────┘
     │
     ▼
┌─────────────────────────┐
│   CacheMiddleware       │  Serves cached responses
└─────────────────────────┘
     │
     ▼
┌─────────────────────────┐
│    AuthMiddleware       │  Validates JWT tokens, sets request.user
└─────────────────────────┘
     │
     ▼
┌─────────────────────────┐
│   Your Route Handler    │  Collection CRUD, Auth, Realtime, etc.
└─────────────────────────┘
     │
     ▼
Response to Client
```

## Middleware Details

### ErrorHandlerMiddleware

Catches all unhandled exceptions and returns standardized JSON error responses:

```json
{
  "status": 500,
  "error": "Internal server error"
}
```

ZorkError exceptions return their own status and message:

```json
{
  "status": 400,
  "error": "Validation failed"
}
```

### RequestIDMiddleware

Generates a unique UUID for each request and includes it in the response header:

```
X-Request-ID: abc-123-def-456
```

This ID is also available in hook context for logging and debugging.

### CORSMiddleware

Handles Cross-Origin Resource Sharing for browser-based clients. Zork configures CORS to allow all origins by default:

```python
allow_origins=["*"]
allow_credentials=True
allow_methods=["*"]
allow_headers=["*"]
```

For production, you may want to restrict origins:

```python
# Set specific origins in your app configuration
```

### RateLimitMiddleware

Enforces request rate limits to protect your API. See the [Rate Limiting](/rate-limiting/setup) guide for configuration.

### CacheMiddleware

Implements cache-aside caching for GET requests. See the [Caching](/caching/setup) guide for configuration.

### AuthMiddleware

Validates JWT tokens from the Authorization header and attaches the user to the request:

```
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

The user object is available in hooks via `ctx.user`.

## Accessing Request Data

### In Hooks

The context object provides access to the current request:

```python
@posts.on("before_create")
async def log_request(data, ctx):
    request = ctx.request
    
    # Access request attributes
    method = request.method
    headers = dict(request.headers)
    client_ip = request.client.host
    
    return data
```

### Available Context Properties

| Property | Description |
|----------|-------------|
| `ctx.request` | The Starlette Request object |
| `ctx.user` | The authenticated user dict or None |
| `ctx.request_id` | The unique request ID |
| `ctx.collection` | The collection name |
| `ctx.operation` | The operation type |

## Response Headers

Zork adds several headers to responses:

| Header | Description |
|--------|-------------|
| `X-Request-ID` | Unique request identifier |
| `X-Cache` | HIT or MISS (when caching is enabled) |

## Custom Error Responses

Raise ZorkError from hooks to return custom errors:

```python
from zork.errors import ZorkError

@posts.on("before_create")
async def check_permission(data, ctx):
    if not ctx.user or ctx.user.get("role") != "author":
        raise ZorkError(403, "Only authors can create posts")
    return data
```

## Request Validation

Zork validates request data using Pydantic models generated from your field definitions:

```python
# Zork generates a Pydantic model from your fields
posts = Collection("posts", fields=[
    TextField("title", required=True, max_length=100),
    IntField("views", default=0),
])
```

Invalid data returns a 400 error with validation details:

```json
{
  "status": 400,
  "error": "Field 'title' must be at least 1 character"
}
```

## Handling CORS

For browser clients making cross-origin requests, the CORSMiddleware handles preflight requests automatically.

### Simple Requests

Simple GET and POST requests work with default CORS settings.

### Preflight Requests

OPTIONS requests are handled automatically for preflight checking.

### Configuring CORS

The default CORS configuration allows all origins. To customize, you would modify the middleware configuration in your app's pipeline.

## WebSocket Connections

WebSocket upgrades bypass some HTTP middleware but still go through:

- ErrorHandlerMiddleware
- AuthMiddleware (for token validation)
- Your WebSocket handler

See the [Realtime](/realtime/overview) guide for WebSocket details.

## Next Steps

- [Error Handling](/core-concepts/errors) — Custom error responses
- [Authentication](/authentication/setup) — JWT authentication
- [Caching](/caching/setup) — Response caching
- [Rate Limiting](/rate-limiting/setup) — API protection
