<div align="center">

# yubal

**YouTube albums, downloaded and tagged automatically**

[![ci](https://github.com/guillevc/yubal/actions/workflows/ci.yaml/badge.svg)](https://github.com/guillevc/yubal/actions/workflows/ci.yaml)
[![GitHub Release](https://img.shields.io/github/v/release/guillevc/yubal)](https://github.com/guillevc/yubal/releases)
[![Docker](https://img.shields.io/badge/Docker-GHCR-2496ED?logo=docker&logoColor=white)](https://ghcr.io/guillevc/yubal)
[![License: MIT](https://img.shields.io/badge/License-MIT-purple)](LICENSE)

<picture>
  <img src="docs/demo.gif" alt="Demo" width="700">
</picture>
</div>

## How It Works

Paste a YouTube Music album URL, and _yubal_ handles the rest:

```
                                 ┌──────────┐
                ┌─────────┐      │ Spotify  │
                │ YouTube │      │ metadata │
                └──────▲──┘      └──▲───────┘
                       │            │
                    ┌──────────────────┐
                    │       yubal      │──────► /Artist/Year - Album
YouTube Music ─────►│                  │        ├─01 - Track.opus
  Album URLs        │ (yt-dlp + beets) │        ├─02 - Track.opus
                    └──────────────────┘        ├─...
                                                └─cover.jpg
```

- **[yt-dlp](https://github.com/yt-dlp/yt-dlp)** — Downloads audio from YouTube/YouTube Music
- **[beets](https://beets.io)** — Auto-tags music using Spotify metadata

## Features

- Web UI for submitting albums and monitoring progress
- Sequential job queue — one download at a time, no conflicts
- Auto-tagging via MusicBrainz + Spotify
- Album art fetching and embedding
- Docker-ready with multi-arch support

## Quick Start

```bash
docker run -d \
  --name yubal \
  -p 8000:8000 \
  -v ~/Music:/app/data \
  -v yubal-beets:/app/beets \
  -v yubal-ytdlp:/app/ytdlp \
  ghcr.io/youruser/yubal:latest
```

Open [http://localhost:8000](http://localhost:8000) and paste a YouTube Music album URL.

> **Note:** For age-restricted or private content, add your YouTube cookies to `/app/ytdlp/cookies.txt`

## Configuration

All settings use the `YUBAL_` prefix.

| Variable             | Description             | Default      |
| -------------------- | ----------------------- | ------------ |
| `YUBAL_HOST`         | Server bind address     | `127.0.0.1`  |
| `YUBAL_PORT`         | Server port             | `8000`       |
| `YUBAL_DATA_DIR`     | Music library output    | `/app/data`  |
| `YUBAL_BEETS_DIR`    | Beets config + database | `/app/beets` |
| `YUBAL_YTDLP_DIR`    | yt-dlp config (cookies) | `/app/ytdlp` |
| `YUBAL_AUDIO_FORMAT` | Output format           | `opus`       |
| `YUBAL_TZ`           | Timezone (IANA format)  | `UTC`        |

### Volumes

| Path         | Purpose                               |
| ------------ | ------------------------------------- |
| `/app/data`  | Your music library — mount to persist |
| `/app/beets` | Beets config and database             |
| `/app/ytdlp` | yt-dlp cookies and config             |

### Spotify Metadata (Optional)

For better matching, add Spotify API credentials. Create `/app/beets/secrets.yaml`:

```yaml
spotify:
  client_id: your_client_id
  client_secret: your_client_secret
```

Get credentials at [Spotify Developer Dashboard](https://developer.spotify.com/dashboard).

## Development

### Prerequisites

- Python 3.12+
- [uv](https://docs.astral.sh/uv/) (Python package manager)
- [Bun](https://bun.sh/) (JS runtime)
- ffmpeg

### Setup

```bash
git clone https://github.com/youruser/yubal.git
cd yubal
just install   # Install all dependencies
just dev       # Start API + web dev servers
```

### Commands

| Command       | Description                 |
| ------------- | --------------------------- |
| `just dev`    | Run API and web in dev mode |
| `just check`  | Lint, typecheck, and test   |
| `just format` | Format all code             |
| `just build`  | Build for production        |

## Acknowledgments

- Color scheme: [Flexoki](https://stephango.com/flexoki) by Steph Ango

## Disclaimer

This software is provided for **personal use only**. Users are responsible
for complying with YouTube's Terms of Service and applicable copyright laws
in their jurisdiction.

The authors are not responsible for any misuse of this software.

## License

[MIT](LICENSE)
