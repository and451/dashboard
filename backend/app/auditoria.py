"""
Módulo de auditoria fiscal: detecção de saldos alongados (repetidos mes a mes).

Lógica refatorada e robusta a partir do script `Alongados.py` original.
Processa planilhas mensais de saldo de contas contábeis (origem SIAFI/Tesouro
Gerencial) e detecta aquelas cujo saldo permanece inalterado por N meses
consecutivos.

No PoC, usa dados sintéticos. Em produção, consome:
- Arquivos exportados do SIAFI / Tesouro Gerencial
- API Siconfi (MSC Orçamentária): http://apidatalake.tesouro.gov.br/docs/siconfi/
- API Portal da Transparência (despesas): portaldatransparencia.gov.br/api-de-dados
- DaaS SERPRO (opcional / se mantido)
"""
from __future__ import annotations

import logging
import random
import re
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Iterable

logger = logging.getLogger(__name__)

# Regex para detectar mes/ano no formato MMM/YYYY (ex: JAN/2024, FEV/2024)
_MES_ANO_RE = re.compile(r"^[A-Z]{3}/20\d{2}$")

# Mapeamento mes abreviado -> numero
_MES_MAP = {
    "JAN": 1, "FEV": 2, "MAR": 3, "ABR": 4, "MAI": 5, "JUN": 6,
    "JUL": 7, "AGO": 8, "SET": 9, "OUT": 10, "NOV": 11, "DEZ": 12,
}


@dataclass(frozen=True, slots=True)
class SaldoMensal:
    """Representa o saldo de uma conta contábil em um determinado mês."""

    mes: date
    ug: str
    desc_ug: str
    contabil: str
    desc_contabil: str
    corrente: str
    saldo: float


@dataclass(frozen=True, slots=True)
class ContaAlongada:
    """Resultado da auditoria: conta com saldo alongado por N meses."""

    ug: str
    desc_ug: str
    contabil: str
    desc_contabil: str
    corrente: str
    meses_alongados: int
    saldo_atual: float
    mes_referencia: date


def _parse_mes_ano(valor: str) -> date | None:
    """Converte string 'MMM/YYYY' para date(ano, mes, 1)."""
    if not _MES_ANO_RE.match(valor):
        return None
    mes_str = valor[:3].upper()
    ano = int(valor[4:8])
    mes_num = _MES_MAP.get(mes_str)
    if mes_num is None:
        return None
    return date(ano, mes_num, 1)


def _parse_excel_file(caminho: Path, *, engine: str = "openpyxl") -> list[SaldoMensal]:
    """Lê um arquivo Excel de saldos SIAFI e retorna lista de SaldoMensal.

    Levanta ValueError se não conseguir detectar a data de referência.
    """
    try:
        import pandas as pd
    except ImportError as exc:
        raise ImportError("pandas é necessário para ler arquivos Excel") from exc

    # Primeiro: detectar a data nas primeiras 12 linhas, coluna F (índice 5)
    df_header = pd.read_excel(caminho, nrows=12, header=None, engine=engine)
    mes_referencia: date | None = None
    for i in range(len(df_header)):
        celula = df_header.iloc[i, 5]
        if pd.isna(celula):
            continue
        mes_referencia = _parse_mes_ano(str(celula).strip())
        if mes_referencia:
            break

    if mes_referencia is None:
        raise ValueError(f"Não foi possível detectar MMM/YYYY em {caminho}")

    # Ler o arquivo completo com nomes de colunas fixos
    df = pd.read_excel(
        caminho,
        names=["UG", "Desc_UG", "Contabil", "Desc_Contabil", "Corrente", "Saldo"],
        dtype={
            "UG": str,
            "Desc_UG": str,
            "Contabil": str,
            "Desc_Contabil": str,
            "Corrente": str,
            "Saldo": str,
        },
        engine=engine,
    )

    # Remover linhas iniciais que não começam com dígito (cabeçalhos)
    def _comeca_com_digito(val: str) -> bool:
        try:
            return str(val)[0].isdigit()
        except Exception:
            return False

    mask = df["UG"].apply(_comeca_com_digito)
    df = df[mask].copy()

    # Remover última linha se só tiver valor na primeira coluna (linha espúria do SIAFI)
    if len(df) > 0:
        ultima = df.iloc[-1]
        if pd.isna(ultima["Desc_UG"]) and pd.isna(ultima["Desc_Contabil"]):
            if pd.isna(ultima["Corrente"]) or str(ultima["Corrente"]).strip() == "":
                df = df.iloc[:-1]

    # Converter saldo para float
    df["Saldo"] = (
        df["Saldo"]
        .astype(str)
        .str.replace(".", "", regex=False)
        .str.replace(",", ".", regex=False)
        .astype(float)
    )

    registros: list[SaldoMensal] = []
    for _, row in df.iterrows():
        registros.append(
            SaldoMensal(
                mes=mes_referencia,
                ug=str(row["UG"]).strip(),
                desc_ug=str(row["Desc_UG"]).strip(),
                contabil=str(row["Contabil"]).strip().zfill(8),
                desc_contabil=str(row["Desc_Contabil"]).strip(),
                corrente=str(row["Corrente"]).strip(),
                saldo=float(row["Saldo"]),
            )
        )
    return registros


