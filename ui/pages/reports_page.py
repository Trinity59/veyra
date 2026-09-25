from __future__ import annotations

from PySide6.QtWidgets import QFileDialog, QHBoxLayout, QLabel, QMessageBox, QPushButton, QComboBox, QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget
from db.engine import SessionLocal
from services.reporting_service import export_rows, inventory_rows, sales_rows


class ReportsPage(QWidget):
    def __init__(self) -> None:
        super().__init__(); self.rows = []; layout = QVBoxLayout(self); title = QLabel("Reports"); title.setObjectName("page_title"); layout.addWidget(title); controls = QHBoxLayout(); self.report = QComboBox(); self.report.addItems(["Sales Report", "Inventory Report"]); self.period = QComboBox(); self.period.addItems(["Today", "Yesterday", "This Week", "This Month"]); refresh = QPushButton("Run Report"); refresh.clicked.connect(self.run); export = QPushButton("Export CSV / XLSX / PDF"); export.clicked.connect(self.export); controls.addWidget(self.report); controls.addWidget(self.period); controls.addWidget(refresh); controls.addWidget(export); layout.addLayout(controls); self.table = QTableWidget(); layout.addWidget(self.table); self.run()

    def run(self) -> None:
        session = SessionLocal()
        try: self.rows = inventory_rows(session) if self.report.currentText() == "Inventory Report" else sales_rows(session, self.period.currentText())
        finally: session.close()
        headers = list(self.rows[0]) if self.rows else []; self.table.setColumnCount(len(headers)); self.table.setHorizontalHeaderLabels(headers); self.table.setRowCount(len(self.rows))
        for r, row in enumerate(self.rows):
            for c, header in enumerate(headers): self.table.setItem(r, c, QTableWidgetItem(str(row[header])))

    def export(self) -> None:
        if not self.rows: QMessageBox.information(self, "Reports", "There is no data to export."); return
        path, _ = QFileDialog.getSaveFileName(self, "Export Report", "veyra-report.csv", "CSV (*.csv);;Excel (*.xlsx);;PDF (*.pdf)")
        if path:
            try: export_rows(self.rows, path, self.report.currentText(), self.period.currentText()); QMessageBox.information(self, "Report Exported", path)
            except Exception as exc: QMessageBox.critical(self, "Export Error", str(exc))
