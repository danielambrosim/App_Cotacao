-- Schema do Supabase para o App_Cotacao
-- Execute no SQL Editor do painel do Supabase (Dashboard > SQL Editor > New query).

-- IMPORTANTE sobre segurança:
-- O backend Flask em produção usa a chave ANON do Supabase (Authorization: Bearer anon)
-- para consultar e inserir. Por isso as políticas RLS abaixo liberam SELECT e INSERT
-- para a role anon. NÃO habilite "Realtime" nesta tabela e, se quiser endurecer,
-- troque o backend para a chave service_role e restrinja as políticas.

-- ---------------------------------------------------------------------------
-- Tabela: emails
-- Cadastro de e-mails para receber atualizações do sistema.
-- ---------------------------------------------------------------------------
create table if not exists public.emails (
    id            bigint generated always as identity primary key,
    email         text not null,
    subscribed_at timestamptz not null default now(),
    constraint emails_email_check check (email ~ '^[^@\s]+@[^@\s]+\.[^@\s]+$')
);

-- Garante que cada e-mail seja cadastrado uma única vez (evita duplicados).
create unique index if not exists emails_email_unique
    on public.emails (lower(email));

-- Índice para busca rápida por e-mail (verificação de duplicado).
create index if not exists emails_email_idx
    on public.emails (lower(email));

-- ---------------------------------------------------------------------------
-- Row Level Security (RLS)
-- ---------------------------------------------------------------------------
alter table public.emails enable row level security;

-- Permite SELECT (usado pelo backend para checar duplicados) com a key anon.
drop policy if exists "emails_select_anon" on public.emails;
create policy "emails_select_anon"
    on public.emails for select
    using (true);

-- Permite INSERT (cadastro de e-mail pelo app) com a key anon.
drop policy if exists "emails_insert_anon" on public.emails;
create policy "emails_insert_anon"
    on public.emails for insert
    with check (true);
