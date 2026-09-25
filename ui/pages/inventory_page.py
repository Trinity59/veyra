from __future__ import annotations

from typing import Any

from PySide6.QtWidgets import (
    QComboBox,
    QDialog,
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
from models.category import Category
from models.product import Product
from services.product_service import ProductService


class AddEditProductDialog(QDialog):
    def __init__(self, parent: QWidget | None = None, product: Product | None = None) -> None:
        super().__init__(parent)
        self.product = product
        self.setWindowTitle("Add Product" if product is None else "Edit Product")
        self.setMinimumWidth(500)

        layout = QVBoxLayout(self)
        form = QFormLayout()

        self.name_edit = QLineEdit(product.name if product else "")
        self.code_edit = QLineEdit(product.code if product else "")
        self.category_edit = QLineEdit(product.category.name if product and product.category else "")
        self.unit_edit = QLineEdit(product.unit if product else "Piece")
        self.cost_edit = QLineEdit(str(product.cost_price if product else ""))
        self.selling_edit = QLineEdit(str(product.selling_price if product else ""))
        self.stock_edit = QLineEdit(str(product.stock_quantity if product else ""))
        self.reorder_edit = QLineEdit(str(product.reorder_level if product else ""))
        self.vat_edit = QComboBox()
        self.vat_edit.addItems(["Yes", "No"])
        if product is not None:
            self.vat_edit.setCurrentText("Yes" if product.vat_applicable else "No")
        else:
            self.vat_edit.setCurrentText("Yes")

        form.addRow("Product Name", self.name_edit)
        form.addRow("Product Code", self.code_edit)
        form.addRow("Category", self.category_edit)
        form.addRow("Unit", self.unit_edit)
        form.addRow("Cost Price", self.cost_edit)
        form.addRow("Selling Price", self.selling_edit)
        form.addRow("Opening Stock", self.stock_edit)
        form.addRow("Reorder Level", self.reorder_edit)
        form.addRow("VAT Applicable", self.vat_edit)
        layout.addLayout(form)

        buttons = QHBoxLayout()
        cancel = QPushButton("Cancel")
        cancel.clicked.connect(self.reject)
        save = QPushButton("Save Product")
        save.clicked.connect(self.save_product)
        buttons.addStretch()
        buttons.addWidget(cancel)
        buttons.addWidget(save)
        layout.addLayout(buttons)

    def save_product(self) -> None:
        try:
            session = SessionLocal()
            if self.product is None:
                ProductService.create(
                    session,
                    code=self.code_edit.text(),
                    name=self.name_edit.text(),
                    category=self.category_edit.text(),
                    unit=self.unit_edit.text() or "Piece",
                    cost_price=self.cost_edit.text(),
                    selling_price=self.selling_edit.text(),
                    opening_stock=self.stock_edit.text(),
                    reorder_level=self.reorder_edit.text(),
                    vat_applicable=self.vat_edit.currentText() == "Yes",
                )
            else:
                self.product.name = self.name_edit.text().strip()
                self.product.code = ProductService.normalize_code(self.code_edit.text())
                self.product.unit = self.unit_edit.text().strip() or "Piece"
                self.product.cost_price = float(self.cost_edit.text() or 0)
                self.product.selling_price = float(self.selling_edit.text() or 0)
                self.product.stock_quantity = int(self.stock_edit.text() or 0)
                self.product.reorder_level = int(self.reorder_edit.text() or 0)
                self.product.vat_applicable = self.vat_edit.currentText() == "Yes"
                if self.category_edit.text().strip():
                    category = session.scalar(select(Category).where(Category.name.ilike(self.category_edit.text().strip())))
                    if category is None:
                        category = Category(name=self.category_edit.text().strip())
                        session.add(category)
                        session.flush()
                    self.product.category = category
            session.commit()
            self.accept()
        except Exception as exc:  # pragma: no cover - UI layer handling
            QMessageBox.critical(self, "Validation Error", str(exc))
        finally:
            session.close()


class ProductPage(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.layout = QVBoxLayout(self)

        header = QHBoxLayout()
        title = QLabel("Products")
        title.setObjectName("page_title")
        header.addWidget(title)
        header.addStretch()
        self.layout.addLayout(header)

        controls = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search products...")
        self.search_input.textChanged.connect(self.refresh_products)
        controls.addWidget(self.search_input)
        controls.addStretch()

        add_product_btn = QPushButton("+ Add Product")
        add_product_btn.clicked.connect(self.open_add_dialog)
        controls.addWidget(add_product_btn)
        self.layout.addLayout(controls)

        self.table = QTableWidget(0, 8)
        self.table.setHorizontalHeaderLabels(["Code", "Product", "Category", "Cost", "Selling", "Stock", "Status", "Action"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.table.setAlternatingRowColors(True)
        self.table.cellClicked.connect(self.handle_table_click)
        self.layout.addWidget(self.table)

        self.refresh_products()

    def refresh_products(self) -> None:
        session = SessionLocal()
        try:
            query = select(Product).join(Product.category, isouter=True)
            text = self.search_input.text().strip().lower()
            if text:
                query = query.where((Product.name.ilike(f"%{text}%")) | (Product.code.ilike(f"%{text}%")))
            rows = session.scalars(query.order_by(Product.name.asc())).all()
            self.table.setRowCount(len(rows))
            for row_index, product in enumerate(rows):
                self.table.setItem(row_index, 0, QTableWidgetItem(product.code))
                self.table.setItem(row_index, 1, QTableWidgetItem(product.name))
                self.table.setItem(row_index, 2, QTableWidgetItem(product.category.name if product.category else "Uncategorized"))
                self.table.setItem(row_index, 3, QTableWidgetItem(f"KSh {product.cost_price:,.2f}"))
                self.table.setItem(row_index, 4, QTableWidgetItem(f"KSh {product.selling_price:,.2f}"))
                self.table.setItem(row_index, 5, QTableWidgetItem(str(product.stock_quantity)))
                status = product.stock_status
                self.table.setItem(row_index, 6, QTableWidgetItem(status))
                action = QPushButton("Edit")
                action.clicked.connect(lambda checked=False, p=product: self.open_edit_dialog(p))
                self.table.setCellWidget(row_index, 7, action)
        finally:
            session.close()

    def open_add_dialog(self) -> None:
        dialog = AddEditProductDialog(self)
        if dialog.exec_():
            self.refresh_products()

    def open_edit_dialog(self, product: Product) -> None:
        dialog = AddEditProductDialog(self, product)
        if dialog.exec_():
            self.refresh_products()

    def handle_table_click(self, row: int, column: int) -> None:
        if column != 7:
            return
        product_id = self.table.item(row, 0).text()
        QMessageBox.information(self, "Product Selected", f"Selected product code: {product_id}")
