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

Handles Cross-Origin Resource Sharing for browser-based clients.

**By default, CORS is disabled (secure).** You must explicitly configure origins to enable CORS:

```python
from zork import Zork

# Option 1: Constructor args
app = Zork(
    database="app.db",
    cors_allow_origins=["https://myapp.com"],
    cors_allow_credentials=True,
    cors_allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE"],
)

# Option 2: Fluent API
app = Zork(database="app.db")
app.cors.allow_origins(["https://myapp.com"])
app.cors.allow_credentials(True)
app.cors.allow_methods(["GET", "POST"])
app.cors.allow_headers(["Content-Type"])
```

### Security Warning

**Never use `allow_origins=["*"]` with `allow_credentials=True`** — this is insecure. Zork logs a warning at startup if you do:

```
⚠️  WARNING: CORS is configured with allow_origins=['*'] and allow_credentials=True.
This is insecure. Use specific origins in production.
```

### CORS Options

| Option | Default | Description |
|--------|---------|-------------|
| `cors_allow_origins` | `[]` (disabled) | List of allowed origins |
| `cors_allow_credentials` | `False` | Allow cookies/auth headers |
| `cors_allow_methods` | `["GET", "POST", "PUT", "PATCH", "DELETE"]` | Allowed HTTP methods |
| `cors_allow_headers` | `[]` (all) | Allowed request headers |

### Environment Variables

You can also configure CORS via environment variables by using the fluent API with defaults:

```python
# In your app initialization
import os

app = Zork(database="app.db")
if origins := os.getenv("CORS_ALLOW_ORIGINS"):
    app.cors.allow_origins(origins.split(","))
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

For browser clients making cross-origin requests, enable CORS first:

```python
app = Zork(database="app.db")
app.cors.allow_origins(["https://myapp.com"])
# Then register collections and build
```

### Simple Requests

Once enabled, simple GET and POST requests include CORS headers automatically.

### Preflight Requests

OPTIONS requests are handled automatically for preflight checking.

### Secure by Default

Zork disables CORS by default to prevent accidental exposure. Always use specific origins in production:

```python
# Development (okay for localhost)
app.cors.allow_origins(["http://localhost:3000"])

# Production (use specific domain)
app.cors.allow_origins(["https://myapp.com"])
```

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
