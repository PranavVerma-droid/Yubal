# CLAUDE.md

## Project Overview

yubal is a self-hosted YouTube Music album downloader with automatic metadata tagging. Monorepo with three packages:

- `packages/core` - Python library (yt-dlp, mutagen)
- `packages/api` - FastAPI backend, SQLite/SQLModel
- `packages/web` - React frontend, HeroUI, TailwindCSS, TanStack Router

## Development Rules

### Workflow

- Run `just format` and `just lint-fix` after code changes
- Prompt to run `just check` after major changes
- Use `just gen-api` after modifying API schemas
- No backwards compatibility—break freely, update all dependent code

### Conventions

- Use expert language subagents for specialized tasks
- Use Context7 MCP for external documentation
- Never prompt to commit/push unless explicitly requested

### Database

Refer to @docs/migrations.md for schema changes. Key commands:

- `just db-generate "message"` - Create migration
- `just db-migrate` - Apply migrations
- `just db-reset` - Nuke and recreate

## Common Workflows

```sh
just d          # Dev servers (API + Web)
just c          # Full CI check
just t          # Tests only
just f          # Format all
just gen-api    # Regenerate TS types from OpenAPI
```

## Just Commands

Run `just` to see all available recipes.
