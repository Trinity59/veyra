from __future__ import annotations

from PySide6.QtWidgets import (
    QComboBox,
    QFormLayout,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)
from sqlalchemy import select

from db.engine import SessionLocal
from models.product import Product
from models.stock_movement import StockMovement
from services.inventory_service import REASONS, record_movement


class InventoryPage(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.layout = QVBoxLayout(self)

        title = QLabel("Inventory")
        title.setObjectName("page_title")
        self.layout.addWidget(title)

        form = QFormLayout()
        self.product_combo = QComboBox()
        self.movement_combo = QComboBox()
        self.movement_combo.addItems(["Stock In", "Stock Out"])
        self.reason_combo = QComboBox()
        self.reason_combo.addItems(sorted(REASONS))
        self.quantity_edit = QLineEdit()
        self.reference_edit = QLineEdit()
        self.notes_edit = QLineEdit()

        form.addRow("Product", self.product_combo)
        form.addRow("Movement", self.movement_combo)
        form.addRow("Reason", self.reason_combo)
        form.addRow("Quantity", self.quantity_edit)
        form.addRow("Reference", self.reference_edit)
        form.addRow("Notes", self.notes_edit)
        self.layout.addLayout(form)

        buttons = QHBoxLayout()
        save = QPushButton("Save Movement")
        save.clicked.connect(self.save_movement)
        buttons.addStretch()
        buttons.addWidget(save)
        self.layout.addLayout(buttons)

        self.table = QTableWidget(0, 6)
        self.table.setHorizontalHeaderLabels(["Date", "Product", "Movement", "Qty", "Reason", "Reference"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.layout.addWidget(self.table)

        self.refresh_products()
        self.refresh_movements()

    def refresh_products(self) -> None:
        session = SessionLocal()
        try:
            products = session.scalars(select(Product).order_by(Product.name.asc())).all()
            self.product_combo.clear()
            for product in products:
                self.product_combo.addItem(f"{product.name} ({product.code})", product.id)
        finally:
            session.close()

    def refresh_movements(self) -> None:
        session = SessionLocal()
        try:
            rows = session.scalars(select(StockMovement).order_by(StockMovement.created_at.desc()).limit(50)).all()
            self.table.setRowCount(len(rows))
            for row_index, movement in enumerate(rows):
                self.table.setItem(row_index, 0, QTableWidgetItem(movement.created_at.strftime("%Y-%m-%d %H:%M")))
                self.table.setItem(row_index, 1, QTableWidgetItem(movement.product.name))
                self.table.setItem(row_index, 2, QTableWidgetItem(movement.movement_type))
                self.table.setItem(row_index, 3, QTableWidgetItem(str(movement.quantity)))
                self.table.setItem(row_index, 4, QTableWidgetItem(movement.reason))
                self.table.setItem(row_index, 5, QTableWidgetItem(movement.reference or ""))
        finally:
            session.close()

    def save_movement(self) -> None:
        product_id = self.product_combo.currentData()
        if product_id is None:
            QMessageBox.warning(self, "Validation", "Select a product.")
            return
        try:
            quantity = int(self.quantity_edit.text() or 0)
        except ValueError:
            QMessageBox.warning(self, "Validation", "Quantity must be a whole number.")
            return
        try:
            session = SessionLocal()
            record_movement(
                session,
                product_id=int(product_id),
                movement_type=self.movement_combo.currentText(),
                quantity=quantity,
                reason=self.reason_combo.currentText(),
                reference=self.reference_edit.text() or None,
                notes=self.notes_edit.text() or None,
            )
            session.commit()
            QMessageBox.information(self, "Stock Movement Saved", "The movement was recorded successfully.")
        except Exception as exc:  # pragma: no cover - UI layer handling
            QMessageBox.critical(self, "Inventory Error", str(exc))
        finally:
            session.close()
        self.refresh_products()
        self.refresh_movements()
