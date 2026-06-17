"""Dados sintéticos - domínio DGEP (Planejamento estratégico)."""
from __future__ import annotations
import random
from functools import lru_cache

EIXOS = ["Eixo I - Ciência e Tecnologia Espacial", "Eixo II - Infraestrutura e Operações", "Eixo III - Gestão e Governança", "Eixo IV - Educação e Formação"]
OBJETIVOS = ["Consolidar o Sistema Espacial Brasileiro", "Desenvolver lançadores nacionais", "Expandir cooperação internacional", "Modernizar o CLA", "Fortalecer capacitação", "Ampliar uso de dados espaciais"]
STATUS_META = ["Concluído", "Em execução", "Atrasado", "Não iniciado", "Concluído com restrição"]


@lru_cache(maxsize=1)
def gerar_pde() -> tuple[dict, ...]:
    rng = random.Random(333)
    registros: list[dict] = []
    for eixo in EIXOS:
        for j in range(rng.randint(3, 6)):
            meta = f"Meta {j+1} - {rng.choice(OBJETIVOS)}"
            registros.append({
                "eixo": eixo,
                "meta": meta,
                "indicador": f"Indicador {j+1}: {rng.choice(['% de satélites operacionais', 'nº lançamentos/ano', 'investimento em P&D', 'nº acordos internacionais', 'taxa de conclusão de cursos'])}",
                "meta_ano": rng.randint(2024, 2030),
                "valor_previsto": round(rng.uniform(1, 100), 1),
                "valor_realizado": round(rng.uniform(0, 100), 1),
                "status": rng.choice(STATUS_META),
                "responsavel": rng.choice(["DGSE", "DIEN", "COF", "DPOA", "DGEP", "CGP"]),
            })
    return tuple(registros)
