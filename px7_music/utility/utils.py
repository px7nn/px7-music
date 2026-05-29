import sys
import time
import threading
import shutil
import re
from px7_music.config import BANNER_TEXT_DEFAULT

class ANSI:
    RESET = "\033[0m"

    # styles
    BOLD    = "\033[1m"
    DIM     = "\033[2m"
    ITALIC  = "\033[3m"

    # colors
    RED     = "\033[31m"
    GREEN   = "\033[32m"
    YELLOW  = "\033[33m"
    BLUE    = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN    = "\033[36m"
    WHITE   = "\033[37m"
    GRAY    = "\033[90m"
    RED_BG  = "\033[41m\033[97m"
    BLUE_BG = "\033[44m\033[97m"

class Preloader:
    def __init__(self, delay: float = 0.2):
        self.delay = delay
        self._running = False
        self._thread = None
        self.frames = ["|", "/", "-", "\\"]

    def _animate(self):
        i = 0
        
        while self._running:
            frame = self.frames[i % 4]
            sys.stdout.write(f"\r\033[K{self.text}{frame}")
            sys.stdout.flush()
            i += 1
            time.sleep(self.delay)

        # clear line when done
        sys.stdout.write("\r\033[K")
        sys.stdout.flush()

    def start(self, text):
        if self._running:
            return
        self.text = text
        self._running = True
        self._thread = threading.Thread(target=self._animate, daemon=True)
        self._thread.start()

    def stop(self):
        self._running = False
        if self._thread:
            self._thread.join()



def animate_print(text: str, delay: float = 0.001):
    for char in text:
        sys.stdout.write(char)
        sys.stdout.flush()

        if char.strip():
            time.sleep(delay)
        else:
            time.sleep(delay / 4)
    print()

def clear_screen(_=None):
    sys.stdout.write("\033[2J\033[3J\033[H")
    sys.stdout.flush()
    animate_print(f"{ANSI.GREEN}{BANNER_TEXT_DEFAULT}{ANSI.RESET}")

def format_duration(seconds) -> str:
    if not seconds:
        return "--:--"

    seconds = int(seconds)

    h = seconds // 3600
    m = (seconds % 3600) // 60
    s = seconds % 60

    if h > 0:
        return f"{h:02}:{m:02}:{s:02}"
    return f"{m:02}:{s:02}"

def truncate_pad(text: str, width: int) -> str:
    if len(text) > width:
        return text[:width-3] + "..."
    return text.ljust(width)

def print_results(results: list[dict]):
    if not results:
        print("No results found.")
        return

    TITLE_W = 45
    CHANNEL_W = 30

    print(f"\n{ANSI.GREEN}{ANSI.BOLD}=== Search Results ==={ANSI.RESET}\n")

    for i, item in enumerate(results, 1):
        title = truncate_pad(item.get("title", "Unknown Title"), TITLE_W)
        channel = truncate_pad(item.get("channel", "Unknown Channel"), CHANNEL_W)
        duration = format_duration(item.get("duration"))

        # first line (aligned)
        print(
            f"{ANSI.YELLOW}{i:>2}.{ANSI.RESET} "
            f"{ANSI.BOLD}{title}{ANSI.RESET} "
            f"{ANSI.GRAY}[{duration:>5}]{ANSI.RESET}"
        )

        # second line (aligned under title)
        print(
            f"    {ANSI.DIM}{channel}{ANSI.RESET}\n"
        )


def print_favs(favs: list[dict]):
    print(f"\n{ANSI.GREEN}{ANSI.BOLD}=== Favorites ({len(favs)}) ==={ANSI.RESET}\n")

    TITLE_W = 45

    for i, track in enumerate(favs, 1):
        title    = truncate_pad(track.get("title",   "Unknown Title"),   TITLE_W)
        channel  = track.get("channel",  "Unknown Channel")
        duration = format_duration(track.get("duration"))

        print(
            f"{ANSI.YELLOW}{i:>2}.{ANSI.RESET} "
            f"{ANSI.BOLD}{title}{ANSI.RESET} "
            f"{ANSI.GRAY}[{duration:>5}]{ANSI.RESET}"
        )
        print(f"    {ANSI.DIM}{channel}{ANSI.RESET}\n")


