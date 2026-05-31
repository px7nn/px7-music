from yt_dlp import YoutubeDL

from px7_music import config
from px7_music.utility import clean_title

_ERROR = -1

def search(query: str, limit: int) -> list[dict] | None | int:
    """
    Search YouTube and return up to *limit* track dicts.
    Returns None on no results, -1 on error.
    """
    try:
        with YoutubeDL(config.YTDLP_SEARCH_OPTS) as ydl:
            info: dict = ydl.extract_info(f"ytsearch{limit}:{query}", download=False)

            entries: list | None = info.get("entries")
            if not entries:
                return None

            return [
                {
                    "title":     clean_title(v.get("title"), v.get("channel")),
                    "channel":   v.get("channel"),
                    "duration":  v.get("duration"),
                    "video_url": f"https://youtube.com/watch?v={v.get('id')}",
                }
                for v in entries
            ]
    except Exception:
        return _ERROR
    

def get_stream_url(url: str) -> str | None:
    """Return a direct audio stream URL, or None on failure."""
    try:
        with YoutubeDL(config.YTDLP_STREAM_OPTS) as ydl:
            info: dict = ydl.extract_info(url, download=False)
            for fmt in reversed(info.get("formats", [])):
                if fmt.get("acodec") != "none":
                    return fmt.get("url")
            return None
    except Exception:
        return None
    

def fetch_playlist(url: str) -> list[dict] | None | int:
    """
    Fetch all tracks from a YouTube playlist URL.
    Returns None on empty/no entries, -1 on error.
    Skips private/deleted entries silently.
    """
    try:
        with YoutubeDL(config.YTDLP_PLAYLIST_OPTS) as ydl:
            info: dict | None = ydl.extract_info(url, download=False)

            entries: list | None = info.get("entries") if info else None
            if not entries:
                return None

            results: list[dict] = [
                {
                    "title":     clean_title(v.get("title"), v.get("channel")),
                    "channel":   v.get("channel") or v.get("uploader"),
                    "duration":  v.get("duration"),
                    "video_url": f"https://youtube.com/watch?v={v['id']}",
                }
                for v in entries
                if v and v.get("id")
            ]

            return results if results else None
    except Exception:
        return _ERROR