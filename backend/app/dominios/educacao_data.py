"""Dados sintéticos - domínio Educação (DGSE cursos, DIEN AEB Escola, URRN)."""
from __future__ import annotations
import random
from functools import lru_cache

CURSOS = [
    "Introdução ao Sistema Espacial Brasileiro", "Gestão de Projetos Espaciais",
    "Sensoriamento Remoto Básico", "Meteorologia Espacial", "Propulsão de Foguete",
    "Engenharia de Satélites", "Navegação por Satélite", "Comunicação via Satélite",
    "Direito Espacial Internacional", "Astronomia para Gestores", "GNSS e Aplicações",
    "Dados Abertos Espaciais", "Qualidade em Software Espacial", "Segurança da Informação",
]
STATUS_CURSO = ["Concluído", "Em andamento", "Cancelado", "Planejado"]
NIVEIS = ["Básico", "Intermediário", "Avançado", "Especialização"]
PUBLICOS = ["Servidores AEB", "Parceiros institucionais", "Estudantes", "Empresas", "Público geral"]
UNIDADES_EXEC = ["DIEN", "URRN", "URSJC", "DGEP", "DGSE"]


@lru_cache(maxsize=1)
def gerar_cursos() -> tuple[dict, ...]:
    rng = random.Random(55)
    registros: list[dict] = []
    for i in range(60):
        vagas = rng.randint(15, 120)
        inscritos = rng.randint(5, vagas + 20)
        concluintes = rng.randint(0, min(inscritos, vagas))
        registros.append({
            "id": f"CUR-{i+1:03d}",
            "nome": rng.choice(CURSOS),
            "unidade": rng.choice(UNIDADES_EXEC),
            "nivel": rng.choice(NIVEIS),
            "publico": rng.choice(PUBLICOS),
            "vagas": vagas,
            "inscritos": inscritos,
            "concluintes": concluintes,
            "taxa_conclusao": round(concluintes / max(inscritos, 1) * 100, 1),
            "carga_horaria": rng.choice([20, 40, 60, 80, 120]),
            "dt_inicio": f"2024-{rng.randint(1,12):02d}-01",
            "status": rng.choice(STATUS_CURSO),
            "custo": round(rng.uniform(5000, 80000), 2),
        })
    return tuple(registros)


@lru_cache(maxsize=1)
def gerar_alunos_aeb_escola() -> tuple[dict, ...]:
    rng = random.Random(56)
    registros: list[dict] = []
    for i in range(300):
        registros.append({
            "id": f"ALU-{i+1:04d}",
            "nome": f"Aluno {i+1}",
            "cpf": f"{rng.randint(100,999):03d}.{rng.randint(100,999):03d}.{rng.randint(100,999):03d}-{rng.randint(10,99):02d}",
            "idade": rng.randint(18, 65),
            "escolaridade": rng.choice(["Ensino Médio", "Graduação", "Pós-graduação", "Mestrado", "Doutorado"]),
            "instituicao_origem": rng.choice(["UFPE", "ITA", "INPE", "UFRJ", "UFSC", "USP", "UnB", "Outra"]),
            "cursos_concluidos": rng.randint(0, 5),
            "cursos_em_andamento": rng.randint(0, 2),
            "certificacoes": rng.randint(0, 3),
            "avaliacao_media": round(rng.uniform(6.0, 10.0), 1),
        })
    return tuple(registros)
