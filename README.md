<div align="center">

# yubal

**YouTube Music album & playlist downloader with automatic metadata tagging.**
<br/>
_No accounts required._

[![CI Status](https://github.com/guillevc/yubal/actions/workflows/ci.yaml/badge.svg)](https://github.com/guillevc/yubal/actions/workflows/ci.yaml)
[![GitHub Release](https://img.shields.io/github/v/release/guillevc/yubal)](https://github.com/guillevc/yubal/releases)
[![Docker Image](https://img.shields.io/badge/ghcr.io-blue?logo=docker&logoColor=white)](https://ghcr.io/guillevc/yubal)
[![Ko-fi](https://img.shields.io/badge/Ko--fi-F16061?logo=ko-fi&logoColor=white)](https://ko-fi.com/guillevc)

<picture>
  <img src="docs/demo.gif" alt="Yubal Demo Interface" width="600">
</picture>

<sub>_GIF is at 3x speed_</sub>

</div>

## 📖 Overview

**yubal** is a self-hosted app for building a local music library. Paste a YouTube Music album or playlist URL, and yubal handles downloading, tagging, and album art — automatically.

### The Pipeline

```
                    ┌─────────────────┐
                    │  YouTube Music  │
                    │   (ytmusicapi)  │
                    └────────┬────────┘
                             │ metadata
                             ▼
                    ┌──────────────────┐
YouTube Music ─────►│       yubal      │──────► /Artist/Year - Album
 Album/Playlist     │                  │        ├─01 - Track.opus
     URLs           │ (yt-dlp + FFmpeg)│        ├─02 - Track.opus
                    └──────────────────┘        ├─...
                                                └─cover.jpg
```

- **[yt-dlp](https://github.com/yt-dlp/yt-dlp):** Downloads highest available quality audio streams from YouTube.
- **[ytmusicapi](https://github.com/sigma67/ytmusicapi):** Extracts rich metadata directly from YouTube Music (album info, track details, artwork).

## ✨ Features

- **Web Interface:** Clean, responsive UI for submitting albums/playlists and monitoring real-time progress
- **Album & Playlist Support:** Download entire albums or playlists with a single URL
- **Job Queue:** Integrated FIFO queue that processes downloads sequentially to ensure reliability and avoid rate limiting
- **Smart Auto-tagging:** Automatic metadata extraction from YouTube Music with fuzzy track matching for accurate tracklists and embedded artwork
- **Format Configuration:** Optimized for `opus` (native YouTube quality), with optional transcoding to `mp3` or `m4a`
- **M3U Playlists:** Automatically generates M3U playlist files for downloaded playlists
- **Docker-ready:** Multi-arch support (amd64/arm64) for easy deployment

## 🚀 Quick Start

The recommended way to run **yubal** is via Docker Compose.

### 1. Create a `compose.yaml`

```yaml
services:
  yubal:
    image: ghcr.io/guillevc/yubal:latest
    container_name: yubal
    ports:
      - 8000:8000
    environment:
      YUBAL_TZ: UTC
      # See Configuration section for all options
    volumes:
      - ./library:/app/library # Music library output
      - ./config:/app/config   # Config (cookies at ytdlp/cookies.txt)
    restart: unless-stopped
```

### 2. Run the container

```bash
docker compose up -d
```

### 3. Start Downloading

Open your browser to `http://localhost:8000` and paste a YouTube Music album or playlist URL.

## 🍪 Cookies (Optional)

To download age-restricted content, access private playlists, or get higher bitrate audio (Premium accounts):

1. Export your cookies using a browser extension. [See yt-dlp FAQ](https://github.com/yt-dlp/yt-dlp/wiki/FAQ#how-do-i-pass-cookies-to-yt-dlp)
2. Save the file as `cookies.txt`
3. Place it at `config/ytdlp/cookies.txt` (or upload via the Web UI)

> [!CAUTION]
> **Cookie usage can backfire.** Authenticated requests may trigger stricter rate limiting from YouTube.
>
> Using cookies may also put your YouTube account at risk. Use at your own discretion.
>
> More info: [#3](https://github.com/guillevc/yubal/issues/3) · [yt-dlp wiki](https://github.com/yt-dlp/yt-dlp/wiki/Extractors#youtube)

## ⚙️ Configuration

yubal is configured via Environment Variables.

| Variable              | Description                                    | Default (Docker)  |
| --------------------- | ---------------------------------------------- | ----------------- |
| `YUBAL_HOST`          | Server bind address                            | `0.0.0.0`         |
| `YUBAL_PORT`          | Server listening port                          | `8000`            |
| `YUBAL_LIBRARY`       | Music library output                           | `/app/library`    |
| `YUBAL_CONFIG`        | Config directory (cookies at `ytdlp/cookies.txt`) | `/app/config`  |
| `YUBAL_AUDIO_FORMAT`  | Audio codec: `opus`, `mp3`, `m4a`              | `opus`            |
| `YUBAL_AUDIO_QUALITY` | Transcoding quality (0=best, 10=worst)         | `0`               |
| `YUBAL_TZ`            | Timezone (IANA format)                         | `UTC`             |
| `YUBAL_DEBUG`         | Enable debug mode                              | `false`           |
| `YUBAL_LOG_LEVEL`     | Log level: `DEBUG`, `INFO`, `WARNING`, `ERROR` | `INFO`            |
| `YUBAL_CORS_ORIGINS`  | Allowed CORS origins                           | `["*"]`           |
| `YUBAL_RELOAD`        | Auto-reload on code changes (dev only)         | `false`           |
| `YUBAL_TEMP`          | Temp directory for downloads                   | System temp       |

> [!NOTE]
> **Audio Transcoding**
> 
> By default, yubal keeps the original `opus` stream from YouTube to maintain maximum quality and processing speed. Transcoding only occurs if you change `YUBAL_AUDIO_FORMAT` or if the source is not natively available in your chosen format.

## 🗺️ Roadmap

- [x] Cookies upload via Web UI
- [x] Docker multi-arch support (amd64/arm64)
- [x] Configurable audio format and quality
- [x] Playlist support (download full playlists with M3U generation)
- [ ] Browser extension
- [ ] Batch import (multiple URLs at once)
- [ ] Post-import webhook (trigger library scan on Gonic/Navidrome/Jellyfin)
- [ ] PWA support for mobile
- [ ] (maybe) Browse YouTube Music albums in the web app

Have a feature request? [Open an issue](https://github.com/guillevc/yubal/issues)!

## 💜 Support

If yubal is useful to you, consider supporting its development:

[![ko-fi](https://ko-fi.com/img/githubbutton_sm.svg)](https://ko-fi.com/guillevc)

## 🤝 Acknowledgments

- **Color Scheme:** [Flexoki](https://stephango.com/flexoki) by Steph Ango.
- **Core Tools:** This project would not be possible without [yt-dlp](https://github.com/yt-dlp/yt-dlp) and [ytmusicapi](https://github.com/sigma67/ytmusicapi).

## 📄 License

[MIT](LICENSE)

---

<sub>This software is for personal archiving only. Users must comply with YouTube's Terms of Service and applicable copyright laws.</sub>
