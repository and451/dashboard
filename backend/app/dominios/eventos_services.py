"""Camada semântica - domínio Eventos."""
from __future__ import annotations
from collections import defaultdict
from .eventos_data import gerar_eventos


def eventos(tipo=None, status=None, area=None) -> list[dict]:
    regs = gerar_eventos()
    out = []
    for r in regs:
        if tipo and r["tipo"] != tipo: continue
        if status and r["status"] != status: continue
        if area and r["area_organizadora"] != area: continue
        out.append(r)
    return out


def kpis_eventos() -> dict:
    regs = gerar_eventos()
    realizados = [r for r in regs if r["status"] == "Realizado"]
    return {
        "total_eventos": len(regs),
        "realizados": len(realizados),
        "participantes_total": sum(r["participantes"] for r in realizados),
        "custo_total": round(sum(r["custo"] for r in realizados), 2),
    }


def eventos_por_tipo() -> list[dict]:
    acc: dict[str, int] = defaultdict(int)
    for r in gerar_eventos():
        acc[r["tipo"]] += 1
    return [{"tipo": t, "quantidade": q} for t, q in acc.items()]
