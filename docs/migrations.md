# Database Migrations Guide

This guide explains how to modify the database schema and create migrations using Alembic.

## Overview

Yubal uses:
- **SQLModel** for ORM models (extends SQLAlchemy + Pydantic)
- **Alembic** for database migrations
- **SQLite** as the database

Migration files are located in `packages/api/src/yubal_api/migrations/versions/`.

## When to Create a Migration

Create a new migration when you:

1. **Add a new column** to an existing table
2. **Remove a column** from an existing table
3. **Create a new table**
4. **Drop a table**
5. **Add/remove indexes**
6. **Change column constraints** (nullable, unique, etc.)

## Step-by-Step: Adding a New Column

### 1. Update the SQLModel

Edit the model in `packages/api/src/yubal_api/db/`:

```python
# subscription.py
class Subscription(SQLModel, table=True):
    # existing fields...
    new_field: str | None = Field(default=None, max_length=200)
```

### 2. Create the Migration File

Generate a unique revision ID:

```bash
python3 -c "import secrets; print(secrets.token_hex(6))"
```

Create a new file in `packages/api/src/yubal_api/migrations/versions/`:

```python
"""Add new_field to subscriptions

Revision ID: <generated_id>
Revises: <previous_revision_id>
Create Date: <current_date>

"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "<generated_id>"
down_revision: str | Sequence[str] | None = "<previous_revision_id>"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        "subscriptions",
        sa.Column("new_field", sa.VARCHAR(length=200), nullable=True),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column("subscriptions", "new_field")
```

### 3. Update Related Code

Don't forget to update:

- **Response schemas** in `schemas/` (for API responses)
- **Repository methods** if the new field needs special handling
- **TypeScript types** by running `just gen-api`

### 4. Run Checks

```bash
just format
just lint-fix
just check
```

## Migration File Naming

Files follow the pattern: `<revision_id>_<description>.py`

Example: `03132d5514f9_add_subscription_thumbnail_url.py`

## Finding the Previous Revision

Look at existing migration files to find the current head revision. The `down_revision` of your new migration should be the `revision` of the most recent migration.

```bash
ls packages/api/src/yubal_api/migrations/versions/
```

## Common Operations

### Add a Column

```python
def upgrade() -> None:
    op.add_column("table_name", sa.Column("column_name", sa.VARCHAR(100), nullable=True))

def downgrade() -> None:
    op.drop_column("table_name", "column_name")
```

### Add a Non-Nullable Column (with default)

For existing data, add as nullable first, then alter:

```python
def upgrade() -> None:
    op.add_column("table_name", sa.Column("column_name", sa.VARCHAR(100), nullable=True))
    op.execute("UPDATE table_name SET column_name = 'default_value' WHERE column_name IS NULL")
    op.alter_column("table_name", "column_name", nullable=False)

def downgrade() -> None:
    op.drop_column("table_name", "column_name")
```

### Create an Index

```python
def upgrade() -> None:
    op.create_index("ix_table_column", "table_name", ["column_name"], unique=False)

def downgrade() -> None:
    op.drop_index("ix_table_column", table_name="table_name")
```

### Create a Table

```python
def upgrade() -> None:
    op.create_table(
        "new_table",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("name", sa.VARCHAR(length=200), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )

def downgrade() -> None:
    op.drop_table("new_table")
```

## SQLite Limitations

SQLite has limited ALTER TABLE support. These operations require recreating the table:

- Dropping a column (SQLite < 3.35)
- Renaming a column (SQLite < 3.25)
- Changing column type
- Adding a foreign key to existing table

For complex changes, use `op.batch_alter_table()`:

```python
def upgrade() -> None:
    with op.batch_alter_table("table_name") as batch_op:
        batch_op.drop_column("old_column")
        batch_op.add_column(sa.Column("new_column", sa.VARCHAR(100)))
```

## Environment Configuration

Migrations use settings from `yubal_api.settings`:

- Database path is configured via `YUBAL_DB_PATH` environment variable
- Default: `~/.local/share/yubal/yubal.db`

The `migrations/env.py` file handles:
- Loading settings
- Creating the database directory if needed
- Configuring the SQLAlchemy URL

## Applying Migrations

Migrations are applied automatically when the API server starts. The startup code in `packages/api/src/yubal_api/db/engine.py` runs pending migrations.

For manual migration (rarely needed):

```bash
cd packages/api/src/yubal_api
uv run alembic upgrade head
```

## Best Practices

1. **Always test migrations** on a copy of production data
2. **Keep migrations small** - one logical change per migration
3. **Write both upgrade and downgrade** functions
4. **Use nullable columns** when adding to tables with existing data
5. **Run `just check`** before committing to catch issues early
6. **Update TypeScript types** with `just gen-api` after schema changes
