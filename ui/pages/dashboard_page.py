from __future__ import annotations
from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget
from db.engine import SessionLocal
from services.reporting_service import dashboard_metrics
class DashboardPage(QWidget):
    def __init__(self) -> None:
        super().__init__(); self.layout = QVBoxLayout(self); title = QLabel("Dashboard"); title.setObjectName("page_title"); self.layout.addWidget(title); self.metrics = QLabel(); self.layout.addWidget(self.metrics); self.refresh(); self.layout.addStretch()
    def refresh(self) -> None:
        session = SessionLocal()
        try: m = dashboard_metrics(session)
        finally: session.close()
        self.metrics.setText(f"Today's Sales: KSh {m['today_sales']:,.2f}\nTransactions: {m['transactions']}\nProducts: {m['products']}\nStock Value: KSh {m['stock_value']:,.2f}\nLow Stock: {m['low_stock']}\nOut of Stock: {m['out_of_stock']}")
