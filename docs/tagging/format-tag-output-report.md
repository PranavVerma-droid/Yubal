# Multi-Artist Tag Output Report

This report documents the actual tag output from yubal for each supported audio format, verifying the dual-tag strategy for Jellyfin + Navidrome compatibility.

## Test Track

- **Title**: Dora Black, Vol.1
- **Artists**: Pimp Flaco, Kinder Malo (multiple artists)
- **Album**: Dora Black, Vol.1
- **Album Artists**: Pimp Flaco, Kinder Malo
- **Year**: 2024
- **Track**: 1/1

## Strategy Summary

| Tag Type | Purpose | Value Written |
|----------|---------|---------------|
| ARTIST (singular) | Jellyfin parsing, display | `"Pimp Flaco / Kinder Malo"` |
| ARTISTS (plural) | Navidrome multi-value | `["Pimp Flaco", "Kinder Malo"]` |
| ALBUMARTIST (singular) | Jellyfin parsing, display | `"Pimp Flaco / Kinder Malo"` |
| ALBUMARTISTS (plural) | Navidrome multi-value | `["Pimp Flaco", "Kinder Malo"]` |

---

## Opus (Vorbis Comments)

Vorbis comments natively support multiple values per tag name.

```
ARTIST              : ['Pimp Flaco / Kinder Malo']      # Single joined string
ARTISTS             : ['Pimp Flaco', 'Kinder Malo']     # Multi-value (2 entries)
ALBUMARTIST         : ['Pimp Flaco / Kinder Malo']      # Single joined string
ALBUMARTISTS        : ['Pimp Flaco', 'Kinder Malo']     # Multi-value (2 entries)
ALBUM               : ['Dora Black, Vol.1']
TITLE               : ['Dora Black, Vol.1']
DATE                : ['2024']
TRACK               : ['1']
TRACKTOTAL          : ['1']
```

### Verification

- **ARTIST**: Single string with ` / ` delimiter for Jellyfin
- **ARTISTS**: Two separate Vorbis comment entries for Navidrome
- **Cover art**: Embedded as METADATA_BLOCK_PICTURE

---

## MP3 (ID3v2.4)

ID3v2 uses specific frame IDs. Multi-value tags use TXXX (user-defined) frames.

```
TPE1                : ['Pimp Flaco / Kinder Malo']      # Artist (joined)
TPE2                : ['Pimp Flaco / Kinder Malo']      # Album Artist (joined)
TXXX:ARTISTS        : ['Pimp Flaco', 'Kinder Malo']     # Multi-value
TXXX:ALBUMARTISTS   : ['Pimp Flaco', 'Kinder Malo']     # Multi-value
TXXX:ALBUM_ARTISTS  : ['Pimp Flaco', 'Kinder Malo']     # Multi-value (alias)
TALB                : ['Dora Black, Vol.1']             # Album
TIT2                : ['Dora Black, Vol.1']             # Title
TDRC                : ['2024']                          # Recording date
TRCK                : ['1/1']                           # Track number
```

### Frame ID Reference

| Frame | Description |
|-------|-------------|
| TPE1 | Lead performer/artist |
| TPE2 | Band/orchestra/accompaniment (album artist) |
| TXXX | User-defined text frame |
| TALB | Album title |
| TIT2 | Track title |
| TDRC | Recording time |
| TRCK | Track number |

### Verification

- **TPE1**: Single string with ` / ` delimiter for Jellyfin
- **TXXX:ARTISTS**: Multi-value TXXX frame for Navidrome
- **Cover art**: Embedded as APIC frame

---

## M4A (MP4/iTunes Atoms)

M4A uses iTunes-style atoms. Custom tags use freeform `----:com.apple.iTunes:` atoms.

```
©ART                : ['Pimp Flaco / Kinder Malo']      # Artist (joined)
aART                : ['Pimp Flaco / Kinder Malo']      # Album Artist (joined)
----:com.apple.iTunes:ARTISTS      : [b'Pimp Flaco', b'Kinder Malo']  # Multi-value
----:com.apple.iTunes:ALBUMARTISTS : [b'Pimp Flaco', b'Kinder Malo']  # Multi-value
----:com.apple.iTunes:ALBUM_ARTISTS: [b'Pimp Flaco', b'Kinder Malo']  # Multi-value (alias)
©alb                : ['Dora Black, Vol.1']             # Album
©nam                : ['Dora Black, Vol.1']             # Title
©day                : ['2024']                          # Year
trkn                : [(1, 1)]                          # Track number (track, total)
```

### Atom Reference

| Atom | Description |
|------|-------------|
| ©ART | Artist |
| aART | Album artist |
| ©alb | Album |
| ©nam | Track name |
| ©day | Year |
| trkn | Track number tuple |
| ---- | Freeform/custom atom |

### Verification

- **©ART**: Single string with ` / ` delimiter for Jellyfin
- **----:com.apple.iTunes:ARTISTS**: Multi-value freeform atoms for Navidrome
- **Cover art**: Embedded as `covr` atom

---

## Server Compatibility Matrix

| Server | Reads ARTIST | Parses ` / ` | Reads ARTISTS | Result |
|--------|--------------|--------------|---------------|--------|
| **Jellyfin** | ✅ | ✅ | ✅ (with setting) | Both artists linked |
| **Navidrome** | ✅ | ✅ | ✅ (preferred) | Both artists linked |
| **Plex** | ✅ | ❌ | ❌ | Single combined artist |

## Conclusion

The dual-tag strategy successfully writes:

1. **Delimiter-joined strings** in standard artist tags for Jellyfin compatibility
2. **Multi-value tags** in format-appropriate locations for Navidrome compatibility

All three formats (Opus, MP3, M4A) correctly implement this strategy using the mediafile library.
