"""Camada semantica: filtros e agregacoes do dominio Orcamento.

Centraliza as REGRAS DE NEGOCIO (metricas) num unico lugar, em vez de
espalha-las por cada painel - resolvendo um dos problemas do cenario atual.
"""
from __future__ import annotations

from collections import defaultdict

from .data import gerar_registros


def _pct(num: float, den: float) -> float:
    return round((num / den) * 100, 2) if den else 0.0


def filtrar(
    ano: int | None = None,
    programa: str | None = None,
    acao: str | None = None,
    funcao: str | None = None,
    grupo_despesa: str | None = None,
    fonte: str | None = None,
    uo: str | None = None,
) -> list[dict]:
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
