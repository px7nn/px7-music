import sys 
import time
import shutil
import threading

import px7_music.player.playback as Playback

from px7_music.utility import autoplay_dashboard, update_seekbar, update_lyrics
from px7_music.core.lrclib import (
    fetch_lyrics,
    parse_lrc,
    extract_artist_and_title,
    find_active_index,
    get_display_lyrics_lines,
)


# -- Module-level state ------------------------------------------------------

JUKEBOX       = False
SHOW_LYRICS   = False
EXIT_MENU     = False
FORCE_REFRESH = False
LOADING       = False

IS_PLAIN_LYRICS = False
PLAIN_LYRIC_MAX = 0
PLAIN_LYRIC_IDX = 0
FORCE_PLAIN     = False


# -- Platform-specific raw key reader ----------------------------------------

if sys.platform.startswith('win'):
    import msvcrt

    def getch() -> str | None:
        ch = msvcrt.getch()
        if ch in (b'\x00', b'\xe0'):        # special / arrow keys
            ch2 = msvcrt.getch()
            if ch2 == b'H': return "UP"
            if ch2 == b'P': return "DOWN"
            return None
        if ch in (b'\x03', b'\x1A'):        # Ctrl + [C, Z]
            raise KeyboardInterrupt
        return ch.decode(errors="ignore")
    
else:
    import tty
    import termios
    import atexit

    _fd  = sys.stdin.fileno()
    _old = termios.tcgetattr(_fd)

    def _restore_terminal():
        termios.tcsetattr(_fd, termios.TCSADRAIN, _old)

    atexit.register(_restore_terminal)

    def getch() -> str | None:
        try:
            tty.setcbreak(_fd)
            ch = sys.stdin.read(1)
            if ch == '\x1b':            # escape sequence
                seq = sys.stdin.read(2)
                if seq == "[A": return "UP"
                if seq == "[B": return "DOWN"
                return None
            if ch in ('\x03', '\x1A'):  # Ctrl+C / Ctrl+Z
                raise KeyboardInterrupt
            return ch
        finally: 
            _restore_terminal()


# -- Cursor helpers ------------------------------------------------------

def _hide_cursor():
    sys.stdout.write("\033[?25l")
    sys.stdout.flush()

def _show_cursor():
    sys.stdout.write("\033[?25h")
    sys.stdout.flush()


# -- Public enable / disable ---------------------------------------------

def enable_jukebox(_=None):
    global JUKEBOX, SHOW_LYRICS
    JUKEBOX = True
    SHOW_LYRICS = False

def enable_lyrics(_=None):
    global JUKEBOX, SHOW_LYRICS
    JUKEBOX = True
    SHOW_LYRICS = True

def disable_jukebox():
    global JUKEBOX, EXIT_MENU
    JUKEBOX = False
    EXIT_MENU = True

def disable_lyrics():
    disable_jukebox()


# -- Key action handlers (module-level so global declarations are valid) ----------

def _vol_up() -> None:
    Playback.player.set_volume(Playback.player.get_volume() + 10)

def _vol_down() -> None:
    Playback.player.set_volume(Playback.player.get_volume() - 10)

def _nav_next() -> None:
    global LOADING, FORCE_REFRESH
    LOADING = True
    FORCE_REFRESH = True
    Playback.play_next()
    LOADING = False
    FORCE_REFRESH = True

def _nav_prev() -> None:
    global LOADING, FORCE_REFRESH
    LOADING = True
    FORCE_REFRESH = True
    Playback.play_prev()
    LOADING = False
    FORCE_REFRESH = True

def _toggle_pause() -> None:
    if not Playback.player.is_idle():
        if Playback.player.is_paused():
            Playback.player.resume()
        else:
            Playback.player.pause()

def _force_refresh() -> None:
    global FORCE_REFRESH
    FORCE_REFRESH = True

def _toggle_lyrics() -> None:
    global SHOW_LYRICS, FORCE_REFRESH
    SHOW_LYRICS = not SHOW_LYRICS
    FORCE_REFRESH = True

