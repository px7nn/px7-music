import sys, time, threading
import px7_music.player.playback as Playback

from px7_music.config           import BANNER_TEXT_DEFAULT
from px7_music.utility.utils    import ANSI


AUTO_PLAY = False
EXIT_MENU = False


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
            key = input().strip().lower()
        except EOFError:
            EXIT_MENU = True
            AUTO_PLAY = False
            break
        
        if key == "q" or key == "Q":
            EXIT_MENU = True
            AUTO_PLAY = False


        elif key == "n" or key == "N":
            Playback.play_next()

        elif key == "p" or key == "P":
            Playback.play_prev()

        elif key == "" and not Playback.player.is_idle():
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
            print(f"\n{ANSI.BOLD}Controls (press key then ENTER):\n")
            print(f"[N] Next | [P] Previous | [Q] Exit{ANSI.RESET}")
            print(f"{ANSI.BOLD}[ENTER] Pause/Resume{ANSI.RESET}\n")

            print(f"\nState: {ANSI.BOLD}{current_state}{ANSI.RESET}\n")

            
            Playback.show_current()
            Playback.show_upnext()

            last_index = current
            last_state = current_state

        time.sleep(0.3)