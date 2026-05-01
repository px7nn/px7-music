from px7_music.config               import DEFAULT_SEARCH_LIMIT, DEFAULT_QUERY_POSTFIX
from px7_music.core.parser          import break_args, parse_flags
from px7_music.player.playback      import search, play, get_volume, set_volume, kill_player, play_next
from px7_music.utility.utils        import ANSI

SEARCH_FLAGS = {
    "limit": int,
    "no-postfix": bool,
}
PLAY_FLAGS = {}
VOLUME_FLAGS = {}

def exit_handler(_=None):
    print("Exiting...")
    kill_player()
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
    search(query, limit)
    

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

    play(idx)
    

def volume_handler(args: list[str]):
    vol, flags = break_args(args)

    try:
        flags = parse_flags(flags, VOLUME_FLAGS)
    except ValueError as e:
        print(f"{ANSI.YELLOW}{e}{ANSI.RESET}")
        return
    
    if not vol:
        get_volume()
        return

    try:
        vol = int(vol)
    except ValueError:
        print("Invalid volume level.")
        return
    
    set_volume(vol)
