import random
import threading

import px7_music.core.youtube        as yt
import px7_music.core.jukebox_mode   as JB

from px7_music.player  import Player
from px7_music.utility import (
    ANSI, 
    Preloader, 
    print_results, 
    truncate_pad, 
    format_duration, 
    print_favs, 
    print_playlist, 
    print_playlist_results
)
from px7_music.config  import COMPACT_THRESHOLD

spinner = Preloader()

# ── Backend state ─────────────────────────────────────────────────────────────

pname: str     | None = None
player: Player | None = None

# ── Queue state ───────────────────────────────────────────────────────────────

CURRENT_INDEX = -1
LAST_RESULTS  = []   # last displayed list (search / favs / queue)
QUEUE         = []   # active playback queue

_track_ended  = threading.Event()


# ── Init ──────────────────────────────────────────────────────────────────────

def init_player(backend: str, backend_player: Player):
    global pname, player
    pname, player = backend, backend_player
    player.set_end_callback(_on_track_end)


def _on_track_end():
    _track_ended.set()


def poll_jukebox():
    if _track_ended.is_set():
        _track_ended.clear()
        play_next()


def kill_player():
    if not player:
        return
    try:
        if pname == "vlc":
            player.stop()
        elif pname == "mpv":
            player.player.terminate()
    except Exception:
        pass


# ── Search ────────────────────────────────────────────────────────────────────

def search(query: str, limit: int):
    spinner.start("Searching ... ")
    results = yt.search(query, limit)
    spinner.stop()

    if results is None:
        print("No result found.")
        return
    elif results == -1:
        print(f"{ANSI.RED}Search failed or timed out.{ANSI.RESET}")
        return

    LAST_RESULTS.clear()
    LAST_RESULTS.extend(results)
    print_results(results)


def search_playlist(url: str):
    spinner.start("Fetching playlist ... ")
    results = yt.fetch_playlist(url)
    spinner.stop()

    if results is None:
        print("Playlist is empty or no entries found.")
        return
    elif results == -1:
        print(f"{ANSI.RED}Failed to fetch playlist. Check the URL or your connection.{ANSI.RESET}")
        return
    
    LAST_RESULTS.clear()
    LAST_RESULTS.extend(results)
    print_playlist_results(results)


# ── Queue management ──────────────────────────────────────────────────────────

def load(_=None):
    global QUEUE, CURRENT_INDEX
    if not LAST_RESULTS:
        print("No results to load.")
        return
    QUEUE = list(LAST_RESULTS)
    CURRENT_INDEX = -1
    _track_ended.clear()
    player.stop()
    print("Queue Loaded.")


def play(idx: int):
    global QUEUE
    if not LAST_RESULTS:
        print("Empty results.")
        return
    if idx < 1 or idx > len(LAST_RESULTS):
        print("Index out of range.")
        return
    QUEUE = list(LAST_RESULTS)
    _play_current(idx - 1)


def _play_current(new_index: int):
    global CURRENT_INDEX
    track = QUEUE[new_index]

    if not JB.JUKEBOX:
        spinner.start("Getting stream url ... ")

    stream_url = yt.get_stream_url(track["video_url"])

    if not JB.JUKEBOX:
        spinner.stop()

    if not stream_url:
        if not JB.JUKEBOX:
            print(
                f"{ANSI.RED}Failed to get stream URL.{ANSI.RESET}\n"
                f"{ANSI.DIM}Use a VPN / different network if YouTube is geo-blocking or rate-limiting{ANSI.RESET}"
            )
        return

    CURRENT_INDEX = new_index
    player.stop()
    _track_ended.clear()
    player.play(stream_url)

    if not JB.JUKEBOX:
        show_current()


def play_prev(_=None):
    if not QUEUE:
        if not JB.JUKEBOX:
            print("Queue is empty.")
        return

    new_index = CURRENT_INDEX - 1
    if new_index < 0:
        if not JB.JUKEBOX:
            print("Start of queue.")
        return

    _play_current(new_index)


def play_next(_=None):
    if not QUEUE:
        if not JB.JUKEBOX:
            print("Queue is empty.")
        return

    new_index = CURRENT_INDEX + 1
    if new_index >= len(QUEUE):
        if not JB.JUKEBOX:
            print("End of queue.")
        return

    _play_current(new_index)


# ── Playback controls ─────────────────────────────────────────────────────────

def pause(_=None):
    player.pause()
    if not JB.JUKEBOX:
        print("Player paused")


def resume(_=None):
    player.resume()
    if not JB.JUKEBOX:
        print("Player resumed")


