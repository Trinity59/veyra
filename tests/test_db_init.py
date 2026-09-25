from sqlalchemy import inspect

from db.engine import engine
from db.init_db import init_db


def test_db_initialization_creates_expected_tables() -> None:
    init_db()
    inspector = inspect(engine)
    table_names = set(inspector.get_table_names())
    expected = {"categories", "products", "sales", "sale_items", "stock_movements", "settings"}
    assert expected.issubset(table_names)
