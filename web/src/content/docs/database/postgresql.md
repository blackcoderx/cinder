---
title: PostgreSQL
description: Use PostgreSQL as your database backend
---

PostgreSQL is recommended for production deployments.

## Install the PostgreSQL Extra

```bash
pip install cinder[postgres]
# or
uv add cinder[postgres]
```

## Connection String

```python
app = Cinder(database="postgresql://user:pass@localhost/mydb")
```

## Environment Variable

```bash
export CINDER_DATABASE_URL=postgresql://user:pass@localhost/mydb
```

## Serverless Postgres (NeonDB, Supabase)

```bash
export DATABASE_URL=postgresql://user:pass@ep-xxx.us-east-2.aws.neon.tech/neondb?sslmode=require
```

No code change — just set the environment variable.

## Connection Pool

Cinder creates a connection pool with configurable settings:

| Parameter | Default | Description |
|-----------|---------|-------------|
| `min_size` | `1` | Minimum pool connections |
| `max_size` | `10` | Maximum pool connections |
| `max_inactive_connection_lifetime` | `300` | Seconds before stale connections are removed |

## Environment Variables for Pool

```bash
export CINDER_DB_POOL_MIN=2
export CINDER_DB_POOL_MAX=20
export CINDER_DB_POOL_TIMEOUT=30
export CINDER_DB_CONNECT_TIMEOUT=10
```

## Programmatic Configuration

For full control over pool size, SSL, and timeouts:

```python
from cinder.db.backends.postgresql import PostgreSQLBackend

app.configure_database(
    PostgreSQLBackend(
        url=os.environ["DATABASE_URL"],
        min_size=2,
        max_size=20,
        max_inactive_connection_lifetime=60,
        ssl="require",
    )
)
```

## Example

```python
import os
from cinder import Cinder, Collection, TextField

app = Cinder(database=os.environ["DATABASE_URL"])

posts = Collection("posts", fields=[
    TextField("title", required=True),
])

app.register(posts, auth=["read:public", "write:authenticated"])
app.serve()
```

## Why PostgreSQL?

- **Production-ready** — Battle-tested, scales well
- **JSON support** — Native JSON/JSONB columns
- **Full-text search** — Built-in search capabilities
- **Connections** — Handles concurrent requests

## Next Steps

- [MySQL](/database/mysql/) — Alternative database
- [SQLite](/database/sqlite/) — Development database
- [Indexes](/database/indexes/) — Optimize queries