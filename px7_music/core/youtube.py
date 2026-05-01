# px7_music/core/youtube.py

from yt_dlp import YoutubeDL
from px7_music import config


def search(query: str, limit: int) -> list[dict] | None:
    try:
        with YoutubeDL(config.YTDLP_SEARCH_OPTS) as ydl:
            info = ydl.extract_info(f"ytsearch{limit}:{query}", download=False)

            if "entries" not in info or not info["entries"]:
                return None

            results = []

            for video in info["entries"]:
                results.append({
                    "title": video.get("title"),
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