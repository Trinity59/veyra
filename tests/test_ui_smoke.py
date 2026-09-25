import os
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
from PySide6.QtWidgets import QApplication
from app import VEYRAMainWindow

def test_main_window_constructs(qtbot=None):
    app = QApplication.instance() or QApplication([])
    window = VEYRAMainWindow()
    assert window.windowTitle() == "VEYRA"
    assert len(window.pages) == 7
    window.close()
