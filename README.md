<a href="#"> <img src="https://github.com/user-attachments/assets/9d7ee524-800b-40e7-8d43-c3dd5e855b0b" alt="PX7 logo" title="PX7.FM" align="right" height="90px" /> </a>

# PX7 Terminal Music

![](https://img.shields.io/badge/interface-CLI-black?style=for-the-badge&color=03A907&labelColor=000000) &nbsp; ![](https://img.shields.io/pypi/v/px7-music?style=for-the-badge&color=03A907&labelColor=000000) 

A fast terminal music player that streams YouTube audio through MPV or VLC.  
Search, queue, favorite, and organize music without leaving your terminal.  

**No downloads. No browser tabs. No ads.**

```
>> search radiohead
  1.  Creep — Radiohead
  2.  No Surprises — Radiohead
  3.  Karma Police — Radiohead

>> play 2
  ♪  Now Playing: No Surprises — Radiohead
```

<div align="center">

## Preview

<img src="https://github.com/user-attachments/assets/c574fc12-bca6-4a9d-ac0b-18af8eeec367" alt="PX7-Music(preview)" width="700">

</div>

---

## Features

- Stream audio directly from YouTube — no downloads, no accounts
- Persistent favorites and playlists saved across sessions
- Queue management with shuffle support
- Hands-free jukebox mode with live playback UI
- MPV and VLC backend support

---

## Comparison

| Feature | PX7 | YouTube | Spotify Free |
|----------|-----|---------|--------------|
| Terminal native | ✅ | ❌ | ❌ |
| No login | ✅ | ✅ | ❌ |
| Playlists | ✅ | ❌ | ✅ |
| Favorites | ✅ | ❌ | ✅ |
| No ads | ✅ | Depends | ❌ |

---

## Requirements

- **Python 3.10+**
- **MPV** *(recommended)* or **VLC**

---

## Installation

```
pip install px7-music
```

Then start PX7:

```
px7-music
```

You should see:

```
>>
```

If you see an error about a missing player, see [Player Not Found](#player-not-found) below.

---

## Quick Start

```
>> search joji
>> play 1
>> fav add

>> /s radiohead -> Favorites

>> jukebox
```

Search, play, save, pipe results straight into a playlist, and listen hands-free.

---

## How Results Work

PX7 always has an **active result list**.

Commands that produce a list — `search`, `favs`, `queue`, `pl show`, `pl load` — replace the active results. `play <index>` always acts on the current active results.

```
>> search the weeknd       # active results = search results
>> play 3                  # plays result #3

>> favs                    # active results = your favorites
>> play 1                  # plays favorite #1

>> pl load Chill Mix       # active results = playlist tracks
>> shuffle
>> play 1
```

This is why `load` works after any of these — it reloads whatever the active results are into the queue.

---

## Usage

```
command [arguments] [--flags]
```

### Search & Play

| Command | Args | Description |
|---------|------|-------------|
| `search` / `/s` | `<query>` | Search YouTube and fill the results |
| `play` | `[index]` | Play a track from the results and load them into the queue |

> `play` with no argument defaults to `play 1`.

**Flags:**

| Flag | Default | Description |
|------|---------|-------------|
| `--limit=<n>` | `DEFAULT_SEARCH_LIMIT` | Number of results to fetch |
| `--no-postfix` | off | Disable the auto-appended query postfix (see `config`) |
| `--p` | off | Treat the query as a YouTube playlist URL and fetch its tracks |

<details>
<summary><b>Examples</b></summary>

```
>> search c418
>> /s the weeknd --limit=10
>> /s radiohead --no-postfix
>> /s https://youtube.com/playlist?list=... --p
>> play 2
```

</details>

---

### Playback Controls

| Command | Description |
|---------|-------------|
| `pause` | Pause the current track |
| `resume` | Resume a paused track |
| `next` | Skip to the next track in the queue |
| `prev` | Go back to the previous track |
| `seek` | Show the current playback position |
| `seek <position>` | Jump to a position in the current track |

**Seek formats:** `1:30` &nbsp;·&nbsp; `90` &nbsp;·&nbsp; `+30` &nbsp;·&nbsp; `-10` &nbsp;·&nbsp; `2:04:15`

---

### Queue & Info

| Command | Description |
|---------|-------------|
| `queue [--no-compact]` | List the queue from the current track onward |
| `current` / `now` | Show info about the currently playing track |
| `load` | Replace the queue with the active results and reset playback |
| `shuffle` | Shuffle the queue — current track stays at position 1 |

---

### Favorites

Persist to `~/.px7/.px7_favorites.json`. New favorites appear at the top.

| Command | Args | Description |
|---------|------|-------------|
| `fav add` | | Add the currently playing track |
| `fav add` | `<index>` | Add a specific track from the queue |
| `fav add` | `all` | Add all queued tracks |
| `fav remove` | `<index>` | Remove a favorite by index |
| `fav remove` | `all` | Clear all favorites *(asks for confirmation)* |
| `favs` | | List all saved favorites *(newest first)* |

**Favs flags:**

| Flag | Default | Description |
|------|---------|-------------|
| `--order=<by>` | newest first | `title` · `channel` · `date-added` · `duration` |
| `--limit=<n>` | all | Show only the first N favorites |
| `--reverse` | off | Reverse the sort direction |
| `--no-compact` | off | Show all, bypassing the compact threshold |

<details>
<summary><b>Examples</b></summary>

```
>> fav add
>> fav add 3
>> fav add all
>> fav remove 2
>> favs
>> favs --order=duration --reverse
>> favs --limit=10 --order=date-added
```

</details>

---

### Playlists

Persist to `~/.px7/.px7_playlists.json`. New tracks in a playlist appear at the top.

| Command | Args | Description |
|---------|------|-------------|
| `pl` / `pl list` | | List all playlists |
| `pl create` | `<name>` | Create a new playlist |
| `pl delete` | `<name>` | Delete a playlist *(asks for confirmation)* |
| `pl rename` | `<old> -> <new>` | Rename a playlist |
| `pl add` | `<name>` | Add the currently playing track |
| `pl add` | `<name> <index>` | Add a queue track by index |
| `pl add` | `<name> all` | Add all queued tracks |
| `pl remove` | `<name> <index>` | Remove a track by index |
| `pl show` | `<name>` | Display tracks in a playlist |
| `pl load` | `<name>` | Load a playlist into the queue |
| `pl <name>` | | Shorthand for `pl show <name>` |

**pl show / pl load flags:**

| Flag | Default | Description |
|------|---------|-------------|
| `--order=<by>` | newest first | `title` · `channel` · `date-added` · `duration` |
| `--limit=<n>` | all | Cap the number of tracks shown or loaded |
| `--reverse` | off | Reverse the sort direction |
| `--no-compact` | off | Show all tracks, bypassing the compact threshold *(show only)* |

**Shorthand — name first, subcommand second (defaults to `show`):**

```
>> pl Chill Mix              # → pl show Chill Mix
>> pl Chill Mix load         # → pl load Chill Mix
>> pl Chill Mix add 3        # → pl add  Chill Mix 3
```

<details>
<summary><b>Examples</b></summary>

```
>> pl create Chill Mix
>> pl add Chill Mix
>> pl add Chill Mix 3
>> pl add Chill Mix all
>> pl Chill Mix
>> pl show Chill Mix --order=duration
>> pl load Chill Mix --reverse
>> pl rename Chill Mix -> Late Night
>> pl remove Late Night 2
>> pl delete Late Night
```

</details>

---

### Pipe `->`

Pipe a result list directly into a playlist. The playlist is auto-created if it doesn't exist.

```
<source> [--flags] -> <playlist name>
```

| Source | Description |
|--------|-------------|
| `search` / `/s` | Pipe search results. Accepts all search flags. |
| `favs` | Pipe favorites. Accepts `--order`, `--limit`, `--reverse`. |
| `queue` | Pipe the current queue. |

<details>
<summary><b>Examples</b></summary>

```
>> /s c418 -> Minecraft Vibes
>> /s joji --limit=20 -> Late Night
>> /s https://youtube.com/playlist?list=... --p -> Imports
>> favs --order=duration --limit=10 -> Top 10
>> queue -> Current Session
```

</details>

---

### Jukebox Mode

Hands-free mode that plays through the queue automatically with a live playback UI.

```
>> jukebox
```

> Alias: `/j`

**Keybinds** — no Enter needed, keys are instant:

| Key | Action |
|-----|--------|
| `N` / `>` / `.` | Next track |
| `P` / `<` / `,` | Previous track |
| `SPACE` | Pause / Resume |
| `+` / `=` | Volume up (+10) |
| `-` / `_` | Volume down (−10) |
| `R` | Force refresh display |
| `Q` / `X` | Quit jukebox mode |

---

### Config

Tune persistent settings that survive across sessions.

| Command | Description |
|---------|-------------|
| `config` | Show all settings |
| `config <key>` | Show the current value of a setting |
| `config <key> <value>` | Set and persist a setting |
| `config <key> *` | Reset a single setting to its default |
| `config reset` | Reset all settings to defaults |

**Tunable keys:**

| Key | Type | Description |
|-----|------|-------------|
| `DEFAULT_SEARCH_LIMIT` | int | Results returned per search *(default: 6)* |
| `DEFAULT_QUERY_POSTFIX` | str | Appended to every query *(default: `"song"`)* |
| `COMPACT_THRESHOLD` | int | Max rows before lists are truncated *(default: 8)* |
| `THEME_COLOR` | str | Color mapped to `ANSI.GREEN` and used as the primary UI accent *(default: `"green"`)* |

```
>> config DEFAULT_SEARCH_LIMIT 10
>> config DEFAULT_SEARCH_LIMIT *    # reset to default
>> config reset                     # reset everything
```

---

### Volume

```
>> volume        # show current volume
>> volume 70     # set volume to 70
```

---

### Utility

| Command | Description |
|---------|-------------|
| `latency` | Check network latency |
| `clear` / `cls` | Clear the screen and redraw the banner |
| `help` | Show the in-app help screen |
| `exit` | Quit PX7 Music |

---

## Player Not Found

PX7 requires MPV or VLC installed on your system, plus its Python bindings.

**Install the Python bindings:**
```
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

> MPV is recommended. Ensure the player binary is available in your system PATH.

---

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

```
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
| `yt-dlp` | YouTube search and stream URL extraction |
| `python-mpv` | MPV player bindings *(optional)* |
| `python-vlc` | VLC player bindings *(optional)* |

> At least one of `python-mpv` or `python-vlc` must be installed, with its corresponding player binary present on the system.

</details>

---

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for the full version history.

## License

MIT — do whatever you want, just don't remove the header.