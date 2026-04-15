---
title: PostgreSQL
description: Use PostgreSQL as your production database
---

PostgreSQL is the recommended database for production deployments.

## Install the extra dependency

```bash
pip install "zork-api[postgres]"
# or
uv add "zork-api[postgres]"
```

This installs [asyncpg](https://github.com/MagicStack/asyncpg), the high-performance async PostgreSQL driver.

## Configuration

Set the connection URL via an environment variable:

```dotenv
DATABASE_URL=postgresql://user:password@localhost:5432/mydb
```

Or pass it directly:

```python
app = Zeno(database="postgresql://user:password@localhost:5432/mydb")
```

## Advanced configuration

For fine-grained control over the connection pool:

```python
from zork.db.backends.postgresql import PostgreSQLBackend

app.configure_database(
    PostgreSQLBackend(
        url="postgresql://user:password@localhost:5432/mydb",
        min_size=2,
        max_size=20,
        ssl="require",
    )
)
```

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `url` | `str` | — | Full connection URL |
| `min_size` | `int` | `2` | Minimum pool connections |
| `max_size` | `int` | `10` | Maximum pool connections |
| `ssl` | `str` | `None` | SSL mode: `"disable"`, `"allow"`, `"prefer"`, `"require"`, `"verify-ca"`, `"verify-full"` |

## Connection URL formats

```
postgresql://user:password@host:5432/dbname
postgresql://user:password@host:5432/dbname?sslmode=require
postgres://user:password@host:5432/dbname   # postgres:// is also accepted
```

## Managed PostgreSQL services

Connection URLs from common providers work directly:

- **Supabase:** `postgresql://postgres:[password]@[host]:5432/postgres`
- **Neon:** `postgresql://[user]:[password]@[host]/[dbname]?sslmode=require`
- **Railway:** provided in dashboard
- **Render:** provided in dashboard
- **AWS RDS / Aurora:** standard PostgreSQL URL

## Running migrations

For production, always run migrations before deploying new code:

```bash
zork migrate --app main.py
```

See [Migrations](/migrations/commands/) for details.
