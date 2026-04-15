---
title: CLI Commands
description: All Zeno CLI commands and their options
---

The `zork` CLI is installed alongside the framework and provides commands for running your app, managing migrations, and inspecting the application.

## `zork serve`

Start the development server.

```bash
zork serve main.py
zork serve main.py --reload
zork serve main.py --host 0.0.0.0 --port 8080
```

| Option | Default | Description |
|--------|---------|-------------|
| `APP_PATH` | — | Path to the Python file containing the `Zeno` instance |
| `--reload` | `false` | Enable auto-reload on file changes (development only) |
| `--host` | `0.0.0.0` | Host to bind to |
| `--port` | `8000` | Port to listen on |

---

## `zork init`

Scaffold a new Zeno project.

```bash
zork init myapp
```

Creates a `myapp/` directory with:
- `main.py` — starter app with a `posts` collection and auth
- `.env` — environment file template
- `.gitignore` — ignores `*.db`, `.env`, and `__pycache__`

---

## `zork promote`

Promote a user to a new role.

```bash
zork promote alice@example.com
zork promote alice@example.com --role moderator
zork promote alice@example.com --database prod.db
```

| Option | Default | Description |
|--------|---------|-------------|
| `EMAIL` | — | Email address of the user to promote |
| `--role` | `admin` | Role to assign |
| `--database` | `app.db` | Path to the SQLite database file |

---

## `zork generate-secret`

Generate a cryptographically secure secret key for `ZENO_SECRET`.

```bash
zork generate-secret
# Output: a3f8b2c1d4e5...
```

Copy the output into your `.env` file.

---

## `zork doctor`

Check connectivity to configured services.

```bash
zork doctor
zork doctor --app main.py
zork doctor --database postgresql://user:pass@localhost/mydb
```

Checks:
- Database connection
- Redis connection (if `ZENO_REDIS_URL` is set)

---

## `zork routes`

List all registered routes for your app.

```bash
zork routes --app main.py
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

## `zork info`

Show a summary of the application configuration.

```bash
zork info --app main.py
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

## `zork deploy`

Generate deployment configuration files for your app. See [Deployment](/deployment/) for full documentation.

```bash
zork deploy --platform docker
zork deploy --platform railway --app main.py
zork deploy --platform render --dry-run
zork deploy --platform fly --force
zork deploy  # auto-detects platform from environment
```

| Option | Default | Description |
|--------|---------|-------------|
| `--platform`, `-p` | auto-detect | Target platform: `docker`, `railway`, `render`, `fly` |
| `--app` | `main.py` | Path to the file containing the `Zeno` instance |
| `--dry-run` | `false` | Print generated files without writing them |
| `--force` | `false` | Overwrite existing files without prompting |

Platform auto-detection reads `RAILWAY_ENVIRONMENT`, `RENDER`, and `FLY_APP_NAME` from the environment. Defaults to `docker` if none are set.

---

## `zork migrate`

Apply pending migrations. See [Migrations](/migrations/commands/) for full documentation.

```bash
zork migrate
zork migrate --app main.py
zork migrate --dir custom/migrations
```

### Sub-commands

| Command | Description |
|---------|-------------|
| `zork migrate run` | Apply all pending migrations (same as `zork migrate`) |
| `zork migrate status` | Show the status of all migrations |
| `zork migrate create <name>` | Create a new blank migration file |
| `zork migrate create <name> --auto` | Auto-generate migration from schema diff |
| `zork migrate rollback` | Roll back the last applied migration |
