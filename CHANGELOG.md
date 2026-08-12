# Changelog

All notable changes to this project will be documented in this file.

## [1.5.0] - 2026-08-12

### Added
- Keyword filtering support using the `/keyword` format for various listing commands:
  - `favs [/keyword]` matches favorite track titles and channels.
  - `pl list [/keyword]` matches playlist names.
  - `pl show <name> [/keyword]` and `pl load <name> [/keyword]` match track titles and channels in the specified playlist.
- Added `queue add <index|all> [--next]` command to add tracks from the active results list to the playback queue (optionally next in line using `--next`).


## [1.4.1] - 2026-06-18

### Changed
- Theme color validation now uses color-coded output for improved readability.

### Fixed
- Missing YouTube channel/uploader metadata now displays as `---` instead of `None`.
- Fixed a Jukebox mode crash when playing tracks with missing channel metadata.
- Fixed favorites and playlist sorting by channel for tracks with missing channel metadata.


## [1.4.0] - 2026-06-07

### Changed
- Renamed `Autoplay Mode` to `Jukebox Mode`.
  - Commands have also been updated:
    - `/a` → `/j`
    - `autoplay` → `jukebox`
- `COMPACT_THRESHOLD` now affects `queue`.
- Updated and reorganized project documentation.

### Added
- Added command piping using the `->` operator.
  - Results from supported commands can now be piped into a new or existing playlist.
- Added runtime configuration management commands.
  - Configuration values can now be changed and saved directly from the application.
- Added `THEME_COLOR` configuration option.
- `--no-compact` flag for `favs`.
- `--no-compact` flag for `queue`.

### Fixed
- In Jukebox mode, stream fetch failures are handled silently by skipping to the next track until a playable stream is found.
- Standardized color rendering across terminals using truecolor ANSI sequences.
- Suppressed PipeWire warnings under WSL by forcing the MPV backend to use PulseAudio.
- Properly close latency check HTTP connections.


## [1.3.1] - 2026-06-01

### Added
- `--order` now supports sorting by `channel` and `title` in both `favs` and playlists.
  (`name` remains supported as an alias)

### Changed
- Title sanitization now also removes emoji characters.

### Fixed
- Improved error handling when stream URL retrieval fails, now displaying a proper error message instead of failing silently.

## [1.3.0] - 2026-05-31

### Added

- Added `set_runtime_banner(version, os_name, player)` in `utility/utils.py` to initialize the banner used by `clear_screen()`.

### Fixed

- Fixed a `FileNotFoundError` that could occur on a clean installation before the `~/.px7/` directory existed.

### Internal

- Refactored the `auto_play_mode` module:
  - Moved from `px7_music/player/auto_play_mode.py`
  - To `px7_music/core/auto_play_mode.py`
  - Updated imports in `main.py` and `playback.py`
- Removed unused `PLAY_MODE = "sequence"` state from `player/playback.py`.
- Moved the `random` import to module scope in `player/playback.py`.
- Updated `PlayerVLC.get_time_pos()` to return `None` instead of `0` when no playback position is available, matching `PlayerMPV` behavior.
- Extracted `_fmt_seconds()` in `seek_handler.py` to centralize duplicated time-formatting logic.
- Updated `library/favorites.py` and `library/playlists.py` to create required directories before writing files.
- Improved `core/parser.py` robustness by handling both `ValueError` and `TypeError` in `parse_flags()`.
- Various minor code cleanup and refactoring improvements.


## [1.2.0] - 2026-05-30
 
### Added
- `search --p` flag: fetch tracks directly from a YouTube playlist URL
  (`/s <url> --p` loads the playlist into results; use `load` → `play` as usual)
- `pl <name>` shorthand: omitting the subcommand now falls back to `pl show <name>`;
  likewise `pl <name> load`, `pl <name> add`, `pl <name> remove <index>` all work
### Changed
- Introduced `COMPACT_THRESHOLD` constant in `config.py` — controls how many
  tracks are shown before the "… and N more" overflow hint in favorites,
  playlists, and playlist search results (previously hardcoded per-function)
- Spinner animation updated to smooth braille frames (`⣾ ⣽ ⣻ ⢿ ⡿ ⣟ ⣯ ⣷`)
  replacing the old ASCII set (`\ | / -`)
### Removed
- `migrate.py` legacy compatibility layer for pre-release favorites paths
  (`~/.px7_favorites.json`) has been dropped
### Fixed
- `--limit=0` now correctly returns all tracks (previously the `> 0` guard
  in `get_favorites` and `get_playlist_tracks` caused `--limit=0` to be
  silently ignored instead of treated as "no limit")


## [1.1.1] - 2026-05-29

### Fixed
- Seek command now handles mm:ss timestamps correctly

## [1.1.0] - 2026-05-29

### Added
- Seek bar in autoplay mode
- Automatic terminal resize handling

### Improved
- Search result formatting

### Fixed
- Playback index handling on stream/load failures


## [1.0.1] - 2026-05-28

### Fixed
- Minor bug fixes


## [1.0.0] - 2026-05-26

### Added
- Playlist system with create, delete, rename, add, remove, show, and load commands
- Seek command to view and change playback position
- Autoplay volume control support with `-` and `+`
- Instant key input support in autoplay mode (no ENTER required)

### Changed
- Updated autoplay mode controls
- Redesigned autoplay UI
- Improved title cleaning for search results

> **Note for pre-release users:**  
> Legacy favorites are automatically migrated on first launch.  
> The temporary `migrate.py` compatibility layer may be removed in future updates.

---

## Pre-release History

## [0.3.2] - 2026-05-08

### Fixed
- `queue` now correctly refreshes the active results list
- Fixed result desync after queue shuffle/view operations

### Changed
- Improved help text and README documentation


## [0.3.1] - 2026-05-07

### Added
- `favs` now supports display flags: `--order=name`, `--order=date-added`, `--order=duration`, `--reverse`, `--limit=<n>`
- Favorites are stored newest-first by default
- `date_added` timestamp (ISO 8601 UTC) is now stamped on every favorite when saved
- `get_favorites(order, reverse, limit)` function in `favorites.py` — centralises all sorting and limiting logic

### Fixed
- `play` with no arguments now behaves the same as `play 1`


## [0.3.0] - 2026-05-06

### Added
- `shuffle` command to randomize the current queue (keeps current track at position 1 / top)
- `load` command to replace the queue with the last results and reset playback state
- `fav` command to manage favorites (`add`, `add <index>`, `add all`, `remove <index>`, `remove all`)
- `favs` command to list all saved favorites (with title, channel, duration)
- Favorites persist across sessions in `~/.px7_favorites.json`

### Fixed
- Improved playback feedback messages


## [0.2.0] - 2026-05-03

### Added
- Unified player state system (`get_state`, `is_idle`, `is_paused`)
- Autoplay mode improvements
