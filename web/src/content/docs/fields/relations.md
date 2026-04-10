---
title: Relations
description: Connect collections with foreign keys and expand related data
---

Use `RelationField` to create foreign key references between collections.

## Defining Relations

```python
categories = Collection("categories", fields=[
    TextField("name", required=True),
])

products = Collection("products", fields=[
    TextField("name", required=True),
    FloatField("price", required=True),
    RelationField("category", collection="categories"),
])

app.register(categories, auth=["read:public", "write:authenticated"])
app.register(products, auth=["read:public", "write:authenticated"])
```

## Creating Records with Relations

When creating a product, pass the related record's ID:

```bash
curl -X POST http://localhost:8000/api/products \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer ..." \
  -d '{"name": "Phone", "price": 999.99, "category": "category-uuid-here"}'
```

## Expanding Relations

By default, relation fields return just the ID. Use `?expand=` to inline the full related record:

```bash
GET /api/products/product-uuid?expand=category
```

Response:
```json
{
  "id": "product-uuid",
  "name": "Phone",
  "price": 999.99,
  "category": "category-uuid",
  "expand": {
    "category": {
      "id": "category-uuid",
      "name": "Electronics",
      "created_at": "...",
      "updated_at": "..."
    }
  }
}
```

## Expanding Multiple Relations

Expand multiple relations with comma-separated field names:

```bash
GET /api/products/product-uuid?expand=category,brand
```

## Expand on List Endpoints

Expand also works on list endpoints:

```bash
GET /api/products?expand=category
```

Response:
```json
{
  "items": [
    {
      "id": "...",
      "name": "Phone",
      "category": "cat-uuid",
      "expand": {
        "category": {
          "id": "cat-uuid",
          "name": "Electronics"
        }
      }
    }
  ],
  "total": 1,
  "limit": 20,
  "offset": 0
}
```

## Self-Referential Relations

Create hierarchical data structures:

```python
comments = Collection("comments", fields=[
    TextField("content", required=True),
    RelationField("parent", collection="comments"),  # Self-reference
])

app.register(comments, auth=["read:public", "write:authenticated"])
```

## Example: Blog with Categories and Tags

```python
# Categories
categories = Collection("categories", fields=[
    TextField("name", required=True),
    TextField("slug", unique=True),
])
app.register(categories)

# Posts with relations
posts = Collection("posts", fields=[
    TextField("title", required=True),
    TextField("content"),
    RelationField("category", collection="categories"),
    JSONField("tags", default=[]),
])
app.register(posts, auth=["read:public", "write:authenticated"])
```

## Next Steps

- [API Endpoints](/api/endpoints/) — REST operations
- [Filtering](/api/filtering/) — Filter by relation fields
- [Hooks](/hooks/lifecycle-events/) — React to relation changes