def set_volume(vol: int):
    try:
        set_vol = player.set_volume(vol)
        print(f"Volume set to {set_vol}")
    except Exception:
        print(f"{ANSI.RED}Failed to set volume.{ANSI.RESET}")


def get_volume():
    print(f"Current Volume: {player.get_volume()}")


# ── Display helpers ───────────────────────────────────────────────────────────

def show_current(_=None):
    if CURRENT_INDEX == -1 or not QUEUE:
        print("No track is currently playing.")
        return

    track = QUEUE[CURRENT_INDEX]
    print(f"\n{ANSI.GREEN}{ANSI.BOLD}=== Now Playing ==={ANSI.RESET}\n")
    print(f"{ANSI.BOLD}{track.get('title', 'Unknown Title')}{ANSI.RESET}")
    print(f"{ANSI.DIM}{track.get('channel', 'Unknown Channel')}{ANSI.RESET}")
    print(f"{ANSI.GRAY}{track.get('video_url')}{ANSI.RESET}\n")


def show_queue(no_compact: bool = False, _=None):
    if not QUEUE:
        print("Queue is empty.")
        return

    # Determine the slice: from current track onward, or full queue if nothing playing
    if CURRENT_INDEX == -1:
        start = 0
    else:
        start = CURRENT_INDEX

    visible_tracks = QUEUE[start:]
    total_visible  = len(visible_tracks)

    compact = not no_compact

    # How many to display
    if compact and total_visible > COMPACT_THRESHOLD:
        display_count = COMPACT_THRESHOLD
    else:
        display_count = total_visible

    LAST_RESULTS.clear()
    LAST_RESULTS.extend(QUEUE)

    print(f"\n{ANSI.GREEN}{ANSI.BOLD}=== Queue ==={ANSI.RESET}\n")

    for offset, track in enumerate(visible_tracks[:display_count]):
        real_i     = start + offset
        display_i  = real_i + 1

        title    = truncate_pad(track.get("title",   "Unknown Title"),   45)
        channel  = truncate_pad(track.get("channel", "Unknown Channel"), 30)
        duration = format_duration(track.get("duration"))

        is_current  = (real_i == CURRENT_INDEX)
        title_style = f"{ANSI.GREEN}{ANSI.BOLD}" if is_current else ANSI.BOLD
        index_style = ANSI.GREEN if is_current else ANSI.YELLOW

        print(
            f"{index_style}{display_i:>2}.{ANSI.RESET} "
            f"{title_style}{title}{ANSI.RESET} "
            f"{ANSI.GRAY}[{duration:>5}]{ANSI.RESET}"
        )
        print(f"    {ANSI.DIM}{channel}{ANSI.RESET}\n")

    if compact and total_visible > COMPACT_THRESHOLD:
        hidden = total_visible - COMPACT_THRESHOLD
        print(
            f"  {ANSI.DIM}... and {hidden} more  "
            f"(use  {ANSI.RESET}{ANSI.CYAN}queue --no-compact{ANSI.RESET}{ANSI.DIM}  to see all){ANSI.RESET}"
        )


def shuffle_queue(_=None):
    global QUEUE, CURRENT_INDEX

    if not QUEUE:
        print("Queue is empty.")
        return
    
    if CURRENT_INDEX == -1:
        random.shuffle(QUEUE)
        show_queue()
        return
    
    current = QUEUE[CURRENT_INDEX]

    remaining = QUEUE[:CURRENT_INDEX] + QUEUE[CURRENT_INDEX + 1:]
    random.shuffle(remaining)

    QUEUE = [current] + remaining
    LAST_RESULTS.clear()
    LAST_RESULTS.extend(QUEUE)
    CURRENT_INDEX = 0 
    show_queue()
    

# ── Playlist helpers ──────────────────────────────────────────────────────────

def list_playlist(name: str, tracks: list[dict], compact: bool = True):
    LAST_RESULTS.clear()
    LAST_RESULTS.extend(tracks)
    print_playlist(name, tracks, compact)

def load_playlist(name: str, tracks: list[dict]):
    global QUEUE, CURRENT_INDEX

    QUEUE = list(tracks)
    CURRENT_INDEX = -1
    LAST_RESULTS.clear()
    LAST_RESULTS.extend(tracks)

    _track_ended.clear()
    player.stop()

    print(f"{ANSI.GREEN}Loaded playlist '{name}' into queue ({len(tracks)} track{'s' if len(tracks) != 1 else ''}).{ANSI.RESET}")


def list_favs(favs: list[dict], compact: bool = True):
    LAST_RESULTS.clear()
    LAST_RESULTS.extend(favs)
    print_favs(favs, compact)