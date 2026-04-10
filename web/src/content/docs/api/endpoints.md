---
title: Endpoints
description: Auto-generated REST API endpoints for collections
---

For every registered collection, Cinder generates these endpoints automatically.

## CRUD Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/{collection}` | GET | List all records |
| `/api/{collection}` | POST | Create a new record |
| `/api/{collection}/{id}` | GET | Get a single record |
| `/api/{collection}/{id}` | PATCH | Update a record |
| `/api/{collection}/{id}` | DELETE | Delete a record |

## List Records

**`GET /api/{collection}`**

```bash
curl http://localhost:8000/api/products
```

Response (`200`):
```json
{
  "items": [
    {
      "id": "...",
      "name": "Phone",
      "price": 999.99,
      "stock": 50,
      "is_published": true,
      "created_at": "2026-04-09T12:00:00",
      "updated_at": "2026-04-09T12:00:00"
    }
  ],
  "total": 1,
  "limit": 20,
  "offset": 0
}
```

## Get Record

**`GET /api/{collection}/{id}`**

```bash
curl http://localhost:8000/api/products/550e8400-e29b-41d4-a716-446655440000
```

Response (`200`):
```json
{
  "id": "550e8400-...",
  "name": "Phone",
  "price": 999.99,
  "stock": 50,
  "is_published": true,
  "created_at": "...",
  "updated_at": "..."
}
```

Returns `404` if the record does not exist.

## Create Record

**`POST /api/{collection}`**

```bash
curl -X POST http://localhost:8000/api/products \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer eyJhbGciOi..." \
  -d '{"name": "Phone", "price": 999.99, "stock": 50, "is_published": true}'
```

Response (`201`):
```json
{
  "id": "newly-generated-uuid",
  "name": "Phone",
  "price": 999.99,
  "stock": 50,
  "is_published": true,
  "created_at": "...",
  "updated_at": "..."
}
```

Returns `400` if validation fails (missing required fields, type mismatch, constraint violations).

## Update Record

**`PATCH /api/{collection}/{id}`**

Uses PATCH semantics — only send the fields you want to update:

```bash
curl -X PATCH http://localhost:8000/api/products/550e8400-... \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer eyJhbGciOi..." \
  -d '{"stock": 49}'
```

Response (`200`):
```json
{
  "id": "550e8400-...",
  "name": "Phone",
  "price": 999.99,
  "stock": 49,
  "is_published": true,
  "created_at": "...",
  "updated_at": "2026-04-09T13:00:00"
}
```

## Delete Record

**`DELETE /api/{collection}/{id}`**

```bash
curl -X DELETE http://localhost:8000/api/products/550e8400-... \
  -H "Authorization: Bearer eyJhbGciOi..."
```

Response (`200`):
```json
{ "message": "Record deleted" }
```

## System Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/health` | GET | Health check |

### Health Check

**`GET /api/health`**

```bash
curl http://localhost:8000/api/health
```

Response (`200`):
```json
{ "status": "ok" }
```

## Error Responses

| Status | Description |
|--------|-------------|
| `400` | Bad request (validation failed) |
| `401` | Unauthorized (invalid/missing token) |
| `403` | Forbidden (insufficient permissions) |
| `404` | Not found |
| `429` | Too many requests (rate limited) |
| `500` | Internal server error |

Error format:
```json
{ "status": 400, "error": "Email and password are required" }
```

## Next Steps

- [Filtering & Sorting](/api/filtering/) — Filter and sort results
- [Pagination](/api/pagination/) — Control page size
- [OpenAPI](/api/openapi/) — Auto-generated API docs