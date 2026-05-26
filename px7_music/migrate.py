import shutil
from px7_music.config import LEGACY_FAV_FILE, FAV_FILE

def migrate():
    FAV_FILE.parent.mkdir(parents=True, exist_ok=True)
    if LEGACY_FAV_FILE.exists() and not FAV_FILE.exists():
        shutil.move(LEGACY_FAV_FILE, FAV_FILE)