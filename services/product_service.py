from __future__ import annotations

from decimal import Decimal, InvalidOperation

from sqlalchemy import select
from sqlalchemy.orm import Session

from core.exceptions import VEYRAValidationError
from models.category import Category
from models.product import Product


def _money(value: object, field: str) -> float:
    try:
        amount = Decimal(str(value))
    except (InvalidOperation, ValueError, TypeError) as exc:
        raise VEYRAValidationError(f"{field} must be a number.") from exc
    if amount < 0:
        raise VEYRAValidationError(f"{field} cannot be negative.")
    return float(amount.quantize(Decimal("0.01")))


def _non_negative_int(value: object, field: str) -> int:
    try:
        number = int(value)
    except (TypeError, ValueError) as exc:
        raise VEYRAValidationError(f"{field} must be a whole number.") from exc
    if number < 0 or str(value).strip() != str(number):
        raise VEYRAValidationError(f"{field} must be a non-negative whole number.")
    return number


class ProductService:
    @staticmethod
    def normalize_code(code: str) -> str:
        return code.strip().upper()

    @staticmethod
    def get_or_create_category(session: Session, name: str | None) -> Category | None:
        if not name or not name.strip():
            return None
        normalized = " ".join(name.split()).strip()
        category = session.scalar(select(Category).where(Category.name.ilike(normalized)))
        if category is None:
            category = Category(name=normalized)
            session.add(category)
            session.flush()
        return category

    @classmethod
    def create(cls, session: Session, *, code: str, name: str, category: str | None = None,
               unit: str = "Piece", cost_price: object = 0, selling_price: object = 0,
               opening_stock: object = 0, reorder_level: object = 0,
               vat_applicable: bool = True) -> Product:
        normalized_code = cls.normalize_code(code)
        if not normalized_code:
            raise VEYRAValidationError("Product Code is required.")
        if not name or not name.strip():
            raise VEYRAValidationError("Product Name is required.")
        if session.scalar(select(Product).where(Product.code == normalized_code)):
            raise VEYRAValidationError(f"Product code {normalized_code} already exists.")
        product = Product(code=normalized_code, name=name.strip(), unit=(unit or "Piece").strip(),
                          cost_price=_money(cost_price, "Cost Price"),
                          selling_price=_money(selling_price, "Selling Price"),
                          stock_quantity=_non_negative_int(opening_stock, "Opening Stock"),
                          reorder_level=_non_negative_int(reorder_level, "Reorder Level"),
                          vat_applicable=bool(vat_applicable))
        product.category = cls.get_or_create_category(session, category)
        session.add(product)
        session.flush()
        return product
