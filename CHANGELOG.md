# Changelog

All notable changes to this project will be documented in this file.

## [Unreleased]

### Added
- `shuffle` command to randomize the current queue (keeps current track at position 1(top))
- `load` command to replace the queue with the last search results and reset playback state

### Fixed
- Improved playback feedback messages


## [0.2.0] - 2026-05-03

### Added
- Unified player state system (`get_state`, `is_idle`, `is_paused`)
- Autoplay mode improvements