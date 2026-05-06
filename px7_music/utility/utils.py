import sys
import time
import threading
from px7_music.config import BANNER_TEXT_DEFAULT

class ANSI:
    RESET = "\033[0m"

    # styles
    BOLD = "\033[1m"
    DIM = "\033[2m"

    # colors
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    WHITE = "\033[37m"
    GRAY = "\033[90m"

class Preloader:
    def __init__(self, delay: float = 0.2):
        self.delay = delay
        self._running = False
        self._thread = None
        self.frames = ["|", "/", "-", "\\"]

    def _animate(self):
        i = 0
        
        while self._running:
            frame = self.frames[i % 4]
            sys.stdout.write(f"\r\033[K{self.text}{frame}")
            sys.stdout.flush()
            i += 1
            time.sleep(self.delay)

        # clear line when done
        sys.stdout.write("\r\033[K")
        sys.stdout.flush()

    def start(self, text):
        if self._running:
            return
        self.text = text
        self._running = True
        self._thread = threading.Thread(target=self._animate, daemon=True)
        self._thread.start()

    def stop(self):
        self._running = False
        if self._thread:
            self._thread.join()



def animate_print(text: str, delay: float = 0.001):
    for char in text:
        sys.stdout.write(char)
        sys.stdout.flush()

        if char.strip():
            time.sleep(delay)
        else:
            time.sleep(delay / 4)
    print()

def clear_screen(_=None):
    sys.stdout.write("\033[2J\033[3J\033[H")
    sys.stdout.flush()
    animate_print(f"{ANSI.GREEN}{BANNER_TEXT_DEFAULT}{ANSI.RESET}")

def format_duration(seconds) -> str:
    if not seconds:
        return "--:--"

    seconds = int(seconds)

    h = seconds // 3600
    m = (seconds % 3600) // 60
    s = seconds % 60

    if h > 0:
        return f"{h:02}:{m:02}:{s:02}"
    return f"{m:02}:{s:02}"

def truncate_pad(text: str, width: int) -> str:
    if len(text) > width:
        return text[:width-3] + "..."
    return text.ljust(width)

def print_results(results: list[dict]):
    if not results:
        print("No results found.")
        return

    TITLE_W = 45
    CHANNEL_W = 30

    print(f"\n{ANSI.GREEN}{ANSI.BOLD}=== Search Results ==={ANSI.RESET}\n")

    for i, item in enumerate(results, 1):
        title = truncate_pad(item.get("title", "Unknown Title"), TITLE_W)
        channel = truncate_pad(item.get("channel", "Unknown Channel"), CHANNEL_W)
        duration = format_duration(item.get("duration"))

        # first line (aligned)
        print(
            f"{ANSI.YELLOW}{i:>2}.{ANSI.RESET} "
            f"{ANSI.BOLD}{title}{ANSI.RESET} "
            f"{ANSI.GRAY}[{duration:>5}]{ANSI.RESET}"
        )

        # second line (aligned under title)
        print(
            f"    {ANSI.DIM}{channel}{ANSI.RESET}\n"
        )


def print_favs(favs: list[dict]):
    print(f"\n{ANSI.GREEN}{ANSI.BOLD}=== Favorites ({len(favs)}) ==={ANSI.RESET}\n")

    TITLE_W = 45

    for i, track in enumerate(favs, 1):
        title    = truncate_pad(track.get("title",   "Unknown Title"),   TITLE_W)
        channel  = track.get("channel",  "Unknown Channel")
        duration = format_duration(track.get("duration"))

        print(
            f"{ANSI.YELLOW}{i:>2}.{ANSI.RESET} "
            f"{ANSI.BOLD}{title}{ANSI.RESET} "
            f"{ANSI.GRAY}[{duration:>5}]{ANSI.RESET}"
        )
        print(f"    {ANSI.DIM}{channel}{ANSI.RESET}\n")


def fmt_track(track: dict) -> str:
    """Return a short 'Title — Channel' string for display."""
    title   = truncate_pad(track.get("title",   "Unknown Title"),   40)
    channel = track.get("channel", "Unknown Channel")
    return f"{ANSI.BOLD}{title.strip()}{ANSI.RESET} {ANSI.DIM}— {channel}{ANSI.RESET}"