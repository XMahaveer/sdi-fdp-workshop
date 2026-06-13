-- ======================================================================
-- SDI Lab Cloud — V2 dashboard persistence schema (Supabase / Postgres)
-- Run ONCE in the Supabase SQL editor:
--   Project -> SQL Editor -> New query -> paste -> Run.
-- Idempotent: safe to re-run.
-- Xenith Brand Labs
-- ======================================================================

create table if not exists sessions (
  id uuid default gen_random_uuid() primary key,
  college_name text,
  trainer_name text,
  join_code text unique,
  created_at timestamp default now()
);

create table if not exists participants (
  id uuid default gen_random_uuid() primary key,
  session_id uuid references sessions(id),
  name text,
  joined_at timestamp default now()
);

create table if not exists progress (
  id uuid default gen_random_uuid() primary key,
  participant_id uuid references participants(id),
  exercise_id text,
  completed_at timestamp default now(),
  -- HARDENING (approved): one row per (participant, exercise) so the
  -- table mirrors the checkboxes exactly. The dashboard upserts with
  -- on_conflict and deletes on un-tick.
  unique (participant_id, exercise_id)
);

-- ----------------------------------------------------------------------
-- HARDENING (approved): Row-Level Security with explicit anon policies.
-- This is a workshop tool and the anon key is already shared with
-- participants, so the anon role gets full access to these 3 tables.
-- Without these policies, enabling RLS would block the anon key and the
-- dashboard would silently fall back to in-memory (looking like
-- "nothing saves"). Keeping RLS ON + explicit policies makes the access
-- intentional rather than accidental.
-- ----------------------------------------------------------------------
alter table sessions     enable row level security;
alter table participants enable row level security;
alter table progress     enable row level security;

drop policy if exists "anon all sessions"     on sessions;
drop policy if exists "anon all participants" on participants;
drop policy if exists "anon all progress"     on progress;

create policy "anon all sessions"     on sessions
  for all to anon using (true) with check (true);
create policy "anon all participants" on participants
  for all to anon using (true) with check (true);
create policy "anon all progress"     on progress
  for all to anon using (true) with check (true);
