from __future__ import annotations

from PySide6.QtWidgets import QDialog, QFormLayout, QHBoxLayout, QHeaderView, QLabel, QLineEdit, QMessageBox, QPushButton, QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget
from sqlalchemy import select
from db.engine import SessionLocal
from models.category import Category
from models.product import Product
from services.product_service import ProductService

class ProductDialog(QDialog):
    def __init__(self, parent=None, product: Product | None = None):
        super().__init__(parent); self.product = product; self.setWindowTitle("Add Product" if product is None else "Edit Product")
        form = QFormLayout(self); self.name = QLineEdit(product.name if product else ""); self.code = QLineEdit(product.code if product else ""); self.category = QLineEdit(product.category.name if product and product.category else ""); self.unit = QLineEdit(product.unit if product else "Piece"); self.cost = QLineEdit(str(product.cost_price) if product else "0"); self.price = QLineEdit(str(product.selling_price) if product else "0"); self.stock = QLineEdit(str(product.stock_quantity) if product else "0"); self.reorder = QLineEdit(str(product.reorder_level) if product else "0")
        for label, field in (("Product Name", self.name), ("Product Code", self.code), ("Category", self.category), ("Unit", self.unit), ("Cost Price", self.cost), ("Selling Price", self.price), ("Opening Stock", self.stock), ("Reorder Level", self.reorder)): form.addRow(label, field)
        buttons = QHBoxLayout(); cancel = QPushButton("Cancel"); cancel.clicked.connect(self.reject); save = QPushButton("Save"); save.clicked.connect(self.save); buttons.addWidget(cancel); buttons.addWidget(save); form.addRow(buttons)
    def save(self):
        session = SessionLocal()
        try:
            if self.product is None:
                ProductService.create(session, code=self.code.text(), name=self.name.text(), category=self.category.text(), unit=self.unit.text(), cost_price=self.cost.text(), selling_price=self.price.text(), opening_stock=self.stock.text(), reorder_level=self.reorder.text())
            else:
                self.product.name = self.name.text().strip(); self.product.code = ProductService.normalize_code(self.code.text()); self.product.unit = self.unit.text().strip() or "Piece"; self.product.cost_price = float(self.cost.text()); self.product.selling_price = float(self.price.text()); self.product.reorder_level = int(self.reorder.text())
                category = ProductService.get_or_create_category(session, self.category.text()); self.product.category = category
            session.commit(); self.accept()
        except Exception as exc:
            session.rollback(); QMessageBox.critical(self, "Product Error", str(exc))
        finally: session.close()

class ProductPage(QWidget):
    def __init__(self):
        super().__init__(); layout = QVBoxLayout(self); title = QLabel("Products"); title.setObjectName("page_title"); layout.addWidget(title); controls = QHBoxLayout(); self.search = QLineEdit(); self.search.setPlaceholderText("Search products..."); self.search.textChanged.connect(self.refresh); add = QPushButton("+ Add Product"); add.clicked.connect(self.add_product); controls.addWidget(self.search); controls.addWidget(add); layout.addLayout(controls); self.table = QTableWidget(0, 8); self.table.setHorizontalHeaderLabels(["Code", "Product", "Category", "Cost", "Selling", "Stock", "Status", "Action"]); self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch); layout.addWidget(self.table); self.refresh()
    def refresh(self):
        session = SessionLocal()
        try:
            query = select(Product).where(Product.is_active.is_(True)).order_by(Product.name)
            term = self.search.text().strip() if hasattr(self, "search") else ""
            if term: query = query.where((Product.name.ilike(f"%{term}%")) | (Product.code.ilike(f"%{term}%")))
            products = session.scalars(query).all(); self.table.setRowCount(len(products))
            for row, p in enumerate(products):
                values = [p.code, p.name, p.category.name if p.category else "Uncategorized", f"KSh {p.cost_price:,.2f}", f"KSh {p.selling_price:,.2f}", str(p.stock_quantity), p.stock_status]
                for col, value in enumerate(values): self.table.setItem(row, col, QTableWidgetItem(value))
                edit = QPushButton("Edit"); edit.clicked.connect(lambda _=False, product_id=p.id: self.edit_product(product_id)); self.table.setCellWidget(row, 7, edit)
        finally: session.close()
    def add_product(self):
        if ProductDialog(self).exec(): self.refresh()
    def edit_product(self, product_id: int):
        session = SessionLocal()
        try: product = session.get(Product, product_id)
        finally: session.close()
        if product and ProductDialog(self, product).exec(): self.refresh()
