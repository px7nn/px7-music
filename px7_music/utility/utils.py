import re
import sys
import shutil
import threading
import time

from px7_music.config import COMPACT_THRESHOLD


# ── ANSI escape codes ─────────────────────────────────────────────────────────

class ANSI:
    RESET   = "\033[0m"

    BOLD    = "\033[1m"
    DIM     = "\033[2m"
    ITALIC  = "\033[3m"

    RED     = "\033[38;2;205;49;49m"
    GREEN   = "\033[38;2;30;215;96m"
    YELLOW  = "\033[38;2;229;229;16m"
    BLUE    = "\033[38;2;36;114;200m"
    MAGENTA = "\033[38;2;188;63;188m"
    CYAN    = "\033[38;2;17;168;205m"
    WHITE   = "\033[38;2;229;229;229m"
    GRAY    = "\033[38;2;118;118;118m"

    RED_BG  = "\033[48;2;180;50;50m\033[38;2;240;240;240m"   # red bg, light fg
    BLUE_BG = "\033[48;2;50;100;180m\033[38;2;240;240;240m"  # blue bg, light fg


# ── Spinner / preloader ───────────────────────────────────────────────────────

class Preloader:
    _FRAMES = ("⣾", "⣽", "⣻", "⢿", "⡿", "⣟", "⣯", "⣷")

    def __init__(self, delay: float = 0.1):
        self.delay    = delay
        self._running = False
        self._thread  = None
        self.text     = ""

    def _animate(self):
        i = 0
        while self._running:
            sys.stdout.write(f"\r\033[K{self.text}{self._FRAMES[i % 8]}")
            sys.stdout.flush()
            i += 1
            time.sleep(self.delay)
        sys.stdout.write("\r\033[K")
        sys.stdout.flush()

    def start(self, text):
        if self._running:
            return
        self.text     = text
        self._running = True
        self._thread  = threading.Thread(target=self._animate, daemon=True)
        self._thread.start()

    def stop(self):
        self._running = False
        if self._thread:
            self._thread.join()


# ── Banner ────────────────────────────────────────────────────────────────────

_LOGO_LINES = [
    f"{ANSI.GREEN}    ██████╗ ██╗  ██╗███████╗  {ANSI.RESET}",
    f"{ANSI.GREEN}    ██╔══██╗╚██╗██╔╝╚════██║  {ANSI.RESET}",
    f"{ANSI.GREEN}    ██████╔╝ ╚███╔╝     ██╔╝  {ANSI.RESET}",
    f"{ANSI.GREEN}    ██╔═══╝  ██╔██╗    ██╔╝   {ANSI.RESET}",
    f"{ANSI.GREEN}    ██║     ██╔╝ ██╗   ██║    {ANSI.RESET}",
    f"{ANSI.GREEN}    ╚═╝     ╚═╝  ╚═╝   ╚═╝    {ANSI.RESET}",
    f"{ANSI.DIM} - - - - Terminal Music - - - - {ANSI.RESET}",
]

_banner: str = ""


def set_runtime_banner(version: str, os_name: str, player: str) -> None:
    global _banner

    annotations = [
        ("version", f"v{version}"),
        ("os",      os_name),
        ("player",  player),
    ]

    lines = list(_LOGO_LINES)
    for ann_i, line_i in enumerate((1, 2, 3)):
        label, value = annotations[ann_i]
        ann = f"{ANSI.DIM}{label}{ANSI.RESET} {ANSI.GREEN}{value}{ANSI.RESET}"
        lines[line_i] = lines[line_i] + "    " + ann

    _banner = "\n" + "\n".join(lines) + "\n"


# ── Terminal helpers ──────────────────────────────────────────────────────────

def animate_print(text: str, delay: float = 0.001):
    for char in text:
        sys.stdout.write(char)
        sys.stdout.flush()
        time.sleep(delay if char.strip() else delay / 4)
    print()


def clear_screen(_=None):
    sys.stdout.write("\033[2J\033[3J\033[H")
    sys.stdout.flush()
    animate_print(f"{ANSI.GREEN}{_banner}{ANSI.RESET}")


def truncate_pad(text: str, width: int) -> str:
    return text[:width - 3] + "..." if len(text) > width else text.ljust(width)


def format_duration(seconds) -> str:
    if not seconds:
        return "--:--"
    s: int = int(seconds)
    h, rem = divmod(s, 3600)
    m, sec = divmod(rem, 60)
    return f"{h:02}:{m:02}:{sec:02}" if h else f"{m:02}:{sec:02}"

