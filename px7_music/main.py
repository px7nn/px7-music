import os
import sys
import px7_music.core.handler               as Handler
import px7_music.core.auto_play_mode        as AP
import px7_music.player.playback            as Playback

from px7_music                   import __version__, __os__
from px7_music.config            import ERROR_TRACEBACK
from px7_music.core              import latency
from px7_music.core              import CommandParser
from px7_music.core              import seek_handler
from px7_music.player            import get_player
from px7_music.utility           import ANSI, Preloader, clear_screen, set_runtime_banner
from px7_music.utility.docs      import print_installation_guide, get_help_text

sys.tracebacklimit = ERROR_TRACEBACK
sys.stderr = open(os.devnull, "w")

cmd_parser  =   CommandParser()
spinner     =   Preloader()


def register_commands():
    cmd_parser.register("autoplay", AP.enable_auto_play)    # enables autoplay
    cmd_parser.register("/a",       AP.enable_auto_play)    # enables autoplay

    cmd_parser.register("volume",   Handler.volume_handler) # set or get volume
    cmd_parser.register("search",   Handler.search_handler) # search and fills the queue {supports flag}
    cmd_parser.register("/s",       Handler.search_handler) # search and fills the queue {supports flag}
    cmd_parser.register("pl",       Handler.pl_handler)     # playlist commands
    cmd_parser.register("play",     Handler.play_handler)   # play <index from queue>
    cmd_parser.register("fav",      Handler.fav_handler)
    cmd_parser.register("favs",     Handler.favs_handler)
    cmd_parser.register("latency",  Handler.latency_handler)# shows network latency
    cmd_parser.register("seek",     seek_handler)           # seek current or change
    cmd_parser.register("exit",     Handler.exit_handler)   # exits the program

    cmd_parser.register("current",  Playback.show_current)  # shows info of current playing track
    cmd_parser.register("now",      Playback.show_current)  # shows info of current playing track
    cmd_parser.register("next",     Playback.play_next)     # plays next track from queue
    cmd_parser.register("prev",     Playback.play_prev)     # plays prev track from queue
    cmd_parser.register("queue",    Playback.show_queue)    # shows current queue
    cmd_parser.register("resume",   Playback.resume)        # resume track
    cmd_parser.register("pause",    Playback.pause)         # pause track
    cmd_parser.register("load",     Playback.load)          # loads last searched result into queue
    cmd_parser.register("shuffle",  Playback.shuffle_queue) # shuffles the queue respecting the current playing track

    cmd_parser.register("help",     get_help_text)          # detailed documentation of available commands
    cmd_parser.register("clear",    clear_screen)           # clears the terminal and prints banner
    cmd_parser.register("cls",      clear_screen)           # clears the terminal and prints banner


def startup() -> int | None:
    spinner.start("Getting player ... ")
    try:
        pname, player = get_player()
    finally:
        spinner.stop()

    if pname is None:
        print_installation_guide(__os__)
        return None

    Playback.init_player(pname, player)

    # Banner is built here — first and only clear_screen
    set_runtime_banner(version=__version__, os_name=__os__, player=pname)
    clear_screen()

    spinner.start("Checking Network ... ")
    connectivity: int | None = latency.get_latency()
    spinner.stop()

    if connectivity is None:
        print(f"{ANSI.RED}⚠ Network check failed.{ANSI.RESET}")
        return None

    register_commands()
    return 0


def main():
    if startup() is None:
        return

    # main loop
    while True:
        try:
            if AP.AUTO_PLAY:
                AP.run_auto_play_mode()
                # EXECUTES AFTER AP is disabled
                clear_screen()
                print(f"{ANSI.DIM}Exited autoplay mode{ANSI.RESET}\n")
                continue

            command: str = input(">> ")
            cmd_parser.parse(command)

        except (KeyboardInterrupt, EOFError):
            Handler.exit_handler()
            break


if __name__ == "__main__":
    main()