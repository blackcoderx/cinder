---
title: CLI Commands
description: All Zeno CLI commands and their options
---

The `zeno` CLI is installed alongside the framework and provides commands for running your app, managing migrations, and inspecting the application.

## `zeno serve`

Start the development server.

```bash
zeno serve main.py
zeno serve main.py --reload
zeno serve main.py --host 0.0.0.0 --port 8080
```

| Option | Default | Description |
|--------|---------|-------------|
| `APP_PATH` | — | Path to the Python file containing the `Zeno` instance |
| `--reload` | `false` | Enable auto-reload on file changes (development only) |
| `--host` | `0.0.0.0` | Host to bind to |
| `--port` | `8000` | Port to listen on |

---

## `zeno init`

Scaffold a new Zeno project.

```bash
zeno init myapp
```

Creates a `myapp/` directory with:
- `main.py` — starter app with a `posts` collection and auth
- `.env` — environment file template
- `.gitignore` — ignores `*.db`, `.env`, and `__pycache__`

---

## `zeno promote`

Promote a user to a new role.

```bash
zeno promote alice@example.com
zeno promote alice@example.com --role moderator
zeno promote alice@example.com --database prod.db
```

| Option | Default | Description |
|--------|---------|-------------|
| `EMAIL` | — | Email address of the user to promote |
| `--role` | `admin` | Role to assign |
| `--database` | `app.db` | Path to the SQLite database file |

---

## `zeno generate-secret`

Generate a cryptographically secure secret key for `ZENO_SECRET`.

```bash
zeno generate-secret
# Output: a3f8b2c1d4e5...
```

Copy the output into your `.env` file.

---

## `zeno doctor`

Check connectivity to configured services.

```bash
zeno doctor
zeno doctor --app main.py
zeno doctor --database postgresql://user:pass@localhost/mydb
```

Checks:
- Database connection
- Redis connection (if `ZENO_REDIS_URL` is set)

---

## `zeno routes`

List all registered routes for your app.

```bash
zeno routes --app main.py
```

Output:

```
Method               Path                                               Name
---------------------------------------------------------------------------
GET                  /                                                  index
GET                  /api/health                                        health
GET                  /api/posts                                         posts_list
POST                 /api/posts                                         posts_create
GET                  /api/posts/{id}                                    posts_get
PATCH                /api/posts/{id}                                    posts_update
DELETE               /api/posts/{id}                                    posts_delete
...
```

---

## `zeno info`

Show a summary of the application configuration.

```bash
zeno info --app main.py
```

Output:

```
Title:            My API
Version:          1.0.0
Python version:   3.12.0
Zeno version:   0.1.0
Database:         app.db
Collections (2):  posts, comments
Auth:             enabled
Storage:          LocalFileBackend
Realtime broker:  RealtimeBroker
```

---

## `zeno deploy`

Generate deployment configuration files for your app. See [Deployment](/deployment/) for full documentation.

```bash
zeno deploy --platform docker
zeno deploy --platform railway --app main.py
zeno deploy --platform render --dry-run
zeno deploy --platform fly --force
zeno deploy  # auto-detects platform from environment
```

| Option | Default | Description |
|--------|---------|-------------|
| `--platform`, `-p` | auto-detect | Target platform: `docker`, `railway`, `render`, `fly` |
| `--app` | `main.py` | Path to the file containing the `Zeno` instance |
| `--dry-run` | `false` | Print generated files without writing them |
| `--force` | `false` | Overwrite existing files without prompting |

Platform auto-detection reads `RAILWAY_ENVIRONMENT`, `RENDER`, and `FLY_APP_NAME` from the environment. Defaults to `docker` if none are set.

---

## `zeno migrate`

Apply pending migrations. See [Migrations](/migrations/commands/) for full documentation.

```bash
zeno migrate
zeno migrate --app main.py
zeno migrate --dir custom/migrations
```

### Sub-commands

| Command | Description |
|---------|-------------|
| `zeno migrate run` | Apply all pending migrations (same as `zeno migrate`) |
| `zeno migrate status` | Show the status of all migrations |
| `zeno migrate create <name>` | Create a new blank migration file |
| `zeno migrate create <name> --auto` | Auto-generate migration from schema diff |
| `zeno migrate rollback` | Roll back the last applied migration |
