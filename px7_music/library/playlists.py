import json
from datetime import datetime, timezone

from px7_music.config import PL_FILE


class PlaylistError(Exception):
    pass


def load_playlists() -> dict:
    if not PL_FILE.exists():
        return {}
    try:
        with open(PL_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}
    

def save_playlists(data: dict) -> None:
    PL_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(PL_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    

def create_playlist(name: str):
    pls = load_playlists()
    if name in pls:
        raise PlaylistError(f"Playlist '{name}' already exists.")
    pls[name] = {"created": datetime.now(timezone.utc).isoformat(), "tracks": []}
    save_playlists(pls)


def delete_playlist(name: str) -> None:
    pls = load_playlists()
    if name not in pls:
        raise PlaylistError(f"Playlist '{name}' not found.")
    del pls[name]
    save_playlists(pls)


def rename_playlist(old_name: str, new_name: str) -> None:
    pls = load_playlists()
    if old_name not in pls:
        raise PlaylistError(f"Playlist '{old_name}' not found.")
    if new_name in pls:
        raise PlaylistError(f"Playlist '{new_name}' already exists.")
    pls[new_name] = pls.pop(old_name)
    save_playlists(pls)


def add_track(playlist_name: str, track: dict) -> None:
    pls = load_playlists()
    if playlist_name not in pls:
        raise PlaylistError(f"Playlist '{playlist_name}' not found.")

    tracks = pls[playlist_name]["tracks"]
    if any(t["video_url"] == track["video_url"] for t in tracks):
        raise PlaylistError(f"'{track.get('title', 'Unknown')}' is already in '{playlist_name}'.")
        
    entry: dict = {**track, "date_added": datetime.now(timezone.utc).isoformat()}
    tracks.insert(0, entry)
    save_playlists(pls)


def remove_track(playlist_name: str, index: int) -> dict:
    pls = load_playlists()
    if playlist_name not in pls:
        raise PlaylistError(f"Playlist '{playlist_name}' not found.")
    
    tracks = pls[playlist_name]["tracks"]
    if not tracks:
        raise PlaylistError(f"Playlist '{playlist_name}' is empty.")
    if index < 0 or index >= len(tracks):
        raise PlaylistError(
            f"Index {index + 1} is out of range "
            f"(playlist has {len(tracks)} track{'s' if len(tracks) != 1 else ''})."
        )
    
    track = tracks.pop(index)
    save_playlists(pls)
    return track


def list_playlists() -> list[dict]:
    pls = load_playlists()
    results = [
        {
            "name":        name,
            "track_count": len(data.get("tracks", [])),
            "created":     data.get("created", ""),
        }
        for name, data in pls.items()
    ]
    results.sort(key=lambda x: x["created"], reverse=True)
    return results


def get_playlist_tracks(
    name:    str,
    order:   str  | None = None,
    reverse: bool        = False,
    limit:   int  | None = None,
) -> list[dict]:
    pls = load_playlists()
    if name not in pls:
        raise PlaylistError(f"Playlist '{name}' not found.")
    
    tracks = list(pls[name]["tracks"])

    if order == "name":
        tracks = sorted(tracks, key=lambda t: t.get("title", "").lower(), reverse=reverse)
    elif order == "date-added":
        tracks = sorted(tracks, key=lambda t: t.get("date_added", ""), reverse=reverse)
    elif order == "duration":
        tracks = sorted(tracks, key=lambda t: t.get("duration") or 0, reverse=reverse)
    elif reverse:
        tracks = list(reversed(tracks))
 
    if limit is not None and limit > 0:
        tracks = tracks[:limit]

    return tracks