# User Model

Zork creates and manages a users table for authentication. This guide explains the user model structure and how to extend it.

## Default User Table

When you enable authentication, Zork creates a `_users` table with these columns:

| Column | Type | Description |
|--------|------|-------------|
| `id` | TEXT | UUID primary key |
| `email` | TEXT | Unique email address |
| `username` | TEXT | Optional unique username |
| `password` | TEXT | Bcrypt hashed password |
| `is_verified` | INTEGER | Email verification status (0 or 1) |
| `is_active` | INTEGER | Account active status (0 or 1) |
| `role` | TEXT | User role (default: "user") |
| `created_at` | TEXT | Registration timestamp |
| `updated_at` | TEXT | Last update timestamp |

## Default User Fields

| Field | Default | Description |
|-------|---------|-------------|
| `email` | Required | Must be unique and valid format |
| `password` | Required | At least 8 characters |
| `username` | Optional | If provided, must be unique |
| `role` | "user" | User role for access control |
| `is_verified` | false | Email not verified by default |
| `is_active` | true | Account is active |

## User Roles

Zork uses a simple role system for access control:

| Role | Description |
|------|-------------|
| `user` | Default role for regular users |
| `admin` | Full access to admin-protected resources |
| Custom | You can set any role name |

### Checking Roles in Hooks

```python
@posts.on("before_create")
async def check_role(data, ctx):
    if ctx.user.get("role") == "admin":
        # Admin can do anything
        pass
    elif ctx.user.get("role") != "author":
        raise ZorkError(403, "Only authors can create posts")
    return data
```

### Promoting Users to Admin

Use the CLI to grant admin access:

```bash
# Make a user an admin
zork promote alice@example.com

# Make a user a moderator
zork promote bob@example.com --role moderator
```

Or update directly in the database:

```python
await db.execute(
    "UPDATE _users SET role = 'admin' WHERE email = ?",
    ("alice@example.com",)
)
```

## Extending the User Model

Add custom fields to the user model using `extend_user`:

```python
from zork import Auth, TextField, BoolField

auth = Auth(
    allow_registration=True,
    extend_user=[
        TextField("first_name"),
        TextField("last_name"),
        TextField("display_name"),
        BoolField("wants_newsletter", default=False),
    ],
)
```

Now users can include these fields during registration:

```bash
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "alice@example.com",
    "password": "secret123",
    "first_name": "Alice",
    "last_name": "Smith"
  }'
```

### Extended Fields in User Response

The `/api/auth/me` endpoint returns extended fields:

```json
{
  "id": "user-123",
  "email": "alice@example.com",
  "role": "user",
  "is_verified": false,
  "is_active": true,
  "first_name": "Alice",
  "last_name": "Smith",
  "created_at": "2024-01-15T10:30:00Z"
}
```

## Available Field Types for Users

You can use these field types when extending the user model:

```python
from zork import Auth, TextField, IntField, BoolField, DateTimeField

auth = Auth(
    extend_user=[
        TextField("first_name"),
        TextField("last_name"),
        TextField("phone"),
        DateTimeField("date_of_birth"),
        BoolField("is_subscribed"),
    ],
)
```

Note: Avoid adding sensitive fields directly to the user model. Consider storing sensitive data in separate collections with appropriate access controls.

## Reading Users

You can query the `_users` table in hooks or custom code:

```python
from zork.db.connection import Database

db = Database("app.db")
await db.connect()

# Find user by email
user = await db.fetch_one(
    "SELECT * FROM _users WHERE email = ?",
    ("alice@example.com",)
)

# List all users
users = await db.fetch_all("SELECT id, email, role FROM _users")

await db.disconnect()
```

## Updating Users

Update user fields in hooks:

```python
@app.on("app:startup")
async def setup_default_admin(ctx):
    # Check if admin exists
    admin = await db.fetch_one(
        "SELECT id FROM _users WHERE role = 'admin' LIMIT 1"
    )
    
    if not admin:
        # Create admin user
        from zork.auth.passwords import hash_password
        import uuid
        from datetime import datetime, timezone
        
        await db.execute("""
            INSERT INTO _users (id, email, password, is_verified, is_active, role, created_at, updated_at)
            VALUES (?, ?, ?, 1, 1, 'admin', ?, ?)
        """, (
            str(uuid.uuid4()),
            "admin@example.com",
            hash_password("admin_password"),
            datetime.now(timezone.utc).isoformat(),
            datetime.now(timezone.utc).isoformat(),
        ))
```

## User Verification

Users created through registration are unverified by default. See the [Auth Endpoints](/authentication/endpoints) guide for email verification flow.

## Next Steps

- [Auth Endpoints](/authentication/endpoints) — Registration, login, and other endpoints
- [Security](/authentication/security) — Password hashing and security best practices
- [Lifecycle Hooks](/core-concepts/lifecycle-hooks) — Hooks for user events
