.PHONY: install test

install:
	uv sync

test:
	uv run ytad --help