def renomeia_arquivos(
    pasta_origem: Path,
    pasta_destino: Path,
    prefixo: str = "Alongados",
    *,
    engine: str = "openpyxl",
) -> list[Path]:
    """Lê arquivos .xlsx da pasta_origem, detecta o mês/ano e salva
    padronizado em pasta_destino com formato {prefixo}AAAAMM.xlsx.

    NÃO deleta os originais (cópia segura).
    """
    pasta_destino.mkdir(parents=True, exist_ok=True)
    gerados: list[Path] = []

    for arq in pasta_origem.iterdir():
        if not arq.is_file():
            continue
        if arq.suffix.lower() != ".xlsx":
            continue
        if arq.name.startswith("~"):
            continue
        if arq.name.lower().startswith(prefixo.lower()):
            continue

        try:
            registros = _parse_excel_file(arq, engine=engine)
        except Exception as exc:
            logger.warning("Ignorando %s: %s", arq.name, exc)
            continue

        if not registros:
            continue

        mes_ref = registros[0].mes
        nome_novo = f"{prefixo}{mes_ref.year}{mes_ref.month:02d}.xlsx"
        destino = pasta_destino / nome_novo

        # Salvar como novo arquivo padronizado
        try:
            import pandas as pd
            df_out = pd.DataFrame([r.__dict__ for r in registros])
            df_out.to_excel(destino, index=False, sheet_name=prefixo)
            gerados.append(destino)
            logger.info("Gerado: %s (origem: %s)", destino.name, arq.name)
        except Exception as exc:
            logger.error("Falha ao salvar %s: %s", destino, exc)

    return gerados


def calcular_alongamento(
    registros: Iterable[SaldoMensal],
    tolerancia: float = 0.001,
) -> list[ContaAlongada]:
    """Agrupa registros por (UG, Contabil, Corrente) e calcula quantos
    meses consecutivos o saldo permaneceu praticamente igual.
    """
    from collections import defaultdict

    # Agrupar por chave e ordenar por mês
    por_chave: dict[tuple, list[SaldoMensal]] = defaultdict(list)
    for r in registros:
        por_chave[(r.ug, r.contabil, r.corrente)].append(r)

    resultados: list[ContaAlongada] = []
    for (ug, contabil, corrente), lista in por_chave.items():
        lista.sort(key=lambda x: x.mes)
        max_rep = 0
        rep_atual = 0
        saldo_referencia = 0.0
        desc_ug = lista[0].desc_ug
        desc_contabil = lista[0].desc_contabil
        mes_ref = lista[0].mes

        for item in lista:
            if rep_atual == 0:
                saldo_referencia = item.saldo
                rep_atual = 1
                mes_ref = item.mes
            elif abs(item.saldo - saldo_referencia) < tolerancia:
                rep_atual += 1
            else:
                if rep_atual > max_rep:
                    max_rep = rep_atual
                saldo_referencia = item.saldo
                rep_atual = 1
                mes_ref = item.mes

        if rep_atual > max_rep:
            max_rep = rep_atual

        if max_rep >= 2:  # Só reporta se houver 2+ meses consecutivos
            saldo_atual = lista[-1].saldo
            resultados.append(
                ContaAlongada(
                    ug=ug,
                    desc_ug=desc_ug,
                    contabil=contabil,
                    desc_contabil=desc_contabil,
                    corrente=corrente,
                    meses_alongados=max_rep,
                    saldo_atual=saldo_atual,
                    mes_referencia=mes_ref,
                )
            )

    # Ordenar por meses alongados (decrescente) e saldo (decrescente)
    resultados.sort(key=lambda x: (-x.meses_alongados, -x.saldo_atual))
    return resultados


