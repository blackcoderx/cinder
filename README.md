# Zeno

<p align="center">

[![PyPI version](https://img.shields.io/pypi/v/zeno-api?color=f47b20&label=zeno&style=flat-square)](https://pypi.org/project/zeno-api/)
[![Python](https://img.shields.io/pypi/pyversions/zeno-api?color=3572A5&style=flat-square)](https://pypi.org/project/zeno/)
[![License: MIT](https://img.shields.io/badge/license-MIT-green?style=flat-square)](LICENSE)
[![Docs](https://img.shields.io/badge/docs-zeno.vercel.app-f47b20?style=flat-square)](https://zeno.vercel.app)

</p>

A lightweight, open-source backend framework for Python. Define your data schema — Zeno auto-generates a full REST API with auth, CRUD, filtering, and more.

## Install

```bash
pip install zeno-api
```

Or with [uv](https://docs.astral.sh/uv/):

```bash
uv add zeno-api
```

**Optional extras:**

| Extra | What it adds |
|-------|-------------|
| `zeno-api[postgres]` | PostgreSQL support (asyncpg) |
| `zeno-api[mysql]` | MySQL support (aiomysql) |
| `zeno-api[s3]` | S3-compatible file storage (boto3) |
| `zeno-api[email]` | Email delivery (aiosmtplib) |
| `zeno-api[redis]` | Redis caching & sessions |
| `zeno-api[all]` | Everything above |

## Quick Start

```python
from zeno import Zeno, Collection, TextField, IntField, Auth

app = Zeno(database="app.db")

posts = Collection("posts", fields=[
    TextField("title", required=True),
    TextField("body"),
    IntField("views", default=0),
])

auth = Auth(token_expiry=86400, allow_registration=True)

app.register(posts, auth=["read:public", "write:authenticated"])
app.use_auth(auth)
app.serve()
```

```bash
zeno serve main.py
# Server running at http://localhost:8000
```

You now have:

- `POST /api/auth/register` — register users
- `POST /api/auth/login` — get a JWT token
- `GET /api/posts` — list posts (public)
- `POST /api/posts` — create a post (requires auth)
- `GET /api/posts/{id}` — get a single post
- `PATCH /api/posts/{id}` — update a post
- `DELETE /api/posts/{id}` — delete a post
- `GET /openapi.json` — OpenAPI 3.1 schema
- `GET /docs` — Swagger UI

## Features

- Auto-generated CRUD REST API from Python schemas
- JWT authentication with role-based access control
- Multi-database support — SQLite, PostgreSQL, MySQL
- Realtime via WebSocket and Server-Sent Events
- File storage — local filesystem or S3-compatible (AWS, R2, MinIO, and more)
- Lifecycle hooks — `before_create`, `after_update`, `before_delete`, etc.
- Built-in caching with in-memory or Redis backends
- Redis support — caching, sessions, and realtime pub/sub scaling
- Rate limiting per route
- Email delivery with SMTP and provider presets
- Schema migrations via CLI
- One-command deployment — generate Docker, Railway, Render, and Fly.io configs with `zeno deploy`
- Auto-generated OpenAPI 3.1 + Swagger UI
- Zero boilerplate — one file to a working API

## Documentation

Full documentation at **[zenoapi.vercel.app](https://zenoapi.vercel.app)**

## License

[MIT](LICENSE)
