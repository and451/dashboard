"""Dados sintéticos - domínio Governança (DPOA assessoria: atos, integridade, agendas, portais)."""
from __future__ import annotations
import random
from functools import lru_cache

TIPOS_ATO = ["Portaria", "Resolução", "Instrução Normativa", "Decreto", "Lei", "Ordem de Serviço", "Memorando"]
STATUS_ATO = ["Vigente", "Revogado", "Em tramitação", "Arquivado"]
AREAS_ATO = ["DGSE", "DIEN", "COF", "DPOA", "DGEP", "AUDIN", "CGP", "COAD", "DGTEC", "Geral"]
TIPOS_INTEGRIDADE = ["Denúncia", "Solicitação de informação", "Reclamação", "Sugestão", "Elogio"]
STATUS_INTEGRIDADE = ["Recebida", "Em análise", "Encaminhada", "Concluída", "Arquivada"]
CANAIS_PORTAL = ["Fale Conosco", "Ouvidoria", "Acesso à Informação", "Serviços Online", "Biblioteca", "Dados Abertos"]


@lru_cache(maxsize=1)
def gerar_atos() -> tuple[dict, ...]:
    rng = random.Random(33)
    registros: list[dict] = []
    for i in range(150):
        registros.append({
            "id": f"ATO-{i+1:04d}",
            "numero": f"{rng.randint(1, 500)}/{rng.randint(2018, 2025)}",
            "tipo": rng.choice(TIPOS_ATO),
            "area": rng.choice(AREAS_ATO),
            "ementa": f"Regulamenta {rng.choice(['procedimentos', 'diretrizes', 'normas', 'critérios'])} de {rng.choice(['contratação', 'gestão', 'execução', 'fiscalização'])}",
            "dt_publicacao": f"{rng.randint(2018, 2025)}-{rng.randint(1,12):02d}-{rng.randint(1,28):02d}",
            "status": rng.choice(STATUS_ATO),
            "link": f"https://www.aeb.gov.br/atos/{i+1}",
        })
    return tuple(registros)


@lru_cache(maxsize=1)
def gerar_integridade() -> tuple[dict, ...]:
    rng = random.Random(34)
    registros: list[dict] = []
    for i in range(60):
        registros.append({
            "id": f"INT-{i+1:04d}",
            "data": f"2024-{rng.randint(1,12):02d}-{rng.randint(1,28):02d}",
            "tipo": rng.choice(TIPOS_INTEGRIDADE),
            "area": rng.choice(AREAS_ATO),
            "status": rng.choice(STATUS_INTEGRIDADE),
            "dias_aberto": rng.randint(0, 90),
            "anonimo": rng.choice([True, False]),
        })
    return tuple(registros)


@lru_cache(maxsize=1)
def gerar_agendas() -> tuple[dict, ...]:
    rng = random.Random(35)
    registros: list[dict] = []
    for i in range(80):
        registros.append({
            "id": f"AGE-{i+1:04d}",
            "titulo": f"Reunião/Compromisso {i+1}",
            "data": f"2024-{rng.randint(1,12):02d}-{rng.randint(1,28):02d}",
            "hora": f"{rng.randint(8,18):02d}:00",
            "local": rng.choice(["Presencial", "Videoconferência", "Híbrido"]),
            "participantes": rng.randint(2, 20),
            "area": rng.choice(AREAS_ATO),
            "tipo": rng.choice(["Reunião", "Audiência", "Evento", "Curso", "Visita técnica"]),
        })
    return tuple(registros)


@lru_cache(maxsize=1)
def gerar_portais() -> tuple[dict, ...]:
    rng = random.Random(36)
    registros: list[dict] = []
    for canal in CANAIS_PORTAL:
        for mes in range(1, 13):
            registros.append({
                "canal": canal,
                "ano": 2024,
                "mes": mes,
                "acessos": rng.randint(1000, 50000),
                "sessoes": rng.randint(500, 20000),
                "solicitacoes": rng.randint(10, 500),
                "atendidas": rng.randint(5, 450),
                "taxa_atendimento": round(rng.uniform(70, 99), 1),
            })
    return tuple(registros)
