# VEYRA
Offline-first, single-user desktop inventory and POS system built with Python, PySide6, and SQLite for small-to-medium retail businesses (KES/KSh).

## Project status
This repository is being implemented incrementally in line with the approved VEYRA blueprint.

### Current implementation phase
- Phase 0: project structure and environment setup
- Phase 1: base PySide6 application shell
- Phase 2: SQLite + SQLAlchemy models and database initialization

### Core stack
- Python 3.11+
- PySide6
- SQLAlchemy
- SQLite
- pytest
- openpyxl

### Quick start
```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

### Repository layout
```text
veyra/
├── app.py
├── main.py
├── requirements.txt
├── README.md
├── core/
├── db/
├── models/
├── repositories/
├── services/
├── imports/
├── reports/
├── ui/
├── assets/
├── media/
├── backups/
├── logs/
├── tests/
└── .gitignore
```

### Notes
The application follows the approved blueprint with strict separation between UI, services, repositories, business rules, and database models.
