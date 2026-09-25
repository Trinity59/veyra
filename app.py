import sys
from PySide6.QtWidgets import QApplication, QLabel, QMainWindow

from core.config import APP_NAME
from db.init_db import init_db


class VEYRAMainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle(APP_NAME)
        self.setMinimumSize(1200, 720)

        label = QLabel("VEYRA - Business Inventory & Sales Management System")
        label.setAlignment(__import__("PySide6.QtCore").Qt.AlignmentFlag.AlignCenter)
        self.setCentralWidget(label)


def main() -> int:
    init_db()
    app = QApplication(sys.argv)
    window = VEYRAMainWindow()
    window.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
