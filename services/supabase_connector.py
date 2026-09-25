from __future__ import annotations

import asyncio
import os
from concurrent.futures import ThreadPoolExecutor
from typing import Any, Mapping

import httpx

_EXECUTOR = ThreadPoolExecutor(max_workers=1, thread_name_prefix="veyra-sync")

class SupabaseConfigError(RuntimeError):
    pass

class SupabaseConnector:
    """Optional, non-blocking JSON uploader. Local SQLite remains authoritative."""
    def __init__(self, url: str | None = None, publishable_key: str | None = None, table: str = "veyra_events"):
        self.url = (url or os.getenv("SUPABASE_URL", "")).rstrip("/")
        self.publishable_key = publishable_key or os.getenv("SUPABASE_PUBLISHABLE_KEY", "")
        self.table = table
    @property
    def enabled(self) -> bool:
        return bool(self.url and self.publishable_key)
    async def upload_json(self, payload: Mapping[str, Any]) -> dict[str, Any]:
        if not self.enabled: raise SupabaseConfigError("SUPABASE_URL and SUPABASE_PUBLISHABLE_KEY are required.")
        endpoint=f"{self.url}/rest/v1/{self.table}"
        headers={"apikey":self.publishable_key,"Authorization":f"Bearer {self.publishable_key}","Content-Type":"application/json","Prefer":"return=minimal"}
        async with httpx.AsyncClient(timeout=15) as client:
            response=await client.post(endpoint,json=dict(payload),headers=headers); response.raise_for_status()
            return {"status_code": response.status_code}
    def upload_json_background(self, payload: Mapping[str, Any]):
        return _EXECUTOR.submit(lambda: asyncio.run(self.upload_json(payload)))
    def close(self): _EXECUTOR.shutdown(wait=False, cancel_futures=True)
