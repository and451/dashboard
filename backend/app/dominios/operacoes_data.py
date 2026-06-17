"""Dados sintéticos - domínio Operações Espaciais (DGSE foguetes, lançamento satélites)."""
from __future__ import annotations
import random
from functools import lru_cache

FOGUETES = ["VSB-30", "VS-30", "VS-40", "VSB-40", "Sonda", "Cruzeiro do Sul (VLM)", "Satélite Laucher Vehicle (SLV)"]
STATUS_MISSAO = ["Concluída", "Planejada", "Em preparação", "Lançada", "Cancelada", "Adiada"]
BASES = ["CLA - Alcântara", "CLA - Barreira do Inferno", "CIS - Cuiabá", "Outra"]
SATELITES = ["CBERS-4A", "Amazonia-1", "SGDC", "SCD-1", "SCD-2", "CICERO", "SPORT", "SARA", "PLANKTON", "AESP-14"]
STATUS_SAT = ["Operacional", "Em operação", "Fim de missão", "Em desenvolvimento", "Lançado"]
APLICACOES = ["Sensoriamento Remoto", "Comunicações", "Meteorologia", "Navegação", "Pesquisa científica", "Defesa"]


@lru_cache(maxsize=1)
def gerar_lancamentos() -> tuple[dict, ...]:
    rng = random.Random(77)
    registros: list[dict] = []
    for i in range(25):
        registros.append({
            "id": f"LAN-{i+1:03d}",
            "nome": f"Missão {rng.choice(FOGUETES)} - {2020+i}",
            "foguete": rng.choice(FOGUETES),
            "base": rng.choice(BASES),
            "data_prevista": f"{rng.randint(2020,2026)}-{rng.randint(1,12):02d}-{rng.randint(1,28):02d}",
            "data_real": f"{rng.randint(2020,2026)}-{rng.randint(1,12):02d}-{rng.randint(1,28):02d}" if rng.random() < 0.7 else None,
            "status": rng.choice(STATUS_MISSAO),
            "carga": rng.choice(["Microgravidade", "Satélite", "Experimento", "Foguete de sondagem", "Teste"]),
            "altitude_km": round(rng.uniform(100, 600), 1) if rng.random() < 0.7 else None,
            "custo_missao": round(rng.uniform(1, 50) * 1_000_000, 2),
            "sucesso": rng.choice([True, False]) if rng.random() < 0.8 else None,
        })
    return tuple(registros)


@lru_cache(maxsize=1)
def gerar_satelites() -> tuple[dict, ...]:
    rng = random.Random(78)
    registros: list[dict] = []
    for sat in SATELITES:
        registros.append({
            "nome": sat,
            "aplicacao": rng.choice(APLICACOES),
            "status": rng.choice(STATUS_SAT),
            "dt_lancamento": f"{rng.randint(1993, 2024)}-{rng.randint(1,12):02d}-{rng.randint(1,28):02d}",
            "operador": rng.choice(["AEB", "INPE", "Censipam", "Parceiro internacional"]),
            "vida_util_anos": rng.randint(3, 15),
            "massa_kg": round(rng.uniform(100, 2000), 1),
            "custo_desenvolvimento": round(rng.uniform(10, 500) * 1_000_000, 2),
        })
    return tuple(registros)
