# API Endpoints

Zork auto-generates RESTful endpoints from your collection definitions. This guide documents all available operations.

## Collection Endpoints

For a collection named `posts`, these endpoints are created:

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/posts` | List all records |
| POST | `/api/posts` | Create a new record |
| GET | `/api/posts/{id}` | Get a single record |
| PATCH | `/api/posts/{id}` | Update a record |
| DELETE | `/api/posts/{id}` | Delete a record |

## Listing Records

**Endpoint:** `GET /api/posts`

### Query Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `limit` | int | 20 | Maximum records to return |
| `offset` | int | 0 | Records to skip |
| `order_by` | string | created_at | Field to sort by |
| `expand` | string | - | Relations to expand |

### Example

```bash
# Get first page
curl "http://localhost:8000/api/posts?limit=10"

# Get second page
curl "http://localhost:8000/api/posts?limit=10&offset=10"

# Sort by title
curl "http://localhost:8000/api/posts?order_by=title"

# Reverse sort
curl "http://localhost:8000/api/posts?order_by=-created_at"
```

### Response

```json
{
  "items": [
    {
      "id": "post-123",
      "title": "First Post",
      "body": "Content here",
      "created_at": "2024-01-15T10:30:00Z",
      "updated_at": "2024-01-15T10:30:00Z"
    }
  ],
  "total": 50,
  "limit": 20,
  "offset": 0
}
```

## Creating Records

**Endpoint:** `POST /api/posts`

### Request Body

```json
{
  "title": "New Post",
  "body": "Post content"
}
```

### Example

```bash
curl -X POST http://localhost:8000/api/posts \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title": "My Post", "body": "Content here"}'
```

### Response (201 Created)

```json
{
  "id": "new-post-id",
  "title": "My Post",
  "body": "Content here",
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T10:30:00Z"
}
```

## Getting a Single Record

**Endpoint:** `GET /api/posts/{id}`

### Example

```bash
curl http://localhost:8000/api/posts/post-123
```

### With Expands

```bash
curl "http://localhost:8000/api/posts/post-123?expand=author,category"
```

### Response

```json
{
  "id": "post-123",
  "title": "My Post",
  "body": "Content here",
  "author": "user-456",
  "expand": {
    "author": {
      "id": "user-456",
      "username": "alice"
    }
  },
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T10:30:00Z"
}
```

## Updating Records

**Endpoint:** `PATCH /api/posts/{id}`

Only the provided fields are updated. Other fields remain unchanged.

### Request Body

```json
{
  "title": "Updated Title"
}
```

### Example

```bash
curl -X PATCH http://localhost:8000/api/posts/post-123 \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"title": "Updated Title"}'
```

### Response

```json
{
  "id": "post-123",
  "title": "Updated Title",
  "body": "Original content",
  "updated_at": "2024-01-15T11:00:00Z"
}
```

## Deleting Records

**Endpoint:** `DELETE /api/posts/{id}`

### Example

```bash
curl -X DELETE http://localhost:8000/api/posts/post-123 \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Response

```json
{
  "message": "Record deleted"
}
```

## Filtering

Filter records by field values:

```bash
# Filter by exact match
curl "http://localhost:8000/api/posts?status=published"

# Multiple filters
curl "http://localhost:8000/api/posts?status=published&author=user-123"
```

Add filtering to collection hooks for custom logic:

```python
@posts.on("before_list")
async def filter_by_user(query, ctx):
    if ctx.user:
        query["filters"]["author_id"] = ctx.user["id"]
    return query
```

## Pagination

### Offset Pagination

```bash
# Page 1
curl "http://localhost:8000/api/posts?limit=10&offset=0"

# Page 2
curl "http://localhost:8000/api/posts?limit=10&offset=10"

# Page 3
curl "http://localhost:8000/api/posts?limit=10&offset=20"
```

### Response Metadata

The list response includes pagination metadata:

```json
{
  "items": [...],
  "total": 150,
  "limit": 10,
  "offset": 20
}
```

Use `total` and `limit` to calculate total pages:

```
total_pages = ceil(total / limit)
```

## Sorting

Sort by any field:

```bash
# Ascending order
curl "http://localhost:8000/api/posts?order_by=created_at"

# Descending order
curl "http://localhost:8000/api/posts?order_by=-created_at"

# Multiple fields
curl "http://localhost:8000/api/posts?order_by=status,-created_at"
```

## Error Responses

### Validation Error (400)

```json
{
  "status": 400,
  "error": "Field 'title' is required"
}
```

### Not Found (404)

```json
{
  "status": 404,
  "error": "Record not found"
}
```

### Unauthorized (401)

```json
{
  "status": 401,
  "error": "Authentication required"
}
```

### Forbidden (403)

```json
{
  "status": 403,
  "error": "Permission denied"
}
```

## Next Steps

- [OpenAPI](/api/openapi) — API documentation
- [Filtering](/api/filtering) — Advanced filtering options
- [Pagination](/api/pagination) — Pagination options
