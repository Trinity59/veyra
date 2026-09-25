from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal, ROUND_HALF_UP
from uuid import uuid4

from sqlalchemy import select
from sqlalchemy.orm import Session

from core.exceptions import VEYRABusinessRuleError, VEYRAValidationError
from models.product import Product
from models.sale import Sale
from models.sale_item import SaleItem
from models.settings import Settings
from models.stock_movement import StockMovement


@dataclass(frozen=True)
class CartLine:
    product_id: int
    quantity: int


def _q(value: Decimal) -> Decimal:
    return value.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def complete_sale(session: Session, lines: list[CartLine], discount: object = 0) -> Sale:
    if not lines:
        raise VEYRAValidationError("Cart cannot be empty.")
    try:
        discount_amount = _q(Decimal(str(discount)))
    except Exception as exc:
        raise VEYRAValidationError("Discount must be a number.") from exc
    if discount_amount < 0:
        raise VEYRAValidationError("Discount cannot be negative.")

    settings = session.scalar(select(Settings).limit(1))
    vat_rate = Decimal(str(settings.vat_rate if settings and settings.vat_enabled else 0)) / 100
    products: list[tuple[Product, CartLine]] = []
    subtotal = Decimal("0")
    for line in lines:
        if line.quantity <= 0:
            raise VEYRAValidationError("Cart quantities must be greater than zero.")
        product = session.get(Product, line.product_id)
        if product is None or not product.is_active:
            raise VEYRAValidationError("A cart product no longer exists or is inactive.")
        if product.stock_quantity < line.quantity:
            raise VEYRABusinessRuleError(f"Not enough stock for {product.name}.")
        products.append((product, line))
        subtotal += Decimal(str(product.selling_price)) * line.quantity
    if discount_amount > subtotal:
        raise VEYRAValidationError("Discount cannot exceed the subtotal.")

    taxable_base = subtotal - discount_amount
    vat = Decimal("0")
    for product, line in products:
        if product.vat_applicable:
            vat += Decimal(str(product.selling_price)) * line.quantity / subtotal * taxable_base * vat_rate
    vat = _q(vat)
    total = _q(subtotal + vat - discount_amount)
    sale = Sale(invoice_number=f"INV-{uuid4().hex[:8].upper()}", subtotal=float(_q(subtotal)),
                vat=float(vat), discount=float(discount_amount), total=float(total))
    session.add(sale)
    session.flush()
    for product, line in products:
        line_total = _q(Decimal(str(product.selling_price)) * line.quantity)
        item = SaleItem(sale=sale, product=product, product_code_snapshot=product.code,
                        product_name_snapshot=product.name, quantity=line.quantity,
                        unit_price=product.selling_price, cost_price_snapshot=product.cost_price,
                        vat_amount=0.0, line_total=float(line_total))
        product.stock_quantity -= line.quantity
        session.add(item)
        session.add(StockMovement(product=product, movement_type="Stock Out", quantity=line.quantity,
                                  direction="out", reason="Sale", reference=sale.invoice_number))
    session.flush()
    return sale
