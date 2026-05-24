import sys, time, threading
import px7_music.player.playback as Playback

from px7_music.config           import BANNER_TEXT_DEFAULT
from px7_music.utility.utils    import ANSI


AUTO_PLAY = False
EXIT_MENU = False


if sys.platform.startswith('win'):
    import msvcrt
    def getch():
        ch = msvcrt.getch()
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
    global EXIT_MENU, AUTO_PLAY

    while not EXIT_MENU:
        try:
            key = getch().lower()
        except (EOFError, KeyboardInterrupt):
            EXIT_MENU = True
            AUTO_PLAY = False
            break
        
        if key == "q":
            EXIT_MENU = True
            AUTO_PLAY = False


        elif key == "n":
            Playback.play_next()

        elif key == "p":
            Playback.play_prev()

        elif key == " " and not Playback.player.is_idle():
            if Playback.player.is_paused():
                Playback.player.resume()
            else:
                Playback.player.pause()


def run_auto_play_mode():
    global EXIT_MENU

    EXIT_MENU = False

    last_index = None
    last_state = None

    # start input thread
    t = threading.Thread(target=_input_listener, daemon=True)
    t.start()

    while not EXIT_MENU:
        Playback.poll_autoplay()

        current = Playback.CURRENT_INDEX
        current_state = Playback.player.get_state()

        if current != last_index or current_state != last_state:
            sys.stdout.write("\033[2J\033[3J\033[H")
            sys.stdout.flush()

            print(f"{ANSI.RED}{BANNER_TEXT_DEFAULT}{ANSI.RESET}")
            print(f"{ANSI.RED}     - - Auto Play Mode - -{ANSI.RESET}")
            print(f"\n{ANSI.BOLD}Controls:{ANSI.RESET}")
            print("     [N] Next        [P] Previous")
            print("     [Space] Pause/Play  [Q] Exit\n")

            print(f"\nState: {ANSI.BOLD}{current_state}{ANSI.RESET}\n")

            
            Playback.show_current()
            Playback.show_upnext()

            last_index = current
            last_state = current_state

        time.sleep(0.3)