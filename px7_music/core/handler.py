import px7_music.player.playback    as Playback

from px7_music.config               import DEFAULT_SEARCH_LIMIT, DEFAULT_QUERY_POSTFIX
from px7_music.core.parser          import break_args, parse_flags
from px7_music.utility.utils        import ANSI

SEARCH_FLAGS = {
    "limit": int,
    "no-postfix": bool,
}
PLAY_FLAGS = {}
VOLUME_FLAGS = {}

def exit_handler(_=None):
    print("Exiting...")
    Playback.kill_player()
    exit(0)


def search_handler(args: list[str]):
    query, flags = break_args(args)

    if not query:
        print(f"{ANSI.YELLOW}Usage: search <query> [--limit=n] [--no-postfix]{ANSI.RESET}")
        return

    try:
        flags = parse_flags(flags, SEARCH_FLAGS)
    except ValueError as e:
        print(f"{ANSI.YELLOW}{e}{ANSI.RESET}")
        return

    limit = flags.get("limit", DEFAULT_SEARCH_LIMIT)
    no_postfix = flags.get("no-postfix", False)

    query += DEFAULT_QUERY_POSTFIX if not no_postfix else ""
    Playback.search(query, limit)
    

def play_handler(args: list[str]):
    idx, flags = break_args(args)

    if not idx:
        print(f"{ANSI.YELLOW}Usage: play <index>{ANSI.RESET}")
        return

    try:
        flags = parse_flags(flags, PLAY_FLAGS)
    except ValueError as e:
        print(f"{ANSI.YELLOW}{e}{ANSI.RESET}")
        return

    try:
        idx = int(idx)
    except ValueError:
        print("Invalid index")
        return

    Playback.play(idx)
    

def volume_handler(args: list[str]):
    vol, flags = break_args(args)

    try:
        flags = parse_flags(flags, VOLUME_FLAGS)
    except ValueError as e:
        print(f"{ANSI.YELLOW}{e}{ANSI.RESET}")
        return
    
    if not vol:
        Playback.get_volume()
        return

    try:
        vol = int(vol)
    except ValueError:
        print("Invalid volume level.")
        return
    
    Playback.set_volume(vol)