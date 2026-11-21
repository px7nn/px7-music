import json, re, html

import urllib.parse
import urllib.request

from collections import OrderedDict

from px7_music               import __version__
from px7_music.utility.utils import clean_title

import px7_music.config as config


LRCLIB_API_BASE = "https://lrclib.net/api"
USER_AGENT      = f"px7-music/{__version__} (https://github.com/px7nn/px7-music)"

TIMESTAMP_RE    = re.compile(r"\[(\d+):(\d+(?:\.\d+)?)\]")


_LYRICS_CACHE: OrderedDict[tuple[str, str], dict | None] = OrderedDict()

# -- CACHE LYRICS ------------------------

def _cache_put(key: tuple[str, str], val: dict | None) -> None:
    if key in _LYRICS_CACHE:
        _LYRICS_CACHE.move_to_end(key)          # Marks as recently used
    _LYRICS_CACHE[key] = val
    max_size = max(1, config.LYRICS_CACHE_SIZE) # Should not be -ve
    while len(_LYRICS_CACHE) > max_size:        # Pop all the items based the runtime config
        _LYRICS_CACHE.popitem(last=False)       

def _cache_get(key: tuple[str, str]) -> tuple[bool, dict | None]:
    if key in _LYRICS_CACHE:
        _LYRICS_CACHE.move_to_end(key)      # Marks as recently used
        return True, _LYRICS_CACHE[key]
    return False, None


# -- LRCLIB FETCH API ---------------------------------------

def fetch_lyrics(title: str, artist: str = "", duration: int | float | None = None) -> dict | None:
    """
    Fetch synchronized or plain lyrics for LRCLIB.
    
    Returns a dict with:
        'track_name', 'artist_name', 'synced_lyrics', 'plain_lyrics', 'instrumental'
        or None if not found or network failure.
    """
    
    cache_key = (artist.strip().lower(), title.strip().lower())
    
    hit, val = _cache_get(cache_key)
    if hit:
        return val
    
    headers = {"User-Agent": USER_AGENT}
    
    # Exact lookup /api/get if both artist and title is available
    if artist and title:
        params = {"track_name": title, "artist_name": artist}
        if duration and duration > 0:
            params["duration"] = str(int((duration)))
        url = f"{LRCLIB_API_BASE}/get?" + urllib.parse.urlencode(params)
        
        try: 
            req = urllib.request.Request(url, headers=headers)
            
            with urllib.request.urlopen(req, timeout=3.5) as res:
                data = json.loads(res.read().decode("utf-8"))
                result = {
                    "track_name"    : data.get("trackName")  or title,
                    "artist_name"   : data.get("artistName") or artist,
                    "synced_lyrics" : data.get("syncedLyrics"),
                    "plain_lyrics"  : data.get("plainLyrics"),
                    "instrumental"  : data.get("instrumental", False)
                }
                _cache_put(cache_key, result)
                return result
        except Exception:
            ...
    
    # Fallback to /api/search
    search_queries = []
    if artist and title:
        search_queries.append(f"{artist} {title}")
    if title:
        search_queries.append(title)
        
    for query in search_queries:
        url = f"{LRCLIB_API_BASE}/search?" + urllib.parse.urlencode({"q": query})
        
        try:
            req = urllib.request.Request(url, headers=headers)
            
            with urllib.request.urlopen(req, timeout=4.0) as res:
                items = json.loads(res.read().decode("utf-8"))
                if not items:
                    continue
                
                # Synced Lyrics first
                synced = [i for i in items if i.get("syncedLyrics")]
                
                selected = None
                if synced:
                    if duration and duration > 0:
                        synced.sort(key=lambda x: abs((x.get("duration") or 0) - duration))
                        selected = synced[0]
                else:
                    plain = [i for i in items if i.get("plainLyrics")]
                    if plain:
                        selected = plain[0]
                        
                if selected:
                    result = {
                        "track_name"    : selected.get("trackName")  or title,
                        "artist_name"   : selected.get("artistName") or artist,
                        "synced_lyrics" : selected.get("syncedLyrics"),
                        "plain_lyrics"  : selected.get("plainLyrics"),
                        "instrumental"  : selected.get("instrumental", False)
                    }
                    _cache_put(cache_key, result)
                    return result
        except Exception:
            ...
            
    _cache_put(cache_key, None)
    return None


