BANNER_TEXT_DEFAULT = """          
    ██████╗ ██╗  ██╗███████╗
    ██╔══██╗╚██╗██╔╝╚════██║
    ██████╔╝ ╚███╔╝     ██╔╝
    ██╔═══╝  ██╔██╗    ██╔╝ 
    ██║     ██╔╝ ██╗   ██║  
    ╚═╝     ╚═╝  ╚═╝   ╚═╝  
 - - - - Terminal Music - - - -         
"""

ERROR_TRACBACK = 0

DEFAULT_SEARCH_LIMIT = 6
DEFAULT_QUERY_POSTFIX = " song"

YTDLP_BASE_OPTS = {
    "quiet": True,
    "no_warnings": True,
    "noplaylist": True,
    "format": "bestaudio/best",
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
    "skip_download": True,
    "default_search": "ytsearch1",
}