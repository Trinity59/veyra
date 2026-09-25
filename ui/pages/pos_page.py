from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import QInputDialog, QLineEdit, QHBoxLayout, QLabel, QListWidget, QListWidgetItem, QMessageBox, QPushButton, QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget
from sqlalchemy import select
from db.engine import SessionLocal
from models.product import Product
from services.pos_service import CartLine, complete_sale

class POSPage(QWidget):
    def __init__(self):
        super().__init__(); self.cart = {}; layout = QVBoxLayout(self); title = QLabel("POS"); title.setObjectName("page_title"); layout.addWidget(title); controls = QHBoxLayout(); self.search = QLineEdit(); self.search.setPlaceholderText("Search product or code..."); self.search.textChanged.connect(self.refresh); controls.addWidget(self.search); add = QPushButton("Add Selected"); add.clicked.connect(self.add_selected); controls.addWidget(add); layout.addLayout(controls); self.products = QListWidget(); self.products.itemDoubleClicked.connect(lambda _: self.add_selected()); layout.addWidget(self.products); self.cart_table = QTableWidget(0, 4); self.cart_table.setHorizontalHeaderLabels(["Product", "Qty", "Price", "Total"]); layout.addWidget(self.cart_table); actions = QHBoxLayout(); clear = QPushButton("Clear Cart"); clear.clicked.connect(self.clear_cart); sale = QPushButton("Complete Sale"); sale.clicked.connect(self.complete); actions.addWidget(clear); actions.addWidget(sale); layout.addLayout(actions); self.refresh(); self.refresh_cart()
    def refresh(self):
        session = SessionLocal()
        try:
            term = self.search.text().strip() if hasattr(self, "search") else ""; query = select(Product).where(Product.is_active.is_(True)).order_by(Product.name)
            if term: query = query.where((Product.name.ilike(f"%{term}%")) | (Product.code.ilike(f"%{term}%")))
            self.products.clear()
            for product in session.scalars(query):
                item = QListWidgetItem(f"{product.name} | KSh {product.selling_price:,.2f} | Stock: {product.stock_quantity}"); item.setData(Qt.ItemDataRole.UserRole, product.id)
                if product.stock_quantity <= 0: item.setFlags(item.flags() & ~Qt.ItemFlag.ItemIsEnabled)
                self.products.addItem(item)
        finally: session.close()
    def add_selected(self):
        item = self.products.currentItem()
        if item is None or not (item.flags() & Qt.ItemFlag.ItemIsEnabled): return
        product_id = int(item.data(Qt.ItemDataRole.UserRole)); session = SessionLocal()
        try: available = (session.get(Product, product_id).stock_quantity)
        finally: session.close()
        quantity, accepted = QInputDialog.getInt(self, "Quantity", f"Available: {available}", 1, 1, available or 1)
        if accepted and available and self.cart.get(product_id, 0) + quantity <= available: self.cart[product_id] = self.cart.get(product_id, 0) + quantity; self.refresh_cart()
        elif accepted: QMessageBox.warning(self, "POS", "Quantity exceeds available stock.")
    def refresh_cart(self):
        session = SessionLocal()
        try:
            self.cart_table.setRowCount(0)
            for row, (product_id, quantity) in enumerate(self.cart.items()):
                product = session.get(Product, product_id)
                if product is None: continue
                self.cart_table.insertRow(row)
                for column, value in enumerate((product.name, str(quantity), f"KSh {product.selling_price:,.2f}", f"KSh {product.selling_price * quantity:,.2f}")): self.cart_table.setItem(row, column, QTableWidgetItem(value))
        finally: session.close()
    def clear_cart(self): self.cart.clear(); self.refresh_cart()
    def complete(self):
        if not self.cart: QMessageBox.warning(self, "POS", "Cart is empty."); return
        session = SessionLocal()
        try:
            sale = complete_sale(session, [CartLine(product_id, quantity) for product_id, quantity in self.cart.items()]); session.commit(); invoice, total = sale.invoice_number, sale.total; self.cart.clear(); self.refresh_cart(); self.refresh(); QMessageBox.information(self, "Sale Completed", f"{invoice} — KSh {total:,.2f}")
        except Exception as exc: session.rollback(); QMessageBox.critical(self, "Sale Error", f"Sale could not be completed. No stock was changed.\n{exc}")
        finally: session.close()
