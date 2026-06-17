"""Camada semântica - domínio TransfereGov."""
from __future__ import annotations
from collections import defaultdict
from .transferegov_data import gerar_programas_transfere, gerar_repasses


def programas(status=None) -> list[dict]:
    regs = gerar_programas_transfere()
    out = []
    for r in regs:
        if status and r["status"] != status: continue
        out.append(r)
    return out


def repasses(status=None) -> list[dict]:
    regs = gerar_repasses()
    out = []
    for r in regs:
        if status and r["status"] != status: continue
        out.append(r)
    return out


def kpis_transferegov() -> dict:
    progs = gerar_programas_transfere()
    reps = gerar_repasses()
    return {
        "total_programas": len(progs),
        "valor_total_programado": round(sum(p["valor_total"] for p in progs), 2),
        "valor_total_executado": round(sum(p["valor_executado"] for p in progs), 2),
        "total_repasses": len(reps),
        "repasses_efetivados": len([r for r in reps if r["status"] == "Efetivado"]),
    }
