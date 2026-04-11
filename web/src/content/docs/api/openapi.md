---
title: OpenAPI
description: Auto-generated OpenAPI 3.1 schema and Swagger UI
sidebar:
  order: 4
---

Cinder auto-generates an OpenAPI 3.1 specification for your entire API — including all collections, auth endpoints, and file routes.

## Endpoints

| Path | Description |
|------|-------------|
| `GET /openapi.json` | OpenAPI 3.1 schema (JSON) |
| `GET /docs` | Swagger UI |

## Swagger UI

Navigate to `http://localhost:8000/docs` in your browser to explore and test all endpoints interactively.

The Swagger UI includes:
- All collection CRUD endpoints
- Auth endpoints (if auth is enabled)
- Request/response schemas
- Authentication (click "Authorize" and enter your JWT token)

## Using the schema

### With code generation tools

Feed the schema to a client generator:

```bash
# openapi-generator-cli
openapi-generator-cli generate \
  -i http://localhost:8000/openapi.json \
  -g typescript-fetch \
  -o ./src/api-client
```

### With Postman

1. Open Postman → Import
2. Paste `http://localhost:8000/openapi.json` as the URL
3. Click Import

### With Insomnia

1. Create → Import
2. URL: `http://localhost:8000/openapi.json`

## API title and version

Set the title and version when creating the `Cinder` instance:

```python
app = Cinder(
    database="app.db",
    title="My Blog API",
    version="2.1.0",
)
```

These appear in the OpenAPI schema and Swagger UI.
