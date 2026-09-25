import json
from services.supabase_connector import SupabaseConnector, SupabaseConfigError

def test_supabase_connector_is_disabled_without_configuration(monkeypatch):
    monkeypatch.delenv("SUPABASE_URL", raising=False); monkeypatch.delenv("SUPABASE_PUBLISHABLE_KEY", raising=False)
    connector=SupabaseConnector(); assert not connector.enabled
    try: __import__("asyncio").run(connector.upload_json({"event":"test"}))
    except SupabaseConfigError: pass
    else: raise AssertionError("Missing Supabase configuration should fail clearly")
