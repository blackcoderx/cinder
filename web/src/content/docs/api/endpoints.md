---
title: API Endpoints
description: Complete reference for all auto-generated REST endpoints
sidebar:
  order: 1
---

Zeno generates a standard set of REST endpoints for each registered collection and optional auth system.

## Collection endpoints

For a collection named `{name}`:

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| `GET` | `/api/{name}` | Depends on `read` rule | List records |
| `POST` | `/api/{name}` | Depends on `write` rule | Create a record |
| `GET` | `/api/{name}/{id}` | Depends on `read` rule | Get a single record |
| `PATCH` | `/api/{name}/{id}` | Depends on `write` rule | Partial update |
| `DELETE` | `/api/{name}/{id}` | Depends on `write` rule | Delete a record |

## File endpoints

Generated for each `FileField` on a collection:

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/api/{name}/{id}/files/{field}` | Upload a file |
| `GET` | `/api/{name}/{id}/files/{field}` | Download a file |
| `DELETE` | `/api/{name}/{id}/files/{field}` | Delete a file |

## Auth endpoints

Available when `app.use_auth(auth)` is called:

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/api/auth/register` | Register a new user |
| `POST` | `/api/auth/login` | Log in and get a token |
| `GET` | `/api/auth/me` | Get the current user |
| `POST` | `/api/auth/logout` | Revoke the current token |
| `POST` | `/api/auth/refresh` | Issue a new token |
| `POST` | `/api/auth/forgot-password` | Request a password reset |
| `POST` | `/api/auth/reset-password` | Apply a password reset |
| `GET` | `/api/auth/verify-email` | Verify email address |

## Realtime endpoints

| Protocol | Path | Description |
|----------|------|-------------|
| WS | `/api/realtime` | WebSocket connection |
| `GET` | `/api/realtime/sse` | Server-Sent Events stream |

## System endpoints

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/api/health` | Health check — returns `{"status": "ok"}` |
| `GET` | `/openapi.json` | OpenAPI 3.1 schema |
| `GET` | `/docs` | Swagger UI |
| `GET` | `/` | Default landing page |

## Response format

**Single record:**
```json
{
  "id": "abc123",
  "title": "My Post",
  "created_at": "2024-01-01T00:00:00+00:00",
  "updated_at": "2024-01-01T00:00:00+00:00"
}
```

**List:**
```json
{
  "items": [ ... ],
  "total": 42,
  "page": 1,
  "per_page": 50
}
```

**Error:**
```json
{ "detail": "Not found" }
```

## HTTP status codes

| Code | Meaning |
|------|---------|
| `200` | Success |
| `201` | Created (POST) |
| `400` | Bad request (validation error) |
| `401` | Authentication required or token invalid |
| `403` | Forbidden (access control) |
| `404` | Record not found |
| `413` | File too large |
| `422` | Unprocessable entity (schema validation) |
| `429` | Rate limit exceeded |
| `500` | Server error |
