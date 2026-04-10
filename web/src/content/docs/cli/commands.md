---
title: Commands
description: Cinder CLI command reference
---

The `cinder` command provides various tools for managing your application.

## serve

Start the application server:

```bash
cinder serve main.py
cinder serve main.py --host 127.0.0.1 --port 3000
cinder serve main.py --reload   # Auto-reload on file changes
```

| Option | Default | Description |
|--------|---------|-------------|
| `--host` | `0.0.0.0` | Host to bind to |
| `--port` | `8000` | Port to bind to |
| `--reload` | `False` | Enable auto-reload for development |

## init

Scaffold a new project:

```bash
cinder init myproject
cd myproject
cinder serve main.py
```

Generated project structure:
```
myproject/
  main.py      # Starter app with posts collection + auth
  .env         # CINDER_SECRET placeholder
  .gitignore   # Ignores .db, .env, __pycache__, .venv
```

## promote

Promote a user to a new role:

```bash
cinder promote user@example.com --role admin
cinder promote user@example.com --role moderator --database myapp.db
```

| Option | Default | Description |
|--------|---------|-------------|
| `--role` | `admin` | Role to assign |
| `--database` | `app.db` | Path to the SQLite database |

## generate-secret

Print a cryptographically secure random secret:

```bash
cinder generate-secret
# e.g. a3f9d2c1b4e8f7a6d5c3b2e1f0a9d8c7b6e5f4a3d2c1b0e9f8a7d6c5b4e3f2a1
```

## doctor

Check connectivity for your database and Redis:

```bash
cinder doctor --app main.py
cinder doctor --database postgresql://user:pass@host/db
```

| Option | Description |
|--------|-------------|
| `--app APP` | Load DB URL from the Cinder app |
| `--database URL` | Database URL to test directly |

Exits with code 1 if any check fails.

## routes

Print every registered route:

```bash
cinder routes --app main.py
```

Output:
```
METHOD   PATH                        NAME
GET      /api/posts                  list_posts
POST     /api/posts                  create_posts
GET      /api/posts/{id}             get_posts
...
GET      /docs                       swagger_ui
GET      /openapi.json               openapi
```

## info

Print app metadata without starting the server:

```bash
cinder info --app main.py
```

Output:
```
Title:      My App
Version:    1.0.0
Python:     3.13.0
Cinder:     0.1.0
Database:   postgresql://***:***@host/mydb
Collections (3): posts, comments, users
Auth:       enabled
Storage:    S3CompatibleBackend
Broker:     RealtimeBroker
```

## migrate

Apply pending migration files. See [Migrations](/migrations/commands/) for full guide.

```bash
cinder migrate --app main.py           # apply pending
cinder migrate status --app main.py   # show history
cinder migrate rollback --app main.py # undo last
cinder migrate create add_index_posts --app main.py          # blank template
cinder migrate create add_missing_cols --app main.py --auto  # auto-generate
```

## Next Steps

- [Migrations](/migrations/overview/) — Schema version control
- [Configuration](/configuration/env-variables/) — Environment variables