---
title: Pagination
description: Control page size and navigate through results
---

## Pagination Parameters

Control pagination with `limit` and `offset`:

| Parameter | Default | Description |
|-----------|---------|-------------|
| `limit` | `20` | Number of items per page |
| `offset` | `0` | Number of items to skip |

## Examples

### First Page (10 items)

```bash
GET /api/products?limit=10&offset=0
```

### Second Page

```bash
GET /api/products?limit=10&offset=10
```

### Third Page

```bash
GET /api/products?limit=10&offset=20
```

## Response Format

Every list response includes pagination metadata:

```json
{
  "items": [
    { "id": "...", "name": "Phone", ... }
  ],
  "total": 42,
  "limit": 20,
  "offset": 0
}
```

| Field | Description |
|-------|-------------|
| `items` | Array of records for the current page |
| `total` | Total number of matching records |
| `limit` | Items per page |
| `offset` | Current offset position |

## Calculating Pagination

Use `total` to calculate pages:

```javascript
const totalPages = Math.ceil(response.total / response.limit);
const currentPage = Math.floor(response.offset / response.limit) + 1;
```

## Maximum Limit

The maximum allowed `limit` is `100`. Requests with `limit > 100` are capped.

## Next Steps

- [Filtering](/api/filtering/) — Filter results
- [Endpoints](/api/endpoints/) — Full API reference
- [OpenAPI](/api/openapi/) — Auto-generated docs