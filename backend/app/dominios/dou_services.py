"""Camada semântica - domínio DOU."""
from __future__ import annotations
from collections import defaultdict
from .dou_data import gerar_publicacoes_dou


def publicacoes(secao=None, tipo=None, orgao=None, referencia_aeb=None) -> list[dict]:
    regs = gerar_publicacoes_dou()
    out = []
    for r in regs:
        if secao and r["secao"] != secao: continue
        if tipo and r["tipo"] != tipo: continue
        if orgao and r["orgao"] != orgao: continue
        if referencia_aeb is not None and r["referencia_aeb"] != referencia_aeb: continue
        out.append(r)
    return out


def kpis_dou() -> dict:
    regs = gerar_publicacoes_dou()
    aeb = [r for r in regs if r["referencia_aeb"]]
    return {
        "total_publicacoes": len(regs),
        "referentes_aeb": len(aeb),
        "por_secao": [{"secao": s, "quantidade": len([r for r in regs if r["secao"] == s])} for s in set(r["secao"] for r in regs)],
    }
