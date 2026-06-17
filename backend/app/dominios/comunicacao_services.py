"""Camada semântica - domínio Comunicação."""
from __future__ import annotations
from collections import defaultdict
from .comunicacao_data import gerar_materias, gerar_atendimentos, gerar_postagens


def materias(veiculo=None, categoria=None, clipping=None) -> list[dict]:
    regs = gerar_materias()
    out = []
    for r in regs:
        if veiculo and r["veiculo"] != veiculo: continue
        if categoria and r["categoria"] != categoria: continue
        if clipping is not None and r["clipping"] != clipping: continue
        out.append(r)
    return out


def kpis_comunicacao() -> dict:
    mats = gerar_materias()
    atds = gerar_atendimentos()
    posts = gerar_postagens()
    return {
        "total_materias": len(mats),
        "total_atendimentos": len(atds),
        "total_postagens": len(posts),
        "materias_clipping": len([m for m in mats if m["clipping"]]),
        "repercussao_total": sum(m["repercussao"] for m in mats),
        "alcance_total": sum(p["alcance"] for p in posts),
    }


def materias_por_categoria() -> list[dict]:
    acc: dict[str, int] = defaultdict(int)
    for r in gerar_materias():
        acc[r["categoria"]] += 1
    return [{"categoria": c, "quantidade": q} for c, q in acc.items()]


def atendimentos_por_status() -> list[dict]:
    acc: dict[str, int] = defaultdict(int)
    for r in gerar_atendimentos():
        acc[r["status"]] += 1
    return [{"status": s, "quantidade": q} for s, q in acc.items()]


def postagens_por_plataforma() -> list[dict]:
    acc: dict[str, dict] = defaultdict(lambda: {"quantidade": 0, "alcance": 0, "engajamento": 0})
    for r in gerar_postagens():
        acc[r["plataforma"]]["quantidade"] += 1
        acc[r["plataforma"]]["alcance"] += r["alcance"]
        acc[r["plataforma"]]["engajamento"] += r["engajamento"]
    return [{"plataforma": p, "quantidade": v["quantidade"], "alcance": v["alcance"], "engajamento": v["engajamento"]} for p, v in acc.items()]
