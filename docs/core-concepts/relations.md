# Relations

RelationField lets you create relationships between collections, similar to foreign keys in traditional databases.

## Defining Relations

Add a RelationField to your collection pointing to another collection:

```python
from zork import Collection, TextField, RelationField

users = Collection("users", fields=[
    TextField("username", required=True),
])

posts = Collection("posts", fields=[
    TextField("title", required=True),
    TextField("body"),
    RelationField("author", collection="users"),
])
```

The `collection` parameter must match the name of the related collection exactly.

## Self-Referential Relations

Create relationships within the same collection:

```python
comments = Collection("comments", fields=[
    TextField("body", required=True),
    RelationField("parent", collection="comments"),  # Replies
    RelationField("post", collection="posts"),
])
```

## Required Relations

Make the relation required:

```python
posts = Collection("posts", fields=[
    TextField("title", required=True),
    RelationField("author", collection="users", required=True),
])
```

## Using Relations

### Creating Records with Relations

When creating a record, provide the ID of the related record:

```bash
curl -X POST http://localhost:8000/api/posts \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "My First Post",
    "body": "Post content here",
    "author": "USER_ID_HERE"
  }'
```

### Filtering by Relation

Filter records by their relation field value:

```bash
# Get all posts by a specific author
curl "http://localhost:8000/api/posts?author=USER_ID_HERE"
```

## Expanding Relations

The `expand` parameter lets you fetch related records in a single request. Instead of just the author ID, you get the full author object.

### Expanding a Single Relation

```bash
curl "http://localhost:8000/api/posts?expand=author"
```

The response includes the expanded author:

```json
{
  "id": "post-123",
  "title": "My First Post",
  "body": "Post content here",
  "author": "USER_ID_HERE",
  "expand": {
    "author": {
      "id": "user-456",
      "username": "alice",
      "email": "alice@example.com"
    }
  }
}
```

### Expanding Multiple Relations

```bash
curl "http://localhost:8000/api/posts?expand=author,category"
```

### Expanding in List Endpoints

Expand relations when listing records:

```bash
curl "http://localhost:8000/api/posts?expand=author&limit=10"
```

## How Expansion Works

The expand feature performs a database lookup to fetch the related record:

1. Your request includes `?expand=author`
2. Zork reads the `author` field from the post (contains user ID)
3. Zork looks up the user by that ID
4. The result is added to `expand.author` in the response

This is useful for avoiding multiple API calls and getting all the data you need.

## Cascading Deletes

Zork does not automatically delete related records. If you delete a user, posts referencing that user will have an invalid author reference.

You can handle this with lifecycle hooks:

```python
@posts.on("before_delete")
async def cleanup_author_posts(post, ctx):
    # Find and delete all posts by this author
    # Or set author to null, or move to a "deleted user" placeholder
    pass
```

## Many-to-Many Relations

Zork does not have built-in many-to-many relations. Implement this pattern manually:

### Option 1: Store as JSON Array

```python
posts = Collection("posts", fields=[
    TextField("title"),
    JSONField("tags", default=[]),  # Store tag names or IDs
])
```

### Option 2: Create a Junction Collection

```python
# Junction table for post-tag relationships
post_tags = Collection("post_tags", fields=[
    RelationField("post", collection="posts", required=True),
    RelationField("tag", collection="tags", required=True),
])

tags = Collection("tags", fields=[
    TextField("name", required=True),
])
```

Query posts with a specific tag:

```bash
curl "http://localhost:8000/api/post_tags?tag=TAG_ID"
```

## Performance Considerations

### Index Your Relation Fields

If you frequently filter by a relation, add an index:

```python
posts = Collection("posts", fields=[
    TextField("title"),
    RelationField("author", collection="users", indexed=True),
])
```

### Use Expansion Judiciously

Expanding relations on large lists can be slow. Consider:

- Expanding on detail endpoints (`/api/posts/{id}`) rather than lists
- Limiting expanded results
- Caching expanded data if it does not change frequently

## Complete Example

```python
from zork import Zork, Collection, TextField, IntField, RelationField

app = Zork(database="blog.db")

users = Collection("users", fields=[
    TextField("username", required=True),
    TextField("email"),
])

categories = Collection("categories", fields=[
    TextField("name", required=True),
    TextField("slug", required=True),
])

posts = Collection("posts", fields=[
    TextField("title", required=True),
    TextField("content"),
    RelationField("author", collection="users", required=True),
    RelationField("category", collection="categories"),
    IntField("view_count", default=0),
])

comments = Collection("comments", fields=[
    TextField("body", required=True),
    RelationField("post", collection="posts", required=True),
    RelationField("author", collection="users"),
])

app.register(users)
app.register(categories)
app.register(posts)
app.register(comments)
```

## Next Steps

- [Lifecycle Hooks](/core-concepts/lifecycle-hooks) — Handle relation cleanup on delete
- [Caching](/caching/setup) — Cache expanded relations for performance
