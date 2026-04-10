---
title: Access Control
description: Role-based access control (RBAC) for your collections
---

Access control in Cinder works like doors with locks. Each collection endpoint is a door, and auth rules specify what "keys" (credentials) open each door.

## The Mental Model

```
┌─────────────────────────────────────────────────────────────┐
│                     Collection: posts                       │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│   GET /api/posts ──────────→ read:public ──────────→ PUBLIC │
│   GET /api/posts ──────────→ read:authenticated ──→ LOGGEDIN │
│   GET /api/posts ──────────→ read:owner ────────────→ OWNER  │
│   GET /api/posts ──────────→ read:admin ────────────→ ADMIN  │
│                                                              │
│   POST /api/posts ─────────→ write:public ─────────→ PUBLIC │
│   POST /api/posts ─────────→ write:authenticated → LOGGEDIN │
│   POST /api/posts ─────────→ write:owner ───────────→ OWNER │
│   POST /api/posts ─────────→ write:admin ───────────→ ADMIN │
│                                                              │
└─────────────────────────────────────────────────────────────┘

Anyone with ANY matching key can pass through.
```

## Auth Rules Reference

### Read Operations (GET endpoints)

| Rule | When access is granted |
|------|------------------------|
| `read:public` | Always — no token required |
| `read:authenticated` | Valid JWT token present |
| `read:owner` | Valid token + you created the record |
| `read:admin` | Valid token + your role is "admin" |

### Write Operations (POST, PATCH, DELETE endpoints)

| Rule | When access is granted |
|------|------------------------|
| `write:public` | Always — no token required |
| `write:authenticated` | Valid JWT token present |
| `write:owner` | Valid token + you created the record |
| `write:admin` | Valid token + your role is "admin" |

## Rule Evaluation

Rules use **OR logic** — access is granted if **any** matching rule permits it.

```python
app.register(posts, auth=[
    "read:public",            # Rule 1: Anyone can read
    "write:authenticated",    # Rule 2: Authenticated can write
])
```

For this collection:
- GET requests work without a token
- POST/PATCH/DELETE require a valid JWT

### Multiple Rules of Same Type

```python
app.register(posts, auth=[
    "read:public",            # Rule 1
    "read:authenticated",     # Rule 2 (redundant but valid)
    "write:authenticated",    # Rule 3
])
```

Both `read` rules grant access — this is redundant but harmless.

## The Owner Rule

The `owner` rule automatically tracks which user created each record.

```python
notes = Collection("notes", fields=[
    TextField("title", required=True),
    TextField("content"),
])

app.register(notes, auth=["read:owner", "write:owner"])
```

When you use any `owner` rule:

1. Cinder adds a hidden `created_by` field to the collection
2. On create, the current user's ID is stored in `created_by`
3. On read/update/delete, queries filter by `created_by = current_user.id`

### Example Flow

```bash
# Alice creates a note
curl -X POST /api/notes \
  -H "Authorization: Bearer alice-token" \
  -d '{"title": "Alice's Secret"}'
# created_by = alice-uuid (automatic)

# Alice reads her notes
curl /api/notes \
  -H "Authorization: Bearer alice-token"
# Returns only Alice's notes

# Bob tries to read Alice's note directly
curl /api/notes/note-uuid \
  -H "Authorization: Bearer bob-token"
# Returns 404 (Bob can't see Alice's records)
```

## Admin Users

Admin status is stored in each user's `role` field:

| Role | Access |
|------|--------|
| `"user"` | Default role, normal permissions |
| `"admin"` | Full access to admin-protected resources |

### Promoting a User to Admin

Use the CLI:

```bash
cinder promote user@example.com --role admin
```

### Admin-Only Collections

```python
app.register(settings, auth=["read:admin", "write:admin"])
```

Only users with `role: admin` can access this collection.

## Common Patterns

### Pattern 1: Public Read, Protected Write

```python
app.register(posts, auth=["read:public", "write:authenticated"])
```

- Anyone can read posts
- Only logged-in users can create/edit/delete

### Pattern 2: Private Content (Owner-Only)

```python
app.register(notes, auth=["read:owner", "write:owner"])
```

- Users can only see their own notes
- Users can only edit/delete their own notes

### Pattern 3: Public Create, Protected Edit

```python
app.register(comments, auth=[
    "read:public",
    "write:public",
    "write:owner",   # Original creator can edit
])
```

- Anyone can read and create comments
- Only the original commenter can edit their comment
- Deletion requires `write:owner` (implicit from the rule)

### Pattern 4: Tiered Access

```python
app.register(content, auth=[
    "read:public",
    "write:authenticated",
    "read:admin",    # Admins see all content
    "write:admin",   # Admins can edit anything
])
```

- Public can read
- Authenticated users can create
- Admins can read and edit everything

## Debugging Access Issues

### Problem: 401 Unauthorized

**Symptoms:** Request returns 401 even with a token.

**Causes:**
1. Token expired (default: 24 hours)
2. Token malformed (check the `Bearer ` prefix)
3. Token revoked via logout

**Fix:** Login again to get a fresh token.

### Problem: 403 Forbidden

**Symptoms:** Valid token but request returns 403.

**Causes:**
1. Insufficient permissions (e.g., accessing admin collection as regular user)
2. Owner rule preventing access to another user's record

**Fix:** Check your auth rules. For owner rules, ensure you're accessing your own records.

### Problem: 404 Instead of 403 on Owner Rule

**Symptoms:** Accessing another user's record returns 404, not 403.

**This is intentional.** Returning 404 prevents information leakage about which records exist. A malicious user shouldn't know if record ID 123 exists if they don't own it.

### Debugging Hook

Log access decisions in a hook:

```python
async def log_access(data, ctx):
    if ctx.user:
        print(f"User {ctx.user['id']} accessing {ctx.collection}")
    else:
        print(f"Anonymous access to {ctx.collection}")
    return data

posts.on("before_read", log_access)
```

## Next Steps

- [Authentication](/authentication/setup/) — Configure auth options
- [Hooks](/core-concepts/lifecycle-hooks/) — Execute logic based on access
