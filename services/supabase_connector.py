from __future__ import annotations

import os
from concurrent.futures import ThreadPoolExecutor
from typing import Any, Mapping

import httpx

_EXECUTOR = ThreadPoolExecutor(max_workers=1, thread_name_prefix="veyra-sync")


class SupabaseConfigError(RuntimeError):
    """Raised when optional remote sync is requested without public configuration."""


class SupabaseConnector:
    """Opt-in JSON event upload; local SQLite remains authoritative.

    The connector accepts only the publishable key. Never use a secret/service-role
    key in this desktop application. Configure RLS in Supabase before enabling it.
    """

    def __init__(self, url: str | None = None, publishable_key: str | None = None, table: str = "veyra_events"):
        self.url = (url or os.getenv("SUPABASE_URL", "")).rstrip("/")
        self.publishable_key = publishable_key or os.getenv("SUPABASE_PUBLISHABLE_KEY", "")
        self.table = table

    @property
    def enabled(self) -> bool:
        return bool(self.url and self.publishable_key)

    async def upload_json(self, payload: Mapping[str, Any], event_type: str = "event") -> dict[str, Any]:
        if not self.enabled:
            raise SupabaseConfigError("SUPABASE_URL and SUPABASE_PUBLISHABLE_KEY are required.")
        if not isinstance(payload, Mapping):
            raise TypeError("payload must be a mapping.")
        endpoint = f"{self.url}/rest/v1/{self.table}"
        headers = {
            "apikey": self.publishable_key,
            "Authorization": f"Bearer {self.publishable_key}",
            "Content-Type": "application/json",
            "Prefer": "return=minimal",
        }
        row = {"event_type": event_type, "payload": dict(payload)}
        async with httpx.AsyncClient(timeout=15) as client:
            response = await client.post(endpoint, json=row, headers=headers)
            response.raise_for_status()
            return {"status_code": response.status_code}

    def upload_json_background(self, payload: Mapping[str, Any], event_type: str = "event"):
        if not self.enabled:
            raise SupabaseConfigError("Supabase sync is disabled until URL and publishable key are configured.")
        return _EXECUTOR.submit(self._upload_in_worker, dict(payload), event_type)

    def _upload_in_worker(self, payload: dict[str, Any], event_type: str) -> dict[str, Any]:
        import asyncio
        return asyncio.run(self.upload_json(payload, event_type))