def _scroll_lyrics_up() -> None:
    global PLAIN_LYRIC_IDX
    if SHOW_LYRICS and IS_PLAIN_LYRICS:
        if PLAIN_LYRIC_IDX > 0:
            PLAIN_LYRIC_IDX -= 1

def _scroll_lyrics_down() -> None:
    global PLAIN_LYRIC_IDX
    if SHOW_LYRICS and IS_PLAIN_LYRICS:
        if PLAIN_LYRIC_IDX < PLAIN_LYRIC_MAX:
            PLAIN_LYRIC_IDX += 1

def _toggle_lyrics_mode() -> None:
    global FORCE_PLAIN, FORCE_REFRESH
    if SHOW_LYRICS:
        FORCE_PLAIN = not FORCE_PLAIN
        FORCE_REFRESH = True

def _quit() -> None:
    global EXIT_MENU, JUKEBOX
    EXIT_MENU = True
    JUKEBOX = False

_KEY_MAP = {
    "q":    _quit,
    "x":    _quit,
    "r":    _force_refresh,
    "l":    _toggle_lyrics,
    "\t":   _toggle_lyrics,
    "s":    _toggle_lyrics_mode,
    "+":    _vol_up,
    "=":    _vol_up,
    "-":    _vol_down,
    "_":    _vol_down,
    "n":    _nav_next,
    ">":    _nav_next,
    ".":    _nav_next,
    "p":    _nav_prev,
    "<":    _nav_prev,
    ",":    _nav_prev,
    " ":    _toggle_pause,
    "up":   _scroll_lyrics_up,
    "down": _scroll_lyrics_down,
}


# -- Input listener thread ---------------------------------------------------------

def _input_listener():
    global EXIT_MENU, JUKEBOX, FORCE_REFRESH, LOADING
    while not EXIT_MENU:
        try:
            key = getch()
        except (EOFError, KeyboardInterrupt):
            EXIT_MENU = True
            JUKEBOX = False
            break

        if key is None: continue
            
        action = _KEY_MAP.get(key.lower())
        if action:
            try:
                action()
            except Exception:
                pass


# -- Main loop -----------------------------------------------------------

