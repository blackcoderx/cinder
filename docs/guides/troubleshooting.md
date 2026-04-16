# Troubleshooting

This guide covers common issues and their solutions when using Zork.

## Installation Issues

### "Command not found" after installation

Make sure your Python environment is on your PATH:

```bash
# Check Python path
python -c "import sys; print(sys.executable)"

# Reinstall Zork
pip uninstall zork
pip install zork
```

### "Module not found" errors

Install the required extras:

```bash
# For PostgreSQL support
pip install "zork[postgres]"

# For Redis support
pip install "zork[redis]"

# For file storage
pip install "zork[s3]"

# For email
pip install "zork[email]"
```

## Authentication Issues

### "Invalid token" errors

1. Check that `ZORK_SECRET` is set and consistent:
   ```bash
   echo $ZORK_SECRET
   ```

2. If using cookie delivery, ensure `cookie_secure=True` is set when using HTTPS

3. Token may have expired - try logging in again

### "Authentication required" on public endpoints

If you have `auth=["read:public"]` but still need auth, check:

1. The auth object is registered:
   ```python
   auth = Auth(allow_registration=True)
   app.use_auth(auth)
   ```

2. You're not accidentally requiring auth on the collection

### Registration disabled

If registration is not working:

```python
auth = Auth(allow_registration=True)  # Must be True
app.use_auth(auth)
```

## Database Issues

### "Table not found" errors

Zork should create tables automatically. If not:

1. Start the server - tables are created on startup
2. Check the server logs for errors
3. Manually run:
   ```bash
   zork serve main.py
   ```

### "UNIQUE constraint failed"

A record with that value already exists. Either:

1. Use a different value
2. Update the existing record
3. Remove the `unique=True` constraint if not needed

### SQLite file issues

If using SQLite:

1. Check the file path exists
2. Ensure write permissions
3. Use an absolute path:
   ```python
   app = Zork(database="/absolute/path/to/app.db")
   ```

## File Upload Issues

### "No storage backend configured"

Configure storage before using FileField:

```python
from zork.storage import LocalFileBackend

app.configure_storage(LocalFileBackend("./uploads"))
```

### Upload fails silently

1. Check file size is under `max_size`
2. Verify file type is in `allowed_types`
3. Check storage backend is configured
4. Ensure upload directory exists and is writable

## Realtime Issues

### WebSocket connection refused

1. Check the server is running
2. Verify the WebSocket URL:
   ```javascript
   const ws = new WebSocket("ws://localhost:8000/api/realtime");
   ```

### Events not received

1. Ensure you're subscribed to the correct channels
2. Check the collection has realtime enabled
3. Verify authentication if required

## Rate Limiting

### "Rate limit exceeded" errors

1. Wait for the window to reset
2. Check the `Retry-After` header
3. Adjust limits in configuration:
   ```python
   app.rate_limit.rule("/api/posts", limit=100, window=60)
   ```

### Rate limiting not working

Ensure rate limiting is enabled:

```python
app.rate_limit.enable(True)
```

## CORS Issues

### "CORS policy" errors in browser

Zork allows all origins by default. If you need restrictions:

1. For development, ensure you're using the correct origin
2. For production, configure specific allowed origins

## Hook Issues

### Hook not running

1. Check hook is registered:
   ```python
   @posts.on("before_create")
   async def my_hook(data, ctx):
       return data
   ```

2. Ensure the collection is registered:
   ```python
   app.register(posts)  # Hooks work after registration
   ```

### "ZorkError not defined"

Import the error class:

```python
from zork.errors import ZorkError
```

## Server Issues

### Server won't start

1. Check for syntax errors in your code
2. Verify the port is not in use:
   ```bash
   # Linux/Mac
   lsof -i :8000
   
   # Windows
   netstat -ano | findstr :8000
   ```

3. Check the error message in the console

### Auto-reload not working

Use the reload flag:

```bash
zork serve main.py --reload
```

## Debugging Tips

### Enable Logging

Add logging to your app:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Check Server Info

Use the info command:

```bash
zork info --app main.py
```

### Verify Routes

List all routes:

```bash
zork routes --app main.py
```

### Check Connectivity

Use the doctor command:

```bash
zork doctor --app main.py
```

## Getting Help

If you need more help:

1. Check the [GitHub Issues](https://github.com/blackcoderx/zork/issues)
2. Review existing documentation
3. Enable debug logging and check server output

## Common Error Messages

| Error | Cause | Solution |
|-------|-------|----------|
| "No Zork instance found" | App not found in file | Ensure `app = Zork()` in your file |
| "Authentication required" | Missing/invalid token | Include `Authorization: Bearer TOKEN` header |
| "Record not found" | Invalid ID | Verify the record ID exists |
| "Field 'x' is required" | Missing required field | Include the field in your request |
| "No storage backend configured" | Storage not set up | Call `app.configure_storage(...)` |
