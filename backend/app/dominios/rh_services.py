"""Camada semântica - domínio RH."""
from __future__ import annotations
from collections import defaultdict
from .rh_data import gerar_servidores, gerar_forca_trabalho


def filtrar_servidores(cargo=None, lotacao=None, regime=None, situacao=None) -> list[dict]:
    regs = gerar_servidores()
    out = []
    for r in regs:
        if cargo and r["cargo"] != cargo: continue
        if lotacao and r["lotacao"] != lotacao: continue
        if regime and r["regime"] != regime: continue
        if situacao and r["situacao"] != situacao: continue
        out.append(r)
    return out


def kpis_rh(regs: list[dict]) -> dict:
    total = len(regs)
    ativos = len([r for r in regs if r["situacao"] == "Ativo"])
    pgd = len([r for r in regs if r["pgd_participante"]])
    return {
        "total_servidores": total,
        "ativos": ativos,
        "participantes_pgd": pgd,
        "media_salarial": round(sum(r["salario"] for r in regs) / max(total, 1), 2),
    }


def por_cargo(regs: list[dict]) -> list[dict]:
    acc: dict[str, int] = defaultdict(int)
    for r in regs:
        acc[r["cargo"]] += 1
    return [{"cargo": c, "quantidade": q} for c, q in acc.items()]


def por_lotacao(regs: list[dict]) -> list[dict]:
    acc: dict[str, int] = defaultdict(int)
    for r in regs:
        acc[r["lotacao"]] += 1
    return [{"lotacao": l, "quantidade": q} for l, q in acc.items()]


def forca_trabalho() -> list[dict]:
    return list(gerar_forca_trabalho())
