from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
MEDIA_DIR = BASE_DIR / "media"
BACKUP_DIR = BASE_DIR / "backups"
LOG_DIR = BASE_DIR / "logs"
ASSET_DIR = BASE_DIR / "assets"

for directory in (MEDIA_DIR, BACKUP_DIR, LOG_DIR, ASSET_DIR):
    directory.mkdir(exist_ok=True)

