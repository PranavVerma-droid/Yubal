# Build frontend
FROM oven/bun:1-alpine AS web
WORKDIR /app/web
COPY web/package.json web/bun.lock* ./
RUN bun install --frozen-lockfile
COPY web/ ./
RUN bun run build

# Deno binary (for yt-dlp)
FROM denoland/deno:bin AS deno

# Runtime
FROM ghcr.io/astral-sh/uv:python3.12-bookworm-slim

COPY --from=deno /deno /usr/local/bin/deno
RUN apt-get update && apt-get install -y --no-install-recommends ffmpeg \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY pyproject.toml uv.lock README.md ./
RUN uv sync --no-dev --frozen

COPY yubal/ ./yubal/
COPY --from=web /app/web/dist ./web/dist
COPY beets/config.yaml ./beets/config.yaml

ENV YUBAL_HOST=0.0.0.0 \
    YUBAL_PORT=8000 \
    YUBAL_DATA_DIR=/app/data \
    YUBAL_BEETS_DIR=/app/beets

EXPOSE 8000
CMD ["uv", "run", "python", "-m", "yubal"]
