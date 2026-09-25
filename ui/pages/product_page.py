from __future__ import annotations

from sqlalchemy import select
from PySide6.QtWidgets import (
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

from db.engine import SessionLocal
from models.category import Category
from models.product import Product
from services.product_service import ProductService


class ProductDialog(QDialog):
    def __init__(self, parent=None, product_id: int | None = None):
        super().__init__(parent)
        self.product_id = product_id
        product = None
        if product_id is not None:
            session = SessionLocal()
            try:
                product = session.get(Product, product_id)
                category_name = product.category.name if product and product.category else ""
            finally:
                session.close()
        else:
            category_name = ""
        self.setWindowTitle("Add Product" if product is None else "Edit Product")
        form = QFormLayout(self)
        self.name = QLineEdit(product.name if product else "")
        self.code = QLineEdit(product.code if product else "")
        self.category = QLineEdit(category_name)
        self.unit = QLineEdit(product.unit if product else "Piece")
        self.cost = QLineEdit(str(product.cost_price) if product else "0")
        self.price = QLineEdit(str(product.selling_price) if product else "0")
        self.stock = QLineEdit(str(product.stock_quantity) if product else "0")
        self.reorder = QLineEdit(str(product.reorder_level) if product else "0")
        for label, field in (
            ("Product Name", self.name), ("Product Code", self.code), ("Category", self.category),
            ("Unit", self.unit), ("Cost Price", self.cost), ("Selling Price", self.price),
            ("Opening Stock", self.stock), ("Reorder Level", self.reorder),
        ):
            form.addRow(label, field)
        buttons = QHBoxLayout()
        cancel = QPushButton("Cancel")
        cancel.clicked.connect(self.reject)
        save = QPushButton("Save")
        save.clicked.connect(self.save)
        buttons.addWidget(cancel)
        buttons.addWidget(save)
        form.addRow(buttons)

    def save(self) -> None:
        session = SessionLocal()
        try:
            if self.product_id is None:
                ProductService.create(
                    session, code=self.code.text(), name=self.name.text(), category=self.category.text(),
                    unit=self.unit.text(), cost_price=self.cost.text(), selling_price=self.price.text(),
                    opening_stock=self.stock.text(), reorder_level=self.reorder.text(),
                )
            else:
                product = session.get(Product, self.product_id)
                if product is None:
                    raise ValueError("The selected product no longer exists.")
                normalized_code = ProductService.normalize_code(self.code.text())
                duplicate = session.scalar(
                    select(Product).where(Product.code == normalized_code, Product.id != product.id)
                )
                if duplicate:
                    raise ValueError(f"Product code {normalized_code} already exists.")
                product.name = self.name.text().strip()
                product.code = normalized_code
                product.unit = self.unit.text().strip() or "Piece"
                product.cost_price = float(self.cost.text())
                product.selling_price = float(self.price.text())
                product.reorder_level = int(self.reorder.text())
                product.category = ProductService.get_or_create_category(session, self.category.text())
            session.commit()
            self.accept()
        except Exception as exc:
            session.rollback()
            QMessageBox.critical(self, "Product Error", str(exc))
        finally:
            session.close()


class ProductPage(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        title = QLabel("Products")
        title.setObjectName("page_title")
        layout.addWidget(title)
        controls = QHBoxLayout()
        self.search = QLineEdit()
        self.search.setPlaceholderText("Search products...")
        self.search.textChanged.connect(self.refresh)
        add = QPushButton("+ Add Product")
        add.clicked.connect(self.add_product)
        controls.addWidget(self.search)
        controls.addWidget(add)
        layout.addLayout(controls)
        self.table = QTableWidget(0, 8)
        self.table.setHorizontalHeaderLabels(["Code", "Product", "Category", "Cost", "Selling", "Stock", "Status", "Action"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        layout.addWidget(self.table)
        self.refresh()

    def refresh(self):
        session = SessionLocal()
        try:
            query = select(Product).where(Product.is_active.is_(True)).order_by(Product.name)
            term = self.search.text().strip() if hasattr(self, "search") else ""
            if term:
                query = query.where((Product.name.ilike(f"%{term}%")) | (Product.code.ilike(f"%{term}%")))
            products = session.scalars(query).all()
            self.table.setRowCount(len(products))
            for row, product in enumerate(products):
                values = [product.code, product.name, product.category.name if product.category else "Uncategorized", f"KSh {product.cost_price:,.2f}", f"KSh {product.selling_price:,.2f}", str(product.stock_quantity), product.stock_status]
                for column, value in enumerate(values):
                    self.table.setItem(row, column, QTableWidgetItem(value))
                edit = QPushButton("Edit")
                edit.clicked.connect(lambda _=False, product_id=product.id: self.edit_product(product_id))
                self.table.setCellWidget(row, 7, edit)
        finally:
            session.close()

    def add_product(self):
        if ProductDialog(self).exec():
            self.refresh()

    def edit_product(self, product_id: int):
        if ProductDialog(self, product_id).exec():
            self.refresh()
