"""Dados sintéticos - domínio TransfereGov (URSJC)."""
from __future__ import annotations
import random
from functools import lru_cache

PROGRAMAS_TG = ["Capitalização da AEB", "Modernização do CLA", "Desenvolvimento de Satélites", "Programa Espacial Nacional", "Formação de Recursos Humanos", "Infraestrutura de Dados Espaciais"]
STATUS_TG = ["Ativo", "Suspenso", "Concluído", "Em análise", "Cancelado"]
REPASSES = ["AEB -> INPE", "AEB -> Censipam", "AEB -> UFSC", "AEB -> ITA", "AEB -> UFRJ", "AEB -> MCTI"]


@lru_cache(maxsize=1)
def gerar_programas_transfere() -> tuple[dict, ...]:
    rng = random.Random(99)
    registros: list[dict] = []
    for prog in PROGRAMAS_TG:
        repasses = rng.randint(1, 8)
        total = rng.uniform(5, 200) * 1_000_000
        executado = total * rng.uniform(0.3, 0.95)
        registros.append({
            "programa": prog,
            "codigo": f"TG-{rng.randint(1000,9999)}",
            "status": rng.choice(STATUS_TG),
            "valor_total": round(total, 2),
            "valor_executado": round(executado, 2),
            "pct_execucao": round(executado / total * 100, 1),
            "repasses": repasses,
            "convenentes": rng.randint(2, 10),
            "dt_inicio": f"{rng.randint(2020,2024)}-01-01",
            "dt_fim_prevista": f"{rng.randint(2024,2028)}-12-31",
        })
    return tuple(registros)


@lru_cache(maxsize=1)
def gerar_repasses() -> tuple[dict, ...]:
    rng = random.Random(100)
    registros: list[dict] = []
    for i in range(40):
        val = rng.uniform(0.5, 30) * 1_000_000
        registros.append({
            "id": f"REP-{i+1:04d}",
            "programa": rng.choice(PROGRAMAS_TG),
            "repasse": rng.choice(REPASSES),
            "valor": round(val, 2),
            "data": f"2024-{rng.randint(1,12):02d}-{rng.randint(1,28):02d}",
            "status": rng.choice(["Efetivado", "Pendente", "Cancelado", "Bloqueado"]),
        })
    return tuple(registros)
