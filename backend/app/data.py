"""Gerador de dados sinteticos de execucao orcamentaria.

Substitui, no PoC, a extracao real do DaaS SERPRO / SIAFI (tabelas WD_*).
Os dados sao DETERMINISTICOS (seed fixa) e tem o mesmo formato dimensional
que a fonte real (UO 24205 / AEB), permitindo demonstrar a arquitetura sem
depender de acesso ao SERPRO.

Na producao, este modulo seria substituido por um repositorio que le o
Data Warehouse (PostgreSQL) populado pelo processo ELT (Python + dbt).
"""
from __future__ import annotations

import csv
import random
from functools import lru_cache
from pathlib import Path

UO = "24205"  # Agencia Espacial Brasileira

# Dados reais extraidos do painel COF (Base_Orcamentaria / SIAFI), ver _extracao/
_DADOS_DIR = Path(__file__).resolve().parent / "dados_reais" / "orcamento_cof"

# CO_ITEM_INFORMACAO -> campo do schema (fases orcamentarias do SIAFI)
_FASES = {9: "dotacao_inicial", 13: "dotacao_atual", 29: "empenhado", 31: "liquidado", 34: "pago"}

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


def _gerar_registros_sinteticos() -> tuple[dict, ...]:
    """Fallback sintetico (mantido para ambientes sem os dados reais)."""
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


# ----------------------------------------------------------------------------
# Carga real (COF / Base_Orcamentaria — SIAFI), formato longo pivotado por fase
# ----------------------------------------------------------------------------
def _f(v: str | None) -> float:
    if not v:
        return 0.0
    s = str(v).strip()
    if s == "" or s.lower() in ("nan", "nat", "none"):
        return 0.0
    try:
        return float(s)
    except ValueError:
        try:
            return float(s.replace(".", "").replace(",", "."))
        except ValueError:
            return 0.0


def _lab(cod: str | None, nome: str | None) -> str:
    c = (cod or "").strip()
    n = (nome or "").strip()
    if c and n:
        return f"{c} - {n}"
    return c or n or "Não informado"


def _carregar_reais_cof() -> tuple[dict, ...]:
    arq = _DADOS_DIR / "Base_Orcamentaria.csv"
    if not arq.is_file():
        return ()
    grupos: dict[tuple, dict] = {}
    with open(arq, encoding="utf-8-sig", newline="") as fh:
        for r in csv.DictReader(fh):
            try:
                co = int(float(r.get("CO_ITEM_INFORMACAO") or 0))
            except ValueError:
                continue
            campo = _FASES.get(co)
            if not campo:                       # ignora fases fora do schema
                continue
            try:
                ano = int(r.get("ID_ANO_LANC") or 0)
            except ValueError:
                continue
            mes_raw = int(_f(r.get("ID_MES_LANC")))
            mes = 12 if mes_raw >= 13 else (mes_raw if 1 <= mes_raw <= 12 else 12)
            programa = _lab(r.get("Cod Programa Orçamentário"), r.get("Título do Programa Orçamentário"))
            acao = _lab(r.get("ID_ACAO_PT"), r.get("NO_ACAO_PT"))
            ptres = (r.get("ID_PTRES") or "").strip()
            funcao = (r.get("ID_FUNCAO_PT") or "").strip() or "Não informado"
            grupo = _lab(r.get("ID_GRUPO_DESPESA_NADE"), r.get("NO_GRUPO_DESPESA_NADE"))
            fonte = _lab(r.get("ID_IN_RESULTADO_LEI_CEOR"), r.get("NO_IN_RESULTADO_LEI_CEOR"))
            uo = (r.get("ID_UO") or UO).strip()

            chave = (ano, mes, uo, programa, acao, ptres, funcao, grupo, fonte)
            reg = grupos.get(chave)
            if reg is None:
                reg = {
                    "ano": ano, "mes": mes, "uo": uo, "programa": programa,
                    "acao": acao, "ptres": ptres, "funcao": funcao,
                    "grupo_despesa": grupo, "fonte": fonte,
                    "dotacao_inicial": 0.0, "dotacao_atual": 0.0,
                    "empenhado": 0.0, "liquidado": 0.0, "pago": 0.0,
                }
                grupos[chave] = reg
            reg[campo] += _f(r.get("SALDORITEMINFORMAO"))

    for reg in grupos.values():
        for c in ("dotacao_inicial", "dotacao_atual", "empenhado", "liquidado", "pago"):
            reg[c] = round(reg[c], 2)
    return tuple(grupos.values())


@lru_cache(maxsize=1)
def gerar_registros() -> tuple[dict, ...]:
    """Conjunto de fatos de execucao orcamentaria (real COF, com fallback sintetico)."""
    reais = _carregar_reais_cof()
    return reais if reais else _gerar_registros_sinteticos()