def parse_lrc(lrc_text: str) -> list[tuple[float, str]]:
    """Parse an LRC formatted string into sorted [(timestamp_seconds, line_text), ...]"""
    if not lrc_text:
        return []

    parsed: list[tuple[float, str]] = []
    
    for line in lrc_text.splitlines():
        line = line.strip()
        if not line:
            continue
        matches = list(TIMESTAMP_RE.finditer(line))
        if not matches:
            continue

        raw_text = TIMESTAMP_RE.sub("", line).strip()
        text = html.unescape(raw_text)
        if not text:
            text = "& & &"

        for match in matches:
            mins = int(match.group(1))
            secs = float(match.group(2))
            timestamp = mins * 60.0 + secs
            parsed.append((timestamp, text))

    parsed.sort(key=lambda x: x[0])
    return parsed


def extract_artist_and_title(raw_title: str, channel: str = "") -> tuple[str, str]:
    if not raw_title:
        return "", ""

    for sep in (" - ", " – ", " — ", " | ", ": "):
        if sep in raw_title:
            parts = raw_title.split(sep, 1)
            artist = clean_title(parts[0], "").strip(" -_")
            title  = clean_title(parts[1], "").strip(" -_")
            if artist and title:
                return artist, title

    clean_chan = (
        channel.replace(" - Topic", "")
        .replace(" Official", "")
        .replace(" VEVO", "")
        .strip(" -_")
    )
    artist = clean_chan or channel.strip()
    title  = clean_title(raw_title, channel).strip(" -_")
    return artist, title


def find_active_index(parsed_lrc: list[tuple[float, str]], time_pos: float) -> int:
    if not parsed_lrc or time_pos < parsed_lrc[0][0]:
        return -1
    active = 0
    for idx, (t, _) in enumerate(parsed_lrc):
        if t <= time_pos:
            active = idx
        else:
            break
    return active


def get_display_lyrics_lines(
    lyrics_data: dict | None,
    parsed_lrc: list[tuple[float, str]],
    time_pos: float | None,
    loading: bool = False,
    count: int = 4,
    plain_idx: int = 0,
) -> list[tuple[str, str]]:
    half = count // 2
    rem  = count - half - 1

    if loading:
        return [("", "")] * half + [("info", "Loading lyrics...")] + [("", "")] * rem

    if not lyrics_data:
        return [("", "")] * half + [("info", "No lyrics found")] + [("", "")] * rem

    if lyrics_data.get("instrumental"):
        return [("", "")] * half + [("info", "... Instrumental ...")] + [("", "")] * rem

    if not parsed_lrc:
        plain = lyrics_data.get("plain_lyrics")
        if plain:
            raw_lines = [l.strip() for l in plain.splitlines() if l.strip()]
            lines: list[tuple[str, str]] = []
            for offset in range(-half, count - half):
                idx = plain_idx + offset
                if 0 <= idx < len(raw_lines):
                    text = raw_lines[idx]
                    if offset < 0:
                        lines.append(("past", text))
                    elif offset == 0:
                        lines.append(("plain_active", text))
                    else:
                        lines.append(("upcoming", text))
                else:
                    lines.append(("", ""))
            return lines
        return [("", "")] * half + [("info", "No lyrics found")] + [("", "")] * rem

    pos = time_pos or 0
    active_idx = find_active_index(parsed_lrc, pos)

    lines: list[tuple[str, str]] = []
    half = count // 2
    for offset in range(-half, count - half):
        idx = active_idx + offset
        if active_idx == -1 and offset == 0:
            lines.append(("info", "... Intro ..."))
        elif 0 <= idx < len(parsed_lrc):
            _, text = parsed_lrc[idx]
            if offset < 0:
                lines.append(("past", text))
            elif offset == 0:
                lines.append(("active", text))
            else:
                lines.append(("upcoming", text))
        else:
            lines.append(("", ""))

    return lines