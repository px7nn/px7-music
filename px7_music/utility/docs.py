from px7_music.utility.utils import ANSI


def print_installation_guide(os_name: str) -> None:
    line = "─" * 50
    header = f"{ANSI.RED}{ANSI.BOLD}Error: No media player detected{ANSI.RESET}\n"
    section = f"\n{ANSI.BOLD}Install one of the following:{ANSI.RESET}\n\n"
    pip_note = (
        f"\n{ANSI.BOLD}Also install Python bindings:{ANSI.RESET}\n"
        f"  • pip install python-mpv\n"
        f"  • pip install python-vlc\n"
    )

    if os_name == "Windows":
        print(
            f"{line}\n"
            f"{header}"
            f"{section}"
            f"  ▶ {ANSI.BOLD}MPV (recommended){ANSI.RESET}\n"
            f"    • winget install mpv\n"
            f"    • https://mpv.io\n\n"
            f"  ▶ {ANSI.BOLD}VLC{ANSI.RESET}\n"
            f"    • winget install VideoLAN.VLC\n"
            f"    • https://www.videolan.org/vlc/\n"
            f"{pip_note}"
            f"{line}"
        )
        return

    if os_name == "Linux":
        print(
            f"{line}\n"
            f"{header}"
            f"{section}"
            f"  ▶ {ANSI.BOLD}MPV (recommended){ANSI.RESET}\n"
            f"    • sudo apt install mpv        # Debian/Ubuntu\n"
            f"    • sudo pacman -S mpv          # Arch\n\n"
            f"  ▶ {ANSI.BOLD}VLC{ANSI.RESET}\n"
            f"    • sudo apt install vlc\n"
            f"{pip_note}"
            f"{line}"
        )
        return

    if os_name == "Darwin":
        print(
            f"{line}\n"
            f"{header}"
            f"{section}"
            f"  ▶ {ANSI.BOLD}MPV (recommended){ANSI.RESET}\n"
            f"    • brew install mpv\n\n"
            f"  ▶ {ANSI.BOLD}VLC{ANSI.RESET}\n"
            f"    • brew install --cask vlc\n"
            f"{pip_note}"
            f"{line}"
        )
        return

    print(
        f"{line}\n"
        f"{header}\n"
        f"{ANSI.BOLD}Install mpv or VLC using your system package manager.{ANSI.RESET}\n"
        f"{pip_note}"
        f"{line}"
    )