def print_playlists(plist: list[dict]):
    print(f"\n{ANSI.GREEN}{ANSI.BOLD}=== Playlists ({len(plist)}) ==={ANSI.RESET}\n")
    for i, pl in enumerate(plist, 1):
        name  = pl["name"]
        count = pl["track_count"]
        print(
            f"{ANSI.YELLOW}{i:>2}.{ANSI.RESET} "
            f"{ANSI.BOLD}{name}{ANSI.RESET}  "
            f"{ANSI.DIM}{count} track{'s' if count != 1 else ''}{ANSI.RESET}"
        )
    print()
 
 
def print_playlist(name: str, tracks: list[dict]):
    TITLE_W = 45
    print(f"\n{ANSI.GREEN}{ANSI.BOLD}=== Playlist: {name} ({len(tracks)}) ==={ANSI.RESET}\n")
    for i, track in enumerate(tracks, 1):
        title    = truncate_pad(track.get("title",   "Unknown Title"), TITLE_W)
        channel  = track.get("channel",  "Unknown Channel")
        duration = format_duration(track.get("duration"))
        print(
            f"{ANSI.YELLOW}{i:>2}.{ANSI.RESET} "
            f"{ANSI.BOLD}{title}{ANSI.RESET} "
            f"{ANSI.GRAY}[{duration:>5}]{ANSI.RESET}"
        )
        print(f"    {ANSI.DIM}{channel}{ANSI.RESET}\n")


def fmt_track(track: dict) -> str:
    """Return a short 'Title — Channel' string for display."""
    title   = truncate_pad(track.get("title",   "Unknown Title"),   40)
    channel = track.get("channel", "Unknown Channel")
    return f"{ANSI.BOLD}{title.strip()}{ANSI.RESET} {ANSI.DIM}— {channel}{ANSI.RESET}"


def clean_title(title, channel=""):
    if not title:
        return ""

    cleaned = title.strip()

    if channel:
        t = cleaned.lower().strip()
        c = channel.lower().strip()

        if t.startswith(c + " - "):
            cleaned = cleaned[len(channel) + 3:]

    # remove youtube garbage
    cleaned = re.sub(
        r'\((?:official|lyrics?|audio|video|mv|hd|4k|music video|visualizer)[^)]*\)',
        '',
        cleaned,
        flags=re.IGNORECASE
    )

    cleaned = re.sub(
        r'\[(?:official|lyrics?|audio|video|mv|hd|4k|music video|visualizer)[^\]]*\]',
        '',
        cleaned,
        flags=re.IGNORECASE
    )

    return cleaned.strip()


_ansi_escape = re.compile(r'\x1B\[[0-?]*[ -/]*[@-~]')

def _strip_ansi(text):
    return _ansi_escape.sub('', text)

def _visible_len(text):
    return len(_strip_ansi(text))

def _build_seekbar_content(time_pos, duration, inner: int) -> str:
    pos_sec = int(time_pos or 0)
    dur_sec = int(duration or 0)

    pos_str = format_duration(pos_sec)
    dur_str = format_duration(dur_sec) if dur_sec else "--:--"

    # Fixed cost: 1 space + pos + 1 space +  1 space + dur + 1 space
    fixed = 1 + len(pos_str) + 1 + 1 + len(dur_str) + 1
    bar_width = max(4, inner - fixed)

    if dur_sec > 0:
        filled = int((pos_sec / dur_sec) * bar_width)
        filled = max(0, min(filled, bar_width))
    else:
        filled = 0

    bar = (f"{ANSI.GREEN}{'█' * filled}{ANSI.RESET}{ANSI.DIM}{'░' * (bar_width - filled)}{ANSI.RESET}")

    return (
        f" {ANSI.CYAN}{pos_str}{ANSI.RESET} "
        f"{bar}"
        f" {ANSI.GRAY}{dur_str}{ANSI.RESET} "
    )

def update_seekbar(row: int, time_pos, duration):
    width = min(shutil.get_terminal_size((90, 30)).columns - 2, 86)
    width = max(width, 30)
    inner = width - 2

    content = _build_seekbar_content(time_pos, duration, inner)
    padding = inner - _visible_len(content)
    full_line = "│" + content + (" " * max(0, padding)) + "│"

    # Move cursor to that row, overwrite, then park cursor safely off-screen
    sys.stdout.write(f"\033[{row};1H{full_line}\033[999;1H")
    sys.stdout.flush()


