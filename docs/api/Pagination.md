# Pagination

Zork provides comprehensive pagination metadata for all list endpoints, following REST API best practices and including HAL-style navigation links.

## Overview

All collection list endpoints return paginated responses with rich metadata:

```json
{
  "items": [
    { "id": "1", "title": "Post 1" },
    { "id": "2", "title": "Post 2" }
  ],
  "pagination": {
    "total": 150,
    "limit": 20,
    "offset": 0,
    "has_more": true,
    "next_offset": 20,
    "prev_offset": null,
    "page": 1,
    "total_pages": 8
  },
  "links": {
    "self": "/api/posts?offset=0&limit=20",
    "next": "/api/posts?offset=20&limit=20",
    "prev": null,
    "first": "/api/posts?offset=0&limit=20",
    "last": "/api/posts?offset=140&limit=20"
  }
}
```

## Configuration

Zork allows you to configure pagination at the collection level or override it per-request.

### Collection-Level Configuration

You can control pagination behavior when defining a collection:

```python
from zork import Collection, TextField

# Always include pagination (default)
posts = Collection("posts", fields=[TextField("title")])

# Never include pagination metadata
posts = Collection("posts", fields=[TextField("title")], pagination=False)

# Smart mode - include only when needed
posts = Collection("posts", fields=[TextField("title")], pagination="auto")

# Or use the fluent API
posts = Collection("posts", fields=[TextField("title")]).paginate(False)
```

#### Pagination Options

| Value | Behavior |
|-------|----------|
| `True` | Always include pagination metadata |
| `False` | Never include pagination metadata |
| `"auto"` | Smart mode - include only when there are multiple pages or not on first page |

### Per-Request Override

You can override the pagination behavior for individual requests using the `pagination` query parameter:

```bash
# Disable pagination for this request
curl "http://localhost:8000/api/posts?pagination=false"

# Force pagination even when disabled at collection level
curl "http://localhost:8000/api/posts?pagination=true"
```

## Query Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `limit` | int | 20 | Maximum records to return |
| `offset` | int | 0 | Number of records to skip |
| `pagination` | string | "auto" | Control pagination: "true", "false", "auto" |

## Pagination Fields

### `pagination` Object

| Field | Type | Description |
|-------|------|-------------|
| `total` | integer | Total count of all records (unpaginated) |
| `limit` | integer | Items per page |
| `offset` | integer | Current offset position |
| `has_more` | boolean | `true` if more records exist after this page |
| `next_offset` | integer \| null | Offset to fetch next page (null if on last page) |
| `prev_offset` | integer \| null | Offset to fetch previous page (null if on first page) |
| `page` | integer | Current page number (1-indexed) |
| `total_pages` | integer | Total number of pages |

### `links` Object

The `links` object provides URLs for easy navigation, following the [HAL specification](https://tools.ietf.org/html/draft-kelly-json-hal):

| Relation | Description |
|----------|-------------|
| `self` | URL of the current page |
| `next` | URL of the next page (null if no more pages) |
| `prev` | URL of the previous page (null if on first page) |
| `first` | URL of the first page |
| `last` | URL of the last page |

## Examples

### Basic Pagination

```bash
# Get first page (20 items)
curl "http://localhost:8000/api/posts"

# Get first page explicitly
curl "http://localhost:8000/api/posts?limit=20&offset=0"

# Get second page
curl "http://localhost:8000/api/posts?limit=20&offset=20"

# Get third page
curl "http://localhost:8000/api/posts?limit=20&offset=40"
```

### With Filters

Query parameters are preserved in pagination links:

```bash
# Filter and paginate
curl "http://localhost:8000/api/posts?status=published&limit=10&offset=0"
```

The response links will include the filter:
```json
{
  "links": {
    "self": "/api/posts?status=published&offset=0&limit=10",
    "next": "/api/posts?status=published&offset=10&limit=10",
    "first": "/api/posts?status=published&offset=0&limit=10",
    "last": "/api/posts?status=published&offset=90&limit=10"
  }
}
```

### With Sorting

Sort parameters are also preserved:

```bash
curl "http://localhost:8000/api/posts?order_by=-created_at&limit=10&offset=0"
```

## Client Implementation

### JavaScript/TypeScript

```typescript
interface Pagination {
  total: number;
  limit: number;
  offset: number;
  has_more: boolean;
  next_offset: number | null;
  prev_offset: number | null;
  page: number;
  total_pages: number;
}

interface PaginatedResponse<T> {
  items: T[];
  pagination: Pagination;
  links: {
    self: string;
    next: string | null;
    prev: string | null;
    first: string;
    last: string;
  };
}

// Fetch next page
async function fetchNextPage(response: PaginatedResponse<any>) {
  if (!response.links.next) return null;
  return fetch(response.links.next);
}
```

### Python

```python
import math

def calculate_pagination(total: int, limit: int, offset: int) -> dict:
    page = (offset // limit) + 1
    total_pages = math.ceil(total / limit) if limit > 0 else 1
    has_more = offset + limit < total
    
    return {
        "page": page,
        "total_pages": total_pages,
        "has_more": has_more,
        "next_offset": offset + limit if has_more else None,
        "prev_offset": max(0, offset - limit) if offset > 0 else None
    }
```

## Edge Cases

### Empty Results

```json
{
  "items": [],
  "pagination": {
    "total": 0,
    "limit": 20,
    "offset": 0,
    "has_more": false,
    "next_offset": null,
    "prev_offset": null,
    "page": 1,
    "total_pages": 1
  },
  "links": {
    "self": "/api/posts?offset=0&limit=20",
    "next": null,
    "prev": null,
    "first": "/api/posts?offset=0&limit=20",
    "last": "/api/posts?offset=0&limit=20"
  }
}
```

### Last Page

When on the last page, `has_more` is `false` and `next_offset` is `null`:

```json
{
  "pagination": {
    "total": 45,
    "limit": 20,
    "offset": 40,
    "has_more": false,
    "next_offset": null,
    "prev_offset": 20,
    "page": 3,
    "total_pages": 3
  }
}
```

### Exact Page Match

When items fill exact number of pages:

```json
{
  "pagination": {
    "total": 60,
    "limit": 20,
    "offset": 40,
    "has_more": false,
    "next_offset": null,
    "prev_offset": 20,
    "page": 3,
    "total_pages": 3
  }
}
```

## OpenAPI Specification

The pagination metadata is fully documented in the OpenAPI schema. You can view it at:

- Swagger UI: `/docs`
- OpenAPI JSON: `/openapi.json`

## Related Topics

- [Filtering](/api/filtering) — Advanced filtering options
- [Sorting](/api/sorting) — Sorting options
- [Response Models](/core-concepts/response-models) — Customize response formatting
