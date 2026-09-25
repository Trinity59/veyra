from __future__ import annotations
from PySide6.QtWidgets import QHBoxLayout, QLabel, QListWidget, QListWidgetItem, QMessageBox, QPushButton, QSpinBox, QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget
from sqlalchemy import select
from db.engine import SessionLocal
from models.product import Product
from services.pos_service import CartLine, complete_sale

class POSPage(QWidget):
    def __init__(self):
        super().__init__(); self.cart: dict[int,int]={}; layout=QVBoxLayout(self); title=QLabel("POS"); title.setObjectName("page_title"); layout.addWidget(title); controls=QHBoxLayout(); self.search=QLineEdit(); self.search.setPlaceholderText("Search product or code..."); self.search.textChanged.connect(self.refresh); controls.addWidget(self.search); add=QPushButton("Add Selected"); add.clicked.connect(self.add_selected); controls.addWidget(add); layout.addLayout(controls); self.products=QListWidget(); self.products.itemDoubleClicked.connect(lambda _item: self.add_selected()); layout.addWidget(self.products); self.cart_table=QTableWidget(0,4); self.cart_table.setHorizontalHeaderLabels(["Product","Qty","Price","Total"]); layout.addWidget(self.cart_table); actions=QHBoxLayout(); clear=QPushButton("Clear Cart"); clear.clicked.connect(self.clear_cart); sale=QPushButton("Complete Sale"); sale.clicked.connect(self.complete); actions.addWidget(clear); actions.addWidget(sale); layout.addLayout(actions); self.refresh(); self.refresh_cart()
    def refresh(self):
        session=SessionLocal()
        try:
            term=self.search.text().strip() if hasattr(self,"search") else ""; query=select(Product).where(Product.is_active.is_(True)).order_by(Product.name)
            if term: query=query.where((Product.name.ilike(f"%{term}%")) | (Product.code.ilike(f"%{term}%")))
            self.products.clear()
            for p in session.scalars(query).all():
                item=QListWidgetItem(f"{p.name} | KSh {p.selling_price:,.2f} | Stock: {p.stock_quantity}"); item.setData(32,p.id); item.setFlags(item.flags() if p.stock_quantity else item.flags() & ~Qt.ItemIsEnabled); self.products.addItem(item)
        finally: session.close()
    def add_selected(self):
        item=self.products.currentItem()
        if not item: return
        product_id=int(item.data(32)); session=SessionLocal()
        try: p=session.get(Product,product_id); available=p.stock_quantity if p else 0
        finally: session.close()
        quantity,ok=QInputDialog.getInt(self,"Quantity",f"Available: {available}",1,1,available or 1)
        if ok and available and self.cart.get(product_id,0)+quantity<=available: self.cart[product_id]=self.cart.get(product_id,0)+quantity; self.refresh_cart()
        elif ok: QMessageBox.warning(self,"POS","Quantity exceeds available stock.")
    def refresh_cart(self):
        session=SessionLocal()
        try:
            self.cart_table.setRowCount(0)
            for r,(pid,qty) in enumerate(self.cart.items()):
                p=session.get(Product,pid)
                if not p: continue
                self.cart_table.insertRow(r); values=(p.name,str(qty),f"KSh {p.selling_price:,.2f}",f"KSh {p.selling_price*qty:,.2f}")
                for c,v in enumerate(values): self.cart_table.setItem(r,c,QTableWidgetItem(v))
        finally: session.close()
    def clear_cart(self): self.cart.clear(); self.refresh_cart()
    def complete(self):
        if not self.cart: QMessageBox.warning(self,"POS","Cart is empty."); return
        session=SessionLocal()
        try: sale=complete_sale(session,[CartLine(pid,qty) for pid,qty in self.cart.items()]); session.commit(); self.cart.clear(); self.refresh_cart(); self.refresh(); QMessageBox.information(self,"Sale Completed",f"{sale.invoice_number} — KSh {sale.total:,.2f}")
        except Exception as exc: session.rollback(); QMessageBox.critical(self,"Sale Error",f"Sale could not be completed. No stock was changed.\n{exc}")
        finally: session.close()
