# Collections

Collections are the core building block of Zork. A collection defines a data schema, and Zork automatically creates the database table and REST API endpoints for it.

## Defining a Collection

Import `Collection` and field types, then define your schema:

```python
from zork import Collection, TextField, IntField, BoolField

articles = Collection("articles", fields=[
    TextField("title", required=True),
    TextField("body"),
    IntField("view_count", default=0),
    BoolField("published", default=False),
])
```

## Naming Rules

The collection name becomes the database table name and the URL segment:

- `Collection("articles")` creates table `articles` with endpoints at `/api/articles`
- Use lowercase letters, numbers, and underscores only
- Names must be unique across all registered collections

## Auto-Generated Columns

Every collection automatically gets three additional columns:

| Column | Type | Description |
|--------|------|-------------|
| `id` | TEXT (UUID) | Auto-generated unique identifier |
| `created_at` | TEXT (ISO 8601) | Timestamp when record was created |
| `updated_at` | TEXT (ISO 8601) | Timestamp when record was last updated |

You do not need to declare these columns. They are added automatically.

## Auto-Generated Endpoints

Registering a collection automatically creates five REST endpoints:

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/{name}` | List records with filtering and pagination |
| POST | `/api/{name}` | Create a new record |
| GET | `/api/{name}/{id}` | Get a single record by ID |
| PATCH | `/api/{name}/{id}` | Update specific fields of a record |
| DELETE | `/api/{name}/{id}` | Delete a record |

## Query Validation

Zork automatically validates query parameters to prevent security issues and ensure API reliability:

### Filter Validation

Filter keys must match valid collection field names:

```python
# Valid - filters on defined fields
 GET /api/articles?status=published

# Invalid - returns 400 error
GET /api/articles?invalid_field=value
# Error: "Invalid field: invalid_field"
```

Built-in columns (`id`, `created_at`, `updated_at`) are always allowed.

### Pagination Limits

Query parameters are validated with sensible defaults:

| Parameter | Default | Maximum | Minimum |
|-----------|---------|---------|---------|
| `limit` | 20 | 100 | 1 |
| `offset` | 0 | 10000 | 0 |

```python
# These are automatically clamped to valid ranges
GET /api/articles?limit=500   # → limit=100 (max)
GET /api/articles?limit=-5      # → limit=1 (min)
GET /api/articles?offset=20000  # → offset=10000 (max)
```

### Order By Validation

The `order_by` parameter must reference a valid field:

```python
# Valid - sorts by created_at
GET /api/articles?order_by=created_at

# Invalid - returns 400 error
GET /api/articles?order_by=invalid_column
```

## Registering a Collection

Add your collection to the app:

```python
app.register(articles)
```

With access control rules:

```python
app.register(articles, auth=["read:public", "write:authenticated"])
```

See [Access Control](/core-concepts/access-control) for all available rules.

## Field Reference

Here is how each field type maps to a database column:

| Field Type | Database Type | Notes |
|------------|---------------|-------|
| `TextField` | TEXT | Arbitrary length string |
| `IntField` | INTEGER | 64-bit integer |
| `FloatField` | REAL | Double-precision float |
| `BoolField` | INTEGER | 0 or 1 |
| `DateTimeField` | TEXT | ISO 8601 string |
| `URLField` | TEXT | Validated URL string |
| `JSONField` | TEXT | JSON-serialized string |
| `FileField` | TEXT | JSON metadata for uploaded files |
| `RelationField` | TEXT | UUID of related record |

See the [Field Types](/core-concepts/fields) guide for detailed field options.

## Indexes

Add database indexes for faster queries on specific fields.

### Single-Field Indexes

Mark fields as indexed for faster filtering and sorting:

```python
from zork import Collection, TextField

posts = Collection("posts", fields=[
    TextField("slug", required=True, indexed=True),
    TextField("status"),
])
```

### Composite Indexes

Create multi-column indexes for queries that filter on combinations:

```python
posts = Collection(
    "posts",
    fields=[
        TextField("author_id"),
        TextField("status"),
        DateTimeField("published_at"),
    ],
    indexes=[
        ("author_id", "status"),         # Index on (author_id, status)
        ("status", "published_at"),      # Index on (status, published_at)
    ],
)
```

## Lifecycle Hooks

Collections support lifecycle hooks for running code before and after operations.

```python
@articles.on("before_create")
async def validate_article(data, ctx):
    # Transform data before saving
    data["slug"] = data["title"].lower().replace(" ", "-")
    return data

@articles.on("after_create")
async def notify_new_article(article, ctx):
    # Send notification after creation
    await send_notification(f"New article: {article['title']}")
```

See the [Lifecycle Hooks](/core-concepts/lifecycle-hooks) guide for all available events.

## Schema Management

Zork offers two modes for managing database schema changes: auto-sync for rapid development, and migrations for controlled production deployments.

### Development Mode (Auto-Sync)

In development, Zork automatically syncs your collection definitions with the database:

- New tables are created automatically
- Missing columns are added on startup
- Indexes are created automatically

This is convenient for rapid development but requires caution in production.

### Production Mode (Migrations)

For production environments, disable auto-sync and use explicit migrations:

```python
app = Zork(
    database="postgresql://user:pass@host:5432/mydb",
    auto_sync=False,
)
```

Or via environment variable:

```bash
ZORK_AUTO_SYNC=false
```

### Previewing Schema Changes

Before applying changes, preview what will be different:

```bash
zork schema diff --app main.py
```

This shows:

- Columns that would be added
- Columns that exist but are not in your schema
- Potential typos detected
- Indexes that would be created

### Converting to Migrations

Convert auto-sync decisions to migration files:

```bash
zork migrate sync --app main.py
```

This creates proper migration files that you can review and commit.

### Safety Warnings

Zork detects potential issues:

| Warning | Meaning |
|---------|---------|
| `Possible typo detected` | Column name looks similar to an orphan column |
| `Orphan column exists` | Column in DB not in your schema |

### When to Use Migrations

Always use migrations for:

- Renaming columns
- Changing column types
- Dropping columns
- Complex data transforms
- Production deployments

## Example: Blog Collections

Here is a complete example with multiple related collections:

```python
from zork import Zork, Collection, TextField, IntField, DateTimeField, RelationField, Auth

app = Zork(database="blog.db")

# Categories collection
categories = Collection("categories", fields=[
    TextField("name", required=True),
    TextField("slug", required=True, unique=True),
])

# Posts collection
posts = Collection("posts", fields=[
    TextField("title", required=True),
    TextField("content"),
    RelationField("category", collection="categories"),
    DateTimeField("published_at"),
    IntField("view_count", default=0),
])

# Comments collection
comments = Collection("comments", fields=[
    TextField("body", required=True),
    RelationField("post", collection="posts"),
    TextField("author_name"),
])

# Register with access control
app.register(categories, auth=["read:public", "write:admin"])
app.register(posts, auth=["read:public", "write:authenticated"])
app.register(comments, auth=["read:public", "write:public"])

auth = Auth(allow_registration=True)
app.use_auth(auth)
```

## Next Steps

- [Field Types](/core-concepts/fields) — Explore all available field types
- [Relations](/core-concepts/relations) — Link collections together
- [Lifecycle Hooks](/core-concepts/lifecycle-hooks) — Add custom logic to operations
- [Access Control](/core-concepts/access-control) — Control who can access data
