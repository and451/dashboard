"""Dados sintéticos - domínio DOU (AUDIN)."""
from __future__ import annotations
import random
from functools import lru_cache

SECOES = ["Seção 1", "Seção 2", "Seção 3", "Edição Extra"]
TIPOS_PUBLICACAO = ["Portaria", "Despacho", "Extrato de contrato", "Retificação", "Aviso de licitação", "Resultado de licitação", "Nomeação", "Exoneração"]
ATOS_DOU = ["AEB", "INCRA", "MCTI", "MD", "MRE", "MS", "CGMI", "ANEEL", "ANP", "ANVISA"]


@lru_cache(maxsize=1)
def gerar_publicacoes_dou() -> tuple[dict, ...]:
    rng = random.Random(111)
    registros: list[dict] = []
    for i in range(200):
        ato = rng.choice(ATOS_DOU)
        registros.append({
            "id": f"DOU-{i+1:04d}",
            "data": f"2024-{rng.randint(1,12):02d}-{rng.randint(1,28):02d}",
            "secao": rng.choice(SECOES),
            "tipo": rng.choice(TIPOS_PUBLICACAO),
            "orgao": ato,
            "ementa": f"{rng.choice(TIPOS_PUBLICACAO)} referente a {rng.choice(['contratação', 'nomeação', 'dispensa', 'autorização', 'concessão'])}",
            "referencia_aeb": ato == "AEB",
            "link": f"https://www.in.gov.br/web/dou/-/dou-{i+1}",
        })
    return tuple(registros)
