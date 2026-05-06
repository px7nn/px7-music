import json
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
    """
    favs = load_favorites()

    for item in favs:
        if track["video_url"] == item["video_url"]:
            raise FavoriteError(f"Already in favorites: {track.get('title', 'Unknown')}")

    favs.append(track)
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