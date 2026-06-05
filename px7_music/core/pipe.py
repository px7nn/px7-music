from px7_music.utility import ANSI, Preloader
from px7_music.core    import handler
from px7_music.library import PlaylistError, playlists

spinner = Preloader()

# ── Source resolvers ──────────────────────────────────────────────────────────

def _resolve_search(source_args: list[str]) -> list[dict] | None:
    return handler.search_handler(source_args)
    

def _resolve_favs(source_args: list[str]) -> list[dict] | None:
    return handler.favs_handler(source_args)

def _resolve_queue(source_args: list[str]) -> list[dict] | None:
    return handler.queue_handler(source_args)

_RESOLVER = {
    "search": _resolve_search,
    "/s":     _resolve_search, 
    "favs":   _resolve_favs,
    "queue":  _resolve_queue,
}


# ── Playlist writer ───────────────────────────────────────────────────────────

def _write_to_playlist(results: list[dict], playlist_name: str):
    spinner.start("Resolving Playlist ... ")
    created = False

    try:
        playlists.create_playlist(playlist_name)
        created = True
    except PlaylistError:
        pass

    added, skipped = 0, 0
    for track in reversed(results):
        try:
            playlists.add_track(playlist_name, track)
            added += 1
        except PlaylistError:
            skipped += 1

    parts = []
    if created:
        parts.append(f"{ANSI.DIM}Created playlist{ANSI.RESET} {ANSI.BOLD}{playlist_name}{ANSI.RESET}")
    
    if added:
        parts.append(
            f"{ANSI.GREEN}♪  Added {added} track{'s' if added != 1 else ''} "
            f"to '{playlist_name}'{ANSI.RESET}"
        )
    if skipped:
        parts.append(f"{ANSI.DIM}{skipped} already present{ANSI.RESET}")

    spinner.stop()
    print("  ".join(parts) if parts else "No tracks added.")
    print()


# ── Public entry point ────────────────────────────────────────────────────────

def handle_pipe(source_cmd: str, source_args: list[str], playlist_name: str):
    resolver = _RESOLVER.get(source_cmd)

    if resolver is None:
        print(
            f"{ANSI.YELLOW}'{source_cmd}' cannot be used as a pipe source."
            f"Supported: search (/s), favs, queue{ANSI.RESET}"
        )
        return
    
    results = resolver(source_args)
    if results is None:
        print(f"{ANSI.YELLOW}Command failed; unable to pipe results.{ANSI.RESET}")
        return
    
    _write_to_playlist(results, playlist_name)
