---
title: Troubleshooting
description: Common authentication issues and solutions
---

Solutions for frequent authentication problems.

## Common Errors

### "Invalid email or password"

This error occurs when:
- Email doesn't exist in the database
- Password doesn't match the hash

**Diagnosis:**

```python
# Check if user exists
user = await db.fetch_one(
    "SELECT * FROM _users WHERE email = ?",
    (email,)
)
print(user)  # None = user doesn't exist
```

**Solutions:**
- Verify the email is correct
- Check for typos (e.g., `gmal.com` vs `gmail.com`)
- Try password reset if you can't remember

### "Token has expired"

Tokens expire based on `token_expiry` setting (default: 24 hours).

**Diagnosis:**

```python
import jwt
from datetime import datetime

token = "your-token-here"
decoded = jwt.decode(token, options={"verify_signature": False})
print(f"Expires: {datetime.fromtimestamp(decoded['exp'])}")
```

**Solutions:**
- Call `/api/auth/refresh` to get a new token
- Login again for a fresh token
- Increase `token_expiry` if users complain frequently

### "Account is disabled"

The user's `is_active` field is set to `0`.

**Diagnosis:**

```python
user = await db.fetch_one(
    "SELECT is_active FROM _users WHERE email = ?",
    (email,)
)
print(f"Active: {user['is_active']}")  # 0 = disabled
```

**Solutions:**
- Admin can re-enable via CLI:
  ```bash
  cinder promote user@example.com --role user
  ```
- Or update directly:
  ```python
  await db.execute(
      "UPDATE _users SET is_active = 1 WHERE email = ?",
      (email,)
  )
  ```

## Token Issues

### Tokens Don't Survive Restart

**Cause:** No `CINDER_SECRET` set — Cinder generates a random secret each time.

**Solution:** Set the environment variable:

```bash
# Generate a secret
cinder generate-secret

# Set it (add to .env or environment)
export CINDER_SECRET="your-secret-here"
```

### Tokens Work in One Instance But Not Another

**Cause:** Different secrets across instances.

**Solution:** Ensure all instances use the same `CINDER_SECRET`.

### Logout Doesn't Work (Token Still Valid)

**Cause:** Blocklist not being checked, or using a different secret.

**Solution:**

```python
# Check if token's jti is in blocklist
jti = decode_token(token)["jti"]
blocked = await db.fetch_one(
    "SELECT * FROM _token_blocklist WHERE jti = ?",
    (jti,)
)
print(f"Blocked: {blocked is not None}")
```

## Registration Problems

### Registration Returns 403

**Cause:** `allow_registration=False` in Auth config.

**Solution:**

```python
auth = Auth(allow_registration=True)  # Enable registration
```

### Duplicate Email/Username Error

**Cause:** Email or username already exists.

**Solution:** Use a different email/username, or delete the existing account.

### Extended Fields Not Saving

**Cause:** Field name mismatch or wrong type.

**Solution:** Ensure extended fields match exactly:

```python
# Register with same fields
auth = Auth(extend_user=[
    TextField("display_name"),  # Must match exactly
])

# When registering
{
    "email": "...",
    "password": "...",
    "display_name": "John Doe"  # This field
}
```

## Login Problems

### Login Always Fails

**Checklist:**

1. Is the database accessible?
2. Is the password correct?
3. Is the account active?

```python
# Debug login flow
async def debug_login(email, password):
    from cinder.auth import passwords
    
    user = await db.fetch_one(
        "SELECT * FROM _users WHERE email = ?",
        (email,)
    )
    
    if not user:
        return "User not found"
    
    if not user["is_active"]:
        return "Account disabled"
    
    if not passwords.verify_password(password, user["password"]):
        return "Wrong password"
    
    return "OK"
```

### Token Returns None for User

**Cause:** Auth middleware not running, or token not in request.

**Solution:** Ensure `Authorization: Bearer <token>` header is present:

```python
# In your request
headers = {
    "Authorization": f"Bearer {token}"
}
```

## Debug Mode

### Print Auth Context

```python
@auth.on("auth:before_login")
async def debug_login(data, ctx):
    print(f"Request from: {ctx.request.client.host}")
    print(f"Headers: {dict(ctx.request.headers)}")
    return data
```

### Check Middleware Order

Auth middleware must be before your routes:

```python
# In pipeline.py, middleware order should be:
# 1. ErrorHandler
# 2. RequestID
# 3. CORS
# 4. RateLimit
# 5. Cache
# 6. Auth  ← This one
```

### Verify Token Decoding

```python
from cinder.auth.tokens import decode_token

try:
    payload = decode_token(token, secret)
    print(f"User: {payload['sub']}")
    print(f"Role: {payload['role']}")
except Exception as e:
    print(f"Error: {e}")
```

## Database Issues

### Missing Auth Tables

Tables are created on first `app.build()`:

```python
# This creates auth tables
app = Cinder(database="app.db")
auth = Auth()
app.use_auth(auth)
app.build()  # Tables created here
```

### Database Locked (SQLite)

With multiple workers, SQLite can have locking issues:

```python
# Production: Use PostgreSQL or MySQL
app = Cinder(database="postgresql://user:pass@host/db")

# Development: Add wait time
app = Cinder(database="app.db?timeout=10")
```

## Getting Help

If you're still stuck:

1. Check server logs for error messages
2. Verify environment variables are set correctly
3. Ensure database is accessible and writable
4. Try with a fresh database to rule out schema issues

## Related

- [Setup](/authentication/setup/) — Auth configuration
- [Security](/authentication/security/) — How auth works
- [Endpoints](/authentication/endpoints/) — API reference
