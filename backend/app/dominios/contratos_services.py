"""Camada semântica - domínio Contratos."""
from __future__ import annotations
from collections import defaultdict
from .contratos_data import gerar_contratos


def filtrar(status=None, modalidade=None, area=None, fornecedor=None, ano=None) -> list[dict]:
    regs = gerar_contratos()
    out = []
    for r in regs:
        if status and r["status"] != status: continue
        if modalidade and r["modalidade"] != modalidade: continue
        if area and r["area"] != area: continue
        if fornecedor and fornecedor.lower() not in r["fornecedor"].lower(): continue
        if ano:
            yi = int(r["dt_inicio"].split("-")[0])
            if yi != ano: continue
        out.append(r)
    return out


def kpis(regs: list[dict]) -> dict:
    total = len(regs)
    valor_total = sum(r["valor_atual"] for r in regs)
    saldo = sum(r["saldo_executar"] for r in regs)
    em_exec = len([r for r in regs if r["status"] == "Em execução"])
    return {
        "total_contratos": total,
        "valor_total": round(valor_total, 2),
        "saldo_executar": round(saldo, 2),
        "em_execucao": em_exec,
        "pct_execucao_media": round(sum(r["pct_execucao"] for r in regs) / max(total, 1), 1),
    }


def por_status(regs: list[dict]) -> list[dict]:
    acc: dict[str, dict] = defaultdict(lambda: {"quantidade": 0, "valor": 0.0})
    for r in regs:
        acc[r["status"]]["quantidade"] += 1
        acc[r["status"]]["valor"] += r["valor_atual"]
    return [{"status": s, "quantidade": v["quantidade"], "valor": round(v["valor"], 2)} for s, v in acc.items()]


def por_area(regs: list[dict]) -> list[dict]:
    acc: dict[str, dict] = defaultdict(lambda: {"quantidade": 0, "valor": 0.0})
    for r in regs:
        acc[r["area"]]["quantidade"] += 1
        acc[r["area"]]["valor"] += r["valor_atual"]
    return [{"area": a, "quantidade": v["quantidade"], "valor": round(v["valor"], 2)} for a, v in acc.items()]
