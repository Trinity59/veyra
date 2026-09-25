import os
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
from PySide6.QtWidgets import QApplication
from app import VEYRAMainWindow

def test_main_window_constructs():
    app = QApplication.instance() or QApplication([])
    window = VEYRAMainWindow()
    assert window.windowTitle() == "VEYRA"
    assert set(window.pages) == {"Dashboard", "Products", "Inventory", "POS", "Sales", "Reports", "Settings"}
    window.close()
