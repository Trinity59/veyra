# VEYRA
Offline-first, single-user desktop inventory and POS system for SME shop owners, using Python, PySide6, SQLite, and KSh/KES.

## Current capabilities
- Product, category, stock movement, POS, and sales workflows
- Dashboard KPI cards for today's sales, transactions, products, stock value, low stock, and out-of-stock items
- Sales and inventory reports with CSV, XLSX, and PDF export
- Business profile, VAT, theme/font preferences, and local database backup/restore
- SQLAlchemy persistence with SQLite foreign-key enforcement

## Run on Windows
```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python main.py
```

## Test
```powershell
pytest -q
```

## Package for demonstration
```powershell
pyinstaller --noconfirm --windowed --name VEYRA main.py
```

All monetary values are displayed in KSh/KES. VEYRA is intentionally offline-first and single-user in Version 1.
