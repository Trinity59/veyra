from __future__ import annotations
from PySide6.QtWidgets import QComboBox, QFormLayout, QHBoxLayout, QHeaderView, QLabel, QLineEdit, QMessageBox, QPushButton, QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget
from sqlalchemy import select
from db.engine import SessionLocal
from models.product import Product
from models.stock_movement import StockMovement
from services.inventory_service import REASONS, record_movement

class InventoryPage(QWidget):
    def __init__(self):
        super().__init__(); layout=QVBoxLayout(self); title=QLabel("Inventory"); title.setObjectName("page_title"); layout.addWidget(title); form=QFormLayout(); self.product=QComboBox(); self.movement=QComboBox(); self.movement.addItems(["Stock In","Stock Out"]); self.reason=QComboBox(); self.reason.addItems(sorted(REASONS)); self.quantity=QLineEdit(); self.reference=QLineEdit(); self.notes=QLineEdit()
        for label, field in (("Product",self.product),("Movement",self.movement),("Reason",self.reason),("Quantity",self.quantity),("Reference",self.reference),("Notes",self.notes)): form.addRow(label,field)
        layout.addLayout(form); save=QPushButton("Save Movement"); save.clicked.connect(self.save_movement); layout.addWidget(save); self.table=QTableWidget(0,6); self.table.setHorizontalHeaderLabels(["Date","Product","Movement","Qty","Reason","Reference"]); self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch); layout.addWidget(self.table); self.refresh()
    def refresh(self):
        session=SessionLocal()
        try:
            products=session.scalars(select(Product).where(Product.is_active.is_(True)).order_by(Product.name)).all(); self.product.clear(); [self.product.addItem(f"{p.name} ({p.code})",p.id) for p in products]
            rows=session.scalars(select(StockMovement).order_by(StockMovement.created_at.desc()).limit(100)).all(); self.table.setRowCount(len(rows))
            for r,m in enumerate(rows):
                for c,v in enumerate((m.created_at.strftime("%Y-%m-%d %H:%M"),m.product.name,m.movement_type,str(m.quantity),m.reason,m.reference or "")): self.table.setItem(r,c,QTableWidgetItem(v))
        finally: session.close()
    def save_movement(self):
        if self.product.currentData() is None: QMessageBox.warning(self,"Inventory","Select a product."); return
        session=SessionLocal()
        try: record_movement(session, product_id=int(self.product.currentData()), movement_type=self.movement.currentText(), quantity=int(self.quantity.text()), reason=self.reason.currentText(), reference=self.reference.text() or None, notes=self.notes.text() or None); session.commit(); QMessageBox.information(self,"Inventory","Movement saved.")
        except Exception as exc: session.rollback(); QMessageBox.critical(self,"Inventory Error",str(exc))
        finally: session.close()
        self.refresh()
