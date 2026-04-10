---
title: Auth Hooks
description: React to authentication events with hooks
---

Auth hooks let you execute custom code at specific points during authentication flows.

## Available Hooks

| Hook | Timing | Trigger |
|------|--------|---------|
| `auth:before_register` | Before | New user registration |
| `auth:after_register` | After | Successful registration |
| `auth:before_login` | Before | Login attempt |
| `auth:after_login` | After | Successful login |
| `auth:before_logout` | Before | Logout request |
| `auth:after_logout` | After | Token revoked |
| `auth:before_password_reset` | Before | Password reset requested |
| `auth:after_password_reset` | After | Reset token created |
| `auth:after_verify_email` | After | Email verified |

## Registering Auth Hooks

### Method 1: Decorator (Recommended)

```python
from cinder import Cinder, Auth
from cinder.email import EmailMessage

app = Cinder(database="app.db")
auth = Auth()

@app.on("auth:after_register")
async def welcome_email(user, ctx):
    await app.email.send(EmailMessage(
        to=user["email"],
        subject="Welcome!",
        html_body="<h1>Thanks for signing up!</h1>"
    ))

app.use_auth(auth)
```

### Method 2: Direct Call

```python
async def log_registration(user, ctx):
    print(f"New user: {user['email']}")

auth.on("after_register", log_registration)
```

## Hook Payloads

Each hook receives specific payload data:

### Registration Hooks

```python
@auth.on("auth:before_register")
async def before_register(data, ctx):
    # data: {"email": "...", "password": "...", "username": "..."}
    # Can modify data before user is created
    data["referral_code"] = ctx.extra.get("referral")
    return data

@auth.on("auth:after_register")
async def after_register(user, ctx):
    # user: Complete user object (without password)
    await send_welcome_email(user)
```

### Login Hooks

```python
@auth.on("auth:before_login")
async def before_login(data, ctx):
    # data: {"email": "...", "password": "..."}
    # Can block login by raising CinderError
    if is_account_locked(data["email"]):
        raise CinderError(403, "Account is locked")
    return data

@auth.on("auth:after_login")
async def after_login(user, ctx):
    # user: Complete user object
    await track_login(user)
```

### Logout Hooks

```python
@auth.on("auth:before_logout")
async def before_logout(user, ctx):
    # user: Current user
    await cleanup_session(user)

@auth.on("auth:after_logout")
async def after_logout(user, ctx):
    # user: User who logged out
    await log_activity(user, "logout")
```

### Password Reset Hooks

```python
@auth.on("auth:before_password_reset")
async def before_password_reset(data, ctx):
    # data: {"email": "..."}
    # Can rate limit reset requests
    if too_many_requests(data["email"]):
        raise CinderError(429, "Try again later")
    return data

@auth.on("auth:after_password_reset")
async def after_password_reset(info, ctx):
    # info: {"email": "...", "user_id": "..."}
    await notify_security_team(info["email"])
```

### Email Verification Hook

```python
@auth.on("auth:after_verify_email")
async def after_verify_email(info, ctx):
    # info: {"user_id": "...", "email": "..."}
    await grant_verified_badge(info["user_id"])
```

## The Context Object

All hooks receive a `CinderContext` with additional information:

```python
class CinderContext:
    user: dict | None      # Authenticated user (or None for public routes)
    request_id: str        # Unique request ID for tracing
    collection: str        # Collection name (empty for auth events)
    operation: str         # Operation type
    request: Request       # Starlette Request object
    extra: dict           # Ad-hoc data storage
```

Access in hooks:

```python
@auth.on("auth:after_register")
async def hook(user, ctx):
    print(f"IP: {ctx.request.client.host}")
    print(f"Request ID: {ctx.request_id}")
```

## Common Patterns

### Pattern 1: Welcome Email

```python
from cinder.email import EmailMessage

@auth.on("auth:after_register")
async def send_welcome(user, ctx):
    await app.email.send(EmailMessage(
        to=user["email"],
        subject=f"Welcome to {app.email._app_name}!",
        html_body=f"""
            <h1>Welcome, {user.get('username', 'there')}!</h1>
            <p>Thanks for joining us.</p>
        """
    ))
```

### Pattern 2: Analytics

```python
import analytics  # your analytics library

@auth.on("auth:after_login")
async def track_login(user, ctx):
    analytics.track(user["id"], "Logged In", {
        "ip": ctx.request.client.host,
    })
```

### Pattern 3: Block Login

```python
from cinder.errors import CinderError

@auth.on("auth:before_login")
async def block_suspicious_login(data, ctx):
    # Block login from certain IPs
    client_ip = ctx.request.client.host
    if is_suspicious_ip(client_ip):
        raise CinderError(403, "Login blocked")
    
    # Block login for inactive users (before password check)
    user = await db.fetch_one(
        "SELECT is_active FROM _users WHERE email = ?",
        (data["email"],)
    )
    if user and not user["is_active"]:
        raise CinderError(403, "Account is disabled")
    
    return data
```

### Pattern 4: Force Email Verification

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

### Pattern 5: Custom Registration Fields

```python
@auth.on("auth:before_register")
async def validate_referral(data, ctx):
    referral = ctx.extra.get("referral_code")
    if referral:
        if not is_valid_referral(referral):
            raise CinderError(400, "Invalid referral code")
        data["referred_by"] = referral
    return data
```

### Pattern 6: Cleanup on Logout

```python
@auth.on("auth:before_logout")
async def cleanup_user_session(user, ctx):
    # Remove user-specific cache
    await app.cache.delete(f"session:{user['id']}")
    
    # Close any open resources
    await close_user_connections(user['id'])
```

## Raising Errors in Hooks

Use `CinderError` to abort an operation:

```python
from cinder.errors import CinderError

@auth.on("auth:before_login")
async def check_account_status(data, ctx):
    # Return 403 to block login
    raise CinderError(403, "Account is suspended")
    
    # Return 400 for validation errors
    raise CinderError(400, "Invalid request")
```

## Chaining Multiple Hooks

Register multiple handlers for the same event:

```python
@auth.on("auth:after_register")
async def handler1(user, ctx):
    # Runs first (registration order)
    pass

@auth.on("auth:after_register")
async def handler2(user, ctx):
    # Runs second
    pass
```

## Related

- [Lifecycle Hooks](/core-concepts/lifecycle-hooks/) — Hook system overview
- [Custom Events](/hooks/custom-events/) — Define your own events
- [Email](/email/setup/) — Send emails from hooks