# ── Text utilities ────────────────────────────────────────────────────────────

_ANSI_ESCAPE = re.compile(r'\x1B\[[0-?]*[ -/]*[@-~]')

def _strip_ansi(text):
    return _ANSI_ESCAPE.sub('', text)

def _visible_len(text):
    return len(_strip_ansi(text))


_GARBAGE_PARENS: re.Pattern = re.compile(
    r"\((?:official|lyrics?|audio|video|mv|hd|4k|music video|visualizer)[^)]*\)",
    re.IGNORECASE,
)
_GARBAGE_BRACKETS: re.Pattern = re.compile(
    r"\[(?:official|lyrics?|audio|video|mv|hd|4k|music video|visualizer)[^\]]*\]",
    re.IGNORECASE,
)
_EMOJI: re.Pattern = re.compile(
    "["
    "\U0001F600-\U0001F64F"   # emoticons
    "\U0001F300-\U0001F5FF"   # symbols & pictographs
    "\U0001F680-\U0001F6FF"   # transport & map
    "\U0001F1E0-\U0001F1FF"   # flags
    "\U00002700-\U000027BF"   # dingbats
    "\U000024C2-\U0001F251"   # enclosed chars
    "\U0001F900-\U0001F9FF"   # supplemental symbols
    "\U0001FA00-\U0001FA6F"   # chess / other
    "\U0001FA70-\U0001FAFF"   # symbols extended
    "\U00002000-\U00002BFF"   # misc symbols & arrows
    "]+",
    flags=re.UNICODE,
)


def clean_title(title: str | None, channel: str = "") -> str:
    if not title:
        return ""
    cleaned: str = title.strip()
    if channel:
        t, c = cleaned.lower().strip(), channel.lower().strip()
        if t.startswith(c + " - "):
            cleaned = cleaned[len(channel) + 3:]
    cleaned = _GARBAGE_PARENS.sub("", cleaned)
    cleaned = _GARBAGE_BRACKETS.sub("", cleaned)
    cleaned = _EMOJI.sub("", cleaned)
    return cleaned.strip()


def fmt_track(track: dict) -> str:
    """Return a short 'Title — Channel' string for display."""
    title   = truncate_pad(track.get("title",   "Unknown Title"),   40)
    channel = track.get("channel", "Unknown Channel")
    return f"{ANSI.BOLD}{title.strip()}{ANSI.RESET} {ANSI.DIM}— {channel}{ANSI.RESET}"


# ── Duration ────────────────────────────────────────────────────────

def _total_duration(tracks: list[dict]) -> str:
    total = int(sum(t.get("duration") or 0 for t in tracks))
    return format_duration(total) if total else "--:--"


# ── Print helpers ─────────────────────────────────────────────────────────────

def _print_track_line(i: int, title_raw: str, channel: str, duration: str):
    term_w  = shutil.get_terminal_size((80, 24)).columns
    INDEX_W = 4
    DUR_W   = len(f"[{duration:>5}]") + 1
    title_w = max(10, term_w - INDEX_W - DUR_W - 1)
    title   = truncate_pad(title_raw, title_w)
    print(
        f"{ANSI.YELLOW}{i:>2}.{ANSI.RESET} "
        f"{ANSI.BOLD}{title}{ANSI.RESET} "
        f"{ANSI.GRAY}[{duration:>5}]{ANSI.RESET}"
    )
    print(f"    {ANSI.DIM}{channel}{ANSI.RESET}\n")


def _print_collection_header(kind: str, name: str | None, tracks: list[dict]):
    term_w  = shutil.get_terminal_size((80, 24)).columns
    divider = f"{ANSI.DIM}{'─' * min(term_w, 52)}{ANSI.RESET}"
    total   = _total_duration(tracks)
    count   = len(tracks)
    print()
    if name:
        print(f"  {ANSI.BOLD}{kind}:{ANSI.RESET} {ANSI.GREEN}{ANSI.BOLD}{name}{ANSI.RESET}")
    else:
        print(f"  {ANSI.BOLD}{kind}{ANSI.RESET}")
    print(
        f"  {ANSI.DIM}Duration:{ANSI.RESET} {ANSI.CYAN}{total}{ANSI.RESET}"
        f"   {ANSI.DIM}Showing:{ANSI.RESET} {ANSI.CYAN}{count}{ANSI.RESET}"
    )
    print(f"  {divider}\n")


