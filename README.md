# VEYRA

The repository now has one authoritative application entry point (`main.py` -> `app.py`) and one page implementation for each approved module.

## Validation
```powershell
py -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
pytest -q
python main.py
pyinstaller --noconfirm --windowed --name VEYRA main.py
```

For headless test environments, set `QT_QPA_PLATFORM=offscreen`.

## Optional Supabase sync
Supabase is not required for VEYRA to operate. SQLite remains authoritative and all core features work offline. To opt in, set `SUPABASE_URL` and `SUPABASE_PUBLISHABLE_KEY` in the environment or use `services.supabase_connector.SupabaseConnector` directly.

Create a table such as `veyra_events` with a JSON column and configure Row Level Security policies appropriate for the client. Do not place a Supabase secret/service-role key in the desktop application, `.env`, or repository. The secret key supplied during setup should be rotated in Supabase because it was exposed in chat.
