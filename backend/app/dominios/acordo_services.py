"""Camada semântica - domínio Acordos."""
from __future__ import annotations
from collections import defaultdict
from .acordo_data import gerar_acordos


def acordos(tipo=None, pais=None, status=None, area=None) -> list[dict]:
    regs = gerar_acordos()
    out = []
    for r in regs:
        if tipo and r["tipo"] != tipo: continue
        if pais and r["pais"] != pais: continue
        if status and r["status"] != status: continue
        if area and r["area"] != area: continue
        out.append(r)
    return out


def kpis_acordos() -> dict:
    regs = gerar_acordos()
    vigentes = [r for r in regs if r["status"] == "Vigente"]
    return {
        "total_acordos": len(regs),
        "vigentes": len(vigentes),
        "projetos_vinculados": sum(r["projetos_vinculados"] for r in regs),
        "valor_total_previsto": round(sum(r["valor_previsto"] or 0 for r in regs), 2),
    }


def acordos_por_pais() -> list[dict]:
    acc: dict[str, int] = defaultdict(int)
    for r in gerar_acordos():
        acc[r["pais"]] += 1
    return [{"pais": p, "quantidade": q} for p, q in acc.items()]
