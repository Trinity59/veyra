from __future__ import annotations

from datetime import datetime
from pathlib import Path
import shutil

from core.paths import BACKUP_DIR
from core.config import BASE_DIR, DATABASE_NAME


def backup_database(destination: str | Path | None = None) -> Path:
    source = BASE_DIR / DATABASE_NAME
    if not source.exists():
        raise FileNotFoundError("The VEYRA database does not exist yet.")
    target = Path(destination) if destination else BACKUP_DIR / f"veyra-{datetime.now():%Y%m%d-%H%M%S}.db"
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, target)
    return target


def restore_database(source: str | Path) -> Path:
    backup = Path(source)
    database = BASE_DIR / DATABASE_NAME
    if not backup.exists():
        raise FileNotFoundError("Selected backup file was not found.")
    backup_database(BACKUP_DIR / f"pre-restore-{datetime.now():%Y%m%d-%H%M%S}.db")
    shutil.copy2(backup, database)
    return database