def get_help_text(_=None) -> None:
    D  = ANSI.DIM
    R  = ANSI.RESET
    B  = ANSI.BOLD
    C  = ANSI.CYAN
    G  = ANSI.GRAY
    Y  = ANSI.YELLOW
    GR = ANSI.GREEN

    div = f"{D}{'─' * 52}{R}"

    def section(title: str) -> str:
        return f"\n{B}{title}{R}\n"

    def cmd(name: str, alias: str = "", args: str = "", desc: str = "") -> str:
        label = f"{C}{name}{R}"
        if alias:
            label += f" {D}({alias}){R}"
        if args:
            label += f"  {Y}{args}{R}"
        return f"  {label}\n  {D}  {desc}{R}\n"

    def flag(name: str, desc: str) -> str:
        return f"      {D}{C}--{name:<14}{R}{D}{desc}{R}\n"

    def example(*lines) -> str:
        return "".join(f"      {G}>> {ln}{R}\n" for ln in lines)

    print(
        f"\n{GR}{B}PX7 Music{R}  {D}— terminal music player{R}\n"
        f"\n{D}  usage: <command> [args] [--flags]{R}\n"
        f"\n{div}"

        + section("SEARCH & PLAY")
        + cmd("search", "/s", "<query>",
              "Search YouTube and load results into the queue")
        + flag("limit=<n>",   f"max results  {D}(default: DEFAULT_SEARCH_LIMIT){R}")
        + flag("no-postfix",  f"don't append the query postfix (see config)")
        + flag("p <url>",     f"fetch tracks from a YouTube playlist URL")
        + example("/s radiohead --limit=10")
        + f"\n"

        + cmd("play", "", "[index]",
              "Stream a track and load all results into the queue  (default: 1)")
        + example("play 2")

        + f"\n{div}"
        + section("PLAYBACK")
        + cmd("pause",  "", "", "Pause the current track")
        + cmd("resume", "", "", "Resume a paused track")
        + cmd("next",   "", "", "Skip to the next track in the queue")
        + cmd("prev",   "", "", "Go back to the previous track")
        + f"\n"
        + cmd("seek", "", "[position]",
              "Show current position, or jump to one")
        + f"      {D}Formats: {R}{Y}1:30{R}  {Y}90{R}  {Y}+30{R}  {Y}-10{R}  {Y}2:04:15{R}\n"
        + example("seek +30", "seek 2:14")

        + f"\n{div}"
        + section("QUEUE & INFO")
        + cmd("queue",   "", "[--no-compact]",
              "Show the queue from the current track onward")
        + flag("no-compact", "show all tracks, bypassing the compact threshold")
        + f"\n"
        + cmd("current", "now", "", "Show info for the currently playing track")
        + cmd("shuffle", "",    "", "Shuffle the queue, keeping the current track at position 1")
        + cmd("load",    "",    "", "Replace the queue with the last result list, stop playback")

        + f"\n{div}"
        + section("FAVORITES")
        + cmd("fav add",    "", "[index|all]", "Add currently playing track, a queue track by index, or all")
        + cmd("fav remove", "", "<index|all>", "Remove a favorite by index, or clear all  (asks for confirmation)")
        + f"\n"
        + cmd("favs", "", "[--flags]",
              "List saved favorites  (newest first by default)")
        + flag("order=<by>",  "title | date-added | duration | channel")
        + flag("limit=<n>",   "show only the first N results")
        + flag("reverse",     "reverse the sort direction")
        + flag("no-compact",  "show all, bypassing the compact threshold")
        + example("favs --order=duration --reverse")

        + f"\n{div}"
        + section("PLAYLISTS")
        + cmd("pl",          "", "",                   "List all playlists")
        + cmd("pl create",   "", "<name>",             "Create a new playlist")
        + cmd("pl delete",   "", "<name>",             "Delete a playlist  (asks for confirmation)")
        + cmd("pl rename",   "", "<old> -> <new>",     "Rename a playlist")
        + cmd("pl add",      "", "<name> [index|all]", "Add currently playing, a queue track, or all tracks")
        + cmd("pl remove",   "", "<name> <index>",     "Remove a track from a playlist by index")
        + cmd("pl show",     "", "<name> [--flags]",   "Display tracks in a playlist")
        + cmd("pl load",     "", "<name> [--flags]",   "Load a playlist into the queue")
        + f"\n"
        + flag("order=<by>",  "title | date-added | duration | channel  (show / load)")
        + flag("limit=<n>",   "cap the number of tracks shown or loaded")
        + flag("reverse",     "reverse the sort direction")
        + flag("no-compact",  "show all tracks  (show only)")
        + f"\n"
        + f"  {D}Shorthand — name first, subcommand second (defaults to {R}{C}show{R}{D}):{R}\n"
        + example(
            "pl Chill Mix              # → pl show Chill Mix",
            "pl Chill Mix load         # → pl load Chill Mix",
        )

        + f"\n{div}"
        + section("PIPE  ->")
        + f"  {D}Pipe a result list directly into a playlist.\n"
        + f"  The playlist is auto-created if it doesn't exist.{R}\n\n"
        + f"  {C}search{R} {D}({C}/s{R}{D}){R}  {Y}<query> [--flags]{R}  {D}->{R}  {Y}<playlist>{R}\n"
        + f"  {C}favs{R}  {Y}[--flags]{R}                 {D}->{R}  {Y}<playlist>{R}\n"
        + f"  {C}queue{R}                           {D}->{R}  {Y}<playlist>{R}\n\n"
        + example(
            "/s c418 -> Minecraft Vibes",
            "favs --order=duration --limit=10 -> Top 10",
        )

        + f"\n{div}"
        + section("JUKEBOX MODE")
        + cmd("jukebox", "/j", "",
              "Hands-free mode — plays through the queue automatically")
        + f"  {D}Keys are instant, no Enter needed:{R}\n\n"
        + f"      {Y}N  >  .{R}      {D}next track{R}\n"
        + f"      {Y}P  <  ,{R}      {D}previous track{R}\n"
        + f"      {Y}SPACE{R}        {D}pause / resume{R}\n"
        + f"      {Y}+  ={R}         {D}volume up  (+10){R}\n"
        + f"      {Y}-  _{R}         {D}volume down (−10){R}\n"
        + f"      {Y}R{R}            {D}force refresh display{R}\n"
        + f"      {Y}Q  X{R}         {D}quit jukebox mode{R}\n"

        + f"\n{div}"
        + section("CONFIG")
        + cmd("config", "", "",              "Show all tunable settings")
        + cmd("config", "", "<key>",         "Show the current value of a setting")
        + cmd("config", "", "<key> <value>", "Set and persist a setting")
        + cmd("config", "", "<key> *",       "Reset a single setting to its default")
        + cmd("config", "", "reset",         "Restore all settings to defaults")
        + f"\n"
        + f"  {D}Tunable keys:{R}\n"
        + f"      {C}DEFAULT_SEARCH_LIMIT{R}   {D}int   — results returned per search{R}\n"
        + f"      {C}DEFAULT_QUERY_POSTFIX{R}  {D}str   — appended to every query (default: \"song\"){R}\n"
        + f"      {C}COMPACT_THRESHOLD{R}      {D}int   — max rows before lists are truncated{R}\n"
        + example("config DEFAULT_SEARCH_LIMIT 10", "config DEFAULT_SEARCH_LIMIT *")

        + f"\n{div}"
        + section("UTILITY")
        + cmd("volume",  "", "[0–100]", "Get or set the volume level")
        + cmd("latency", "", "",        "Check network latency")
        + cmd("clear",   "cls", "",     "Clear the screen and redraw the banner")
        + cmd("help",    "", "",        "Show this help screen")
        + cmd("exit",    "", "",        "Quit PX7 Music")

        + f"\n{div}\n"
        + f"  {D}Tip:{R}  {C}play{R}{D} loads results into the queue — {R}{C}load{R}{D} reloads without replaying.{R}\n"
        + f"  {D}      {C}favs{R}{D} and {R}{C}pl load{R}{D} also fill last results, so {R}{C}load{R}{D} works after both.{R}\n"
        + f"  {D}      Requires {R}{B}mpv{R}{D} or {R}{B}vlc{R}{D}.{R}\n"
    )