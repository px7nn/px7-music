### [← Back to README](../README.md)

**Sections:** [Search & Play](#search--play) • [Playback](#playback-controls) • [Queue & Info](#queue--info) • [Favorites](#favorites) • [Playlists](#playlists) • [Piping](#pipe--) • [Jukebox (/j)](#jukebox-mode) • [Config](#config) • [Volume](#volume) • [Utility](#utility)

---

<br/>

# Usage

## How Results Work

PX7 always has an **active result list**.

Commands that produce a list — `search`, `favs`, `queue`, `pl show`, `pl load` — replace the active results. `play <index>` always acts on the current active results.

```shell
>> /s the weeknd           # active results = search results
>> play 3                  # plays result #3

>> favs                    # active results = your favorites
>> play 1                  # plays favorite #1

>> pl load Chill Mix       # active results = playlist tracks
>> shuffle
>> play 1
```

The active results can also be loaded directly into the queue with `load`.

## Commands

```shell
command [arguments] [--flags]
```

### Search & Play

| Command | Args | Description |
|---------|------|-------------|
| `search` / `/s` | `<query>` | Search YouTube and fill the results |
| `play` | `[index]` | Play a track from the results and load the result list into the queue |

> `play` with no argument defaults to `play 1`.

**Flags:**

| Flag | Default | Description |
|------|---------|-------------|
| `--limit=<n>` | `DEFAULT_SEARCH_LIMIT` | Number of results to fetch |
| `--no-postfix` | off | Disable the auto-appended query postfix (see `config`) |
| `--p` | off | Treat the query as a YouTube playlist URL and fetch its tracks |

<details>
<summary><b>Examples</b></summary>

```shell
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
| `queue` | List the queue from the current track onward |
| `queue add <index>` | Add a track from active results to the queue |
| `queue add all` | Add all active results to the queue |
| `current` / `now` | Show info about the currently playing track |
| `load` | Replace the queue with the active results and reset playback |
| `shuffle` | Shuffle the queue — current track stays at position 1 |

**Queue flags:**

| Flag | Default | Description |
|------|---------|-------------|
| `--no-compact` | off | Show all tracks, bypassing the compact threshold *(queue only)* |
| `--next` | off | Insert the track(s) next in the queue *(queue add only)* |

<details>
<summary><b>Examples</b></summary>

```shell
>> queue
>> queue --no-compact
>> queue add 3
>> queue add all --next
```

</details>

---

### Favorites

Saved to `~/.px7/.px7_favorites.json`. New favorites appear at the top.

| Command | Args | Description |
|---------|------|-------------|
| `fav add` | | Add the currently playing track |
| `fav add` | `<index>` | Add a specific track from the queue |
| `fav add` | `all` | Add all queued tracks |
| `fav remove` | `<index>` | Remove a favorite by index |
| `fav remove` | `all` | Clear all favorites *(asks for confirmation)* |
| `favs` | `[/keyword]` | List all saved favorites, optionally filtered by keyword *(newest first)* |

**Favs flags:**

| Flag | Default | Description |
|------|---------|-------------|
| `--order=<by>` | newest first | `title` · `channel` · `date-added` · `duration` |
| `--limit=<n>` | all | Show only the first N favorites |
| `--reverse` | off | Reverse the sort direction |
| `--no-compact` | off | Show all, bypassing the compact threshold |

<details>
<summary><b>Examples</b></summary>

```shell
>> fav add
>> fav add 3
>> fav add all
>> fav remove 2
>> favs
>> favs /rock
>> favs /lofi --order=duration --reverse
>> favs --limit=10 --order=date-added
```

</details>

---

### Playlists

Saved to `~/.px7/.px7_playlists.json`. New tracks in a playlist appear at the top.

| Command | Args | Description |
|---------|------|-------------|
| `pl` / `pl list` | `[/keyword]` | List all playlists, optionally filtered by keyword |
| `pl create` | `<name>` | Create a new playlist |
| `pl delete` | `<name>` | Delete a playlist *(asks for confirmation)* |
| `pl rename` | `<old> -> <new>` | Rename a playlist |
| `pl add` | `<name>` | Add the currently playing track |
| `pl add` | `<name> <index>` | Add a queue track by index |
| `pl add` | `<name> all` | Add all queued tracks |
| `pl remove` | `<name> <index>` | Remove a track by index |
| `pl show` | `<name> [/keyword]` | Display tracks in a playlist, optionally filtered by keyword |
| `pl load` | `<name> [/keyword]` | Load a playlist into the queue, optionally filtered by keyword |
| `pl <name>` | `[/keyword]` | Shorthand for `pl show <name> [/keyword]` |

**pl show / pl load flags:**

| Flag | Default | Description |
|------|---------|-------------|
| `--order=<by>` | newest first | `title` · `channel` · `date-added` · `duration` |
| `--limit=<n>` | all | Cap the number of tracks shown or loaded |
| `--reverse` | off | Reverse the sort direction |
| `--no-compact` | off | Show all tracks, bypassing the compact threshold *(show only)* |

**Shorthand — name first, subcommand second (defaults to `show`):**

```shell
>> pl Chill Mix              # → pl show Chill Mix
>> pl Chill Mix load         # → pl load Chill Mix
>> pl Chill Mix add 3        # → pl add  Chill Mix 3
```

<details>
<summary><b>Examples</b></summary>

```shell
>> pl create Chill Mix
>> pl add Chill Mix
>> pl add Chill Mix 3
>> pl add Chill Mix all
>> pl Chill Mix
>> pl list /chill
>> pl show Chill Mix /rock --order=duration
>> pl load Chill Mix /lofi --reverse
>> pl rename Chill Mix -> Late Night
>> pl remove Late Night 2
>> pl delete Late Night
```

</details>

---

### Pipe `->`

Pipe a result list directly into a playlist. The playlist is auto-created if it doesn't exist.

```shell
<source> [--flags] -> <playlist name>
```

| Source | Description |
|--------|-------------|
| `search` / `/s` | Pipe search results. Accepts all search flags. |
| `favs` | Pipe favorites. Accepts `--order`, `--limit`, `--reverse`. |
| `queue` | Pipe the current queue. |

<details>
<summary><b>Examples</b></summary>

```shell
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

```shell
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

> **Available `THEME_COLOR` options:** green · blue · cyan · purple · violet · pink · rose · orange · teal · white

```shell
>> config DEFAULT_SEARCH_LIMIT 10
>> config DEFAULT_SEARCH_LIMIT *    # reset to default
>> config reset                     # reset everything
```

---

### Volume

```shell
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
