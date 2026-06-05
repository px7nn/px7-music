import px7_music.player.playback as Playback

from px7_music.core    import break_args, parse_flags, get_latency
from px7_music.config  import DEFAULT_SEARCH_LIMIT, DEFAULT_QUERY_POSTFIX
from px7_music.library import *
from px7_music.utility import ANSI, fmt_track, print_playlists

SEARCH_FLAGS = {
    "p":          bool,
    "limit":      int,
    "no-postfix": bool,
}
PLAY_FLAGS   = {}
VOLUME_FLAGS = {}
FAV_FLAGS    = {}
FAVS_FLAGS   = {
    "order":      str,   
    "limit":      int,   
    "reverse":    bool,
    "no-compact": bool,
}
PL_FLAGS = {
    "order":      str,   
    "limit":      int,
    "reverse":    bool,
    "no-compact": bool,
}
QUEUE_FLAGS = {
    "no-compact": bool,
}

RESERVED = {"list", "create", "delete", "rename", "add", "remove", "show", "load"}


# ── Utility handlers ──────────────────────────────────────────────────────────

def exit_handler(_=None):
    print("Exiting...")
    Playback.kill_player()
    exit(0)


def latency_handler(_: list | None = None) -> None:
    ms: int | None = get_latency()
    if ms is None:
        print(f"{ANSI.RED}⚠ Network check failed.{ANSI.RESET}")
    else:
        print(f"Latency: {ms} ms")


# ── Search / play ─────────────────────────────────────────────────────────────

def search_handler(args: list[str]):
    query, raw_flags = break_args(args)

    if not query:
        print(f"{ANSI.YELLOW}Usage: search <query> [--limit=n] [--no-postfix]{ANSI.RESET}")
        return

    try:
        flags = parse_flags(raw_flags, SEARCH_FLAGS)
    except ValueError as e:
        print(f"{ANSI.YELLOW}{e}{ANSI.RESET}")
        return
    
    if flags.get('p'):
        Playback.search_playlist(query)
        return

    limit      = flags.get("limit", DEFAULT_SEARCH_LIMIT)
    no_postfix = flags.get("no-postfix", False)
    full_query = query + ("" if no_postfix else DEFAULT_QUERY_POSTFIX)

    Playback.search(full_query, limit)
    

def play_handler(args: list[str]):
    idx_str, raw_flags = break_args(args)

    try:
        parse_flags(raw_flags, PLAY_FLAGS)
    except ValueError as e:
        print(f"{ANSI.YELLOW}{e}{ANSI.RESET}")
        return
    
    if not idx_str:
        Playback.play(1)
        return

    try:
        Playback.play(int(idx_str))
    except ValueError:
        print("Invalid index")
    

def volume_handler(args: list[str]):
    vol_str, raw_flags = break_args(args)

    try:
        parse_flags(raw_flags, VOLUME_FLAGS)
    except ValueError as e:
        print(f"{ANSI.YELLOW}{e}{ANSI.RESET}")
        return
    
    if not vol_str:
        Playback.get_volume()
        return

    try:
        Playback.set_volume(int(vol_str))
    except ValueError:
        print("Invalid volume level.")


# ── Queue ─────────────────────────────────────────────────────────────────────

def queue_handler(args: list[str]):
    _, raw_flags = break_args(args)

    try:
        flags = parse_flags(raw_flags, QUEUE_FLAGS)
    except ValueError as e:
        print(f"{ANSI.YELLOW}{e}{ANSI.RESET}")
        return

    no_compact = flags.get("no-compact", False)
    Playback.show_queue(no_compact=no_compact)


# ── Favorites ─────────────────────────────────────────────────────────────────

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


def favs_handler(args):
    sub, flags = break_args(args)
    if sub:
        print(f"{ANSI.YELLOW}Usage: favs [--limit=<n>] [--reverse] [--order=<name|date-added|duration>] [--no-compact]{ANSI.RESET}")
        return
    
    try:
        flags = parse_flags(flags, FAVS_FLAGS)
    except ValueError as e:
        print(f"{ANSI.YELLOW}{e}{ANSI.RESET}")
        return

    order      = flags.get("order",      None)
    reverse    = flags.get("reverse",    False)
    limit      = flags.get("limit",      None)
    no_compact = flags.get("no-compact", False)
    favs = favorites.get_favorites(order, reverse, limit)

    if not favs:
        print(
            f"{ANSI.DIM}No favorites yet.  "
            f"Use {ANSI.RESET}{ANSI.CYAN}fav add{ANSI.RESET}"
            f"{ANSI.DIM} to save a track.{ANSI.RESET}"
        )
        return

    # compact=False when --no-compact is set OR when a --limit was explicitly given
    compact = not no_compact and limit is None
    Playback.list_favs(favs, compact=compact)


