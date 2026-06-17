"""Camada semântica - domínio Governança."""
from __future__ import annotations
from collections import defaultdict
from .governanca_data import gerar_atos, gerar_integridade, gerar_agendas, gerar_portais


def atos(tipo=None, area=None, status=None) -> list[dict]:
    regs = gerar_atos()
    out = []
    for r in regs:
        if tipo and r["tipo"] != tipo: continue
        if area and r["area"] != area: continue
        if status and r["status"] != status: continue
        out.append(r)
    return out


def integridade(tipo=None, status=None) -> list[dict]:
    regs = gerar_integridade()
    out = []
    for r in regs:
        if tipo and r["tipo"] != tipo: continue
        if status and r["status"] != status: continue
        out.append(r)
    return out


def agendas(area=None) -> list[dict]:
    regs = gerar_agendas()
    out = []
    for r in regs:
        if area and r["area"] != area: continue
        out.append(r)
    return out


def portais() -> list[dict]:
    return list(gerar_portais())


def kpis_governanca() -> dict:
    return {
        "total_atos": len(gerar_atos()),
        "atos_vigentes": len([a for a in gerar_atos() if a["status"] == "Vigente"]),
        "total_integridade": len(gerar_integridade()),
        "pendencias_integridade": len([i for i in gerar_integridade() if i["status"] in ("Recebida", "Em análise")]),
        "total_agendas": len(gerar_agendas()),
        "acessos_portais": sum(p["acessos"] for p in gerar_portais()),
    }
