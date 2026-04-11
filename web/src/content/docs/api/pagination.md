---
title: Pagination
description: Page through collection results
sidebar:
  order: 3
---

All list endpoints (`GET /api/{collection}`) are paginated. The response includes metadata to navigate through pages.

## Query parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| `page` | `1` | Page number (1-indexed) |
| `per_page` | `50` | Results per page |

```
GET /api/posts?page=2&per_page=20
```

## Response envelope

```json
{
  "items": [
    { "id": "...", "title": "Post 21", ... },
    { "id": "...", "title": "Post 22", ... }
  ],
  "total": 143,
  "page": 2,
  "per_page": 20
}
```

| Field | Description |
|-------|-------------|
| `items` | Array of records on the current page |
| `total` | Total number of records matching the current filters |
| `page` | Current page number |
| `per_page` | Records per page |

## Calculating total pages

```javascript
const totalPages = Math.ceil(response.total / response.per_page);
```

## Fetching all records

Set `per_page` to a large value to retrieve everything in one request:

```
GET /api/posts?per_page=1000
```

Note that very large values can put significant load on the database for large collections.

## Combined with filters and sort

```
GET /api/posts?filter[status]=published&sort=-created_at&page=1&per_page=10
```
