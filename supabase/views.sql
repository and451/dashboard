-- ============================================================================
-- Views agregadas para o frontend (Vercel) — evitam o limite de 1000 linhas do
-- PostgREST entregando os cards já somados por ano. Rode no SQL Editor.
-- ============================================================================

-- Cards do painel "Demonstrativo Orçamentário e Financeiro", 1 linha por ano/UO.
create or replace view public.orcamento_cards as
select
    id_uo,
    id_ano_lanc,
    sum(saldo_item_informacao) filter (where co_item_informacao = 8)  as ploa,
    sum(saldo_item_informacao) filter (where co_item_informacao = 9)  as loa_inicial,
    sum(saldo_item_informacao) filter (where co_item_informacao = 13) as loa_atualizada,
    sum(saldo_item_informacao) filter (where co_item_informacao = 20) as indisponivel,
    sum(saldo_item_informacao) filter (where co_item_informacao = 18) as descentralizado,
    sum(saldo_item_informacao) filter (where co_item_informacao = 22) as pre_empenhado,
    sum(saldo_item_informacao) filter (where co_item_informacao = 29) as empenhado,
    sum(saldo_item_informacao) filter (where co_item_informacao = 31) as liquidado,
    sum(saldo_item_informacao) filter (where co_item_informacao = 34) as pago,
    sum(saldo_item_informacao) filter (where co_item_informacao = 19) as disponivel,
    -- separação AEB x Outras UGs (NO_UG contém 'ESPACIAL' = AEB)
    sum(saldo_item_informacao) filter (where co_item_informacao = 29 and upper(no_ug) like '%ESPACIAL%')     as empenhado_aeb,
    sum(saldo_item_informacao) filter (where co_item_informacao = 29 and upper(no_ug) not like '%ESPACIAL%') as empenhado_outras,
    sum(saldo_item_informacao) filter (where co_item_informacao = 31 and upper(no_ug) like '%ESPACIAL%')     as liquidado_aeb,
    sum(saldo_item_informacao) filter (where co_item_informacao = 34 and upper(no_ug) like '%ESPACIAL%')     as pago_aeb,
    round(
        coalesce(sum(saldo_item_informacao) filter (where co_item_informacao = 29), 0)
        / nullif(sum(saldo_item_informacao) filter (where co_item_informacao = 13), 0) * 100, 2
    ) as execucao_pct
from public.orcamento
group by id_uo, id_ano_lanc;

-- Execução por ação (para o detalhamento / ranking), 1 linha por ano/ação.
create or replace view public.orcamento_por_acao as
select
    id_uo,
    id_ano_lanc,
    id_acao_pt,
    max(no_acao_pt)    as no_acao_pt,
    max(no_programa_pt) as no_programa_pt,
    sum(saldo_item_informacao) filter (where co_item_informacao = 13) as loa_atualizada,
    sum(saldo_item_informacao) filter (where co_item_informacao = 29) as empenhado,
    sum(saldo_item_informacao) filter (where co_item_informacao = 31) as liquidado,
    sum(saldo_item_informacao) filter (where co_item_informacao = 34) as pago
from public.orcamento
group by id_uo, id_ano_lanc, id_acao_pt;

-- Leitura pública das views (o frontend usa a chave anon).
grant select on public.orcamento_cards   to anon, authenticated;
grant select on public.orcamento_por_acao to anon, authenticated;

-- Conferência: select * from public.orcamento_cards where id_uo='24205' order by id_ano_lanc;