# ============================================================================
# Dados sintéticos para o PoC (simulam saída da API SIAFI / Tesouro Gerencial)
# ============================================================================

_UGS = [
    ("24205000", "Agencia Espacial Brasileira - Sede"),
    ("24205001", "AEB - Unidade de Lançamento de Alcântara"),
    ("24205002", "AEB - Instituto Nacional de Pesquisas Espaciais"),
]

_CONTAS = [
    ("11111001", "Caixa e Equivalentes"),
    ("11111002", "Banco do Brasil - Conta Corrente"),
    ("11111003", "Caixa Econômica - Conta Corrente"),
    ("11121001", "Aplicações Financeiras"),
    ("11121002", "Títulos Públicos Federais"),
    ("11211001", "Contas a Receber"),
    ("11211002", "Contas a Receber - Convênios"),
    ("11311001", "Estoques"),
    ("11311002", "Materiais de Consumo"),
    ("11411001", "Adiantamentos"),
    ("21111001", "Fornecedores"),
    ("21111002", "Fornecedores - Serviços"),
    ("21211001", "Empréstimos e Financiamentos"),
    ("21311001", "Contribuições Sociais a Pagar"),
    ("21411001", "Impostos e Taxas a Recolher"),
    ("31111001", "Patrimônio Líquido"),
    ("41111001", "Resultado do Exercício"),
]

_CORRENTES = ["100", "150", "200", "250", "300"]


def gerar_dados_sinteticos(
    meses: int = 12,
    seed: int = 2024,
) -> list[SaldoMensal]:
    """Gera dados sintéticos de saldo contábil mensal para o PoC."""
    rng = random.Random(seed)
    registros: list[SaldoMensal] = []

    ano_base = 2024
    for i in range(meses):
        mes = date(ano_base, i + 1, 1)
        for ug_cod, ug_desc in _UGS:
            # Cada UG tem um subconjunto de contas
            num_contas = rng.randint(5, len(_CONTAS))
            contas_ug = rng.sample(_CONTAS, num_contas)
            for cont_cod, cont_desc in contas_ug:
                corrente = rng.choice(_CORRENTES)
                # Saldo base com variação controlada
                saldo_base = rng.uniform(-500000, 2000000)
                # 30% das contas têm saldo alongado (mesmo valor por vários meses)
                if rng.random() < 0.3 and i > 0:
                    # Buscar saldo do mês anterior para manter igual
                    prev = [r for r in registros
                            if r.mes.month == mes.month - 1 and r.ug == ug_cod
                            and r.contabil == cont_cod and r.corrente == corrente]
                    if prev:
                        saldo = prev[0].saldo
                    else:
                        saldo = saldo_base
                else:
                    # Pequena variação
                    saldo = saldo_base + rng.uniform(-5000, 5000)

                registros.append(
                    SaldoMensal(
                        mes=mes,
                        ug=ug_cod,
                        desc_ug=ug_desc,
                        contabil=cont_cod,
                        desc_contabil=cont_desc,
                        corrente=corrente,
                        saldo=round(saldo, 2),
                    )
                )

    return registros


def obter_saldos_alongados_sinteticos(
    meses: int = 12,
    min_meses: int = 3,
    ug: str | None = None,
) -> list[ContaAlongada]:
    """Retorna contas alongadas com dados sintéticos para o PoC.

    Se ug for informado, filtra apenas contas da UG especificada.
    """
    todos = gerar_dados_sinteticos(meses=meses)
    if ug:
        todos = [r for r in todos if r.ug == ug]
    alongados = calcular_alongamento(todos)
    return [a for a in alongados if a.meses_alongados >= min_meses]
