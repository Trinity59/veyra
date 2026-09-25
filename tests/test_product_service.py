from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from db.base import Base
from models.category import Category
from models.product import Product
from services.product_service import ProductService


def test_product_service_normalizes_code_and_reuses_category() -> None:
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    session = sessionmaker(bind=engine)()
    first = ProductService.create(session, code=" det001 ", name="Soap", category="Cleaning")
    second = ProductService.create(session, code="det002", name="Brush", category=" cleaning ")
    session.commit()
    assert first.code == "DET001"
    assert second.category_id == first.category_id
    assert session.query(Category).count() == 1
