from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QApplication,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from db.init_db import init_db
from ui.pages.inventory_page import InventoryPage
from ui.pages.pos_page import POSPage
from ui.pages.product_page import ProductPage
from ui.pages.sales_page import SalesPage
from ui.theme import APPLICATION_STYLESHEET


class DashboardPage(QWidget):
    def __init__(self) -> None:
        super().__init__()
        layout = QVBoxLayout(self)
        title = QLabel("Dashboard")
        title.setObjectName("page_title")
        label = QLabel("VEYRA operational overview is ready for the next analytics phase.")
        label.setObjectName("muted")
        layout.addWidget(title)
        layout.addWidget(label)
        layout.addStretch()


class PlaceholderPage(QWidget):
    def __init__(self, title: str, description: str) -> None:
        super().__init__()
        layout = QVBoxLayout(self)
        page_title = QLabel(title)
        page_title.setObjectName("page_title")
        detail = QLabel(description)
        detail.setObjectName("muted")
        layout.addWidget(page_title)
        layout.addWidget(detail)
        layout.addStretch()


class VEYRAMainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("VEYRA")
        self.resize(1400, 900)

        app = QApplication.instance()
        if app is not None:
            app.setStyleSheet(APPLICATION_STYLESHEET)

        self.central = QWidget()
        self.setCentralWidget(self.central)
        self.layout = QHBoxLayout(self.central)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(0)

        self.sidebar = QWidget()
        self.sidebar.setObjectName("sidebar")
        self.sidebar_layout = QVBoxLayout(self.sidebar)
        self.sidebar_layout.setContentsMargins(18, 18, 18, 18)
        self.sidebar_layout.setSpacing(10)

        logo = QLabel("VEYRA")
        logo.setStyleSheet("color: white; font-size: 26px; font-weight: 700;")
        self.sidebar_layout.addWidget(logo)

        self.nav_buttons = {}
        for name in ["Dashboard", "Products", "Inventory", "POS", "Sales", "Reports", "Settings"]:
            button = QPushButton(name)
            button.setObjectName("nav_button")
            button.clicked.connect(lambda checked=False, n=name: self.show_page(n))
            self.nav_buttons[name] = button
            self.sidebar_layout.addWidget(button)

        self.sidebar_layout.addStretch()
        self.layout.addWidget(self.sidebar, 220)

        self.stacked_widget = QStackedWidget()
        self.dashboard_page = DashboardPage()
        self.products_page = ProductPage()
        self.inventory_page = InventoryPage()
        self.pos_page = POSPage()
        self.sales_page = SalesPage()
        self.reports_page = PlaceholderPage("Reports", "Report generation, exports, and KPI summaries are scheduled for the next phase.")
        self.settings_page = PlaceholderPage("Settings", "Business profile, VAT, theme, and backup controls are scheduled for the next phase.")

        self.stacked_widget.addWidget(self.dashboard_page)
        self.stacked_widget.addWidget(self.products_page)
        self.stacked_widget.addWidget(self.inventory_page)
        self.stacked_widget.addWidget(self.pos_page)
        self.stacked_widget.addWidget(self.sales_page)
        self.stacked_widget.addWidget(self.reports_page)
        self.stacked_widget.addWidget(self.settings_page)

        self.layout.addWidget(self.stacked_widget, 1)
        self.show_page("Products")

    def show_page(self, name: str) -> None:
        mapping = {
            "Dashboard": 0,
            "Products": 1,
            "Inventory": 2,
            "POS": 3,
            "Sales": 4,
            "Reports": 5,
            "Settings": 6,
        }
        index = mapping.get(name, 0)
        self.stacked_widget.setCurrentIndex(index)
        for nav_name, button in self.nav_buttons.items():
            button.setChecked(nav_name == name)


def main() -> int:
    init_db()
    app = QApplication([])
    window = VEYRAMainWindow()
    window.show()
    return app.exec()
