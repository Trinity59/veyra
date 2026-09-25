-- VEYRA optional Supabase event sink.
-- Run this in Supabase SQL Editor for the project configured by SUPABASE_URL.
-- SQLite remains VEYRA's authoritative offline database.

create table if not exists public.veyra_events (
    id uuid primary key default gen_random_uuid(),
    event_type text not null default 'event',
    payload jsonb not null,
    created_at timestamptz not null default timezone('utc', now())
);

create index if not exists veyra_events_created_at_idx
    on public.veyra_events (created_at desc);

alter table public.veyra_events enable row level security;

-- Publishable-key desktop clients may append events, but cannot update or delete them.
drop policy if exists "veyra_events_public_insert" on public.veyra_events;
create policy "veyra_events_public_insert"
on public.veyra_events
for insert
to anon, authenticated
with check (jsonb_typeof(payload) = 'object');

-- No select/update/delete policies are intentionally provided for the client.
-- Add authenticated read policies only if a trusted server/admin workflow requires them.
