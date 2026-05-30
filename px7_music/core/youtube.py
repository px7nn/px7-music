# px7_music/core/youtube.py

from yt_dlp import YoutubeDL
from px7_music import config
from px7_music.utility.utils import clean_title


def search(query: str, limit: int) -> list[dict] | None:
    try:
        with YoutubeDL(config.YTDLP_SEARCH_OPTS) as ydl:
            info = ydl.extract_info(f"ytsearch{limit}:{query}", download=False)

            if "entries" not in info or not info["entries"]:
                return None

            results = []

            for video in info["entries"]:
                results.append({
                    "title": clean_title(video.get("title"), video.get("channel")),
                    "channel": video.get("channel"),
                    "duration": video.get("duration"),
                    "video_url": f"https://youtube.com/watch?v={video.get('id')}",
                })

            return results

    except Exception:
        return -1
    
def get_stream_url(url: str) -> str | None:
    """
    Returns direct audio stream URL.
    """
    try:
        with YoutubeDL(config.YTDLP_STREAM_OPTS) as ydl:
            info = ydl.extract_info(url, download=False)

            # pick best audio format
            formats = info.get("formats", [])

            for f in formats[::-1]:  # iterate from best quality
                if f.get("acodec") != "none":
                    return f.get("url")

            return None

    except Exception:
        return None
    
def fetch_playlist(url: str) -> list[dict] | None:
    """
    Fetches all entries from a YouTube playlist URL.
    Returns a list of track dicts, or None on empty, or -1 on error.
    Skips entries that fail to resolve (private/deleted videos).
    """
    try:
        with YoutubeDL(config.YTDLP_PLAYLIST_OPTS) as ydl:
            info = ydl.extract_info(url, download=False)

            entries = info.get("entries") if info else None
            if not entries:
                return None

            results = []
            for video in entries:
                if not video:
                    continue  # deleted/private entry — skip silently
                vid_id = video.get("id")
                if not vid_id:
                    continue
                results.append({
                    "title":     clean_title(video.get("title"), video.get("channel")),
                    "channel":   video.get("channel") or video.get("uploader"),
                    "duration":  video.get("duration"),
                    "video_url": f"https://youtube.com/watch?v={vid_id}",
                })

            return results if results else None

    except Exception:
        return -1