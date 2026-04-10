---
title: Relations
description: Connect collections together with foreign keys
---

Relations let you link collections together, forming a data model similar to foreign keys in traditional databases.

## What is a Relation?

A **RelationField** stores the ID of another record, creating a link between two collections. For example, a `posts` collection might link to a `categories` collection:

```
┌─────────────────┐         ┌─────────────────┐
│     posts       │         │   categories    │
├─────────────────┤         ├─────────────────┤
│ id (UUID)       │    ┌───→│ id (UUID)       │
│ title           │    │    │ name            │
│ content         │    │    │                 │
│ category ────────┼────┘    │                 │
│ created_at      │         │ created_at      │
└─────────────────┘         └─────────────────┘
```

The `category` field stores a category's UUID, not the entire category object.

## Defining Relations

```python
from cinder import Cinder, Collection, TextField, FloatField, RelationField

app = Cinder(database="app.db")

# Define the related collection first
categories = Collection("categories", fields=[
    TextField("name", required=True),
])

# Add a RelationField to another collection
products = Collection("products", fields=[
    TextField("name", required=True),
    FloatField("price", required=True),
    RelationField("category", collection="categories"),
])

app.register(categories, auth=["read:public", "write:authenticated"])
app.register(products, auth=["read:public", "write:authenticated"])
```

**Note:** The `collection` parameter takes the **string name** of the target collection, not the collection object itself.

### RelationField Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `collection` | `str` | (required) | Name of the target collection |
| `required` | `bool` | `False` | Whether the relation is mandatory |
| `unique` | `bool` | `False` | One-to-one relationship (each record links to at most one target) |
| `indexed` | `bool` | `False` | Create database index for faster lookups |

```python
# Mandatory relation
RelationField("author", collection="users", required=True)

# One-to-one: each user has one profile
RelationField("profile", collection="profiles", unique=True)

# Indexed for faster queries
RelationField("department", collection="departments", indexed=True)
```

## The expand Parameter

By default, relation fields return just the ID. Use `?expand=` to fetch the full related record:

```bash
# Get a product with its category
GET /api/products/abc123?expand=category
```

**Response:**

```json
{
  "id": "abc123",
  "name": "Phone",
  "price": 999.99,
  "category": "cat-uuid-456",
  "expand": {
    "category": {
      "id": "cat-uuid-456",
      "name": "Electronics",
      "created_at": "2026-04-10T12:00:00Z",
      "updated_at": "2026-04-10T12:00:00Z"
    }
  }
}
```

Expand works on list endpoints too:

```bash
# Get first 10 products with their categories
GET /api/products?expand=category&limit=10
```

Expand multiple relations with comma separation:

```bash
GET /api/orders/123?expand=customer,shipping_address,billing_address
```

## Creating Records with Relations

When creating a record, provide the target record's ID:

```bash
curl -X POST http://localhost:8000/api/products \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer eyJ..." \
  -d '{
    "name": "Phone",
    "price": 999.99,
    "category": "cat-uuid-456"
  }'
```

## Common Patterns

### One-to-Many

A category has many products:

```python
categories = Collection("categories", fields=[
    TextField("name", required=True),
])

products = Collection("products", fields=[
    TextField("name", required=True),
    RelationField("category", collection="categories"),
])
```

### Self-Referencing

Categories can have parent categories (e.g., "Electronics" → "Phones" → "Smartphones"):

```python
categories = Collection("categories", fields=[
    TextField("name", required=True),
    RelationField("parent", collection="categories"),  # References itself
])
```

### Multiple Relations to Same Collection

An article can have a primary author and contributors:

```python
articles = Collection("articles", fields=[
    TextField("title", required=True),
    RelationField("primary_author", collection="authors", required=True),
    RelationField("contributor", collection="authors"),
])
```

### Many-to-Many (via Junction Table)

Cinder doesn't have built-in many-to-many relations. Implement them with a junction collection:

```python
# Junction table for posts <-> tags
post_tags = Collection("post_tags", fields=[
    RelationField("post", collection="posts", required=True),
    RelationField("tag", collection="tags", required=True),
], indexes=[("post", "tag")])  # Composite unique index

# To find all tags for a post:
# 1. GET /api/post_tags?post=post-uuid → get tag IDs
# 2. For each tag, expand or fetch separately
```

## Limitations

| Limitation | Workaround |
|------------|------------|
| No nested expand | Fetch related records in your application code |
| No cascade delete | Use hooks to manually delete related records |
| No foreign key constraints | Data integrity is enforced at the application layer |
| N+1 queries on expand | Use caching for frequently expanded relations |

### N+1 Query Consideration

Each `expand` triggers a separate database query per item:

```bash
# Expands 10 products → 11 queries (1 for products + 10 for categories)
GET /api/products?expand=category&limit=10
```

For high-traffic endpoints, consider:
- Caching the expanded data
- Denormalizing data into the parent collection
- Using database views

## Next Steps

- [Field Types](/fields/field-types/) — All available field definitions
- [Collections](/core-concepts/collections/) — Define your data schemas
- [Hooks](/core-concepts/lifecycle-hooks/) — React to relation changes
