# Changelog

All notable changes to this project will be documented in this file.

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