# ── Playlists ─────────────────────────────────────────────────────────────────

def pl_handler(args: list[str]):
    if not args:
        args = ["list"]

    sub = args[0].lower()

    # ── Shorthand: pl <name> [show|load|add|remove] [...] ────────────────────
    if sub not in RESERVED:
        name = args[0]
        rest = args[1:]
        action = rest[0].lower() if rest and rest[0].lower() in RESERVED else "show"
        tail   = rest[1:] if action != "show" or (rest and rest[0].lower() == "show") else rest
        return pl_handler([action, name] + tail)

    # ── pl list ───────────────────────────────────────────────────────────────
    if sub == "list":
        plist = playlists.list_playlists()
        if not plist:
            print(f"{ANSI.DIM}No playlists yet.  {ANSI.RESET}Use {ANSI.CYAN}pl create <name>{ANSI.RESET}{ANSI.DIM} to make one.{ANSI.RESET}")
        else:
            print_playlists(plist)
        return

    # ── pl create <name> ─────────────────────────────────────────────────────
    if sub == "create":
        name = " ".join(args[1:])
        if not name:
            print(f"{ANSI.YELLOW}Usage: pl create <name>{ANSI.RESET}")
            return
        if name.lower() in RESERVED:
            print(f"{ANSI.YELLOW}Name cannot be a reserved keyword.{ANSI.RESET}")
            return
        try:
            playlists.create_playlist(name)
            print(f"{ANSI.GREEN}Created playlist:{ANSI.RESET} {ANSI.BOLD}{name}{ANSI.RESET}")
        except PlaylistError as e:
            print(f"{ANSI.YELLOW}{e}{ANSI.RESET}")
        return

    # ── pl delete <name> ─────────────────────────────────────────────────────
    if sub == "delete":
        name = " ".join(args[1:])
        if not name:
            print(f"{ANSI.YELLOW}Usage: pl delete <name>{ANSI.RESET}")
            return
        confirm = input(f"{ANSI.YELLOW}WARNING: Permanently delete playlist '{name}'?{ANSI.RESET}\nContinue? (y/n): ").strip().lower()
        if confirm != "y":
            print("Cancelled.")
            return
        try:
            playlists.delete_playlist(name)
            print(f"{ANSI.DIM}Deleted playlist '{name}'.{ANSI.RESET}")
        except PlaylistError as e:
            print(f"{ANSI.YELLOW}{e}{ANSI.RESET}")
        return

    # ── pl rename <old> -> <new> ──────────────────────────────────────────────
    if sub == "rename":
        rest = args[1:]
        if "->" not in rest:
            print(f"{ANSI.YELLOW}Usage: pl rename <old-name> -> <new-name>{ANSI.RESET}")
            return
        sep      = rest.index("->")
        old_name = " ".join(rest[:sep]).strip()
        new_name = " ".join(rest[sep + 1:]).strip()
        if not old_name or not new_name:
            print(f"{ANSI.YELLOW}Usage: pl rename <old-name> -> <new-name>{ANSI.RESET}")
            return
        try:
            playlists.rename_playlist(old_name, new_name)
            print(f"{ANSI.GREEN}Renamed:{ANSI.RESET} {ANSI.BOLD}{old_name}{ANSI.RESET} → {ANSI.BOLD}{new_name}{ANSI.RESET}")
        except PlaylistError as e:
            print(f"{ANSI.YELLOW}{e}{ANSI.RESET}")
        return

    # ── pl add <name> [index|all] ─────────────────────────────────────────────
    if sub == "add":
        last   = args[-1].lower() if len(args) > 1 else ""
        target = last if (last == "all" or last.isdigit()) else None
        name   = " ".join(args[1:-1] if target else args[1:])

        if not name:
            print(f"{ANSI.YELLOW}Usage: pl add <name> [index|all]{ANSI.RESET}")
            return

        if target is None:
            if Playback.CURRENT_INDEX == -1:
                print(f"{ANSI.YELLOW}Nothing is playing. Start a track first.{ANSI.RESET}")
                return
            track = Playback.QUEUE[Playback.CURRENT_INDEX]
            try:
                playlists.add_track(name, track)
                print(f"{ANSI.GREEN}♪  Added to '{name}':{ANSI.RESET} {fmt_track(track)}")
            except PlaylistError as e:
                print(f"{ANSI.DIM}{e}{ANSI.RESET}")
            return

        if target == "all":
            if not Playback.QUEUE:
                print(f"{ANSI.YELLOW}Queue is empty.{ANSI.RESET}")
                return
            added, skipped = 0, 0
            for track in Playback.QUEUE:
                try:
                    playlists.add_track(name, track)
                    added += 1
                except PlaylistError:
                    skipped += 1
            parts = []
            if added:   parts.append(f"{ANSI.GREEN}♪  Added {added} track{'s' if added != 1 else ''} to '{name}'{ANSI.RESET}")
            if skipped: parts.append(f"{ANSI.DIM}{skipped} already present{ANSI.RESET}")
            print("  ".join(parts) if parts else "No tracks added.")
            return

        try:
            idx = int(target) - 1
        except ValueError:
            print(f"{ANSI.YELLOW}Invalid index '{target}'.{ANSI.RESET}")
            return

        if not Playback.QUEUE:
            print(f"{ANSI.YELLOW}Queue is empty.{ANSI.RESET}")
            return
        if idx < 0 or idx >= len(Playback.QUEUE):
            print(f"{ANSI.YELLOW}Index {idx + 1} out of range (queue has {len(Playback.QUEUE)} track{'s' if len(Playback.QUEUE) != 1 else ''}).{ANSI.RESET}")
            return
        track = Playback.QUEUE[idx]
        try:
            playlists.add_track(name, track)
            print(f"{ANSI.GREEN}♪  Added to '{name}' (queue #{idx + 1}):{ANSI.RESET} {fmt_track(track)}")
        except PlaylistError as e:
            print(f"{ANSI.DIM}{e}{ANSI.RESET}")
        return

    # ── pl remove <name> <index> ──────────────────────────────────────────────
    if sub == "remove":
        if len(args) < 3:
            print(f"{ANSI.YELLOW}Usage: pl remove <name> <index>{ANSI.RESET}")
            return
        try:
            idx = int(args[-1]) - 1
        except ValueError:
            print(f"{ANSI.YELLOW}Last argument must be a track index.{ANSI.RESET}")
            return
        name = " ".join(args[1:-1])
        if not name:
            print(f"{ANSI.YELLOW}Usage: pl remove <name> <index>{ANSI.RESET}")
            return
        try:
            track = playlists.remove_track(name, idx)
            print(f"{ANSI.DIM}Removed from '{name}' (#{idx + 1}):{ANSI.RESET} {fmt_track(track)}")
        except PlaylistError as e:
            print(f"{ANSI.YELLOW}{e}{ANSI.RESET}")
        return

    # ── pl show/load <name> [--order=...] [--reverse] [--limit=n] [--no-compact] ──
    if sub in ("show", "load"):
        name_parts, flag_parts = [], []
        for token in args[1:]:
            (flag_parts if token.startswith("--") else name_parts).append(token)

        name = " ".join(name_parts)
        if not name:
            print(f"{ANSI.YELLOW}Usage: pl {sub} <name> [--order=...] [--reverse] [--limit=n] [--no-compact]{ANSI.RESET}")
            return

        _, raw_flags = break_args(flag_parts)
        try:
            flags = parse_flags(raw_flags, PL_FLAGS)
        except ValueError as e:
            print(f"{ANSI.YELLOW}{e}{ANSI.RESET}")
            return

        order      = flags.get("order",      None)
        reverse    = flags.get("reverse",    False)
        limit      = flags.get("limit",      None)
        no_compact = flags.get("no-compact", False)

        try:
            tracks = playlists.get_playlist_tracks(name, order, reverse, limit)
        except PlaylistError as e:
            print(f"{ANSI.YELLOW}{e}{ANSI.RESET}")
            return

        if not tracks:
            print(f"{ANSI.DIM}Playlist '{name}' is empty.  Use {ANSI.RESET}{ANSI.CYAN}pl add {name}{ANSI.RESET}{ANSI.DIM} to add tracks.{ANSI.RESET}")
            return

        if sub == "show":
            compact = not no_compact and limit is None
            Playback.list_playlist(name, tracks, compact=compact)
        else:
            Playback.load_playlist(name, tracks)
        return

    print(f"{ANSI.YELLOW}Unknown subcommand '{sub}'. Try: pl list | pl create | pl show | pl load | pl add | pl remove | pl delete | pl rename{ANSI.RESET}")