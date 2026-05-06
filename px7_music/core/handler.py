import px7_music.player.playback    as Playback

from px7_music.config               import DEFAULT_SEARCH_LIMIT, DEFAULT_QUERY_POSTFIX
from px7_music.core.parser          import break_args, parse_flags
from px7_music.library              import favorites
from px7_music.library.favorites    import FavoriteError
from px7_music.utility.utils        import ANSI, fmt_track

SEARCH_FLAGS = {
    "limit": int,
    "no-postfix": bool,
}
PLAY_FLAGS = {}
VOLUME_FLAGS = {}
FAV_FLAGS = {}

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


def fav_handler(args):
    if not args:
        print(
            f"{ANSI.YELLOW}Usage:{ANSI.RESET}\n"
            f"  fav add [index|all]\n"
            f"  fav remove <index|all>"
        )
        return

    cmd = args[0].lower()

    # ── ADD ──────────────────────────────────────────────────────────────────
    if cmd == "add":

        # >> fav add  (currently playing)
        if len(args) == 1:
            if Playback.CURRENT_INDEX == -1:
                print(f"{ANSI.YELLOW}Nothing is playing. Start a track first.{ANSI.RESET}")
                return

            track = Playback.QUEUE[Playback.CURRENT_INDEX]
            try:
                favorites.add_favorite(track)
                print(f"{ANSI.GREEN}♥  Added to favorites:{ANSI.RESET} {fmt_track(track)}")
            except FavoriteError as e:
                print(f"{ANSI.DIM}{e}{ANSI.RESET}")
            return

        target = args[1].lower()

        # >> fav add all
        if target == "all":
            if not Playback.QUEUE:
                print(
                    f"{ANSI.YELLOW}Queue is empty — nothing to add.\n"
                    f"Use 'play' or 'load' after searching.{ANSI.RESET}"
                )
                return

            added, skipped = 0, 0
            for track in Playback.QUEUE:
                try:
                    favorites.add_favorite(track)
                    added += 1
                except FavoriteError:
                    skipped += 1

            parts = []
            if added:
                parts.append(f"{ANSI.GREEN}♥  Added {added} track{'s' if added != 1 else ''}{ANSI.RESET}")
            if skipped:
                parts.append(f"{ANSI.DIM}{skipped} already in favorites{ANSI.RESET}")

            print("  ".join(parts) if parts else "No tracks added.")
            return

        # >> fav add <index>
        try:
            idx = int(target) - 1
        except ValueError:
            print(f"{ANSI.YELLOW}Invalid argument '{target}'. Usage: fav add <index|all>{ANSI.RESET}")
            return

        if not Playback.QUEUE:
            print(f"{ANSI.YELLOW}Queue is empty. Use 'play' or 'load' after searching.{ANSI.RESET}")
            return

        if idx < 0 or idx >= len(Playback.QUEUE):
            print(
                f"{ANSI.YELLOW}Index {idx + 1} is out of range "
                f"(queue has {len(Playback.QUEUE)} track{'s' if len(Playback.QUEUE) != 1 else ''}).{ANSI.RESET}"
            )
            return

        track = Playback.QUEUE[idx]
        try:
            favorites.add_favorite(track)
            print(
                f"{ANSI.GREEN}♥  Added to favorites (queue #{idx + 1}):{ANSI.RESET} "
                f"{fmt_track(track)}"
            )
        except FavoriteError as e:
            print(f"{ANSI.DIM}{e}{ANSI.RESET}")
        return

    # ── REMOVE ───────────────────────────────────────────────────────────────
    elif cmd == "remove":

        if len(args) < 2:
            print(f"{ANSI.YELLOW}Usage: fav remove <index|all>{ANSI.RESET}")
            return

        target = args[1].lower()

        # >> fav remove all
        if target == "all":
            # load first just to show count in the prompt
            favs = favorites.load_favorites()
            if not favs:
                print(f"{ANSI.YELLOW}Favorites are already empty.{ANSI.RESET}")
                return

            count = len(favs)
            confirm = input(
                f"{ANSI.YELLOW}WARNING: This will permanently remove all {count} "
                f"favorite{'s' if count != 1 else ''}.\n"
                f"This action is NOT reversible.\n{ANSI.RESET}"
                "Continue? (y/n): "
            ).strip().lower()

            if confirm != "y":
                print("Cancelled.")
                return

            try:
                count = favorites.clear_favorites()
                print(f"{ANSI.GREEN}Removed all {count} favorite{'s' if count != 1 else ''}.{ANSI.RESET}")
            except FavoriteError as e:
                print(f"{ANSI.YELLOW}{e}{ANSI.RESET}")
            return

        # >> fav remove <index>
        try:
            idx = int(target) - 1
        except ValueError:
            print(f"{ANSI.YELLOW}Invalid argument '{target}'. Usage: fav remove <index|all>{ANSI.RESET}")
            return

        try:
            track = favorites.remove_favorite(idx)
            print(
                f"{ANSI.DIM}Removed from favorites (#{idx + 1}):{ANSI.RESET} "
                f"{fmt_track(track)}"
            )
        except FavoriteError as e:
            print(f"{ANSI.YELLOW}{e}{ANSI.RESET}")
        return

    else:
        print(
            f"{ANSI.YELLOW}Unknown subcommand '{cmd}'. "
            f"Valid options: add, remove{ANSI.RESET}"
        )


def favs_handler(_=None):
    favs = favorites.load_favorites()

    if not favs:
        print(
            f"{ANSI.DIM}No favorites yet.  "
            f"Use {ANSI.RESET}{ANSI.CYAN}fav add{ANSI.RESET}"
            f"{ANSI.DIM} to save a track.{ANSI.RESET}"
        )
        return

    Playback.list_favs(favs)