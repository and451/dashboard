"""Dados do domínio Contratos (COAD/DCONT/DIAP/DIPA/DSG).

PONTE DADOS REAIS: lê os CSVs extraídos do painel "Panorama de Contratos - DSG"
(engenharia reversa do DataModel via pbixray, ver `_extracao/`) e os normaliza
para o schema `Contrato`, **fazendo o join Contratos ↔ Empenhos ↔ Pagamentos**
(ligação por `ID_contrato`) para calcular execução real (empenhado, pago, % e
saldo). Os arquivos ficam em `app/dados_reais/contratos_dsg/` (sistema autocontido).

Se a pasta de dados reais não existir, cai no gerador sintético (compatibilidade).
"""
from __future__ import annotations

import csv
import re
from collections import defaultdict
from datetime import date
from functools import lru_cache
from pathlib import Path

_DADOS_DIR = Path(__file__).resolve().parent.parent / "dados_reais" / "contratos_dsg"
_HOJE = date.today()

# Colunas candidatas para o valor pago (varia por serviço)
_COLS_PAGO = ["Valor_pg", "Valor Pago", "Valor Total", "Pagamento"]


# ----------------------------------------------------------------------------
# Helpers de parsing
# ----------------------------------------------------------------------------
def _f(valor: str | None) -> float:
    if valor is None:
        return 0.0
    s = str(valor).strip().replace(" ", "")
    if s == "" or s.lower() in ("nan", "nat", "none"):
        return 0.0
    try:
        return float(s)
    except ValueError:
        s = s.replace(".", "").replace(",", ".")
        try:
            return float(s)
        except ValueError:
            return 0.0


def _d(valor: str | None) -> str:
    if not valor:
        return ""
    s = str(valor).strip()
    if s.lower() in ("nan", "nat", "none"):
        return ""
    return s[:10]


def _status(raw: str | None, dt_fim: str) -> str:
    s = (raw or "").strip().lower()
    if "rescis" in s:
        return "Rescisão"
    if "venc" in s:
        return "Encerrado"
    if "vig" in s:
        return "Em execução"
    if "conclu" in s:
        return "Concluído"
    if dt_fim:
        return "Em execução" if dt_fim >= _HOJE.isoformat() else "Encerrado"
    return "Em execução"


def _idc(row: dict) -> str:
    """Chave ID_contrato robusta (varia maiúsc/minúsc; pode ser int/str)."""
    v = row.get("ID_contrato", row.get("ID_Contrato", ""))
    return str(v).strip()


def _exec(empenhado: float, pago: float, valor_atual: float) -> tuple[float, float]:
    """(% execução, saldo a executar). Base = empenhado; se ausente, valor do contrato.

    pct é limitado a 0–100% e o saldo a >= 0: alguns contratos plurianuais têm
    pagamentos acumulados maiores que o empenho capturado (lacuna na origem), o que
    geraria execução > 100% / saldo negativo. Os valores brutos de empenhado/pago
    ficam preservados; o cap afeta só os indicadores derivados.
    """
    base = empenhado if empenhado > 0 else valor_atual
    if base <= 0:
        return 0.0, 0.0
    pct = round(min(pago / base * 100, 100.0), 1)
    saldo = round(max(base - pago, 0.0), 2)
    return pct, saldo


def _norm_forn(nome: str) -> str:
    """Normaliza razão social para deduplicação (remove pontuação e sufixos)."""
    s = re.sub(r"[^a-z0-9 ]", " ", (nome or "").lower())
    descartar = {"eireli", "eirelli", "epp", "ltda", "me", "sa", "s", "a",
                 "epp", "comercial", "de", "e", "do", "da"}
    toks = [t for t in s.split() if t not in descartar]
    return " ".join(toks[:3])


def _ler_csv(caminho: Path) -> list[dict]:
    with open(caminho, encoding="utf-8-sig", newline="") as fh:
        return list(csv.DictReader(fh))


def _servico(nome: str) -> str:
    """'Locação Veicular - Empenhos.csv' -> 'Locação Veicular'."""
    base = re.sub(r"\.csv$", "", nome, flags=re.IGNORECASE)
    partes = re.split(r"\s*-\s*", base)
    return partes[0].strip() if len(partes) > 1 else base.strip()


def _tipo(nome: str) -> str:
    n = nome.lower()
    if "controle de empenho" in n:
        return "controle"
    if "empenho" in n:
        return "empenhos"
    if "pagamento" in n or "fatura" in n:
        return "pagamentos"
    if "contrat" in n:
        return "contratos"
    return "outro"


# ----------------------------------------------------------------------------
# Índices de execução (somados por ID_contrato)
# ----------------------------------------------------------------------------
def _idx_empenhos(caminho: Path) -> dict[str, float]:
    idx: dict[str, float] = defaultdict(float)
    for r in _ler_csv(caminho):
        val = _f(r.get("Valor_empenho"))
        if "anul" in (r.get("Operação") or "").lower():
            val = -val
        idx[_idc(r)] += val
    return idx


