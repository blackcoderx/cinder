---
title: Filtering & Ordering
description: Filter and order collection results with query parameters
sidebar:
  order: 2
---

Use query parameters to filter and order list results on any field in the collection.

## Basic filtering

Pass field names directly as query parameters:

```
GET /api/posts?status=published
GET /api/posts?author_id=user-uuid
```

Multiple filters are combined with AND:

```
GET /api/posts?status=published&author_id=user-uuid
```

Only **exact equality** matching is supported. Filters are passed as-is to a `WHERE field = ?` SQL clause.

## Ordering

Use the `order_by` parameter to sort results. The value must be a valid column name:

```
GET /api/posts?order_by=created_at
GET /api/posts?order_by=title
```

Default ordering is by `created_at` ascending. To sort descending, use raw SQL direction syntax (note: only ascending is supported via the API — for descending you must use a hook or a custom query):

```
GET /api/posts?order_by=created_at
```

:::note
Advanced filtering operators (greater than, contains, etc.) and descending sort are not yet implemented in Zeno v0.1.0. Only exact match filtering and ascending `order_by` are currently supported.
:::

## Expanding relations

Use the `expand` parameter to inline related records. Expanded data appears in a nested `expand` object on each record, keyed by field name:

```
GET /api/posts?expand=author
```

```json
{
  "items": [
    {
      "id": "...",
      "title": "Hello",
      "author": "user-uuid",
      "expand": {
        "author": {
          "id": "user-uuid",
          "name": "Alice"
        }
      }
    }
  ]
}
```

Expand multiple relation fields at once:

```
GET /api/posts?expand=author,category
```

Expand on a single-record endpoint:

```
GET /api/posts/some-id?expand=author
```

:::note
Only `RelationField` columns can be expanded. Passing an unknown or non-relation field name in `expand` is silently ignored.
:::

## Combined example

```
GET /api/posts?status=published&order_by=created_at&limit=10&offset=0&expand=author
```
