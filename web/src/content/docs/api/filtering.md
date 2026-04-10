---
title: Filtering & Sorting
description: Filter and sort your API results
---

## Filtering

Filter records by passing field values as query parameters:

### Exact Match

```bash
GET /api/products?is_published=true
```

### Multiple Filters (AND)

```bash
GET /api/products?stock=50&is_published=true
```

### Filter by Any Field

```bash
GET /api/products?name=Phone
```

## Sorting

Sort by any field using `order_by`:

### Ascending Order

```bash
GET /api/products?order_by=price
```

### Descending Order

Prefix with `-` for descending:

```bash
GET /api/products?order_by=-created_at
```

### Default Sort

Default sort is by `created_at` (descending - newest first).

## Combined Example

```bash
GET /api/products?is_published=true&order_by=price&limit=5&offset=0
```

This returns:
- Only published products
- Sorted by price (ascending)
- First 5 results
- Starting from offset 0

## Filtering by Relations

Filter by related collection IDs:

```bash
GET /api/products?category=category-uuid
```

## Filtering by JSON Fields

Filter JSON fields using dot notation:

```bash
GET /api/posts?metadata.author=john
```

## Next Steps

- [Pagination](/api/pagination/) — Control page size and offset
- [Endpoints](/api/endpoints/) — Full API reference
- [Relations](/fields/relations/) — Working with related data