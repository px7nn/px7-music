# Changelog

All notable changes to this project will be documented in this file.

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
