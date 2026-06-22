"""Cliente Supabase para acesso ao PostgreSQL via psycopg2.

Usa a connection string do Supabase (Settings > Database > Connection string > URI)
para ler os dados reais armazenados no schema public.orcamento.
"""
from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path

try:
    import psycopg2
    from psycopg2.extras import RealDictCursor
except ImportError:  # pragma: no cover
    psycopg2 = None  # type: ignore

_DSN = os.getenv("DATABASE_URL", "").strip()


def _conectar():
    if not psycopg2:
        raise RuntimeError("psycopg2 não instalado. Rode: pip install psycopg2-binary")
    if not _DSN:
        raise RuntimeError("DATABASE_URL não configurada")
    return psycopg2.connect(_DSN, cursor_factory=RealDictCursor)


# ============================================================================
# Queries do painel Orçamento (equivalente ao services.py + data.py)
# ============================================================================

def consultar_orcamento(filtros: dict | None = None) -> list[dict]:
    """Retorna registros agregados por (ano, programa, acao, ...)
    pivotando as fases orçamentárias (9, 13, 29, 31, 34).
    Equivalente ao _carregar_reais_cof() em data.py.
    """
    if not _DSN:
        return []

    where = ["id_uo = '24205'"]
    params: list = []
    if filtros:
        for campo, val in filtros.items():
            if val:
                where.append(f"{campo} = %s")
                params.append(val)

    sql = f"""
    select
        id_ano_lanc as ano,
        id_mes_lanc as mes,
        id_programa_pt as programa,
        no_programa_pt as programa_nome,
        id_acao_pt as acao,
        no_acao_pt as acao_nome,
        id_ptres as ptres,
        id_funcao_pt as funcao,
        id_grupo_despesa_nade as grupo_despesa,
        no_grupo_despesa_nade as grupo_despesa_nome,
        id_in_resultado_lei_ceor as fonte,
        sum(case when co_item_informacao = 9  then saldo_item_informacao else 0 end) as dotacao_inicial,
        sum(case when co_item_informacao = 13 then saldo_item_informacao else 0 end) as dotacao_atual,
        sum(case when co_item_informacao = 29 then saldo_item_informacao else 0 end) as empenhado,
        sum(case when co_item_informacao = 31 then saldo_item_informacao else 0 end) as liquidado,
        sum(case when co_item_informacao = 34 then saldo_item_informacao else 0 end) as pago
    from public.orcamento
    where {' and '.join(where)}
    group by 1,2,3,4,5,6,7,8,9,10,11
    order by id_ano_lanc desc, id_programa_pt
    """

    with _conectar() as con, con.cursor() as cur:
        cur.execute(sql, params)
        return [dict(r) for r in cur.fetchall()]


def kpi_orcamento(ano: int | None = None) -> dict:
    """KPIs agregados para o painel de orçamento.
    Equivalente ao calcular_kpis() em services.py.
    """
    if not _DSN:
        return {}

    where = ["id_uo = '24205'"]
    params: list = []
    if ano:
        where.append("id_ano_lanc = %s")
        params.append(ano)

    sql = f"""
    select
        sum(case when co_item_informacao = 13 then saldo_item_informacao else 0 end) as dotacao,
        sum(case when co_item_informacao = 29 then saldo_item_informacao else 0 end) as empenhado,
        sum(case when co_item_informacao = 31 then saldo_item_informacao else 0 end) as liquidado,
        sum(case when co_item_informacao = 34 then saldo_item_informacao else 0 end) as pago
    from public.orcamento
    where {' and '.join(where)}
    """

    with _conectar() as con, con.cursor() as cur:
        cur.execute(sql, params)
        row = cur.fetchone()
        if not row:
            return {}
        dot = float(row["dotacao"] or 0)
        emp = float(row["empenhado"] or 0)
        liq = float(row["liquidado"] or 0)
        pag = float(row["pago"] or 0)
        return {
            "dotacao": round(dot, 2),
            "empenhado": round(emp, 2),
            "liquidado": round(liq, 2),
            "pago": round(pag, 2),
            "pct_empenhado": round(emp / dot * 100, 1) if dot else 0,
            "pct_liquidado": round(liq / dot * 100, 1) if dot else 0,
            "pct_pago": round(pag / dot * 100, 1) if dot else 0,
        }


def dimensoes_orcamento() -> dict:
    """Valores distintos para os filtros do painel de orçamento."""
    if not _DSN:
        return {}

    sql = """
    select distinct id_programa_pt as programa, no_programa_pt as programa_nome
    from public.orcamento where id_uo = '24205' order by 1;
    """
    with _conectar() as con, con.cursor() as cur:
        cur.execute(sql)
        programas = [dict(r) for r in cur.fetchall()]
        return {"programas": programas}
