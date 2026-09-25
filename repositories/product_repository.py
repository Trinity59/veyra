from __future__ import annotations

from datetime import datetime

from PySide6.QtWidgets import (
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QMessageBox,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)
from sqlalchemy import select

from db.engine import SessionLocal
from models.sale import Sale
from models.sale_item import SaleItem


class SalesPage(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.layout = QVBoxLayout(self)

        header = QHBoxLayout()
        title = QLabel("Sales")
        title.setObjectName("page_title")
        header.addWidget(title)
        header.addStretch()
        self.layout.addLayout(header)

        self.table = QTableWidget(0, 5)
        self.table.setHorizontalHeaderLabels(["Invoice", "Date", "Items", "Subtotal", "Total"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.cellClicked.connect(self.show_sale_detail)
        self.layout.addWidget(self.table)

        self.refresh_sales()

    def refresh_sales(self) -> None:
        session = SessionLocal()
        try:
            sales = session.scalars(select(Sale).order_by(Sale.sale_date.desc()).limit(50)).all()
            self.table.setRowCount(len(sales))
            for row_index, sale in enumerate(sales):
                item_count = sum(item.quantity for item in sale.items)
                self.table.setItem(row_index, 0, QTableWidgetItem(sale.invoice_number))
                self.table.setItem(row_index, 1, QTableWidgetItem(sale.sale_date.strftime("%Y-%m-%d %H:%M")))
                self.table.setItem(row_index, 2, QTableWidgetItem(str(item_count)))
                self.table.setItem(row_index, 3, QTableWidgetItem(f"KSh {sale.subtotal:,.2f}"))
                self.table.setItem(row_index, 4, QTableWidgetItem(f"KSh {sale.total:,.2f}"))
        finally:
            session.close()

    def show_sale_detail(self, row: int, column: int) -> None:
        invoice = self.table.item(row, 0).text()
        session = SessionLocal()
        try:
            sale = session.scalar(select(Sale).where(Sale.invoice_number == invoice))
            if sale is None:
                return
            lines = [
                f"{item.product_name_snapshot} x {item.quantity} @ KSh {item.unit_price:,.2f} = KSh {item.line_total:,.2f}"
                for item in sale.items
            ]
            details = "\n".join(lines)
            QMessageBox.information(self, f"Invoice {invoice}", f"{details}\n\nSubtotal: KSh {sale.subtotal:,.2f}\nVAT: KSh {sale.vat:,.2f}\nDiscount: KSh {sale.discount:,.2f}\nTotal: KSh {sale.total:,.2f}")
        finally:
            session.close()
