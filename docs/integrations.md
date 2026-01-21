# Media Server Integrations

Compatibility of yubal features with popular media servers.

## Feature Compatibility

| Feature | Navidrome | Jellyfin | Gonic | Plex |
|---------|:---------:|:--------:|:-----:|:----:|
| M3U playlist files | :white_check_mark: | :white_check_mark: | :x: | :x: |
| Multiple artists tagging | :white_check_mark: | :white_check_mark:* | :white_check_mark:* | :x: |
| Multiple album artists tagging | :white_check_mark: | :white_check_mark:* | :white_check_mark:* | :x: |
| Embedded cover art | :white_check_mark: | :white_check_mark: | :white_check_mark: | :white_check_mark: |
| Playlist cover sidecar images | :white_check_mark: | :white_check_mark: | :x: | :x: |
| Opus audio format | :white_check_mark: | :white_check_mark: | :white_check_mark: | :white_check_mark: |
| Folder structure recognition | :white_check_mark: | :white_check_mark: | :white_check_mark: | :white_check_mark: |

\* Requires configuration (see below)

## Multi-Artist Tagging Strategy

yubal writes dual artist tags for maximum compatibility:

| Tag | Format | Purpose |
|-----|--------|---------|
| `ARTIST` | `Artist1 / Artist2` | Display string, delimiter-joined |
| `ARTISTS` | `["Artist1", "Artist2"]` | Native multi-value tag |
| `ALBUMARTIST` | `Artist1 / Artist2` | Display string, delimiter-joined |
| `ALBUMARTISTS` | `["Artist1", "Artist2"]` | Native multi-value tag |

## Server Configuration

### Navidrome

**Works out of the box.** Navidrome reads the native `ARTISTS` multi-value tag by default.

Optional playlist settings:
```bash
ND_AUTOIMPORTPLAYLISTS=true
ND_DEFAULTPLAYLISTPUBLICVISIBILITY=true
```

### Jellyfin

Enable multi-value artist tags in library settings:

1. Go to **Dashboard → Libraries → Music Library → Manage Library**
2. Check **Prefer embedded tags over filenames**
3. Check **Use non-standard artists tags** (reads ARTISTS tag)
4. Save and rescan library

Without this setting, Jellyfin falls back to parsing the delimiter-joined `ARTIST` string, which may not link artists correctly.

### Gonic

Enable native multi-value tag reading:

```bash
GONIC_MULTI_VALUE_ARTIST=multi
GONIC_MULTI_VALUE_ALBUM_ARTIST=multi
```

Alternative: delimiter-based splitting (not recommended):
```bash
GONIC_MULTI_VALUE_ARTIST="delim /"
```

### Plex

Plex does not support multi-value artist tags or custom delimiters. Artists will display as a single combined string (e.g., "Artist1 / Artist2").

## Format-Specific Tag Mapping

| Format | Artist (singular) | Artists (multi-value) |
|--------|-------------------|----------------------|
| **Opus** | `ARTIST` (Vorbis) | `ARTISTS` (multiple Vorbis comments) |
| **MP3** | `TPE1` (ID3v2) | `TXXX:ARTISTS` (user-defined frame) |
| **M4A** | `©ART` (iTunes atom) | `----:com.apple.iTunes:ARTISTS` (freeform) |

All formats store both the delimiter-joined string and the native multi-value list.
