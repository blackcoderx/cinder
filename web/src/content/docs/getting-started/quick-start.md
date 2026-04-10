---
title: Quick Start
description: Create your first Cinder app in under 5 minutes
---

Create a file called `main.py`:

```python
from cinder import Cinder, Collection, TextField, IntField, Auth

app = Cinder(database="app.db")

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

## Run the Server

```bash
cinder serve main.py
# Server running at http://localhost:8000
```

## What You Get

Your app now includes:

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/auth/register` | POST | Register a new user |
| `/api/auth/login` | POST | Login and get JWT token |
| `/api/auth/me` | GET | Get current user info |
| `/api/auth/logout` | POST | Revoke current token |
| `/api/posts` | GET | List all posts |
| `/api/posts` | POST | Create a new post |
| `/api/posts/{id}` | GET | Get a single post |
| `/api/posts/{id}` | PATCH | Update a post |
| `/api/posts/{id}` | DELETE | Delete a post |
| `/api/health` | GET | Health check |
| `/openapi.json` | GET | OpenAPI 3.1 schema |
| `/docs` | GET | Swagger UI |

## Try It Out

### Register a User

```bash
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email": "user@example.com", "password": "secure123", "username": "john"}'
```

Response:
```json
{
  "token": "eyJhbGciOi...",
  "user": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "email": "user@example.com",
    "username": "john",
    "role": "user"
  }
}
```

### Create a Post (Authenticated)

```bash
curl -X POST http://localhost:8000/api/posts \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer eyJhbGciOi..." \
  -d '{"title": "Hello World", "body": "My first post!"}'
```

### List Posts (Public)

```bash
curl http://localhost:8000/api/posts
```

Response:
```json
{
  "items": [
    {
      "id": "...",
      "title": "Hello World",
      "body": "My first post!",
      "views": 0,
      "created_at": "2026-04-09T12:00:00",
      "updated_at": "2026-04-09T12:00:00"
    }
  ],
  "total": 1,
  "limit": 20,
  "offset": 0
}
```

## Next Steps

- [The Cinder App](/core-concepts/app/) — Understand the central registry
- [Collections](/core-concepts/collections/) — Learn how to define data schemas
- [Access Control](/core-concepts/access-control/) — Control who can access your data
- [Field Types](/fields/field-types/) — Available field definitions