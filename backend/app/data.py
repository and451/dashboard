"""Gerador de dados sinteticos de execucao orcamentaria.

Substitui, no PoC, a extracao real do DaaS SERPRO / SIAFI (tabelas WD_*).
Os dados sao DETERMINISTICOS (seed fixa) e tem o mesmo formato dimensional
que a fonte real (UO 24205 / AEB), permitindo demonstrar a arquitetura sem
depender de acesso ao SERPRO.

Na producao, este modulo seria substituido por um repositorio que le o
Data Warehouse (PostgreSQL) populado pelo processo ELT (Python + dbt).
"""
from __future__ import annotations

import random
from functools import lru_cache

UO = "24205"  # Agencia Espacial Brasileira

PROGRAMAS = [
    "2107 - Programa Espacial Brasileiro",
    "2108 - Ciencia, Tecnologia e Inovacao",
    "0032 - Gestao e Manutencao",
]
ACOES = {
    "2107 - Programa Espacial Brasileiro": [
        "14XJ - Desenvolvimento de Satelites",
        "20V9 - Veiculos Lancadores e Infraestrutura",
        "21C0 - Aplicacoes Espaciais",
    ],
    "2108 - Ciencia, Tecnologia e Inovacao": [
        "20VB - Formacao e Capacitacao",
        "8923 - Pesquisa e Desenvolvimento",
    ],
    "0032 - Gestao e Manutencao": [
        "2000 - Administracao da Unidade",
        "212B - Beneficios aos Servidores",
    ],
}
FUNCOES = ["19 - Ciencia e Tecnologia", "04 - Administracao"]
GRUPOS = [
    "3 - Outras Despesas Correntes",
    "4 - Investimentos",
    "1 - Pessoal e Encargos",
]
FONTES = ["100 - Recursos Ordinarios", "150 - Recursos Proprios", "188 - Convenios"]
ANOS = [2023, 2024, 2025]


def _ptres(programa: str, acao: str) -> str:
    base = abs(hash(programa + acao)) % 900000 + 100000
    return str(base)


@lru_cache(maxsize=1)
def gerar_registros() -> tuple[dict, ...]:
    """Gera o conjunto de fatos (cacheado em memoria)."""
    rng = random.Random(2024)  # seed fixa -> dados estaveis
    registros: list[dict] = []
    for ano in ANOS:
        for programa in PROGRAMAS:
            for acao in ACOES[programa]:
                funcao = FUNCOES[0] if programa.startswith(("2107", "2108")) else FUNCOES[1]
                grupo = "4 - Investimentos" if "Satelites" in acao or "Lancadores" in acao else rng.choice(GRUPOS)
                fonte = rng.choice(FONTES)
                ptres = _ptres(programa, acao)
                # dotacao anual da acao
                dotacao_inicial = rng.randint(5, 80) * 1_000_000.0
                dotacao_atual = dotacao_inicial * rng.uniform(0.9, 1.25)
                # curva de execucao mensal acumulada (cresce ao longo do ano)
                empenhado_total = dotacao_atual * rng.uniform(0.55, 0.98)
                liquidado_total = empenhado_total * rng.uniform(0.6, 0.95)
                pago_total = liquidado_total * rng.uniform(0.85, 0.99)
                meses = 12 if ano < 2025 else 8  # ano corrente parcial
                # pesos mensais
                pesos = [rng.uniform(0.5, 1.5) for _ in range(meses)]
                soma = sum(pesos)
                for i in range(meses):
                    frac = pesos[i] / soma
                    registros.append(
                        {
                            "ano": ano,
                            "mes": i + 1,
                            "uo": UO,
                            "programa": programa,
                            "acao": acao,
                            "ptres": ptres,
                            "funcao": funcao,
                            "grupo_despesa": grupo,
                            "fonte": fonte,
                            "dotacao_inicial": round(dotacao_inicial / meses, 2),
                            "dotacao_atual": round(dotacao_atual / meses, 2),
                            "empenhado": round(empenhado_total * frac, 2),
                            "liquidado": round(liquidado_total * frac, 2),
                            "pago": round(pago_total * frac, 2),
                        }
                    )
    return tuple(registros)
