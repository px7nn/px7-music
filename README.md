<img align="left" src="https://github.com/user-attachments/assets/392ef3a2-86e0-4150-92e1-abecef2d8739" width="333px">

<div id="toc">
  <ul style="list-style: none">
    <summary>
      <h1>PX7 Music</h1>
    </summary>
  </ul>
</div>

**A fast terminal music player that streams YouTube audio through MPV or VLC.**  
  
*Search, queue, favorite, and organize music without leaving your terminal.*  
*No downloads. No browser tabs. No ads.*

```shell
>> search radiohead
  1.  Creep — Radiohead
  2.  No Surprises — Radiohead
  3.  Karma Police — Radiohead

>> play 2
  ♪  Now Playing: No Surprises — Radiohead
```

---

<br clear="left"/>

<p align="center">
  
<img src="https://img.shields.io/badge/python-%3E%3D3.10-22b836?style=for-the-badge&labelColor=000000" height="30px"/>
&nbsp;&nbsp;
<img src="https://img.shields.io/pypi/v/px7-music?style=for-the-badge&color=22b836&labelColor=000000" height="30px"/>
&nbsp;&nbsp;
<img src="https://img.shields.io/badge/interface-CLI-black?style=for-the-badge&color=22b836&labelColor=000000" height="30px"/>
&nbsp;&nbsp;
<img src="https://img.shields.io/github/license/px7nn/px7-music?style=for-the-badge&color=22b836&labelColor=000000" height="30px"/>

</p>

<!-- TODO: add a new preview -->

## Features

- Stream audio directly from YouTube — no downloads, no accounts
- Persistent favorites and playlists saved across sessions
- Queue management with shuffle support
- Hands-free jukebox mode with live playback UI
- MPV and VLC backend support

## Requirements

**Python 3.10+** &nbsp; *•* &nbsp; **MPV** (recommended) or **VLC**

## Installation

```shell
pip install px7-music
px7-music           # Launch normally (auto-detects player)

px7-music --mpv     # Force MPV
px7-music --vlc     # Force VLC
px7-music -v        # Show version and exit (or --version)
```

> Player not found? See [Player Not Found](#player-not-found).

## Quick Start

```shell
>> /s <song/artist to search>   # Queries YT to return a list of songs
>> play 2                       # Plays the #2 result
>> fav add                      # Adds the currently playing song to favs

>> /s radiohead -> My_Playlist  # Creates/prepends the results to My_Playlist

>> /j                           # /j or jukebox enables jukebox mode
```

## Usage

To keep the main page clean, detailed command documentation has been moved to [docs/USAGE.md](./docs/USAGE.md).

## Player Not Found

PX7 requires MPV or VLC installed on your system, plus their Python bindings.

**Install the Python bindings:**

```shell
pip install python-mpv
pip install python-vlc
```

**Install the player:**

| OS | MPV | VLC |
|----|-----|-----|
| Windows | `winget install mpv` | `winget install VideoLAN.VLC` |
| macOS | `brew install mpv` | `brew install --cask vlc` |
| Ubuntu/Debian | `sudo apt install mpv` | `sudo apt install vlc` |
| Arch | `sudo pacman -S mpv` | `sudo pacman -S vlc` |

> **MPV is recommended**. Ensure the player binary and `libmpv` shared library (e.g., `mpv-1.dll`/`mpv-2.dll` on Windows or `libmpv.so` on Linux) are in your system PATH.

## Known Limitations

- Streams directly from YouTube — subject to rate limiting or regional restrictions

---

<details>
<summary><b>How It Works</b></summary>

1. `search` queries YouTube via `yt-dlp` in metadata-only mode — fast, no download
2. Results are stored as the active result list; `play <index>` loads them into the queue and starts streaming
3. `play` fetches the direct audio stream URL and pipes it to MPV or VLC
4. Jukebox mode uses a thread-safe event loop to advance tracks without blocking input
5. Favorites and playlists are saved to `~/.px7/` and persist between sessions

</details>

<details>
<summary><b>Project Structure</b></summary>

```shell
px7_music/
├── config.py               # yt-dlp options, defaults, file paths
├── main.py                 # entry point, command registration, main loop
├── core/
│   ├── handler.py          # command handlers (search, play, volume, fav, pl)
│   ├── jukebox_mode.py     # jukebox UI and input listener thread
│   ├── parser.py           # command parser and flag parser
│   ├── pipe.py             # pipe operator logic
│   ├── latency.py          # network latency check
│   ├── cfg_manager.py      # config persistence and tunable settings
│   ├── seek_handler.py     # seek command parsing and dispatch
│   └── youtube.py          # yt-dlp search and stream URL extraction
├── library/
│   ├── favorites.py        # favorites persistence (load, save, add, remove)
│   └── playlists.py        # playlists persistence (create, delete, rename, add, remove)
├── player/
│   ├── player_base.py      # abstract Player interface
│   ├── player.py           # MPV and VLC backend implementations
│   └── playback.py         # queue state, playback control, jukebox events
└── utility/
    ├── docs.py             # help text and installation guide
    └── utils.py            # ANSI codes, spinner, banner builder, screen utilities
```

</details>

<details>
<summary><b>Dependencies</b></summary>

| Package | Purpose |
|---------|---------|
| `yt-dlp` | YouTube search and stream extraction |
| `python-mpv` | MPV player bindings *(optional)* |
| `python-vlc` | VLC player bindings *(optional)* |

> At least one of `python-mpv` or `python-vlc` must be installed, with its corresponding player binary present on the system.

</details>

---

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for the full version history.

## License

MIT — do whatever you want, just don't remove the header.