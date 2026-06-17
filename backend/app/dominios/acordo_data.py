"""Dados sintéticos - domínio Acordos (ACI)."""
from __future__ import annotations
import random
from functools import lru_cache

TIPOS_ACORDO = ["Cooperação técnica", "Acordo de cooperação internacional", "Memorando de entendimento", "Protocolo de intenções", "Contrato de repasse"]
STATUS_ACORDO = ["Vigente", "Em negociação", "Concluído", "Cancelado", "Renovado"]
PAISES = ["Estados Unidos", "China", "Rússia", "França", "Alemanha", "Japão", "Índia", "Argentina", "Chile", "Portugal", "Itália", "Reino Unido", "Canadá", "Coreia do Sul", "Ucrânia"]
AREAS_COOP = ["Pesquisa espacial", "Lançamento de satélites", "Meteorologia", "Navegação", "Astronomia", "Exploração lunar", "Ciência de dados", "Educação espacial"]


@lru_cache(maxsize=1)
def gerar_acordos() -> tuple[dict, ...]:
    rng = random.Random(222)
    registros: list[dict] = []
    for i in range(35):
        val = rng.uniform(0, 50) * 1_000_000 if rng.random() < 0.4 else 0
        registros.append({
            "id": f"ACD-{i+1:04d}",
            "tipo": rng.choice(TIPOS_ACORDO),
            "pais": rng.choice(PAISES),
            "area": rng.choice(AREAS_COOP),
            "instituicao_parceira": f"Agência Espacial {rng.choice(PAISES)}",
            "dt_assinatura": f"{rng.randint(2010,2024)}-{rng.randint(1,12):02d}-{rng.randint(1,28):02d}",
            "dt_vigencia": f"{rng.randint(2020,2030)}-{rng.randint(1,12):02d}-{rng.randint(1,28):02d}",
            "status": rng.choice(STATUS_ACORDO),
            "valor_previsto": round(val, 2) if val else None,
            "projetos_vinculados": rng.randint(0, 5),
        })
    return tuple(registros)
