from __future__ import annotations

from decimal import Decimal

from PySide6.QtWidgets import (
    QComboBox,
    QHBoxLayout,
    QInputDialog,
    QLabel,
    QListWidget,
    QListWidgetItem,
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
from services.pos_service import CartLine, complete_sale


class POSPage(QWidget):
    def __init__(self) -> None:
        super().__init__()
        self.cart: dict[int, int] = {}
        self.layout = QVBoxLayout(self)

        title = QLabel("POS")
        title.setObjectName("page_title")
        self.layout.addWidget(title)

        top = QHBoxLayout()
        self.search_box = QComboBox()
        self.search_box.setEditable(True)
        self.search_box.addItem("All Products")
        self.search_box.currentTextChanged.connect(self.refresh_products)
        top.addWidget(self.search_box)
        self.layout.addLayout(top)

        self.product_list = QListWidget()
        self.layout.addWidget(self.product_list)

        cart_header = QLabel("Cart")
        cart_header.setObjectName("page_title")
        self.layout.addWidget(cart_header)

        self.cart_table = QTableWidget(0, 4)
        self.cart_table.setHorizontalHeaderLabels(["Product", "Qty", "Price", "Total"])
        self.layout.addWidget(self.cart_table)

        actions = QHBoxLayout()
        clear_btn = QPushButton("Clear Cart")
        clear_btn.clicked.connect(self.clear_cart)
        complete_btn = QPushButton("Complete Sale")
        complete_btn.clicked.connect(self.complete_sale)
        actions.addStretch()
        actions.addWidget(clear_btn)
        actions.addWidget(complete_btn)
        self.layout.addLayout(actions)

        self.refresh_products()
        self.refresh_cart()

    def refresh_products(self) -> None:
        session = SessionLocal()
        try:
            products = session.scalars(select(Product).where(Product.is_active.is_(True)).order_by(Product.name.asc())).all()
            self.product_list.clear()
            for product in products:
                text = f"{product.name} - KSh {product.selling_price:.2f} ({product.stock_quantity} available)"
                item = QListWidgetItem(text)
                item.setData(32, product.id)
                self.product_list.addItem(item)
        finally:
            session.close()

    def add_product_to_cart(self, product_id: int) -> None:
        quantity, ok = QInputDialog.getInt(self, "Add to Cart", "Quantity", 1, 1, 999)
        if not ok:
            return
        self.cart[product_id] = self.cart.get(product_id, 0) + quantity
        self.refresh_cart()

    def clear_cart(self) -> None:
        self.cart.clear()
        self.refresh_cart()

    def refresh_cart(self) -> None:
        self.cart_table.setRowCount(len(self.cart))
        session = SessionLocal()
        try:
            row_index = 0
            subtotal = Decimal("0")
            for product_id, quantity in self.cart.items():
                product = session.get(Product, product_id)
                if product is None:
                    continue
                line_total = Decimal(str(product.selling_price)) * quantity
                subtotal += line_total
                self.cart_table.setItem(row_index, 0, QTableWidgetItem(product.name))
                self.cart_table.setItem(row_index, 1, QTableWidgetItem(str(quantity)))
                self.cart_table.setItem(row_index, 2, QTableWidgetItem(f"KSh {product.selling_price:,.2f}"))
                self.cart_table.setItem(row_index, 3, QTableWidgetItem(f"KSh {line_total:,.2f}"))
                row_index += 1
            self.cart_table.setRowCount(row_index)
            if row_index == 0:
                self.cart_table.setRowCount(1)
                self.cart_table.setItem(0, 0, QTableWidgetItem("Cart is empty"))
        finally:
            session.close()

    def complete_sale(self) -> None:
        if not self.cart:
            QMessageBox.warning(self, "POS", "Cart is empty.")
            return
        lines = [CartLine(product_id=product_id, quantity=quantity) for product_id, quantity in self.cart.items()]
        session = SessionLocal()
        try:
            sale = complete_sale(session, lines)
            session.commit()
            QMessageBox.information(self, "Sale Completed", f"Invoice {sale.invoice_number} generated successfully.")
            self.cart.clear()
            self.refresh_cart()
            self.refresh_products()
        except Exception as exc:  # pragma: no cover - UI layer handling
            session.rollback()
            QMessageBox.critical(self, "Sale Error", str(exc))
        finally:
            session.close()
