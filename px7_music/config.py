from pathlib import Path

ERROR_TRACEBACK = 0

DEFAULT_SEARCH_LIMIT = 6
DEFAULT_QUERY_POSTFIX = "song"
COMPACT_THRESHOLD = 8
THEME_COLOR = "green"

THEME_COLOR_MAP = {
    "green":   "\033[38;2;30;215;96m",
    "blue":    "\033[38;2;36;114;200m",
    "cyan":    "\033[38;2;17;168;205m",
    "purple":  "\033[38;2;155;89;182m",
    "violet":  "\033[38;2;127;90;240m",
    "pink":    "\033[38;2;255;105;180m",
    "rose":    "\033[38;2;220;80;120m",
    "orange":  "\033[38;2;230;130;50m",
    "teal":    "\033[38;2;0;178;160m",
    "white":   "\033[38;2;229;229;229m",
}

YTDLP_BASE_OPTS = {
    "quiet":          True,
    "no_warnings":    True,
    "noplaylist":     True,
    "format":         "bestaudio/best",
    "socket_timeout": 5,
}

# For extracting metadata only (fast)
YTDLP_SEARCH_OPTS = {
    **YTDLP_BASE_OPTS,
    "extract_flat": True,
}

# For getting stream URL
YTDLP_STREAM_OPTS = {
    **YTDLP_BASE_OPTS,
    "skip_download":   True,
    "default_search":  "ytsearch1",
}

YTDLP_PLAYLIST_OPTS = {
    **YTDLP_BASE_OPTS,
    "extract_flat": True,
    "noplaylist":   False,
}

FAV_FILE  = Path.home() / ".px7" / ".px7_favorites.json"
PL_FILE   = Path.home() / ".px7" / ".px7_playlists.json"
PREF_FILE = Path.home() / ".px7" / ".px7_cfg.json"