def run_jukebox_mode():
    global EXIT_MENU, FORCE_REFRESH, LOADING, JUKEBOX, IS_PLAIN_LYRICS, PLAIN_LYRIC_MAX, PLAIN_LYRIC_IDX, FORCE_PLAIN

    EXIT_MENU = False

    _seekbar_row        = None
    _lyrics_row         = None
    _last_seekbar_pos   = -1

    last_index          = None
    last_vol            = None
    last_state          = None
    last_size           = shutil.get_terminal_size()
    last_lyric_idx      = None
    last_lyrics_track   = None

    current_lyrics_data = None
    parsed_lrc          = []

    _hide_cursor()

    t = threading.Thread(target=_input_listener, daemon=True)
    t.start()

    try:
        while not EXIT_MENU:
            Playback.poll_jukebox()

            current       = Playback.CURRENT_INDEX
            current_vol   = Playback.player.get_volume()
            current_state = Playback.player.get_state()
            current_size  = shutil.get_terminal_size()

            queue    = Playback.QUEUE
            no_track = not queue or current == -1
            time_pos = Playback.player.get_time_pos() if not no_track else None
            duration = queue[current].get('duration') if not no_track else None

            # Fetch lyrics when lyrics mode is enabled and lyrics not yet fetched for current track
            if SHOW_LYRICS and not no_track and (current != last_lyrics_track or (FORCE_REFRESH and current_lyrics_data is None)):
                last_lyrics_track = current
                raw_title = queue[current].get('title', '')
                raw_chan  = queue[current].get('channel', '')
                artist, title = extract_artist_and_title(raw_title, raw_chan)
                current_lyrics_data = fetch_lyrics(title, artist, duration)
                if current_lyrics_data and current_lyrics_data.get('synced_lyrics'):
                    parsed_lrc = parse_lrc(current_lyrics_data['synced_lyrics'])
                else:
                    parsed_lrc = []

                if current_lyrics_data and not current_lyrics_data.get('plain_lyrics') and parsed_lrc:
                    current_lyrics_data['plain_lyrics'] = "\n".join(t for _, t in parsed_lrc if t.strip())

                plain_text = (current_lyrics_data or {}).get("plain_lyrics", "")
                plain_count = len([l for l in plain_text.splitlines() if l.strip()]) if plain_text else 0
                PLAIN_LYRIC_MAX = max(0, plain_count - 1)
                PLAIN_LYRIC_IDX = 0
                last_lyric_idx = None
            elif current != last_index:
                last_lyrics_track = None
                current_lyrics_data = None
                parsed_lrc = []
                IS_PLAIN_LYRICS = False
                PLAIN_LYRIC_MAX = 0
                PLAIN_LYRIC_IDX = 0
                FORCE_PLAIN = False
                last_lyric_idx = None

            plain_text = (current_lyrics_data or {}).get("plain_lyrics", "")
            plain_count = len([l for l in plain_text.splitlines() if l.strip()]) if plain_text else 0
            has_synced = bool(parsed_lrc)
            has_plain  = bool(plain_count > 0)

            if SHOW_LYRICS:
                if has_synced and not FORCE_PLAIN:
                    IS_PLAIN_LYRICS = False
                    lyrics_type = "synced"
                    active_lyric_idx = find_active_index(parsed_lrc, time_pos or 0)
                elif has_plain:
                    IS_PLAIN_LYRICS = True
                    lyrics_type = "plain"
                    active_lyric_idx = PLAIN_LYRIC_IDX
                else:
                    IS_PLAIN_LYRICS = False
                    lyrics_type = None
                    active_lyric_idx = None
            else:
                lyrics_type = None
                active_lyric_idx = None

            needs_redraw  = (
                FORCE_REFRESH
                or current       != last_index
                or current_state != last_state
                or current_vol   != last_vol
                or current_size  != last_size
            )
            
            if needs_redraw:
                sys.stdout.write("\033[2J\033[3J\033[H")
                sys.stdout.flush()
                FORCE_REFRESH = False

                up_next = queue[0:5] if no_track else queue[current + 1:current + 6]
                lrc_to_pass = [] if IS_PLAIN_LYRICS else parsed_lrc
                lyrics_lines = get_display_lyrics_lines(
                    current_lyrics_data,
                    lrc_to_pass,
                    time_pos,
                    LOADING,
                    count=5,
                    plain_idx=PLAIN_LYRIC_IDX,
                ) if SHOW_LYRICS else None

                _seekbar_row, _lyrics_row = autoplay_dashboard(
                    queue[current].get('title', 'Unknown Title')     if not no_track else None,
                    queue[current].get('channel', 'Unknown Channel') if not no_track else None,
                    duration,
                    current_vol,
                    current_state,
                    up_next,
                    time_pos,
                    LOADING,
                    show_lyrics=SHOW_LYRICS,
                    lyrics_lines=lyrics_lines,
                    lyrics_type=lyrics_type,
                )

                last_index        = current
                last_vol          = current_vol
                last_state        = current_state
                last_size         = current_size
                last_lyric_idx    = active_lyric_idx
                _last_seekbar_pos = int(time_pos or 0)
            
            else:
                if not no_track:
                    if SHOW_LYRICS and _lyrics_row is not None:
                        if active_lyric_idx != last_lyric_idx:
                            last_lyric_idx = active_lyric_idx
                            lrc_to_pass = [] if IS_PLAIN_LYRICS else parsed_lrc
                            lyrics_lines = get_display_lyrics_lines(
                                current_lyrics_data,
                                lrc_to_pass,
                                time_pos,
                                LOADING,
                                count=5,
                                plain_idx=PLAIN_LYRIC_IDX,
                            )
                            update_lyrics(_lyrics_row, lyrics_lines)

                    if _seekbar_row is not None:
                        cur_sec = int(time_pos or 0)
                        if cur_sec != _last_seekbar_pos:
                            _last_seekbar_pos = cur_sec
                            update_seekbar(_seekbar_row, time_pos, queue[current].get("duration"))

            time.sleep(0.3)

    finally:
        _show_cursor()
        JUKEBOX = False