def print_queue(queue: list[dict], CURRENT_INDEX, no_compact):
    if CURRENT_INDEX == -1:
        start = 0
    else:
        start = CURRENT_INDEX

    visible_tracks = queue[start:]
    total_visible  = len(visible_tracks)

    compact = not no_compact
    if compact and total_visible > COMPACT_THRESHOLD:
        display_count = COMPACT_THRESHOLD
    else:
        display_count = total_visible

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


def print_results(results: list[dict], header: str|None = "=== Search Results ==="):
    if not results:
        print("No results found.")
        return
    if header is not None:
        print(f"\n{ANSI.GREEN}{ANSI.BOLD}{header}{ANSI.RESET}\n")
    for i, item in enumerate(results, 1):
        _print_track_line(
            i,
            item.get("title",   "Unknown Title"),
            item.get("channel", "Unknown Channel"),
            format_duration(item.get("duration")),
        )


def print_playlist_results(results):
    print(
        f"\n{ANSI.GREEN}{ANSI.BOLD}Playlist loaded — "
        f"{len(results)} track{'s' if len(results) != 1 else ''}{ANSI.RESET}\n"
        f"{ANSI.DIM}Use  load  to push to queue, or  play <n>  to start a specific track.{ANSI.RESET}\n"
    )
    print_results(results[:COMPACT_THRESHOLD], None)
    if len(results) > COMPACT_THRESHOLD:
        print(f"  {ANSI.DIM}... and {len(results) - COMPACT_THRESHOLD} more{ANSI.RESET}")
    print()


def print_favs(favs: list[dict], compact: bool = True):
    _print_collection_header("Favorites", None, favs)
    display = favs[:COMPACT_THRESHOLD] if compact and len(favs) > COMPACT_THRESHOLD else favs
    for i, track in enumerate(display, 1):
        _print_track_line(
            i,
            track.get("title",   "Unknown Title"),
            track.get("channel", "Unknown Channel"),
            format_duration(track.get("duration")),
        )
    if compact and len(favs) > COMPACT_THRESHOLD:
        print(f"  {ANSI.DIM}... and {len(favs) - COMPACT_THRESHOLD} more  "
              f"(use  {ANSI.RESET}{ANSI.CYAN}favs --no-compact{ANSI.RESET}{ANSI.DIM}  to see all){ANSI.RESET}")
    print()


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


def print_playlist(name: str, tracks: list[dict], compact: bool = True):
    _print_collection_header("Playlist", name, tracks)
    display = tracks[:COMPACT_THRESHOLD] if compact and len(tracks) > COMPACT_THRESHOLD else tracks
    for i, track in enumerate(display, 1):
        _print_track_line(
            i,
            track.get("title",   "Unknown Title"),
            track.get("channel", "Unknown Channel"),
            format_duration(track.get("duration")),
        )
    if compact and len(tracks) > COMPACT_THRESHOLD:
        print(f"  {ANSI.DIM}... and {len(tracks) - COMPACT_THRESHOLD} more  "
              f"(use  {ANSI.RESET}{ANSI.CYAN}pl show {name} --no-compact{ANSI.RESET}{ANSI.DIM}  to see all){ANSI.RESET}")
    print()


# ── Seekbar ───────────────────────────────────────────────────────────────────

def _build_seekbar_content(time_pos, duration, inner: int) -> str:
    pos_sec = int(time_pos or 0)
    dur_sec = int(duration or 0)

    pos_str = format_duration(pos_sec)
    dur_str = format_duration(dur_sec) if dur_sec else "--:--"

    fixed = 1 + len(pos_str) + 1 + 1 + len(dur_str) + 1
    bar_width = max(4, inner - fixed)

    if dur_sec > 0:
        filled = max(0, min(int((pos_sec / dur_sec) * bar_width), bar_width))
    else:
        filled = 0

    bar = (
        f"{ANSI.GREEN}{'█' * filled}{ANSI.RESET}"
        f"{ANSI.DIM}{'░' * (bar_width - filled)}{ANSI.RESET}"
    )
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

    sys.stdout.write(f"\033[{row};1H{full_line}\033[999;1H")
    sys.stdout.flush()


# ── Autoplay dashboard ────────────────────────────────────────────────────────

