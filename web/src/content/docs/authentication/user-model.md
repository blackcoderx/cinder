---
title: User Model
description: The built-in user model and how to extend it
---

## Database Schema

The `_users` table is created automatically when you configure auth.

```sql
CREATE TABLE _users (
    id TEXT PRIMARY KEY,
    email TEXT UNIQUE NOT NULL,
    username TEXT UNIQUE,
    password TEXT NOT NULL,
    is_verified INTEGER DEFAULT 0,
    is_active INTEGER DEFAULT 1,
    role TEXT DEFAULT 'user',
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    -- + extended columns
);
```

## Default Fields

| Field | Type | Description |
|-------|------|-------------|
| `id` | TEXT | UUID4 primary key |
| `email` | TEXT | Unique email address |
| `username` | TEXT | Optional unique username |
| `password` | TEXT | Bcrypt hashed password (never plain text) |
| `is_verified` | INTEGER | `0` = unverified, `1` = verified |
| `is_active` | INTEGER | `0` = disabled, `1` = active |
| `role` | TEXT | User role (`user`, `admin`, etc.) |
| `created_at` | TEXT | ISO 8601 timestamp |
| `updated_at` | TEXT | ISO 8601 timestamp |

## Account Status

### is_verified

Indicates email verification status:

- `0` — Email not verified (default on registration)
- `1` — Email verified

Verification is optional by default. Require it with a hook:

```python
@auth.on("auth:before_login")
async def require_verification(data, ctx):
    user = await db.fetch_one(
        "SELECT is_verified FROM _users WHERE email = ?",
        (data["email"],)
    )
    if user and not user["is_verified"]:
        raise CinderError(403, "Please verify your email first")
    return data
```

### is_active

Controls account access:

- `1` — Active (default)
- `0` — Disabled (login blocked)

Disable an account:

```python
await db.execute(
    "UPDATE _users SET is_active = 0 WHERE email = ?",
    (email,)
)
```

## Extending the User Model

Add custom fields using `extend_user`:

```python
from cinder import Auth, TextField, IntField, BoolField

auth = Auth(extend_user=[
    TextField("display_name"),
    TextField("avatar_url"),
    IntField("age"),
    BoolField("notifications_enabled"),
])
```

Extended fields are stored in the `_users` table alongside default fields.

### Providing Extended Fields

Extended fields can be included during registration:

```bash
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "secure123",
    "display_name": "John Doe",
    "avatar_url": "https://example.com/avatar.jpg",
    "age": 25
  }'
```

### Updating Extended Fields

Update extended fields via hooks or direct database access:

```python
@app.on("auth:after_register")
async def set_defaults(user, ctx):
    await db.execute(
        "UPDATE _users SET notifications_enabled = 1 WHERE id = ?",
        (user["id"],)
    )
```

## User Roles

### Default Roles

| Role | Description |
|------|-------------|
| `user` | Default role for all new registrations |
| `admin` | Full access to admin-protected resources |

### Promoting Users

**CLI:**
```bash
cinder promote user@example.com --role admin
```

**Programmatically:**

```python
async def promote_user(email: str, role: str = "admin"):
    await db.execute(
        "UPDATE _users SET role = ? WHERE email = ?",
        (role, email)
    )
```

### Role-Based Access Control

Use roles in collection auth rules:

```python
app.register(admin_panel, auth=["read:admin", "write:admin"])
```

Only users with `role: admin` can access this collection.

Check roles in hooks:

```python
@posts.on("before_read")
async def hook(data, ctx):
    if ctx.user and ctx.user["role"] == "admin":
        # Admin can see more
        data["include_internal"] = True
    return data
```

## Checking User in Code

### Via Context

In hooks and custom endpoints:

```python
@posts.on("before_create")
async def hook(data, ctx):
    if ctx.user:
        user_id = ctx.user["id"]
        user_email = ctx.user["email"]
        user_role = ctx.user["role"]
    return data
```

### Via Request State

In custom route handlers:

```python
from starlette.requests import Request

async def my_endpoint(request: Request):
    user = request.state.user
    if user:
        print(f"Logged in as {user['email']}")
```

## Deleting Users

Cinder doesn't have a built-in delete user endpoint. Implement it manually:

```python
@app.on("app:startup")
async def setup_custom_routes(app):
    @app.router.post("/api/users/me/delete")
    async def delete_me(request):
        user = request.state.user
        if not user:
            return JSONResponse({"error": "Unauthorized"}, status_code=401)
        
        # Delete user's data
        await db.execute("DELETE FROM posts WHERE created_by = ?", (user["id"],))
        
        # Delete user
        await db.execute("DELETE FROM _users WHERE id = ?", (user["id"],))
        
        return JSONResponse({"message": "Account deleted"})
```

## Next Steps

- [Setup](/authentication/setup/) — Configure auth
- [Endpoints](/authentication/endpoints/) — Auth API reference
- [Hooks](/authentication/hooks/) — React to user events
