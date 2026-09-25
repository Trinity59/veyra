from __future__ import annotations

APP_NAME = "VEYRA"
APP_VERSION = "0.1.0"
DATABASE_NAME = "veyra.db"
DATABASE_URL = "sqlite:///./veyra.db"
CURRENCY_CODE = "KES"
CURRENCY_SYMBOL = "KSh"
DEFAULT_VAT_RATE = 16.0

BASE_DIR = __import__("pathlib").Path(__file__).resolve().parent
MEDIA_DIR = BASE_DIR / "media"
BACKUP_DIR = BASE_DIR / "backups"
LOG_DIR = BASE_DIR / "logs"
ASSET_DIR = BASE_DIR / "assets"
