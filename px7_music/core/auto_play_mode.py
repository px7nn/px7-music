import sys 
import time
import shutil
import threading

import px7_music.player.playback as Playback

from px7_music.utility import autoplay_dashboard, update_seekbar


# ── Module-level state ────────────────────────────────────────────────────────

AUTO_PLAY     = False
EXIT_MENU     = False
FORCE_REFRESH = False
LOADING       = False


# ── Platform-specific raw key reader ─────────────────────────────────────────

if sys.platform.startswith('win'):
    import msvcrt

    def getch() -> str | None:
        ch = msvcrt.getch()
        if ch in (b'\x00', b'\xe0'):        # special / arrow keys
            msvcrt.getch()
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
                if ch == '\x1b':            # consume escape sequence
                    sys.stdin.read(2)
                    return None
                if ch in ('\x03', '\x1A'):  # Ctrl+C / Ctrl+Z
                    raise KeyboardInterrupt
                return ch
            finally: 
                _restore_terminal()


# ── Cursor helpers ────────────────────────────────────────────────────────────

def _hide_cursor():
    sys.stdout.write("\033[?25l")
    sys.stdout.flush()

def _show_cursor():
    sys.stdout.write("\033[?25h")
    sys.stdout.flush()


# ── Public enable / disable ───────────────────────────────────────────────────

def enable_auto_play(_=None):
    global AUTO_PLAY
    AUTO_PLAY = True


def disable_auto_play():
    global AUTO_PLAY
    AUTO_PLAY = False


# ── Key action handlers (module-level so global declarations are valid) ───────

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

def _quit() -> None:
    global EXIT_MENU, AUTO_PLAY
    EXIT_MENU = True
    AUTO_PLAY = False

_KEY_MAP = {
    "q":  _quit,
    "x":  _quit,
    "r":  _force_refresh,
    "+":  _vol_up,
    "=":  _vol_up,
    "-":  _vol_down,
    "_":  _vol_down,
    "n":  _nav_next,
    ">":  _nav_next,
    ".":  _nav_next,
    "p":  _nav_prev,
    "<":  _nav_prev,
    ",":  _nav_prev,
    " ":  _toggle_pause,
}


# ── Input listener thread ─────────────────────────────────────────────────────

def _input_listener():
    global EXIT_MENU, AUTO_PLAY, FORCE_REFRESH, LOADING
    while not EXIT_MENU:
        try:
            key = getch()
        except (EOFError, KeyboardInterrupt):
            EXIT_MENU = True
            AUTO_PLAY = False
            break

        if key is None: continue
            
        action = _KEY_MAP.get(key.lower())
        if action:
            try:
                action()
            except Exception:
                pass


# ── Main loop ─────────────────────────────────────────────────────────────────

def run_auto_play_mode():
    global EXIT_MENU, FORCE_REFRESH, LOADING

    EXIT_MENU = False

    _seekbar_row        = None
    _last_seekbar_pos   = -1

    last_index  = None
    last_vol    = None
    last_state  = None
    last_size   = shutil.get_terminal_size()

    _hide_cursor()

    t = threading.Thread(target=_input_listener, daemon=True)
    t.start()

    try:
        while not EXIT_MENU:
            Playback.poll_autoplay()

            current       = Playback.CURRENT_INDEX
            current_vol   = Playback.player.get_volume()
            current_state = Playback.player.get_state()
            current_size  = shutil.get_terminal_size()

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

                queue    = Playback.QUEUE
                no_track = not queue or current == -1
                up_next  = queue[0:4] if no_track else queue[current + 1:current + 5]
                time_pos = Playback.player.get_time_pos() if not no_track else None
                duration = queue[current].get('duration') if not no_track else None

                _seekbar_row = autoplay_dashboard(
                    queue[current].get('title', 'Unknown Title')     if not no_track else None,
                    queue[current].get('channel', 'Unknown Channel') if not no_track else None,
                    duration,
                    current_vol,
                    current_state,
                    up_next,
                    time_pos,
                    LOADING,
                )

                last_index  = current
                last_vol    = current_vol
                last_state  = current_state
                last_size   = current_size
                _last_seekbar_pos = int(time_pos or 0)
            
            else:
                if _seekbar_row is not None:
                    queue    = Playback.QUEUE
                    no_track = not queue or current == -1
                    if not no_track:
                        time_pos = Playback.player.get_time_pos()
                        cur_sec  = int(time_pos or 0)
                        if cur_sec != _last_seekbar_pos:
                            _last_seekbar_pos = cur_sec
                            update_seekbar(_seekbar_row, time_pos, queue[current].get("duration"))

            time.sleep(0.3)

    finally:
        _show_cursor()