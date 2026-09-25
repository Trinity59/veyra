from __future__ import annotations

from PySide6.QtWidgets import QGridLayout, QLabel, QPushButton, QVBoxLayout, QWidget
from db.engine import SessionLocal
from services.reporting_service import dashboard_metrics


class DashboardPage(QWidget):
    def __init__(self) -> None:
        super().__init__(); self.layout = QVBoxLayout(self); title = QLabel("Dashboard"); title.setObjectName("page_title"); self.layout.addWidget(title); self.grid = QGridLayout(); self.layout.addLayout(self.grid); refresh = QPushButton("Refresh Dashboard"); refresh.clicked.connect(self.refresh); self.layout.addWidget(refresh); self.layout.addStretch(); self.refresh()

    def refresh(self) -> None:
        while self.grid.count(): self.grid.takeAt(0).widget().deleteLater()
        session = SessionLocal()
        try: metrics = dashboard_metrics(session)
        finally: session.close()
        labels = [("Today's Sales", f"KSh {metrics['today_sales']:,.2f}"), ("Transactions", str(metrics["transactions"])), ("Products", str(metrics["products"])), ("Stock Value", f"KSh {metrics['stock_value']:,.2f}"), ("Low Stock", str(metrics["low_stock"])), ("Out of Stock", str(metrics["out_of_stock"]))]
        for index, (name, value) in enumerate(labels):
            card = QLabel(f"{name}\n{value}"); card.setObjectName("kpi_value"); self.grid.addWidget(card, index // 3, index % 3)
