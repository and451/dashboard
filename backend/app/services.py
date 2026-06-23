"""Camada semantica: filtros e agregacoes do dominio Orcamento.

Centraliza as REGRAS DE NEGOCIO (metricas) num unico lugar, em vez de
espalha-las por cada painel - resolvendo um dos problemas do cenario atual.

Quando DATABASE_URL (Supabase) esta configurada, usa os dados reais do PostgreSQL;
 caso contrario, mantem o fallback para dados locais (CSV ou sinteticos).
"""
from __future__ import annotations

from collections import defaultdict

from .data import gerar_registros

try:
    from . import supabase_client as sb
except Exception:  # psycopg2 nao instalado ou DATABASE_URL ausente
    sb = None  # type: ignore

try:
    from . import supabase_rest as sb_rest
except Exception:
    sb_rest = None  # type: ignore


def _pct(num: float, den: float) -> float:
    return round((num / den) * 100, 2) if den else 0.0


def _tem_supabase() -> bool:
    """Tenta psycopg2 primeiro (com ping rapido); se falhar, tenta API REST."""
    if sb is not None and sb._DSN != "":
        # Testar se a conexao realmente funciona (firewall pode bloquear)
        try:
            import psycopg2
            con = psycopg2.connect(sb._DSN, connect_timeout=3)
            con.close()
            return True
        except Exception:
            pass  # psycopg2 disponivel mas nao consegue conectar (firewall)
    if sb_rest is not None and sb_rest._tem_supabase_rest():
        return True
    return False


def _sb_client():
    """Retorna o cliente ativo (psycopg2 ou REST)."""
    if sb is not None and sb._DSN != "":
        try:
            import psycopg2
            con = psycopg2.connect(sb._DSN, connect_timeout=3)
            con.close()
            return sb
        except Exception:
            pass
    return sb_rest


def filtrar(
    ano: int | None = None,
    programa: str | None = None,
    acao: str | None = None,
    funcao: str | None = None,
    grupo_despesa: str | None = None,
    fonte: str | None = None,
    uo: str | None = None,
) -> list[dict]:
    if _tem_supabase():
        filtros = {}
        if ano: filtros["id_ano_lanc"] = ano
        if programa: filtros["id_programa_pt"] = programa
        if acao: filtros["id_acao_pt"] = acao
        if funcao: filtros["id_funcao_pt"] = funcao
        if grupo_despesa: filtros["id_grupo_despesa_nade"] = grupo_despesa
        if fonte: filtros["id_in_resultado_lei_ceor"] = fonte
        return _sb_client().consultar_orcamento(filtros or None)

    regs = gerar_registros()
    out = []
    for r in regs:
        if ano is not None and r["ano"] != ano:
            continue
        if uo and r["uo"] != uo:
            continue
        if programa and r["programa"] != programa:
            continue
        if acao and r["acao"] != acao:
            continue
        if funcao and r["funcao"] != funcao:
            continue
        if grupo_despesa and r["grupo_despesa"] != grupo_despesa:
            continue
        if fonte and r["fonte"] != fonte:
            continue
        out.append(r)
    return out


def kpis(regs: list[dict]) -> dict:
    if _tem_supabase() and not regs:
        # Quando chamado diretamente sem filtrar, usa a query otimizada do Supabase
        return _sb_client().kpi_orcamento()

    dot = sum(r["dotacao_atual"] for r in regs)
    emp = sum(r["empenhado"] for r in regs)
    liq = sum(r["liquidado"] for r in regs)
    pag = sum(r["pago"] for r in regs)
    return {
        "dotacao_atual": round(dot, 2),
        "empenhado": round(emp, 2),
        "liquidado": round(liq, 2),
        "pago": round(pag, 2),
        "pct_empenhado": _pct(emp, dot),
        "pct_liquidado": _pct(liq, dot),
        "pct_pago": _pct(pag, dot),
        "registros": len(regs),
    }


def serie_mensal(regs: list[dict]) -> list[dict]:
    acc: dict[int, dict] = defaultdict(lambda: {"empenhado": 0.0, "liquidado": 0.0, "pago": 0.0})
    for r in regs:
        m = acc[r["mes"]]
        m["empenhado"] += r["empenhado"]
        m["liquidado"] += r["liquidado"]
        m["pago"] += r["pago"]
    return [
        {
            "mes": mes,
            "empenhado": round(v["empenhado"], 2),
            "liquidado": round(v["liquidado"], 2),
            "pago": round(v["pago"], 2),
        }
        for mes, v in sorted(acc.items())
    ]


def ranking(regs: list[dict], chave: str, limite: int = 10) -> list[dict]:
    acc: dict[str, dict] = defaultdict(
        lambda: {"dotacao_atual": 0.0, "empenhado": 0.0, "liquidado": 0.0, "pago": 0.0}
    )
    for r in regs:
        a = acc[r[chave]]
        a["dotacao_atual"] += r["dotacao_atual"]
        a["empenhado"] += r["empenhado"]
        a["liquidado"] += r["liquidado"]
        a["pago"] += r["pago"]
    itens = [
        {
            "rotulo": rotulo,
            "dotacao_atual": round(v["dotacao_atual"], 2),
            "empenhado": round(v["empenhado"], 2),
            "liquidado": round(v["liquidado"], 2),
            "pago": round(v["pago"], 2),
            "pct_empenhado": _pct(v["empenhado"], v["dotacao_atual"]),
        }
        for rotulo, v in acc.items()
    ]
    itens.sort(key=lambda x: x["dotacao_atual"], reverse=True)
    return itens[:limite]


def dimensoes() -> dict:
    if _tem_supabase():
        client = _sb_client()
        sb_dims = client.dimensoes_orcamento()
        # Adiciona anos via consulta simples (psycopg2) ou fallback para REST
        try:
            if sb is not None and sb._DSN:
                import psycopg2
                from psycopg2.extras import RealDictCursor
                con = psycopg2.connect(sb._DSN, cursor_factory=RealDictCursor)
                with con.cursor() as cur:
                    cur.execute("select distinct id_ano_lanc from public.orcamento where id_uo = '24205' order by 1")
                    anos = [r["id_ano_lanc"] for r in cur.fetchall()]
                    sb_dims["anos"] = anos
                con.close()
            else:
                # REST: extrai anos dos registros retornados
                rows = client.consultar_orcamento()
                sb_dims["anos"] = sorted({r["ano"] for r in rows if r.get("ano")})
        except Exception:
            sb_dims["anos"] = []
        return sb_dims

    regs = gerar_registros()
    def uniq(k):
        return sorted({r[k] for r in regs})
    return {
        "anos": sorted({r["ano"] for r in regs}),
        "programas": uniq("programa"),
        "acoes": uniq("acao"),
        "funcoes": uniq("funcao"),
        "grupos_despesa": uniq("grupo_despesa"),
        "fontes": uniq("fonte"),
    }
