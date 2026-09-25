from __future__ import annotations

from datetime import datetime, timedelta
from sqlalchemy import select
from sqlalchemy.orm import Session

from core.exceptions import VEYRABusinessRuleError
from db.base import Base
from models.category import Category
from models.product import Product
from models.sale import Sale
from models.sale_item import SaleItem
from models.stock_movement import StockMovement
from services.pos_service import CartLine, complete_sale


def test_sale_snapshots_and_stock_are_created_atomically():
    from sqlalchemy import create_engine
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    with Session(engine) as session:
        product = Product(code="A1", name="Soap", selling_price=100, cost_price=60, stock_quantity=3, reorder_level=1)
        session.add(product); session.commit()
        sale = complete_sale(session, [CartLine(product.id, 2)])
        session.commit()
        assert product.stock_quantity == 1
        assert sale.items[0].product_name_snapshot == "Soap"
        assert session.scalar(select(StockMovement).where(StockMovement.reason == "Sale")) is not None


def test_sale_rejects_insufficient_stock():
    from sqlalchemy import create_engine
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    with Session(engine) as session:
        product = Product(code="A1", name="Soap", selling_price=100, stock_quantity=1)
        session.add(product); session.commit()
        try:
            complete_sale(session, [CartLine(product.id, 2)])
        except VEYRABusinessRuleError:
            session.rollback()
        else:
            raise AssertionError("Expected insufficient stock error")
        assert product.stock_quantity == 1
