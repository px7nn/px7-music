import threading
import px7_music.core.youtube           as yt
import px7_music.player.auto_play_mode  as AP

from px7_music.utility.utils    import ANSI, Preloader, print_results, truncate_pad, format_duration, print_favs

pname, player = None, None
spinner       = Preloader()

CURRENT_INDEX = -1
LAST_RESULTS  = []
QUEUE         = []         
PLAY_MODE = "sequence"      # sequnce | shuffle

_track_ended  = threading.Event()


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
        print("No result found.")
        return
    elif results == -1:
        spinner.stop()
        print(f"{ANSI.RED}Search failed or timed out.{ANSI.RESET}")
        return

    spinner.stop()
    LAST_RESULTS.clear()
    LAST_RESULTS.extend(results)
    print_results(results)


def list_favs(favs: list[dict]):
    LAST_RESULTS.clear()
    LAST_RESULTS.extend(favs)
    print_favs(favs)


def load(_=None):
    # SETS QUEUE = LAST_RESULTS and kill current playing track
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
    global CURRENT_INDEX, QUEUE

    if not LAST_RESULTS:
        print("Empty results.")
        return

    if idx < 1 or idx > len(LAST_RESULTS):
        print("Index out of range.")
        return

    QUEUE = list(LAST_RESULTS)
    CURRENT_INDEX = idx - 1

    _play_current()


def _play_current():
    track = QUEUE[CURRENT_INDEX]

    spinner.start("Getting stream url   ")
    stream_url = yt.get_stream_url(track["video_url"])
    spinner.stop()

    if not stream_url:
        print("Failed to get stream URL")
        return

    player.stop()
    _track_ended.clear()
    player.play(stream_url)

    if not AP.AUTO_PLAY:
        show_current()


def play_prev(_=None):
    global CURRENT_INDEX

    if not QUEUE:
        print("Queue is empty.")
        return

    if CURRENT_INDEX - 1 < 0:
        print("Start of queue.")
        return

    CURRENT_INDEX -= 1
    _play_current()


def play_next(_=None):
    global CURRENT_INDEX

    if not QUEUE:
        print("Queue is empty.")
        return

    if CURRENT_INDEX + 1 >= len(QUEUE):
        print("End of queue.")
        return

    CURRENT_INDEX += 1
    _play_current()


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
    if CURRENT_INDEX == -1 or not QUEUE:
        print("No track is currently playing.")
        return

    track = QUEUE[CURRENT_INDEX]
    print(f"\n{ANSI.GREEN}{ANSI.BOLD}=== Now Playing ==={ANSI.RESET}\n")
    print(f"{ANSI.BOLD}{track.get('title', 'Unknown Title')}{ANSI.RESET}")
    print(f"{ANSI.DIM}{track.get('channel', 'Unknown Channel')}{ANSI.RESET}")
    print(f"{ANSI.GRAY}{track.get('video_url')}{ANSI.RESET}\n")


def show_upnext(_=None):
    if not QUEUE:
        print("No upcoming tracks.")
        return

    next_index = CURRENT_INDEX + 1
    if next_index >= len(QUEUE):
        print("No upcoming tracks.")
        return

    track = QUEUE[next_index]
    print(f"\n{ANSI.GREEN}{ANSI.BOLD}=== Up Next ==={ANSI.RESET}\n")
    print(f"{track.get('title', 'Unknown Title')}\n")


def show_queue(_=None):
    if not QUEUE:
        print("Queue is empty.")
        return

    TITLE_W   = 45
    CHANNEL_W = 30

    print(f"\n{ANSI.GREEN}{ANSI.BOLD}=== Queue ==={ANSI.RESET}\n")

    for i, track in enumerate(QUEUE, 1):
        title    = truncate_pad(track.get("title",   "Unknown Title"),   TITLE_W)
        channel  = truncate_pad(track.get("channel", "Unknown Channel"), CHANNEL_W)
        duration = format_duration(track.get("duration"))

        is_current = (i - 1 == CURRENT_INDEX)

        title_style = f"{ANSI.GREEN}{ANSI.BOLD}" if is_current else ANSI.BOLD
        index_style = ANSI.GREEN if is_current else ANSI.YELLOW

        print(
            f"{index_style}{i:>2}.{ANSI.RESET} "
            f"{title_style}{title}{ANSI.RESET} "
            f"{ANSI.GRAY}[{duration:>5}]{ANSI.RESET}"
        )
        print(f"    {ANSI.DIM}{channel}{ANSI.RESET}\n")


def shuffle_queue(_=None):
    import random
    global QUEUE, CURRENT_INDEX, LAST_RESULTS

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
    LAST_RESULTS = list(QUEUE)
    CURRENT_INDEX = 0 
    show_queue()
    