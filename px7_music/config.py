from pathlib import Path

ERROR_TRACEBACK = 0

DEFAULT_SEARCH_LIMIT = 6
DEFAULT_QUERY_POSTFIX = "song"
COMPACT_THRESHOLD = 8

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