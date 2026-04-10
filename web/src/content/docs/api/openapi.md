---
title: OpenAPI / Swagger
description: Auto-generated OpenAPI documentation and interactive API explorer
---

Cinder auto-generates a full OpenAPI 3.1 schema and provides an interactive Swagger UI.

## Endpoints

| Endpoint | Description |
|----------|-------------|
| `GET /openapi.json` | OpenAPI 3.1 schema |
| `GET /docs` | Interactive Swagger UI |

## Accessing the Docs

Visit `http://localhost:8000/docs` in your browser for the interactive Swagger UI.

:::note
Swagger UI requires internet to load assets from CDN.
:::

## Schema

Get the raw OpenAPI schema:

```bash
curl http://localhost:8000/openapi.json | jq .
```

## What's Documented

The schema automatically includes:

- **Auth endpoints** — register, login, logout, refresh, password reset, email verification
- **Collection CRUD** — list, get, create, update, delete
- **Query parameters** — `limit`, `offset`, `order_by`, `expand`
- **Auth requirements** — Bearer token security on protected endpoints
- **Field constraints** — min/max values, required fields, field types

## Customization

Customize the API title and version when initializing Cinder:

```python
app = Cinder(
    title="My API",
    version="1.0.0",
    database="app.db"
)
```

## Example Schema Output

```json
{
  "openapi": "3.1.0",
  "info": {
    "title": "My API",
    "version": "1.0.0"
  },
  "paths": {
    "/api/posts": {
      "get": {
        "tags": ["posts"],
        "summary": "List posts",
        "parameters": [
          {"name": "limit", "in": "query", "schema": {"type": "integer"}},
          {"name": "offset", "in": "query", "schema": {"type": "integer"}},
          {"name": "order_by", "in": "query", "schema": {"type": "string"}}
        ],
        "responses": {
          "200": {
            "description": "Successful response",
            "content": {
              "application/json": {
                "schema": { "$ref": "#/components/schemas/Post" }
              }
            }
          }
        }
      }
    }
  }
}
```

## Next Steps

- [Endpoints](/api/endpoints/) — REST API reference
- [Filtering](/api/filtering/) — Query parameters
- [Configuration](/configuration/env-variables/) — App settings