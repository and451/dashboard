"""Dados sintéticos - domínio Eventos (GAB Presidência)."""
from __future__ import annotations
import random
from functools import lru_cache

TIPOS_EVENTO = ["Cerimônia", "Reunião", "Conferência", "Workshop", "Visita", "Lançamento", "Formatura", "Audiência pública"]
STATUS_EVENTO = ["Realizado", "Planejado", "Cancelado", "Adiado"]
PUBLICO = ["Interno", "Externo", "Misto"]
LOCAL = ["Sede AEB", "CLA", "INPE", "UF", "Centro de Convenções", "Parque tecnológico", "Online"]


@lru_cache(maxsize=1)
def gerar_eventos() -> tuple[dict, ...]:
    rng = random.Random(66)
    registros: list[dict] = []
    for i in range(60):
        participantes = rng.randint(10, 500)
        registros.append({
            "id": f"EVT-{i+1:04d}",
            "titulo": f"Evento {rng.choice(TIPOS_EVENTO)} {i+1}",
            "tipo": rng.choice(TIPOS_EVENTO),
            "data": f"2024-{rng.randint(1,12):02d}-{rng.randint(1,28):02d}",
            "local": rng.choice(LOCAL),
            "publico": rng.choice(PUBLICO),
            "participantes": participantes,
            "participantes_presenciais": rng.randint(0, participantes),
            "custo": round(rng.uniform(5000, 200000), 2),
            "status": rng.choice(STATUS_EVENTO),
            "area_organizadora": rng.choice(["GAB", "DGSE", "DIEN", "DGEP", "COF", "DPOA"]),
        })
    return tuple(registros)