def autoplay_dashboard(title, artist, duration, volume, state, queue, time_pos=None) -> int:
    width = min(shutil.get_terminal_size((90, 30)).columns - 2, 86)
    width = max(width, 30)
    inner = width - 2    

    def top():
        return "╭" + "─" * inner + "╮"

    def mid():
        return "├" + "─" * inner + "┤"

    def bottom():
        return "╰" + "─" * inner + "╯"

    def line(text=""):
        padding = inner - _visible_len(text)
        return "│" + text + (" " * max(0, padding)) + "│"

    def center(text):
        v = _visible_len(text)
        left = (inner - v) // 2
        right = inner - v - left
        return (" " * left) + text + (" " * right)

    state_icon = {
        "playing"   : f"{ANSI.BOLD}>>{ANSI.RESET}",
        "paused"    : f"{ANSI.BOLD}||{ANSI.RESET}",
        "stopped"   : f"{ANSI.BOLD}--{ANSI.RESET}",
        "buffering" : f"{ANSI.BOLD}~~{ANSI.RESET}"
    }.get(state.lower(), "??")

    # volume bar
    vol_len = 10
    fill = int((volume / 100) * vol_len)
    vol_bar = ("■" * fill + "·" * (vol_len - fill))

    row = 1 # track printed lines, count rows as we print so we know where the seek bar lands. Starting from 1 (home after clear)
    def emit(text):
        nonlocal row
        print(text)
        row += 1

    emit(top())

    # top panel
    left_label = f" {ANSI.BOLD}PX7-Music{ANSI.RESET}"
    r_key = f"{ANSI.BLUE_BG}{ANSI.ITALIC} r {ANSI.RESET}"
    q_key = f"{ANSI.RED_BG} X {ANSI.RESET}"
    spacing = inner - _visible_len(left_label) - _visible_len(r_key) - _visible_len(' ') - _visible_len(q_key) - _visible_len(' ')
    emit(line(left_label + (" " * spacing) + r_key + ' ' + q_key + ' '))

    emit(mid())
    emit(line())

    if title is None:
        hint = f"{ANSI.DIM}Press  N  to start{ANSI.RESET}" if queue else f"{ANSI.DIM}Use  play <n>  to start{ANSI.RESET}"
        emit(line(center(f"{ANSI.DIM}No track playing{ANSI.RESET}")))
        emit(line(center(hint)))
    else:
        display_title  = truncate_pad(title,  inner - 10).strip()
        display_artist = truncate_pad(artist, inner - 10).strip()
        emit(line(center(f"{ANSI.BOLD}{display_title}{ANSI.RESET}")))
        emit(line(center(f"{ANSI.DIM}{display_artist}{ANSI.RESET}")))

    emit(line())

    if title is not None:
        seek_content = _build_seekbar_content(time_pos, duration, inner)
        padding      = inner - _visible_len(seek_content)
        seekbar_line = "│" + seek_content + (" " * max(0, padding)) + "│"
        seekbar_row  = row
        emit(seekbar_line)
        emit(line())
    else:
        seekbar_row = None

    # controls
    controls = f"[<]    {state_icon}    [>]"
    emit(line(center(controls)))
    emit(line())

    # volume
    meta = f"{ANSI.GRAY}VOL{ANSI.RESET} {vol_bar} {volume:3d}%"
    emit(line(center(meta)))
    emit(line())

    # queue separator
    label = " UP NEXT "
    left_side = (inner - len(label)) // 2
    right_side = inner - len(label) - left_side
    emit(line("─" * left_side + label + "─" * right_side))

    # queue — each item is a track dict
    if not queue:
        emit(line(center(f"{ANSI.DIM}Queue is empty{ANSI.RESET}")))
    else:
        for idx, track in enumerate(queue):
            item = f"  {track.get('title', 'Unknown Title')}"
            item = truncate_pad(item, inner).rstrip()
            if idx == 0:
                style = ANSI.WHITE 
            elif idx == 1:
                style = ANSI.DIM + ANSI.WHITE
            elif idx == 2:
                style = ANSI.GRAY
            else:
                style = ANSI.GRAY + ANSI.DIM
            emit(line(f"{style}{item}{ANSI.RESET}"))

    emit(line())
    emit(bottom())

    sys.stdout.write("\033[999;1H")
    sys.stdout.flush()

    return seekbar_row