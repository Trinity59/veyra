# Supabase optional sync

Supabase is optional. VEYRA continues to operate offline with SQLite as the authoritative store.

## Create `veyra_events`

1. Open the Supabase SQL Editor for the VEYRA project.
2. Run [`supabase/migrations/001_create_veyra_events.sql`](supabase/migrations/001_create_veyra_events.sql).
3. The migration creates `public.veyra_events` with:
   - `id` UUID primary key
   - `event_type` text
   - `payload` JSONB
   - `created_at` UTC timestamp
4. RLS permits only inserts for `anon` and `authenticated`; the client has no read, update, or delete policy.

## Configure locally

Copy `.env.example` to `.env` and load the two values into the process environment before starting VEYRA. Do not commit `.env`.

The connector sends rows shaped like:

```json
{
  "event_type": "sale_completed",
  "payload": {"invoice_number": "INV-...", "total": 123.45}
}
```

Use `SupabaseConnector.upload_json_background(...)` for non-blocking uploads. A failed remote upload must not fail or roll back a local SQLite transaction.

Never put a Supabase secret/service-role key in the desktop application. Any secret key previously exposed must be rotated in Supabase.
