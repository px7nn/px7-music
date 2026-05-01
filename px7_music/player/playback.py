
import threading
import px7_music.core.youtube   as yt
import px7_music.player.auto_play_mode as AP
from px7_music.player.player    import get_player
from px7_music.utility.utils    import ANSI, Preloader, print_results, truncate_pad, format_duration

pname, player = None, None
spinner         = Preloader()

CURRENT_INDEX = -1
LAST_RESULTS    = []

_track_ended = threading.Event()


def init_player(BACKEND, PLAYER):
    global pname, player

    pname, player = BACKEND, PLAYER
    player.set_end_callback(_on_track_end)


def _on_track_end():
    _track_ended.set()


def poll_autoplay():
    if _track_ended.is_set():
        _track_ended.clear()
        play_next()


def kill_player():
    global player
    if not player:
        return

    try:
        if pname == "vlc":
            player.stop()
            player.release()
        elif pname == "mpv":
            player.terminate()
    except Exception:
        pass


def search(query: str, limit: int):
    spinner.start("Searching   ")
    results = yt.search(query, limit)
    if results is None:
        spinner.stop()
        print(f"No result found.")
        return
    elif results == -1:
        spinner.stop()
        print(f"{ANSI.RED}Search failed or timed out.{ANSI.RESET}")
        return

    spinner.stop()

    LAST_RESULTS.clear()
    LAST_RESULTS.extend(results)

    print_results(results)


def play(idx: int):
    global CURRENT_INDEX

    if len(LAST_RESULTS) == 0:
        print("Empty results.")
        return

    if idx < 1 or idx > len(LAST_RESULTS):
        print("Index out of range.")
        return

    CURRENT_INDEX = idx - 1
    track = LAST_RESULTS[CURRENT_INDEX]
    spinner.start("Getting stream url   ")
    stream_url = yt.get_stream_url(track["video_url"])
    spinner.stop()

    if not stream_url:
        print("Failed to get stream URL")
        return
    
    player.stop()

    _track_ended.clear()  # discard any end event from the stop()
    player.play(stream_url)

    player.play(stream_url)
    if not AP.AUTO_PLAY:
        print(f"Now playing: {track['title']}")

def play_prev(_=None):
    global CURRENT_INDEX

    prev_index = CURRENT_INDEX - 1

    if prev_index < 0:
        print("Start of queue.")
        return

    play(prev_index + 1)

def play_next(_=None):
    global CURRENT_INDEX

    next_index = CURRENT_INDEX + 1

    if next_index >= len(LAST_RESULTS):
        print("End of queue.")
        return

    play(next_index + 1)


def pause(_=None):
    player.pause()
    print("Player paused")


def resume(_=None):
    player.resume()
    print("Player resumed")


def set_volume(vol: int):
    try:
        set_vol = player.set_volume(vol)
        print(f"Volume set to {set_vol}")
    except Exception:
        print(f"{ANSI.RED}Failed to set volume.{ANSI.RESET}")


def get_volume():
    print(f"Current Volume: {player.get_volume()}")


def show_current(_=None):
    if CURRENT_INDEX == -1 or not LAST_RESULTS:
        print("No track is currently playing.")
        return

    track = LAST_RESULTS[CURRENT_INDEX]

    print(f"\n{ANSI.GREEN}{ANSI.BOLD}=== Now Playing ==={ANSI.RESET}\n")
    print(f"{ANSI.BOLD}{track.get('title', 'Unknown Title')}{ANSI.RESET}")
    print(f"{ANSI.DIM}{track.get('channel', 'Unknown Channel')}{ANSI.RESET}")
    print(f"{ANSI.GRAY}{track.get('video_url')}{ANSI.RESET}\n")

def show_upnext(_=None):
    if CURRENT_INDEX == -1 or not LAST_RESULTS:
        print("No upcoming tracks.")
        return

    next_index = CURRENT_INDEX + 1

    if next_index >= len(LAST_RESULTS):
        print("No upcoming tracks.")
        return

    track = LAST_RESULTS[next_index]

    print(f"\n{ANSI.GREEN}{ANSI.BOLD}=== Up Next ==={ANSI.RESET}\n")
    print(f"{track.get('title', 'Unknown Title')}\n")


def show_queue(_=None):
    if not LAST_RESULTS:
        print("Queue is empty.")
        return

    TITLE_W = 45
    CHANNEL_W = 30

    print(f"\n{ANSI.GREEN}{ANSI.BOLD}=== Queue ==={ANSI.RESET}\n")

    for i, track in enumerate(LAST_RESULTS, 1):
        title = truncate_pad(track.get("title", "Unknown Title"), TITLE_W)
        channel = truncate_pad(track.get("channel", "Unknown Channel"), CHANNEL_W)
        duration = format_duration(track.get("duration"))

        is_current = (i - 1 == CURRENT_INDEX)

        # apply green only if current
        title_style = f"{ANSI.GREEN}{ANSI.BOLD}" if is_current else ANSI.BOLD
        index_style = ANSI.GREEN if is_current else ANSI.YELLOW

        # first line
        print(
            f"{index_style}{i:>2}.{ANSI.RESET} "
            f"{title_style}{title}{ANSI.RESET} "
            f"{ANSI.GRAY}[{duration:>5}]{ANSI.RESET}"
        )

        # second line
        print(
            f"    {ANSI.DIM}{channel}{ANSI.RESET}\n"
        )