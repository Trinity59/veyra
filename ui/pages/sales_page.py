from __future__ import annotations
from PySide6.QtWidgets import QHeaderView, QLabel, QMessageBox, QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget
from sqlalchemy import select
from db.engine import SessionLocal
from models.sale import Sale
class SalesPage(QWidget):
    def __init__(self):
        super().__init__(); layout=QVBoxLayout(self); title=QLabel("Sales"); title.setObjectName("page_title"); layout.addWidget(title); self.table=QTableWidget(0,5); self.table.setHorizontalHeaderLabels(["Invoice","Date","Items","Subtotal","Total"]); self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch); self.table.cellDoubleClicked.connect(self.detail); layout.addWidget(self.table); self.refresh()
    def refresh(self):
        session=SessionLocal()
        try:
            rows=session.scalars(select(Sale).order_by(Sale.sale_date.desc()).limit(100)).all(); self.table.setRowCount(len(rows))
            for r,s in enumerate(rows):
                values=(s.invoice_number,s.sale_date.strftime("%Y-%m-%d %H:%M"),str(sum(i.quantity for i in s.items)),f"KSh {s.subtotal:,.2f}",f"KSh {s.total:,.2f}")
                for c,v in enumerate(values): self.table.setItem(r,c,QTableWidgetItem(v))
        finally: session.close()
    def detail(self,row,_column):
        invoice=self.table.item(row,0).text(); session=SessionLocal()
        try:
            sale=session.scalar(select(Sale).where(Sale.invoice_number==invoice)); lines="\n".join(f"{i.product_name_snapshot} x {i.quantity} = KSh {i.line_total:,.2f}" for i in sale.items); QMessageBox.information(self,invoice,f"{lines}\n\nSubtotal: KSh {sale.subtotal:,.2f}\nVAT: KSh {sale.vat:,.2f}\nDiscount: KSh {sale.discount:,.2f}\nTotal: KSh {sale.total:,.2f}")
        finally: session.close()
