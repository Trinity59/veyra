from __future__ import annotations

from sqlalchemy import select

from db.base import Base
from db.engine import engine, SessionLocal


def init_db() -> None:
    # Import all models before create_all so every relationship is registered.
    from models.category import Category  # noqa: F401
    from models.product import Product  # noqa: F401
    from models.sale import Sale  # noqa: F401
    from models.sale_item import SaleItem  # noqa: F401
    from models.settings import Settings  # noqa: F401
    from models.stock_movement import StockMovement  # noqa: F401

    Base.metadata.create_all(bind=engine)
    with SessionLocal.begin() as session:
        if session.scalar(select(Settings).limit(1)) is None:
            session.add(Settings())