def _idx_pagamentos(caminho: Path) -> dict[str, float]:
    idx: dict[str, float] = defaultdict(float)
    linhas = _ler_csv(caminho)
    cols = linhas[0].keys() if linhas else []
    col_pago = next((c for c in _COLS_PAGO if c in cols), None)
    if not col_pago:
        return idx
    for r in linhas:
        idx[_idc(r)] += _f(r.get(col_pago))
    return idx


def _idx_controle(caminho: Path) -> dict[str, tuple[float, float]]:
    """Consolidada: por Número do Processo -> (empenhado_total, pago_estimado)."""
    idx: dict[str, tuple[float, float]] = {}
    for r in _ler_csv(caminho):
        emp = sum(_f(v) for k, v in r.items() if k and k.startswith("Valor Total Empenhado"))
        saldo = _f(r.get("Saldo do Empenho 2024"))
        pago = max(emp - saldo, 0.0)
        proc = (r.get("Número do Processo") or "").strip()
        if proc:
            idx[proc] = (emp, pago)
    return idx


# ----------------------------------------------------------------------------
# Parsers
# ----------------------------------------------------------------------------
def _parse_por_servico(caminho: Path, emp_idx: dict, pag_idx: dict) -> list[dict]:
    servico = _servico(caminho.name)
    linhas = _ler_csv(caminho)
    if not linhas:
        return []
    cols = linhas[0].keys()
    col_ini = "Data_vig_inicial" if "Data_vig_inicial" in cols else "Data Incial"
    col_fim = "Data_vig_final" if "Data_vig_final" in cols else "Data Final"

    grupos: dict[str, list[dict]] = defaultdict(list)
    for r in linhas:
        grupos[(r.get("Contratada") or "—").strip()].append(r)

    slug = re.sub(r"[^a-z0-9]+", "-", servico.lower()).strip("-")
    out: list[dict] = []
    for i, (forn, rows) in enumerate(grupos.items(), start=1):
        rows.sort(key=lambda x: _d(x.get(col_ini)))
        bases = [x for x in rows if "aditiv" not in (x.get("Instrumento") or "").lower()]
        base = bases[0] if bases else rows[0]
        aditivos = sum(1 for x in rows if "aditiv" in (x.get("Instrumento") or "").lower())
        recente = max(rows, key=lambda x: _d(x.get(col_fim)) or "")
        dt_inicio = min((_d(x.get(col_ini)) for x in rows if _d(x.get(col_ini))), default="")
        dt_fim = max((_d(x.get(col_fim)) for x in rows if _d(x.get(col_fim))), default="")
        valor_inicial = _f(base.get("Valor_instrumento"))
        valor_atual = _f(recente.get("Valor_instrumento")) or valor_inicial

        idcs = {_idc(x) for x in rows}
        empenhado = round(sum(emp_idx.get(k, 0.0) for k in idcs), 2)
        pago = round(sum(pag_idx.get(k, 0.0) for k in idcs), 2)
        pct, saldo = _exec(empenhado, pago, valor_atual)

        out.append({
            "id": f"DSG-{slug}-{i:02d}",
            "numero": (base.get("Numero_intrumento") or "").strip(),
            "objeto": servico,
            "fornecedor": forn,
            "cnpj": "",
            "modalidade": "Não informado",
            "area": "DSG",
            "valor_inicial": round(valor_inicial, 2),
            "valor_atual": round(valor_atual, 2),
            "aditivos": aditivos,
            "dt_inicio": dt_inicio,
            "dt_fim": dt_fim,
            "status": _status(recente.get("Status"), dt_fim),
            "pct_execucao": pct,
            "saldo_executar": saldo,
            "uo": "24205",
        })
    return out


def _parse_consolidado(caminho: Path, controle: dict) -> list[dict]:
    out: list[dict] = []
    for r in _ler_csv(caminho):
        dt_fim = _d(r.get("Término da Vigência"))
        valor = _f(r.get("Valor do Contrato"))
        proc = (r.get("Número do Processo") or "").strip()
        empenhado, pago = controle.get(proc, (0.0, 0.0))
        pct, saldo = _exec(empenhado, pago, valor)
        ident = (r.get("Id") or "").strip() or proc
        out.append({
            "id": f"DSG-CG-{ident}",
            "numero": (r.get("Contrato") or proc or "").strip(),
            "objeto": (r.get("Objeto") or "").strip(),
            "fornecedor": (r.get("Empresa") or "—").strip(),
            "cnpj": "",
            "modalidade": (r.get("Natureza do Contrato") or "Não informado").strip(),
            "area": "DSG",
            "valor_inicial": round(valor, 2),
            "valor_atual": round(valor, 2),
            "aditivos": 0,
            "dt_inicio": _d(r.get("Início da Vigência")),
            "dt_fim": dt_fim,
            "status": _status(r.get("Status do Prazo"), dt_fim),
            "pct_execucao": pct,
            "saldo_executar": saldo,
            "uo": "24205",
        })
    return out


