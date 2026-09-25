from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from core.exceptions import VEYRABusinessRuleError, VEYRAValidationError
from models.product import Product
from models.stock_movement import StockMovement

REASONS = {"Restock", "Initial Stock", "Customer Return", "Damaged", "Expired", "Lost", "Disposal", "Internal Use", "Correction", "Other", "Sale"}


def record_movement(session: Session, *, product_id: int, movement_type: str, quantity: int,
                    reason: str, reference: str | None = None, notes: str | None = None,
                    direction: str | None = None) -> StockMovement:
    product = session.get(Product, product_id)
    if product is None or not product.is_active:
        raise VEYRAValidationError("Product does not exist or is inactive.")
    if quantity <= 0:
        raise VEYRAValidationError("Quantity must be greater than zero.")
    if reason not in REASONS:
        raise VEYRAValidationError("Select a valid stock movement reason.")
    if reason == "Correction" and not notes:
        raise VEYRAValidationError("Correction movements require a note.")

    direction = direction or ("in" if movement_type == "Stock In" else "out")
    if direction not in {"in", "out"}:
        raise VEYRAValidationError("Direction must be 'in' or 'out'.")
    if direction == "out" and product.stock_quantity < quantity:
        raise VEYRABusinessRuleError("Quantity cannot exceed available stock.")

    product.stock_quantity += quantity if direction == "in" else -quantity
    movement = StockMovement(product=product, movement_type=movement_type,
                             quantity=quantity, direction=direction, reason=reason,
                             reference=reference.strip() if reference else None,
                             notes=notes.strip() if notes else None)
    session.add(movement)
    session.flush()
    return movement


def list_movements(session: Session, product_id: int | None = None) -> list[StockMovement]:
    statement = select(StockMovement).order_by(StockMovement.created_at.desc())
    if product_id is not None:
        statement = statement.where(StockMovement.product_id == product_id)
    return list(session.scalars(statement))
