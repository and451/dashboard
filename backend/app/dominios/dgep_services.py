"""Camada semântica - domínio DGEP (Planejamento estratégico)."""
from __future__ import annotations
from collections import defaultdict
from .dgep_data import gerar_pde


def pde(eixo=None, status=None) -> list[dict]:
    regs = gerar_pde()
    out = []
    for r in regs:
        if eixo and r["eixo"] != eixo: continue
        if status and r["status"] != status: continue
        out.append(r)
    return out


def kpis_dgep() -> dict:
    regs = gerar_pde()
    concl = [r for r in regs if r["status"] == "Concluído"]
    return {
        "total_metas": len(regs),
        "concluidas": len(concl),
        "pct_conclusao": round(len(concl) / max(len(regs), 1) * 100, 1),
        "atrasadas": len([r for r in regs if r["status"] == "Atrasado"]),
    }


def metas_por_eixo() -> list[dict]:
    acc: dict[str, dict] = defaultdict(lambda: {"total": 0, "concluidas": 0})
    for r in gerar_pde():
        acc[r["eixo"]]["total"] += 1
        if r["status"] == "Concluído":
            acc[r["eixo"]]["concluidas"] += 1
    return [{"eixo": e, "total": v["total"], "concluidas": v["concluidas"]} for e, v in acc.items()]
