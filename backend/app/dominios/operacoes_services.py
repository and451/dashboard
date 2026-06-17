"""Camada semântica - domínio Operações Espaciais."""
from __future__ import annotations
from .operacoes_data import gerar_lancamentos, gerar_satelites


def lancamentos(status=None, foguete=None, base=None) -> list[dict]:
    regs = gerar_lancamentos()
    out = []
    for r in regs:
        if status and r["status"] != status: continue
        if foguete and r["foguete"] != foguete: continue
        if base and r["base"] != base: continue
        out.append(r)
    return out


def satelites(status=None, aplicacao=None) -> list[dict]:
    regs = gerar_satelites()
    out = []
    for r in regs:
        if status and r["status"] != status: continue
        if aplicacao and r["aplicacao"] != aplicacao: continue
        out.append(r)
    return out


def kpis_operacoes() -> dict:
    lan = gerar_lancamentos()
    sat = gerar_satelites()
    concl = [l for l in lan if l["status"] == "Concluída"]
    sucessos = [l for l in lan if l.get("sucesso")]
    return {
        "total_lancamentos": len(lan),
        "concluidos": len(concl),
        "taxa_sucesso": round(len(sucessos) / max(len(concl), 1) * 100, 1),
        "custo_total": round(sum(l["custo_missao"] for l in lan), 2),
        "satelites_operacionais": len([s for s in sat if s["status"] == "Operacional"]),
        "investimento_satelites": round(sum(s["custo_desenvolvimento"] for s in sat), 2),
    }
