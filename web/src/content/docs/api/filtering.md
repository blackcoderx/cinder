---
title: Filtering
description: Filter collection results with query parameters
sidebar:
  order: 2
---

Use `filter` query parameters to narrow down list results. Filters work on any field in the collection.

## Basic filtering

```
GET /api/posts?filter[status]=published
GET /api/posts?filter[author_id]=user-uuid
```

Multiple filters are combined with AND:

```
GET /api/posts?filter[status]=published&filter[author_id]=user-uuid
```

## Filter operators

Append an operator after the field name with double underscores:

| Operator | Meaning | Example |
|----------|---------|---------|
| _(none)_ | Exact match | `filter[status]=published` |
| `__gt` | Greater than | `filter[views__gt]=100` |
| `__gte` | Greater than or equal | `filter[views__gte]=100` |
| `__lt` | Less than | `filter[price__lt]=50` |
| `__lte` | Less than or equal | `filter[price__lte]=50` |
| `__contains` | Case-insensitive substring | `filter[title__contains]=hello` |
| `__startswith` | Starts with (case-insensitive) | `filter[title__startswith]=hello` |
| `__null` | Is null (`true`/`false`) | `filter[avatar__null]=true` |

## Examples

Posts with more than 1000 views:

```
GET /api/posts?filter[views__gt]=1000
```

Products under $50:

```
GET /api/products?filter[price__lt]=50
```

Search by title:

```
GET /api/posts?filter[title__contains]=cinder
```

Records without an avatar:

```
GET /api/users?filter[avatar__null]=true
```

## Filtering on relation fields

Filter by the ID of a related record:

```
GET /api/posts?filter[author_id]=user-uuid
```

## Sorting

Use the `sort` parameter:

```
GET /api/posts?sort=created_at          # ascending
GET /api/posts?sort=-created_at         # descending (prefix with -)
GET /api/posts?sort=author_id,-views    # multiple fields
```

## Combining filters and sort

```
GET /api/posts?filter[status]=published&sort=-created_at&page=2&per_page=20
```
