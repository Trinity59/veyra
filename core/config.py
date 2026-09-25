from __future__ import annotations

import os
from pathlib import Path

APP_NAME = "VEYRA"
APP_VERSION = "0.1.0"
BASE_DIR = Path(__file__).resolve().parent.parent
DATABASE_NAME = "veyra.db"
DATABASE_URL = os.getenv("VEYRA_DATABASE_URL", f"sqlite:///{(BASE_DIR / DATABASE_NAME).as_posix()}")
CURRENCY_CODE = "KES"
CURRENCY_SYMBOL = "KSh"
DEFAULT_VAT_RATE = 16.0
MEDIA_DIR = BASE_DIR / "media"
BACKUP_DIR = BASE_DIR / "backups"
LOG_DIR = BASE_DIR / "logs"
ASSET_DIR = BASE_DIR / "assets"
for directory in (MEDIA_DIR, BACKUP_DIR, LOG_DIR, ASSET_DIR):
    directory.mkdir(parents=True, exist_ok=True)
