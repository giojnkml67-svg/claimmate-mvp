-- VA ClaimMate — Supabase schema and Row-Level Security (RLS)
-- ===========================================================================
-- Run this in the Supabase SQL Editor for your project.
--
-- WHY THIS MATTERS: this app stores veterans' personal and medical-record
-- text. Without RLS, anyone holding the project's anon key could read every
-- user's row. RLS makes the DATABASE enforce that each veteran can only ever
-- read or write their own data — even if there is a bug in the app.
--
-- IMPORTANT: configure the app (Streamlit secrets) with the project's
-- **anon / publishable** key, NOT the service_role key. The service_role key
-- bypasses RLS entirely and must never be shipped in an app. The app
-- authenticates each user and sends their JWT so these policies apply.
-- ===========================================================================

create table if not exists public.claimmate_state (
    user_id    uuid primary key references auth.users (id) on delete cascade,
    state      jsonb       not null default '{}'::jsonb,
    updated_at timestamptz not null default now()
);

-- Keep updated_at current on every write.
create or replace function public.set_updated_at()
returns trigger
language plpgsql
as $$
begin
    new.updated_at = now();
    return new;
end;
$$;

drop trigger if exists trg_claimmate_state_updated_at on public.claimmate_state;
create trigger trg_claimmate_state_updated_at
    before update on public.claimmate_state
    for each row execute function public.set_updated_at();

-- Turn on row-level security and deny by default.
alter table public.claimmate_state enable row level security;
alter table public.claimmate_state force row level security;

-- A signed-in user may only touch the row whose user_id equals their auth uid.
drop policy if exists "claimmate_select_own" on public.claimmate_state;
create policy "claimmate_select_own" on public.claimmate_state
    for select using (auth.uid() = user_id);

drop policy if exists "claimmate_insert_own" on public.claimmate_state;
create policy "claimmate_insert_own" on public.claimmate_state
    for insert with check (auth.uid() = user_id);

drop policy if exists "claimmate_update_own" on public.claimmate_state;
create policy "claimmate_update_own" on public.claimmate_state
    for update using (auth.uid() = user_id) with check (auth.uid() = user_id);

drop policy if exists "claimmate_delete_own" on public.claimmate_state;
create policy "claimmate_delete_own" on public.claimmate_state
    for delete using (auth.uid() = user_id);

-- ---------------------------------------------------------------------------
-- Optional: let a veteran delete their entire account (auth record + data)
-- from inside the app. Deleting from auth.users cascades to claimmate_state
-- via the foreign key above. This runs with elevated rights but only ever
-- deletes the *caller's own* account (auth.uid()).
-- ---------------------------------------------------------------------------
create or replace function public.delete_my_account()
returns void
language plpgsql
security definer
set search_path = public
as $$
begin
    delete from auth.users where id = auth.uid();
end;
$$;

revoke all on function public.delete_my_account() from public, anon;
grant execute on function public.delete_my_account() to authenticated;
