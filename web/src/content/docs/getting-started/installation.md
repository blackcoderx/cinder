---
title: Installation
description: Install Zeno and its optional dependencies
sidebar:
  order: 1
---

## Requirements

- Python 3.11 or higher
- pip or [uv](https://docs.astral.sh/uv/)

## Install

```bash
pip install zeno-api
```

With [uv](https://docs.astral.sh/uv/):

```bash
uv add zeno-api
```

This installs the core framework with SQLite support. No extra configuration needed to get started.

## Optional Dependencies

Zeno uses extras for optional features to keep the core installation minimal.

| Extra | Installs | When to use |
|-------|----------|-------------|
| `[postgres]` | asyncpg | PostgreSQL databases |
| `[mysql]` | aiomysql | MySQL / MariaDB databases |
| `[s3]` | boto3 | S3-compatible file storage (AWS, R2, MinIO, etc.) |
| `[email]` | aiosmtplib | SMTP email delivery |
| `[redis]` | redis | Caching, rate limiting, and realtime at scale |

Install extras:

```bash
# Single extra
pip install "zeno-api[postgres]"

# Multiple extras
pip install "zeno-api[postgres,redis,email]"
```

With uv:

```bash
uv add "zeno-api[postgres,redis,email]"
```

## Scaffold a new project

Use the CLI to create a project with a starter layout:

```bash
zeno init myapp
cd myapp
```

This creates `main.py`, `.env`, and `.gitignore` with sensible defaults.

## Verify the installation

```bash
zeno --version
```

You should see the Zeno version printed. If you see a "command not found" error, ensure your Python environment's `bin` directory is on your `PATH`.
