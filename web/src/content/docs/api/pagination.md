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
| `limit` | `20` | Maximum number of records to return |
| `offset` | `0` | Number of records to skip |

```
GET /api/posts?limit=20&offset=40
```

## Response envelope

```json
{
  "items": [
    { "id": "...", "title": "Post 41", ... },
    { "id": "...", "title": "Post 42", ... }
  ],
  "total": 143,
  "limit": 20,
  "offset": 40
}
```

| Field | Description |
|-------|-------------|
| `items` | Array of records in this page |
| `total` | Total number of records matching the current filters |
| `limit` | The limit applied to this query |
| `offset` | The offset applied to this query |

## Calculating pages

```javascript
const totalPages = Math.ceil(response.total / response.limit);
const currentPage = Math.floor(response.offset / response.limit) + 1;

// Next page offset
const nextOffset = response.offset + response.limit;
const hasMore = nextOffset < response.total;
```

## Fetching all records

Set `limit` to a large value to retrieve everything in one request:

```
GET /api/posts?limit=1000
```

Note that very large values can put significant load on the database for large collections.

## Combined with filters and ordering

```
GET /api/posts?order_by=created_at&limit=10&offset=0
```
