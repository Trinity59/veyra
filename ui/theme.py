APPLICATION_STYLESHEET = """
QMainWindow {
    background: #F5F7FA;
    color: #111827;
}

QWidget {
    font-family: "Segoe UI", sans-serif;
    font-size: 12px;
    color: #111827;
}

QPushButton {
    background: #2563EB;
    color: white;
    border: none;
    border-radius: 8px;
    padding: 8px 14px;
    font-weight: 600;
}

QPushButton:hover {
    background: #1D4ED8;
}

QPushButton#secondary {
    background: #E5E7EB;
    color: #111827;
}

QPushButton#danger {
    background: #DC2626;
}

QLineEdit, QComboBox, QSpinBox, QDoubleSpinBox, QTextEdit {
    border: 1px solid #D1D5DB;
    border-radius: 8px;
    padding: 7px 10px;
    background: white;
}

QTableWidget {
    background: white;
    border: 1px solid #E5E7EB;
    gridline-color: #E5E7EB;
}

QHeaderView::section {
    background: #F3F4F6;
    color: #111827;
    padding: 8px;
    border: none;
    font-weight: 600;
}

QLabel#page_title {
    font-size: 22px;
    font-weight: 700;
    color: #111827;
}

QLabel#muted {
    color: #6B7280;
}

QLabel#kpi_value {
    font-size: 18px;
    font-weight: 700;
}

QFrame#sidebar {
    background: #111827;
    border: none;
}

QPushButton#nav_button {
    background: transparent;
    color: #E5E7EB;
    font-weight: 600;
    text-align: left;
    padding: 10px 14px;
    border-radius: 8px;
}

QPushButton#nav_button:selected, QPushButton#nav_button:checked {
    background: #1F2937;
    color: white;
}

QMessageBox {
    background: white;
}
"""
