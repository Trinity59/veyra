from pathlib import Path
import sqlite3

from services.backup_service import backup_database


def test_backup_writes_database_file(tmp_path, monkeypatch):
    database = tmp_path / "veyra.db"
    with sqlite3.connect(database) as connection:
        connection.execute("create table example (id integer)")
        connection.commit()
    monkeypatch.setattr("services.backup_service.BASE_DIR", tmp_path)
    result = backup_database(tmp_path / "backup.db")
    assert result.exists()
    assert result.stat().st_size == database.stat().st_size
