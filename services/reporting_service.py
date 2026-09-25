from __future__ import annotations

from datetime import date, datetime, timedelta
from pathlib import Path
import csv

from openpyxl import Workbook
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from models.product import Product
from models.sale import Sale
from models.sale_item import SaleItem
from models.stock_movement import StockMovement


def period_bounds(period: str, start: date | None = None, end: date | None = None) -> tuple[datetime, datetime]:
    today = date.today()
    if period == "Yesterday":
        first = today - timedelta(days=1)
        return datetime.combine(first, datetime.min.time()), datetime.combine(first, datetime.max.time())
    if period == "This Week":
        first = today - timedelta(days=today.weekday())
    elif period == "This Month":
        first = today.replace(day=1)
    elif period == "Custom" and start and end:
        return datetime.combine(start, datetime.min.time()), datetime.combine(end, datetime.max.time())
    else:
        first = today
    return datetime.combine(first, datetime.min.time()), datetime.combine(today, datetime.max.time())


def sales_rows(session: Session, period: str = "Today") -> list[dict[str, object]]:
    start, end = period_bounds(period)
    sales = session.scalars(select(Sale).where(Sale.sale_date.between(start, end)).order_by(Sale.sale_date)).all()
    return [{"Invoice": s.invoice_number, "Date": s.sale_date.strftime("%Y-%m-%d %H:%M"), "Subtotal": s.subtotal,
             "VAT": s.vat, "Discount": s.discount, "Total": s.total,
             "Items": sum(item.quantity for item in s.items)} for s in sales]


def inventory_rows(session: Session) -> list[dict[str, object]]:
    products = session.scalars(select(Product).where(Product.is_active.is_(True)).order_by(Product.name)).all()
    return [{"Code": p.code, "Product": p.name, "Category": p.category.name if p.category else "Uncategorized",
             "Cost": p.cost_price, "Selling": p.selling_price, "Stock": p.stock_quantity,
             "Stock Value": round(p.cost_price * p.stock_quantity, 2), "Status": p.stock_status} for p in products]


def export_rows(rows: list[dict[str, object]], path: str | Path, report_name: str, period: str) -> Path:
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    suffix = destination.suffix.lower()
    headers = list(rows[0].keys()) if rows else []
    if suffix == ".csv":
        with destination.open("w", newline="", encoding="utf-8") as handle:
            writer = csv.DictWriter(handle, fieldnames=headers)
            writer.writeheader(); writer.writerows(rows)
    elif suffix == ".xlsx":
        workbook = Workbook(); sheet = workbook.active; sheet.title = report_name[:31]
        sheet.append(["VEYRA", report_name, f"Period: {period}", "Currency: KSh / KES"])
        sheet.append(headers)
        for row in rows: sheet.append([row[h] for h in headers])
        workbook.save(destination)
    elif suffix == ".pdf":
        document = canvas.Canvas(str(destination), pagesize=A4)
        document.setFont("Helvetica-Bold", 14); document.drawString(40, 800, f"VEYRA - {report_name}")
        document.setFont("Helvetica", 9); document.drawString(40, 785, f"Period: {period} | Currency: KSh / KES")
        y = 760
        for row in rows:
            text = " | ".join(f"{key}: {value}" for key, value in row.items())
            document.drawString(40, y, text[:130]); y -= 14
            if y < 40: document.showPage(); y = 800
        document.save()
    else:
        raise ValueError("Supported report formats are CSV, XLSX, and PDF.")
    return destination


def dashboard_metrics(session: Session) -> dict[str, float | int]:
    start, end = period_bounds("Today")
    sales = session.scalars(select(Sale).where(Sale.sale_date.between(start, end))).all()
    products = session.scalars(select(Product).where(Product.is_active.is_(True))).all()
    return {"today_sales": round(sum(s.total for s in sales), 2), "transactions": len(sales),
            "products": len(products), "stock_value": round(sum(p.cost_price * p.stock_quantity for p in products), 2),
            "low_stock": sum(1 for p in products if 0 < p.stock_quantity <= p.reorder_level),
            "out_of_stock": sum(1 for p in products if p.stock_quantity == 0)}
