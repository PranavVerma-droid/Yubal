set dotenv-load

default:
    @just --list

install:
    uv sync
    cd web && bun install

cli *args:
    uv run yubal {{ args }}

dev:
    #!/usr/bin/env bash
    trap 'kill 0' EXIT
    just dev-api & just dev-web & wait

dev-api:
    uv run uvicorn yubal_api.main:app --reload

dev-web:
    cd web && bun run dev

lint:
    uv run ruff check packages

format:
    uv run ruff format packages

test *args:
    uv run pytest {{ args }}

check: lint test
