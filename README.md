<div align="center">

<img width="600" alt="PX7 Terminal Music" src="https://github.com/user-attachments/assets/f1607e3a-e1fe-42df-a455-155aca1a77c3" />

<br>

![](https://img.shields.io/badge/interface-CLI-black?style=for-the-badge&color=03A907&labelColor=000000)
&nbsp;
![](https://img.shields.io/pypi/v/px7-music?style=for-the-badge&color=03A907&labelColor=000000) 


<br>

</div>


# PX7 Terminal Music

Stream music from YouTube directly in your terminal. No browser, no GUI, no nonsense.  
  
PX7 is a lightweight CLI music player that searches YouTube via `yt-dlp` and streams audio through `mpv` or `vlc` — no downloads, no accounts, no ads. Just type a song name and play.


```
>> search radiohead
>> play 2
```

## Features

- Search and Stream directly, no ads
- Hands free auto-play mode
- MPV and VLC support


## Requirements

- **Python 3.10+**
- MPV *(recommended)* or VLC


## Installation

### Install via pip (Recommended)

```
pip install px7-music[all]
```

Start the application:
```
px7-music
```
You will see a prompt:
```
>> 
```

## Usage

```
command [arguments] [--flags]
```

### Search & Play

| Command | Args | Description |
|---------|------|-------------|
| `search` / `/s` | `<query>` | Search YouTube and fill the queue |
| `play` | `<index>` | Stream a track from the current queue |

**Search flags:**

| Flag | Default | Description |
|------|---------|-------------|
| `--limit=<n>` | `6` | Number of results to fetch |
| `--no-postfix` | off | Disable the auto-appended `"song"` keyword |

```
>> search hotel california --limit=1
>> search my dear melancholy
>> play 2
```


### Playback Controls

| Command | Description |
|---------|-------------|
| `pause` | Pause the current track |
| `resume` | Resume a paused track |
| `next` | Skip to the next track in queue |
| `prev` | Go back to the previous track |



### Queue & Info

| Command | Description |
|---------|-------------|
| `queue` | List all tracks in the current queue |
| `current` / `now` | Show info about the currently playing track |



### Volume

```bash
>> volume         # print current volume
>> volume 70      # set volume to 70
```



### Auto-Play Mode

Hands-free mode that plays through the queue automatically.

```bash
>> auto-play
```

| Key | Action |
|-----|--------|
| `N` | Next track |
| `P` | Previous track |
| `Q` | Quit auto-play |



### Utility

| Command | Description |
|---------|-------------|
| `ping` | Check network latency |
| `clear` / `cls` | Clear the screen and redraw the banner |
| `help` | Show the help screen |
| `exit` | Quit PX7 Music |



## How It Works

1. `search` queries YouTube via `yt-dlp` in metadata-only mode (fast, no download)
2. Results are stored in an in-memory queue for the session
3. `play <index>` fetches the direct audio stream URL and pipes it to mpv or vlc
4. Auto-play uses a thread-safe event queue to advance tracks without blocking the input loop


## Project Structure

```
px7_music/
├── config.py               # yt-dlp options, defaults
├── main.py                 # entry point, command registration, main loop
├── core/
│   ├── handler.py          # command handlers (search, play, volume)
│   ├── parser.py           # command parser and flag parser
│   ├── ping.py             # network latency check
│   └── youtube.py          # yt-dlp search and stream URL extraction
├── player/
│   ├── player_base.py      # abstract Player interface
│   ├── player.py           # MPV and VLC backend implementations
│   ├── playback.py         # queue state, playback control, autoplay events
│   └── auto_play_mode.py   # auto-play UI and input listener thread
└── utility/
    ├── docs.py             # help text and installation guide
    └── utils.py            # ANSI codes, spinner, screen utilities
```


## Dependencies

| Package | Purpose |
|---------|---------|
| `yt-dlp` | YouTube search and stream URL extraction |
| `ping3` | Network latency check |
| `python-mpv` | MPV player bindings *(optional)* |
| `python-vlc` | VLC player bindings *(optional)* |

> At least one of `python-mpv` or `python-vlc` must be installed and its corresponding player binary must be present on your system.


## Known Limitations

- Queue is session-only — results reset when you run a new search or exit
- Streams directly from YouTube; subject to rate limiting or regional restrictions
- No playlist or shuffle support yet


## License

MIT — do whatever you want, just don't remove the header.