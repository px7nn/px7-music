import sys
import px7_music.core.handler               as Handler
import px7_music.player.auto_play_mode      as AP
import px7_music.player.playback            as Playback

from px7_music.config           import ERROR_TRACBACK
from px7_music.core             import latency
from px7_music.core.parser      import CommandParser
from px7_music.player.player    import get_player
from px7_music.utility.docs     import get_installation_guide, get_help_text
from px7_music.utility.utils    import ANSI, Preloader, clear_screen


sys.tracebacklimit = ERROR_TRACBACK
cmd_parser  =   CommandParser()
spinner     =   Preloader()


def register_commands():
    cmd_parser.register("auto-play", AP.enable_auto_play) # enables autoplay
    
    cmd_parser.register("volume",   Handler.volume_handler) # set or get volume
    cmd_parser.register("search",   Handler.search_handler) # search and fills the queue {supports flag}
    cmd_parser.register("/s",       Handler.search_handler) # search and fills the queue {supports flag}
    cmd_parser.register("play",     Handler.play_handler)   # play <index from queue>
    cmd_parser.register("exit",     Handler.exit_handler)   # exits the program

    cmd_parser.register("current",  Playback.show_current)  # shows info of current playing track
    cmd_parser.register("now",      Playback.show_current)  # shows info of current playing track
    cmd_parser.register("next",     Playback.play_next)     # plays next track from queue
    cmd_parser.register("prev",     Playback.play_prev)     # plays prev track from queue
    cmd_parser.register("queue",    Playback.show_queue)    # shows current queue
    cmd_parser.register("resume",   Playback.resume)        # resume track
    cmd_parser.register("pause",    Playback.pause)         # pause track

    cmd_parser.register("help",     get_help_text)

    cmd_parser.register("latency",  check_network)          # shows network latency
    cmd_parser.register("clear",    clear_screen)           # clears the terminal and prints banner
    cmd_parser.register("cls",      clear_screen)           # clears the terminal and prints banner
    

def init():
    spinner.start("Getting player   ")
    try:
        pname, player = get_player()
    except RuntimeError as e:
        spinner.stop()
        print(f"\n{ANSI.RED}{e}{ANSI.RESET}")
        return None
    spinner.stop()
    
    if pname is None:
        print(f"{get_installation_guide()}")
        return None
    
    Playback.init_player(pname, player)
    print(f"Player: {pname}\n")
    return 0
    

def check_network(_=None):
    spinner.start("Checking Network   ")
    connectivity: int = latency.get_latency()
    spinner.stop()

    if connectivity is None:
        print(f"{ANSI.RED}⚠ Network check failed.{ANSI.RESET}")
        return None
    if _ != True:
        print(f"Latency: {connectivity} ms\n")
    return 0


def main():
    clear_screen()

    # Check system
    if init() is None or check_network(True) is None:
        return

    register_commands()

    # main loop
    while True:
        try:
            if AP.AUTO_PLAY: 
                AP.run_auto_play_mode()
                clear_screen()
                print(f"{ANSI.DIM}Exited auto-play mode{ANSI.RESET}\n")
                continue

            command: str = input(">> ")
            cmd_parser.parse(command)

        except (KeyboardInterrupt, EOFError):
            Handler.exit_handler()
            break

    
if __name__ == "__main__":
    main()