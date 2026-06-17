"""Dados sintéticos - domínio Comunicação (ARI)."""
from __future__ import annotations
import random
from functools import lru_cache
from datetime import date, timedelta

VEICULOS = ["G1", "Folha de S.Paulo", "Estadão", "Valor Econômico", "Estado de Minas", "O Globo", "Revista Galileu", "SpaceNews", "Space.com", "BBC", "CNN Brasil", "BandNews", "CBN", "Rádio Nacional", "Jornal da AEB"]
TIPOS_MATERIA = ["Matéria", "Entrevista", "Press Release", "Reportagem", "Coluna", "Editorial"]
STATUS_ATENDIMENTO = ["Respondido", "Em análise", "Pendente", "Não se aplica"]
CATEGORIAS = ["Lançamento", "Pesquisa", "Cooperação internacional", "Educação", "Orçamento", "Tecnologia", "Evento"]


@lru_cache(maxsize=1)
def gerar_materias() -> tuple[dict, ...]:
    rng = random.Random(88)
    registros: list[dict] = []
    base = date(2024, 1, 1)
    for i in range(120):
        dt = base + timedelta(days=random.Random(i).randint(0, 365))
        registros.append({
            "id": f"MAT-{i+1:04d}",
            "titulo": f"Matéria sobre {rng.choice(CATEGORIAS)} - {i+1}",
            "veiculo": rng.choice(VEICULOS),
            "tipo": rng.choice(TIPOS_MATERIA),
            "categoria": rng.choice(CATEGORIAS),
            "data": dt.isoformat(),
            "url": f"https://example.com/materia/{i+1}",
            "clipping": rng.choice([True, False]),
            "repercussao": rng.randint(100, 50000),
        })
    return tuple(registros)


@lru_cache(maxsize=1)
def gerar_atendimentos() -> tuple[dict, ...]:
    rng = random.Random(89)
    registros: list[dict] = []
    for i in range(80):
        registros.append({
            "id": f"ATD-{i+1:04d}",
            "data": f"2024-{rng.randint(1,12):02d}-{rng.randint(1,28):02d}",
            "solicitante": rng.choice(["Jornalista", "Pesquisador", "Empresa", "Órgão público", "Cidadão", "Parlamentar"]),
            "assunto": rng.choice(CATEGORIAS),
            "status": rng.choice(STATUS_ATENDIMENTO),
            "prazo_dias": rng.randint(1, 15),
            "respondido_em_dias": rng.randint(0, 20),
        })
    return tuple(registros)


@lru_cache(maxsize=1)
def gerar_postagens() -> tuple[dict, ...]:
    rng = random.Random(90)
    plataformas = ["Twitter/X", "Instagram", "LinkedIn", "Facebook", "YouTube", "Site AEB"]
    registros: list[dict] = []
    for i in range(200):
        registros.append({
            "id": f"PST-{i+1:04d}",
            "plataforma": rng.choice(plataformas),
            "data": f"2024-{rng.randint(1,12):02d}-{rng.randint(1,28):02d}",
            "conteudo": f"Post sobre {rng.choice(CATEGORIAS)}",
            "alcance": rng.randint(500, 100000),
            "engajamento": rng.randint(10, 5000),
            "cliques": rng.randint(50, 15000),
        })
    return tuple(registros)