# ----------------------------------------------------------------------------
# Carga (real com fallback sintético)
# ----------------------------------------------------------------------------
def _carregar_reais() -> list[dict]:
    if not _DADOS_DIR.is_dir():
        return []

    # Agrupa arquivos por serviço e tipo
    por_servico: dict[str, dict[str, Path]] = defaultdict(dict)
    for p in sorted(_DADOS_DIR.glob("*.csv")):
        por_servico[_servico(p.name)][_tipo(p.name)] = p

    registros: list[dict] = []
    for servico, arquivos in por_servico.items():
        contratos_path = arquivos.get("contratos")
        if not contratos_path:
            continue
        try:
            cab = _ler_csv(contratos_path)
            cols = cab[0].keys() if cab else []
            if "Empresa" in cols and "Valor do Contrato" in cols:        # consolidada DSG
                controle = _idx_controle(arquivos["controle"]) if "controle" in arquivos else {}
                registros += _parse_consolidado(contratos_path, controle)
            elif "Contratada" in cols:                                    # por serviço (star)
                emp = _idx_empenhos(arquivos["empenhos"]) if "empenhos" in arquivos else {}
                pag = _idx_pagamentos(arquivos["pagamentos"]) if "pagamentos" in arquivos else {}
                registros += _parse_por_servico(contratos_path, emp, pag)
        except Exception:
            continue

    # dedup (consolidado x por-serviço): preferir o registro consolidado (mais rico).
    # Chave = fornecedor normalizado + valor arredondado ao milhar.
    registros.sort(key=lambda r: 0 if r["id"].startswith("DSG-CG") else 1)
    vistos: set[tuple] = set()
    unicos: list[dict] = []
    for r in registros:
        chave = (_norm_forn(r["fornecedor"]), round(r["valor_atual"], -3))
        if chave in vistos:
            continue
        vistos.add(chave)
        unicos.append(r)
    return unicos


@lru_cache(maxsize=1)
def gerar_contratos() -> tuple[dict, ...]:
    reais = _carregar_reais()
    if reais:
        return tuple(reais)
    return _gerar_contratos_sinteticos()


# ----------------------------------------------------------------------------
# Fallback sintético (mantido para ambientes sem os dados reais)
# ----------------------------------------------------------------------------
def _gerar_contratos_sinteticos() -> tuple[dict, ...]:
    import random
    from datetime import timedelta

    STATUS = ["Em execução", "Concluído", "Rescisão", "Cadastrado", "Aditado"]
    MODALIDADES = ["Pregão", "Dispensa", "Inexigibilidade", "Concorrência", "Convite", "Tomada de Preços"]
    AREAS = ["DGSE", "DIEN", "COF", "DPOA", "DGEP", "AUDIN", "CGP", "COAD", "DGTEC"]
    FORNECEDORES = [
        "SERPRO", "EMBRAER", "AEL Sistemas", "Thales", "Leonardo", "INVAP",
        "Orbital", "SpaceX", "Airbus", "Boeing", "Lockheed Martin", "ISA",
        "Telespazio", "Viasat", "Harris", "Ball Aerospace", "OHB", "SENER",
    ]
    rng = random.Random(2024)
    registros: list[dict] = []
    base = date(2022, 1, 1)
    for i in range(250):
        dt_inicio = base + timedelta(days=rng.randint(0, 900))
        prazo = rng.randint(90, 1095)
        dt_fim = dt_inicio + timedelta(days=prazo)
        valor = rng.randint(50, 5000) * 1000.0
        aditivos = rng.randint(0, 3)
        valor_atual = valor * (1 + aditivos * rng.uniform(0.05, 0.25))
        execucao = rng.uniform(0.1, 1.0)
        registros.append({
            "id": f"CNT-{i+1:04d}",
            "numero": f"{rng.randint(1, 50)}/{dt_inicio.year}",
            "objeto": f"Contratação de {rng.choice(['serviços', 'equipamentos', 'consultoria', 'desenvolvimento', 'manutenção'])} espacial - {rng.choice(FORNECEDORES)}",
            "fornecedor": rng.choice(FORNECEDORES),
            "cnpj": f"{rng.randint(10,99):02d}.{rng.randint(100,999):03d}.{rng.randint(100,999):03d}/0001-{rng.randint(10,99):02d}",
            "modalidade": rng.choice(MODALIDADES),
            "area": rng.choice(AREAS),
            "valor_inicial": round(valor, 2),
            "valor_atual": round(valor_atual, 2),
            "aditivos": aditivos,
            "dt_inicio": dt_inicio.isoformat(),
            "dt_fim": dt_fim.isoformat(),
            "status": rng.choice(STATUS),
            "pct_execucao": round(execucao * 100, 1),
            "saldo_executar": round(valor_atual * (1 - execucao), 2),
            "uo": "24205",
        })
    return tuple(registros)
