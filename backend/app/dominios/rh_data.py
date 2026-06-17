"""Dados sintéticos - domínio RH/Gestão de Pessoas (CGP, PGD)."""
from __future__ import annotations
import random
from functools import lru_cache

CARGOS = ["Pesquisador", "Tecnologista", "Analista", "Técnico", "Administrativo", "Especialista", "Gerente", "Diretor"]
LOTACOES = ["DGSE", "DIEN", "COF", "DPOA", "DGEP", "AUDIN", "CGP", "COAD", "DGTEC", "GAB", "ACI", "ARI"]
REGIMES = ["CLT", "Estatutário", "Temporário", "Comissionado"]
PROGRAMAS_GD = ["PGD 2023", "PGD 2024", "PGD 2025", "Plano de Metas", "Gestão por Resultados"]


@lru_cache(maxsize=1)
def gerar_servidores() -> tuple[dict, ...]:
    rng = random.Random(42)
    registros: list[dict] = []
    for i in range(180):
        cargo = rng.choice(CARGOS)
        lotacao = rng.choice(LOTACOES)
        salario = rng.randint(3500, 28000) if cargo in ["Diretor", "Gerente"] else rng.randint(2500, 15000)
        registros.append({
            "matricula": f"AEB{i+1000:05d}",
            "nome": f"Servidor {i+1}",
            "cargo": cargo,
            "lotacao": lotacao,
            "regime": rng.choice(REGIMES),
            "salario": round(salario, 2),
            "admissao": f"{rng.randint(2010, 2023)}-{rng.randint(1,12):02d}-15",
            "situacao": rng.choice(["Ativo", "Ativo", "Ativo", "Afastado", "Cedido"]),
            "pgd_participante": rng.choice([True, False]),
            "pgd_programa": rng.choice(PROGRAMAS_GD) if rng.random() < 0.4 else None,
            "meta_atual": rng.randint(3, 12) if rng.random() < 0.4 else 0,
            "meta_concluida": rng.randint(0, 10) if rng.random() < 0.4 else 0,
        })
    return tuple(registros)


@lru_cache(maxsize=1)
def gerar_forca_trabalho() -> tuple[dict, ...]:
    rng = random.Random(43)
    registros: list[dict] = []
    for mes in range(1, 13):
        for lot in LOTACOES:
            total = rng.randint(5, 25)
            ocupado = rng.randint(3, total)
            registros.append({
                "ano": 2024,
                "mes": mes,
                "lotacao": lot,
                "quadro_previsto": total,
                "quadro_ocupado": ocupado,
                "quadro_vago": total - ocupado,
                "turnover": round(rng.uniform(0, 15), 1),
            })
    return tuple(registros)
