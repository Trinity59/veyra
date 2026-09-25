from db.base import Base
from db.engine import engine


def init_db() -> None:
    # Imports register every model with Base.metadata before create_all.
    from models.category import Category  # noqa: F401
    from models.product import Product  # noqa: F401
    from models.sale import Sale  # noqa: F401
    from models.sale_item import SaleItem  # noqa: F401
    from models.settings import Settings  # noqa: F401
    from models.stock_movement import StockMovement  # noqa: F401

    Base.metadata.create_all(bind=engine)
