# The App

The `Zork` class is the central component of your application. It registers collections, configures authentication, manages databases, and ties all subsystems together.

## Creating an App

Import and instantiate the Zork class:

```python
from zork import Zork

app = Zork()
```

The constructor accepts the following options:

```python
app = Zork(
    database="app.db",      # Database URL or file path
    title="My API",         # API title for OpenAPI docs
    version="1.0.0"         # API version
)
```

## Database Configuration

By default, Zork uses SQLite with a file named `app.db`. You can customize this:

```python
# SQLite (default)
app = Zork(database="app.db")

# SQLite with explicit path
app = Zork(database="sqlite:///data/mydb.sqlite")

# PostgreSQL
app = Zork(database="postgresql://user:pass@localhost:5432/mydb")

# MySQL
app = Zork(database="mysql://user:pass@localhost:3306/mydb")
```

For more database options, see the [Database Overview](/database/overview) guide.

## Registering Collections

Collections define your data schemas. Register them with your app:

```python
from zork import Collection, TextField, IntField

posts = Collection("posts", fields=[
    TextField("title", required=True),
    TextField("body"),
    IntField("views", default=0),
])

app.register(posts)
```

With access control rules:

```python
app.register(posts, auth=["read:public", "write:authenticated"])
```

See the [Collections](/core-concepts/collections) guide for details.

## Authentication

Add authentication to your app:

```python
from zork import Auth

auth = Auth(allow_registration=True)
app.use_auth(auth)
```

This enables all authentication endpoints at `/api/auth/*`.

See the [Authentication Setup](/authentication/setup) guide for details.

## Configuring Subsystems

Zork provides fluent configuration methods for each subsystem.

### Database Configuration

For advanced database setup:

```python
from zork.db.backends.postgresql import PostgreSQLBackend

app.configure_database(
    PostgreSQLBackend(
        url="postgresql://user:pass@host/db",
        min_size=2,
        max_size=20,
    )
)
```

### File Storage Configuration

Configure where uploaded files are stored:

```python
from zork.storage import LocalFileBackend

# Local storage
app.configure_storage(LocalFileBackend("./uploads"))

# S3 storage
from zork.storage import S3CompatibleBackend

app.configure_storage(S3CompatibleBackend.aws(
    bucket="my-bucket",
    access_key="YOUR_KEY",
    secret_key="YOUR_SECRET",
))
```

See the [File Storage Setup](/file-storage/setup) guide for details.

### Redis Configuration

Enable Redis for caching, rate limiting, and realtime scaling:

```python
app.configure_redis(url="redis://localhost:6379/0")
```

This enables Redis for all subsystems that support it.

### Email Configuration

Configure email sending:

```python
from zork.email import SMTPBackend

app.email.use(SMTPBackend.gmail(
    username="you@gmail.com",
    app_password="xxxx xxxx xxxx xxxx",
))
app.email.configure(
    from_address="noreply@example.com",
    app_name="My App",
    base_url="https://myapp.com",
)
```

See the [Email Setup](/email/setup) guide for details.

### CORS Configuration

Configure Cross-Origin Resource Sharing for browser clients:

```python
# Constructor (recommended)
app = Zork(
    database="app.db",
    cors_allow_origins=["https://myapp.com"],
    cors_allow_credentials=True,
    cors_allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE"],
    cors_allow_headers=["Content-Type", "Authorization"],
)

# Or fluent API
app = Zork(database="app.db")
app.cors.allow_origins(["https://myapp.com"])
app.cors.allow_credentials(True)
app.cors.allow_methods(["GET", "POST"])
app.cors.allow_headers(["Content-Type"])
```

**Security:** By default, CORS is disabled. Never use `allow_origins=["*"]` with `allow_credentials=True`.

See the [Middleware Stack](/core-concepts/middleware-stack) guide for CORS details.

### Caching Configuration

Configure response caching:

```python
app.cache.use(MemoryCacheBackend())  # Default for development
# or
app.cache.configure(default_ttl=300)  # Cache for 5 minutes

# Exclude specific paths from caching
app.cache.exclude("/api/health")
```

See the [Caching Setup](/caching/setup) guide for details.

### Rate Limiting Configuration

Configure request rate limits:

```python
from zork.ratelimit import MemoryRateLimitBackend

app.rate_limit.use(MemoryRateLimitBackend())

# Add custom rules for specific paths
app.rate_limit.rule("/api/search", limit=10, window=60)
```

See the [Rate Limiting Setup](/rate-limiting/setup) guide for details.

## Lifecycle Hooks

Register global hooks that run on all collections:

```python
@app.on("app:startup")
async def on_startup(ctx):
    print("Application started")

@app.on("app:shutdown")
async def on_shutdown(ctx):
    print("Application shutting down")

@app.on("app:error")
async def on_error(error, ctx):
    print(f"Error occurred: {error}")
```

See the [Lifecycle Hooks](/core-concepts/lifecycle-hooks) guide for details.

## Building and Running

### Development Server

For development, use the built-in serve method:

```python
if __name__ == "__main__":
    app.serve()
```

Or use the CLI:

```bash
zork serve main.py
```

### Production Build

For production, build the ASGI app and run with uvicorn or gunicorn:

```python
# main.py
app = Zork()
# ... configuration ...

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app.build(), host="0.0.0.0", port=8000)
```

Or run with gunicorn:

```bash
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker
```

## App Configuration Methods

Here is a summary of all Zork configuration methods:

| Method | Purpose |
|--------|---------|
| `app.register(collection)` | Register a collection |
| `app.use_auth(auth)` | Enable authentication |
| `app.configure_database(backend)` | Set database backend |
| `app.configure_storage(backend)` | Set file storage backend |
| `app.configure_redis(url)` | Configure Redis |
| `app.on(event, handler)` | Register lifecycle hook |
| `app.cors` | Configure CORS |
| `app.cache` | Configure caching |
| `app.rate_limit` | Configure rate limiting |
| `app.email` | Configure email |
| `app.realtime` | Configure realtime features |
| `app.build()` | Build ASGI application |
| `app.serve()` | Start development server |

## Next Steps

- [Collections](/core-concepts/collections) — Learn how to define data schemas
- [Field Types](/core-concepts/fields) — Explore all available field types
- [Authentication](/authentication/setup) — Configure user authentication
- [Lifecycle Hooks](/core-concepts/lifecycle-hooks) — Run code at key moments
