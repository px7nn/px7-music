import sys, time, threading
import px7_music.player.playback as Playback

from px7_music.config           import BANNER_TEXT_DEFAULT
from px7_music.utility.utils    import ANSI, autoplay_dashboard


AUTO_PLAY = False
EXIT_MENU = False
FORCE_REFRESH = False


if sys.platform.startswith('win'):
    import msvcrt
    def getch():
        ch = msvcrt.getch()
        if ch in (b'\x00', b'\xe0'):                        # Special keys (Arrows)
            msvcrt.getch()
            return None
        if ch in (b'\x03', b'\x1A'):                        # Ctrl + [C, Z]
            raise KeyboardInterrupt
        return ch.decode(errors="ignore")
else:
    import tty, termios, atexit

    fd  = sys.stdin.fileno()
    old = termios.tcgetattr(fd)

    def restore_terminal():
        termios.tcsetattr(fd, termios.TCSADRAIN, old)

    atexit.register(restore_terminal)

    def getch():
            try:
                tty.setcbreak(fd)
                ch = sys.stdin.read(1)
                if ch == '\x1b':
                    sys.stdin.read(2)
                    return None                             # Arrows
                if ch in ('\x03', '\x1A'):                  # Ctrl + [C, Z]
                    raise KeyboardInterrupt
                return ch
            finally: restore_terminal()


def enable_auto_play(_=None):
    global AUTO_PLAY
    AUTO_PLAY = True


def disable_auto_play():
    global AUTO_PLAY
    AUTO_PLAY = False


def _input_listener():
    global EXIT_MENU, AUTO_PLAY, FORCE_REFRESH

    while not EXIT_MENU:
        try:
            key = getch()
            if key is None:
                continue
            key = key.lower()
            
        except (EOFError, KeyboardInterrupt):
            EXIT_MENU = True
            AUTO_PLAY = False
            break
        
        if key in ('q', 'x'):
            EXIT_MENU = True
            AUTO_PLAY = False

        elif key == 'r':
            FORCE_REFRESH = True

        elif key in ('+', '='):
            vol = Playback.player.get_volume()
            Playback.player.set_volume(vol + 10)

        elif key in ('-', '_'):
            vol = Playback.player.get_volume()
            Playback.player.set_volume(vol - 10)

        elif key in ('n', '>', '.'):
            Playback.play_next()

        elif key in ('p', '<', ','):
            Playback.play_prev()

        elif key == " " and not Playback.player.is_idle():
            if Playback.player.is_paused():
                Playback.player.resume()
            else:
                Playback.player.pause()


def run_auto_play_mode():
    global EXIT_MENU, FORCE_REFRESH

    EXIT_MENU = False

    last_index  = None
    last_vol = None
    last_state  = None

    # start input thread
    t = threading.Thread(target=_input_listener, daemon=True)
    t.start()

    while not EXIT_MENU:
        Playback.poll_autoplay()

        current = Playback.CURRENT_INDEX
        current_vol = Playback.player.get_volume()
        current_state = Playback.player.get_state()

        if FORCE_REFRESH or current != last_index or current_state != last_state or current_vol != last_vol:
            sys.stdout.write("\033[2J\033[3J\033[H")
            sys.stdout.flush()
            FORCE_REFRESH = False
            queue = Playback.QUEUE
            no_track = not queue or current == -1

            if no_track:
                up_next = queue[0:4]            # queue loaded but nothing playing yet
            else:
                up_next = queue[current+1:current+5]

            autoplay_dashboard(
                queue[current].get('title', 'Unknown Title')        if not no_track else None,
                queue[current].get('channel', 'Unknown Channel')    if not no_track else None,
                queue[current].get('duration')                      if not no_track else None,
                Playback.player.get_volume(),
                current_state,
                up_next,
            )

            last_index = current
            last_vol = current_vol
            last_state = current_state

        time.sleep(0.3)