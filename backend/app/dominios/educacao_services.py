"""Camada semântica - domínio Educação."""
from __future__ import annotations
from collections import defaultdict
from .educacao_data import gerar_cursos, gerar_alunos_aeb_escola


def cursos(unidade=None, nivel=None, status=None) -> list[dict]:
    regs = gerar_cursos()
    out = []
    for r in regs:
        if unidade and r["unidade"] != unidade: continue
        if nivel and r["nivel"] != nivel: continue
        if status and r["status"] != status: continue
        out.append(r)
    return out


def kpis_educacao() -> dict:
    crs = gerar_cursos()
    alu = gerar_alunos_aeb_escola()
    return {
        "total_cursos": len(crs),
        "total_vagas": sum(c["vagas"] for c in crs),
        "total_inscritos": sum(c["inscritos"] for c in crs),
        "total_concluintes": sum(c["concluintes"] for c in crs),
        "total_alunos": len(alu),
        "media_avaliacao": round(sum(a["avaliacao_media"] for a in alu) / max(len(alu), 1), 1),
    }


def cursos_por_unidade() -> list[dict]:
    acc: dict[str, dict] = defaultdict(lambda: {"cursos": 0, "vagas": 0, "concluintes": 0})
    for r in gerar_cursos():
        acc[r["unidade"]]["cursos"] += 1
        acc[r["unidade"]]["vagas"] += r["vagas"]
        acc[r["unidade"]]["concluintes"] += r["concluintes"]
    return [{"unidade": u, "cursos": v["cursos"], "vagas": v["vagas"], "concluintes": v["concluintes"]} for u, v in acc.items()]
