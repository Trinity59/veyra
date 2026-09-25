from __future__ import annotations

import sys
from PySide6.QtWidgets import QApplication, QHBoxLayout, QLabel, QMainWindow, QPushButton, QStackedWidget, QVBoxLayout, QWidget
from core.config import APP_NAME
from db.init_db import init_db
from ui.pages.dashboard_page import DashboardPage
from ui.pages.inventory_page import InventoryPage
from ui.pages.pos_page import POSPage
from ui.pages.product_page import ProductPage
from ui.pages.reports_page import ReportsPage
from ui.pages.sales_page import SalesPage
from ui.pages.settings_page import SettingsPage
from ui.theme import APPLICATION_STYLESHEET

class VEYRAMainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle(APP_NAME)
        self.resize(1400, 900)
        root = QWidget(); root_layout = QHBoxLayout(root); root_layout.setContentsMargins(0, 0, 0, 0)
        side = QWidget(); side.setObjectName("sidebar"); sidebar = QVBoxLayout(side)
        brand = QLabel(APP_NAME); brand.setStyleSheet("color:white;font-size:26px;font-weight:700"); sidebar.addWidget(brand)
        self.stack = QStackedWidget()
        self.pages = {"Dashboard": DashboardPage(), "Products": ProductPage(), "Inventory": InventoryPage(), "POS": POSPage(), "Sales": SalesPage(), "Reports": ReportsPage(), "Settings": SettingsPage()}
        self.buttons = {}
        for name, page in self.pages.items():
            button = QPushButton(name); button.setObjectName("nav_button"); button.setCheckable(True); button.clicked.connect(lambda _=False, n=name: self.show_page(n)); self.buttons[name] = button; sidebar.addWidget(button); self.stack.addWidget(page)
        sidebar.addStretch(); root_layout.addWidget(side, 0); root_layout.addWidget(self.stack, 1); self.setCentralWidget(root); self.show_page("Dashboard")

    def show_page(self, name: str) -> None:
        self.stack.setCurrentWidget(self.pages[name])
        for page_name, button in self.buttons.items(): button.setChecked(page_name == name)
        page = self.pages[name]
        if hasattr(page, "refresh"): page.refresh()

def main() -> int:
    init_db(); app = QApplication.instance() or QApplication(sys.argv); app.setStyleSheet(APPLICATION_STYLESHEET); window = VEYRAMainWindow(); window.show(); return app.exec()
