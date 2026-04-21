# Static Files Setup

Zork includes static file serving for serving CSS, JavaScript, images, and other static assets directly from your application.

## Overview

Static file serving provides:

- **High performance** — Files are served directly by the ASGI server
- **Path traversal protection** — Security against directory traversal attacks
- **Automatic MIME types** — Correct content-type headers for all file types
- **SPA fallback** — Serve `index.html` for unmatched routes (single-page apps)
- **Cache headers** — ETag and Last-Modified headers for efficient caching

## Basic Usage

### Simple Static Mount

Serve static files from a directory:

```python
from zork import Zork

app = Zork(database="app.db")
app.static("/static", "./static")
```

Create a `./static` directory with your files:

```bash
mkdir -p static
echo "body { margin: 0; }" > static/style.css
echo "console.log('hello');" > static/app.js
```

### Directory Structure

Organize static files by type:

```text
static/
├── css/
│   └── style.css
├── js/
│   └── app.js
├── images/
│   └── logo.svg
└── fonts/
    └── open-sans.woff2
```

## Multiple Mounts

Serve files from multiple directories:

```python
app = Zork(database="app.db")

app.static("/static", "./static")
app.static("/assets", "./assets")
app.static("/images", "./images")
```

## SPA Mode

For single-page applications (React, Vue, Svelte), enable HTML mode to serve `index.html` for unmatched routes:

```python
app = Zork(database="app.db")
app.static("/", "./dist", html=True)
```

This configuration:

1. Serves `/index.html` when the file doesn't exist
2. Serves static assets (`/static/app.js`, `/static/style.css`)
3. Falls back to `/index.html` for client-side routing

## Configuration Options

### Path and Directory

```python
app.static("/static", "./static")
```

| Parameter | Description | Example |
|----------|-------------|---------|
| `path` | URL path prefix | `"/static"` |
| `directory` | Filesystem path | `"./static"` |

### Custom Mount Name

```python
app.static("/static", "./static", name="assets")
```

The mount name is used internally for route identification. If not specified, it's derived from the path.

### Cache TTL

```python
app.static("/static", "./static", cache_ttl=3600)
```

Sets the `Cache-Control` header. Without this, browsers handle caching based on ETag/Last-Modified headers.

### SPA Fallback

```python
app.static("/", "./dist", html=True)
```

When `html=True`, unmatched routes return `index.html` instead of 404. Essential for client-side routing.

## Complete Example

```python
from zork import Zork
from zork import Collection, TextField, IntField

app = Zork(database="app.db")

posts = Collection("posts", fields=[
    TextField("title"),
    IntField("views", default=0),
])
app.register(posts, auth=["read:public", "write:authenticated"])

app.static("/static", "./static")
app.static("/assets", "./assets")
app.static("/", "./dist", html=True)

if __name__ == "__main__":
    app.serve()
```

## Security

### Path Traversal Protection

Starlette's StaticFiles blocks path traversal attacks:

```python
# Blocked - returns 404
/static/../../../etc/passwd
/static/..%2F..%2F..%2Fetc/passwd
```

### File Permissions

Ensure your static directory contains only intended files:

```bash
# Create a separate static directory
mkdir -p static
chmod 755 static
```

## Production Considerations

### Development vs Production

In development, Zork serves static files directly. In production:

**Recommended:** Use a reverse proxy or CDN

### Nginx Configuration

Serve static files with Nginx for better performance:

```nginx
server {
    listen 80;
    server_name api.example.com;

    location /static/ {
        alias /var/www/app/static/;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    location / {
        proxy_pass http://127.0.0.1:8000;
    }
}
```

### CDN Setup

For cloud storage (S3, R2, GCS):

```python
# Option 1: Use storage backend for uploaded files
app.configure_storage(S3CompatibleBackend.aws(
    bucket="my-cdn",
    access_key="...",
    secret_key="...",
))

# Option 2: Configure CDN in your reverse proxy
# Point static location to CDN endpoint
```

## Cache Headers

### Default Behavior

Starlette's StaticFiles includes:

- **ETag** — Unique identifier for content
- **Last-Modified** — File modification time
- **Content-Length** — File size

### Browser Caching

With default headers, browsers cache based on:

1. Check ETag against server
2. If unchanged, return 304 Not Modified
3. Otherwise, serve full file

### Long Cache TTL

For production assets:

```python
app.static("/static", "./static", cache_ttl=31536000)  # 1 year
```

Assets are fingerprinted (hash in filename) for cache busting:

```text
/static/app.abc123.js  → Cache for 1 year
/static/app.js         → Versioned separately
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `ZORK_STATIC_DIR` | Default static directory | `./static` |

## Next Steps

- [API Endpoints](/api/endpoints) — Learn about generated endpoints
- [Deployment Overview](/deployment/overview) — Deploy to production
- [SPA Deployment](/deployment/docker) — Deploy with Docker