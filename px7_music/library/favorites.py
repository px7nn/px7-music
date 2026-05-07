import json
from datetime import datetime, timezone
from px7_music.config import FAV_FILE


class FavoriteError(Exception):
    pass


def load_favorites() -> list[dict]:
    if not FAV_FILE.exists():
        return []
    try:
        with open(FAV_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []


def save_favorites(data: list[dict]) -> None:
    with open(FAV_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def add_favorite(track: dict) -> None:
    """
        Add a track. 
        Raises FavoriteError if already present.
        Stamps a 'date_added' (ISO 8601 UTC) on the stored entry.
    """
    favs = load_favorites()

    for item in favs:
        if track["video_url"] == item["video_url"]:
            raise FavoriteError(f"Already in favorites: {track.get('title', 'Unknown')}")

    entry = dict(track)
    entry["date_added"] = datetime.now(timezone.utc).isoformat()

    favs.insert(0, entry)
    save_favorites(favs)


def remove_favorite(index: int) -> dict:
    """
        Remove by 0-based index. 
        Raises FavoriteError if list empty or index out of range.
        Returns the removed track.
    """
    favs = load_favorites()

    if not favs:
        raise FavoriteError("Favorites are empty — nothing to remove.")

    if index < 0 or index >= len(favs):
        raise FavoriteError(
            f"Index {index + 1} is out of range "
            f"(you have {len(favs)} favorite{'s' if len(favs) != 1 else ''})."
        )

    track = favs.pop(index)
    save_favorites(favs)
    return track


def get_favorites(order: str = None, reverse: bool = False, limit: int = None) -> list[dict]:
    favs = load_favorites()

    if order == "name":
        favs = sorted(favs, key=lambda t: t.get("title", "").lower(), reverse=reverse)
    elif order == "date-added":
        favs = sorted(favs, key=lambda t: t.get("date_added", ""), reverse=reverse)
    elif order == "duration":
        favs = sorted(favs, key=lambda t: t.get("duration") or 0, reverse=reverse)
    elif reverse:
        favs = list(reversed(favs))

    if limit is not None and limit > 0:
        favs = favs[:limit]

    return favs


def clear_favorites() -> int:
    """
        Clear all favorites. 
        Raises FavoriteError if already empty.
        Returns the count of removed favorites.
    """
    favs = load_favorites()

    if not favs:
        raise FavoriteError("Favorites are already empty.")

    count = len(favs)
    save_favorites([])
    return count