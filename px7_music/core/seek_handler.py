import re
import px7_music.player.playback as Playback
from px7_music.utility.utils import ANSI

def _parse_seek_args(arg: str) -> int | None:   # returns total seconds
    arg = arg.strip()

    if re.match(r"^\d+:\d{2}:\d{2}$", arg):      # hh:mm:ss
        h, m, s = map(int, arg.split(":"))
        return h * 3600 + m * 60 + s

    if re.match(r"^\d+:\d{2}$", arg):             # mm:ss
        m, s = map(int, arg.split(":"))
        return m * 60 + s

    if re.match(r"^[-+]\d+$", arg):               # +/- sec
        delta = int(arg)
        try:
            current = int(Playback.player.get_time_pos() or 0)
        except Exception:
            current = 0
        return max(0, current + delta)

    if re.match(r'^\d+$', arg):
        return int(arg)

    return None


def seek_handler(args: list[str]):
    if not args:
        if Playback.CURRENT_INDEX == -1 or not Playback.QUEUE:
            print(f"{ANSI.YELLOW}Nothing is playing.{ANSI.RESET}")
            return
        seconds = int(Playback.player.get_time_pos() or 0)
        m, s = divmod(seconds, 60)
        h, m = divmod(m, 60)
        if h:
            print(f"Current: {h}:{m:02}:{s:02}")
        else:
            print(f"Current: {m}:{s:02}")
        return
    
    seconds = _parse_seek_args(args[0])
    if seconds is None:
        print(f"{ANSI.YELLOW}Invalid seek format. Try: seek 1:30 | seek 90 | seek +30 | seek -10{ANSI.RESET}")
        return
    
    if Playback.CURRENT_INDEX == -1 or not Playback.QUEUE:
        print(f"{ANSI.YELLOW}Nothing is playing.{ANSI.RESET}")
        return
    
    try:
        Playback.player.seek(seconds)
        m, s = divmod(seconds, 60)
        h, m = divmod(m, 60)
        if h:
            print(f"Seeked to {h}:{m:02}:{s:02}")
        else:
            print(f"Seeked to {m}:{s:02}")
    except RuntimeError as e:
        print(f"{ANSI.RED}{e}{ANSI.RESET}")