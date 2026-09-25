from __future__ import annotations

from sqlalchemy import inspect

from db.base import Base
from db.engine import engine


def init_db() -> None:
    """Create all tables if they do not already exist."""
    from models.category import Category
    from models.product import Product
    from models.sale import Sale
    from models.sale_item import SaleItem
    from models.settings import Settings
    from models.stock_movement import StockMovement

    Base.metadata.create_all(bind=engine)

    inspector = inspect(engine)
    expected = {
        "categories",
        "products",
        "sales",
        "sale_items",
        "stock_movements",
        "settings",
    }
    existing = set(inspector.get_table_names())
    if not expected.issubset(existing):
        raise RuntimeError("Database initialization did not create all expected VEYRA tables.")

