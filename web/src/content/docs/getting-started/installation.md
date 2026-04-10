---
title: Installation
description: How to install Cinder and its optional extras
---

## Requirements

- Python 3.11+
- pip or uv package manager

## Install

```bash
pip install cinder
```

Or with [uv](https://docs.astral.sh/uv/):

```bash
uv add cinder
```

## Optional Extras

Install only the extras you need:

```bash
# S3-compatible file storage (boto3) — AWS, R2, MinIO, etc.
pip install cinder[s3]

# Email delivery (aiosmtplib)
pip install cinder[email]

# Redis caching & sessions
pip install cinder[redis]

# PostgreSQL support (asyncpg)
pip install cinder[postgres]

# MySQL support (aiomysql)
pip install cinder[mysql]

# All extras
pip install cinder[all]
```

## Verify Installation

Check that Cinder is installed correctly:

```bash
python -c "import cinder; print(cinder.__version__)"
```

Or use the CLI:

```bash
cinder --version
```

## Next Steps

- [Quick Start](/getting-started/quick-start/) — Create your first app
- [Core Concepts](/core-concepts/collections/) — Understand collections and schemas