def autoplay_dashboard(
    title:    str | None,
    artist:   str | None,
    duration: int | None,
    volume:   int,
    state:    str,
    queue:    list[dict],
    time_pos: float | None = None,
    loading:  bool         = False,
) -> int | None:
    width = max(30, min(shutil.get_terminal_size((90, 30)).columns - 2, 86))
    inner = width - 2

    top    = "╭" + "─" * inner + "╮"
    mid    = "├" + "─" * inner + "┤"
    bottom = "╰" + "─" * inner + "╯"

    def line(text=""):
        return "│" + text + (" " * max(0, inner - _visible_len(text))) + "│"

    def center(text):
        v     = _visible_len(text)
        left  = (inner - v) // 2
        right = inner - v - left
        return (" " * left) + text + (" " * right)

    if loading:
        state_icon = f"{ANSI.YELLOW}{ANSI.BOLD}~~{ANSI.RESET}"
    else:
        state_icon = {
            "playing":   f"{ANSI.BOLD}>>{ANSI.RESET}",
            "paused":    f"{ANSI.BOLD}||{ANSI.RESET}",
            "stopped":   f"{ANSI.BOLD}--{ANSI.RESET}",
            "buffering": f"{ANSI.BOLD}~~{ANSI.RESET}",
        }.get(state.lower(), "??")

    vol_len = 10
    fill    = int((volume / 100) * vol_len)
    vol_bar = ("■" * fill + "·" * (vol_len - fill))

    row = 1

    def emit(text):
        nonlocal row
        print(text)
        row += 1

    emit(top)

    left_label = f" {ANSI.BOLD}PX7-Music{ANSI.RESET}"
    r_key      = f"{ANSI.BLUE_BG}{ANSI.ITALIC} r {ANSI.RESET}"
    q_key      = f"{ANSI.RED_BG} X {ANSI.RESET}"
    spacing    = inner - _visible_len(left_label) - _visible_len(r_key) - _visible_len(' ') - _visible_len(q_key) - _visible_len(' ')
    emit(line(left_label + (" " * spacing) + r_key + ' ' + q_key + ' '))

    emit(mid)
    emit(line())

    if title is None:
        hint = f"{ANSI.DIM}Press  N  to start{ANSI.RESET}" if queue else f"{ANSI.DIM}Use  play <n>  to start{ANSI.RESET}"
        emit(line(center(f"{ANSI.DIM}No track playing{ANSI.RESET}")))
        emit(line(center(hint)))
    elif loading:
        emit(line(center(f"{ANSI.DIM}Loading...{ANSI.RESET}")))
        emit(line(center(f"{ANSI.DIM}Loading...{ANSI.RESET}")))
    else:
        display_title  = truncate_pad(title,  inner - 10).strip()
        display_artist = truncate_pad(artist, inner - 10).strip()
        emit(line(center(f"{ANSI.BOLD}{display_title}{ANSI.RESET}")))
        emit(line(center(f"{ANSI.DIM}{display_artist}{ANSI.RESET}")))

    emit(line())

    if title is not None:
        seek_content = _build_seekbar_content(time_pos, duration, inner)
        seekbar_line = "│" + seek_content + (" " * max(0, inner - _visible_len(seek_content))) + "│"
        seekbar_row  = row
        emit(seekbar_line)
        emit(line())
    else:
        seekbar_row = None

    emit(line(center(f"[<]    {state_icon}    [>]")))
    emit(line())

    emit(line(center(f"{ANSI.GRAY}VOL{ANSI.RESET} {vol_bar} {volume:3d}%")))
    emit(line())

    label      = " UP NEXT "
    left_side  = (inner - len(label)) // 2
    right_side = inner - len(label) - left_side
    emit(line("─" * left_side + label + "─" * right_side))

    if not queue:
        emit(line(center(f"{ANSI.DIM}Queue is empty{ANSI.RESET}")))
    else:
        _QUEUE_STYLES: tuple[str, ...] = (
            "\033[38;2;220;220;220m",
            "\033[38;2;130;130;130m",
            "\033[38;2;90;90;90m",
        )
        for idx, track in enumerate(queue):
            item:  str = truncate_pad(f"  {track.get('title', 'Unknown Title')}", inner).rstrip()
            style: str = _QUEUE_STYLES[idx] if idx < len(_QUEUE_STYLES) else "\033[38;2;65;65;65m"
            emit(line(f"{style}{item}{ANSI.RESET}"))

    emit(line())
    emit(bottom)

    sys.stdout.write("\033[999;1H")
    sys.stdout.flush()

    return seekbar_row