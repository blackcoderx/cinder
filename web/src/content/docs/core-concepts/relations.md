---
title: Relations
description: Link collections together with foreign key references
---

`RelationField` stores a reference to a record in another collection. Relations are stored as IDs and can be expanded in-place by the client using the `expand` query parameter.

## Defining a relation

```python
from cinder import Collection, TextField, RelationField

authors = Collection("authors", fields=[
    TextField("name", required=True),
    TextField("bio"),
])

posts = Collection("posts", fields=[
    TextField("title", required=True),
    TextField("body"),
    RelationField("author", collection="authors"),
])

app.register(authors)
app.register(posts, auth=["read:public", "write:authenticated"])
```

## Creating related records

First create the parent:

```bash
curl -X POST /api/authors \
  -H "Content-Type: application/json" \
  -d '{"name": "Alice"}'
# returns: {"id": "author-uuid", ...}
```

Then create the child with the parent ID:

```bash
curl -X POST /api/posts \
  -H "Authorization: Bearer ..." \
  -H "Content-Type: application/json" \
  -d '{"title": "Hello", "author": "author-uuid"}'
```

## Expanding relations

By default, relation fields return the raw ID string. Use `?expand=field_name` to fetch the full related record. The expanded data is placed in a nested `expand` key on the record — the original ID field is kept unchanged:

```bash
GET /api/posts?expand=author
```

```json
{
  "items": [
    {
      "id": "...",
      "title": "Hello",
      "author": "author-uuid",
      "expand": {
        "author": {
          "id": "author-uuid",
          "name": "Alice",
          "bio": null
        }
      }
    }
  ]
}
```

Expand multiple fields at once:

```bash
GET /api/posts?expand=author,category
```

Expand also works on single-record endpoints:

```bash
GET /api/posts/some-id?expand=author
```

## RelationField options

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `name` | `str` | — | Field name (column name) |
| `collection` | `str` | — | Name of the referenced collection |
| `required` | `bool` | `False` | If `True`, the field cannot be null |
| `unique` | `bool` | `False` | Enforce a unique constraint |
| `indexed` | `bool` | `False` | Add a database index for faster lookups |

## Notes

- Relations are stored as `TEXT` columns containing the referenced record's UUID.
- There is no automatic referential integrity at the database level — if you delete an author, their posts will still hold the (now orphaned) author ID.
- For many-to-many relationships, create a join collection with two `RelationField` columns.
