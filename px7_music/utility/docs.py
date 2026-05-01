import platform
from px7_music.utility.utils import ANSI


def get_installation_guide() -> str:
    os_name = platform.system()

    line = "─" * 50

    header = (
        f"{ANSI.RED}{ANSI.BOLD}Error: No media player detected{ANSI.RESET}\n"
    )

    section = f"\n{ANSI.BOLD}Install one of the following:{ANSI.RESET}\n\n"

    pip_note = (
        f"\n{ANSI.BOLD}Also install Python bindings:{ANSI.RESET}\n"
        f"  • pip install python-mpv\n"
        f"  • pip install python-vlc\n"
    )

    if os_name == "Windows":
        return (
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

    elif os_name == "Linux":
        return (
            f"{line}\n"
            f"{header}"
            f"{section}"
            f"  ▶ {ANSI.BOLD}MPV (recommended){ANSI.RESET}\n"
            f"    • sudo apt install mpv        # Debian/Ubuntu\n"
            f"    • sudo pacman -S mpv         # Arch\n\n"
            f"  ▶ {ANSI.BOLD}VLC{ANSI.RESET}\n"
            f"    • sudo apt install vlc\n"
            f"{pip_note}"
            f"{line}"
        )

    elif os_name == "Darwin":
        return (
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

    return (
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
        + cmd("search", "/s", "<query>", "Search YouTube and fill the queue")
        + flag("limit=<n>",    f"max results  {D}(default: 6){R}")
        + flag("no-postfix",   f'skip auto-appending "song" to query')
        + example(
            "search daft punk harder better",
            "search lo-fi --limit=10",
            "/s porter robinson --no-postfix",
        )

        + cmd("play", "", "<index>", "Stream a track from the current queue")
        + example("play 3")

        + f"\n{div}"
        + section("PLAYBACK")
        + cmd("pause",  "",      "",       "Pause the current track")
        + cmd("resume", "",      "",       "Resume a paused track")
        + cmd("next",   "",      "",       "Skip to the next track in queue")
        + cmd("prev",   "",      "",       "Go back to the previous track")

        + f"\n{div}"
        + section("QUEUE & INFO")
        + cmd("queue",   "",         "",  "List all tracks in the current queue")
        + cmd("current", "now",      "",  "Show the currently playing track")

        + f"\n{div}"
        + section("VOLUME")
        + cmd("volume",  "",  "[0–100]", "Get current volume, or set it")
        + example("volume", "volume 60")

        + f"\n{div}"
        + section("AUTOPLAY MODE")
        + f"  {C}autoplay{R}\n"
        + f"  {D}  Hands-free mode — plays through the queue automatically.\n"
        + f"    While active, use these keys:{R}\n"
        + f"      {Y}[N]{R}{D}  next track{R}   "
        + f"{Y}[P]{R}{D}  previous{R}   "
        + f"{Y}[Q]{R}{D}  quit autoplay{R}\n"

        + f"\n{div}"
        + section("UTILITY")
        + cmd("latency",  "",         "",  "Check network latency")
        + cmd("clear", "cls",      "",  "Clear the screen and redraw the banner")
        + cmd("help",  "",         "",  "Show this help screen")
        + cmd("exit",  "",         "",  "Quit PX7 Music")

        + f"\n{div}\n"
        + f"  {D}Tip: run {R}{C}search{R}{D} first — {R}{C}play{R}{D} indexes into those results.{R}\n"
        + f"  {D}     Results reset on each new search.{R}\n"
        + f"  {D}     Requires {R}{B}mpv{R}{D} or {R}{B}vlc{R}{D}.{R}\n"
    )