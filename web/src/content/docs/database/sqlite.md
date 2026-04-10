---
title: SQLite
description: Use SQLite as your database backend
---

SQLite is the zero-config default. No server required.

## Basic Setup

```python
app = Cinder(database="app.db")        # bare path — SQLite
app = Cinder(database="sqlite:///app.db")  # explicit scheme, same thing
```

## Features

- **WAL mode** — Enabled for better concurrent read performance
- **Foreign key enforcement** — Enabled by default
- **Zero configuration** — No server to run

## Environment Variable

```bash
export CINDER_DATABASE_URL=sqlite:///app.db
```

Or use the standard `DATABASE_URL`:

```bash
export DATABASE_URL=sqlite:///app.db
```

## When to Use SQLite

- **Development** — Fastest way to get started
- **Small projects** — Up to ~100K records
- **Single-server deployments** — No multi-server sync needed
- **Prototyping** — Quick iteration

## Limitations

- **Single writer** — Only one write at a time
- **No network access** — File-based, not client/server
- **Smaller scale** — Not ideal for high-traffic production

## Example

```python
from cinder import Cinder, Collection, TextField

app = Cinder(database="app.db")

posts = Collection("posts", fields=[
    TextField("title", required=True),
    TextField("content"),
])

app.register(posts, auth=["read:public", "write:authenticated"])
app.serve()
```

## Next Steps

- [PostgreSQL](/database/postgresql/) — For production scale
- [MySQL](/database/mysql/) — Alternative SQL database
- [Indexes](/database/indexes/) — Optimize queries