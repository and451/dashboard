"""Dados do domínio TransfereGov (URSJC).

PONTE DADOS REAIS: lê os CSVs extraídos do painel "URSJC-Painel de Programas - TransfereGov"
(engenharia reversa do DataModel via pbixray, ver `_extracao/`) e os normaliza
para o schema `ProgramaTransfere` e `Repasse`. Os arquivos ficam em `app/dados_reais/transferegov/`
para o sistema ser autocontido na VM.

Se a pasta de dados reais não existir, cai no gerador sintético (compatibilidade).
"""
from __future__ import annotations

import csv
from datetime import date
from functools import lru_cache
from pathlib import Path

_DADOS_DIR = Path(__file__).resolve().parent.parent / "dados_reais" / "transferegov"
_HOJE = date.today()


def _f(valor: str | None) -> float:
    """String -> float tolerante (vazio/NaN -> 0.0)."""
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
    """String -> data ISO YYYY-MM-DD (vazio -> '')."""
    if not valor:
        return ""
    s = str(valor).strip()
    if s.lower() in ("nan", "nat", "none"):
        return ""
    return s[:10]


def _ler_csv(caminho: Path) -> list[dict]:
    with open(caminho, encoding="utf-8-sig", newline="") as fh:
        return list(csv.DictReader(fh))


def _carregar_reais() -> tuple[dict, ...]:
    """Carrega dados reais dos CSVs do TransfereGov."""
    if not _DADOS_DIR.is_dir():
        return []

    programas_path = _DADOS_DIR / "programas.csv"
    planos_path = _DADOS_DIR / "planos_acao.csv"
    trfs_path = _DADOS_DIR / "trfs.csv"

    if not programas_path.exists() or not planos_path.exists():
        return []

    programas = _ler_csv(programas_path)
    planos = _ler_csv(planos_path)
    trfs = _ler_csv(trfs_path) if trfs_path.exists() else []
    prog_fin_path = _DADOS_DIR / "programacoes_financeiras.csv"
    prog_fin = _ler_csv(prog_fin_path) if prog_fin_path.exists() else []

    def _i(v) -> int:
        try:
            return int(float(str(v).strip()))
        except (TypeError, ValueError):
            return 0

    # Indexar planos por programa
    planos_por_programa: dict[int, list[dict]] = {}
    for p in planos:
        planos_por_programa.setdefault(_i(p.get("id_programa")), []).append(p)

    # Ponte TRF -> plano: a TRF referencia id_programacao; a tabela
    # programacoes_financeiras liga id_programacao -> id_plano_acao.
    plano_por_programacao: dict[int, int] = {}
    for pf in prog_fin:
        plano_por_programacao[_i(pf.get("id_programacao"))] = _i(pf.get("id_plano_acao"))

    # Indexar TRFs por plano de acao (via programacoes_financeiras)
    trfs_por_plano: dict[int, list[dict]] = {}
    for t in trfs:
        plano_id = plano_por_programacao.get(_i(t.get("id_programacao")))
        if plano_id:
            trfs_por_plano.setdefault(plano_id, []).append(t)

    registros: list[dict] = []
    for prog in programas:
        prog_id = _i(prog.get("id_programa"))
        planos_prog = planos_por_programa.get(prog_id, [])

        total_programado = sum(_f(p.get("Total Plano de Ação")) for p in planos_prog)
        total_executado = 0.0
        repasses_count = 0

        for plano in planos_prog:
            plano_id = _i(plano.get("id_plano_acao"))
            trfs_plano = trfs_por_plano.get(plano_id, [])
            repasses_count += len(trfs_plano)
            total_executado += sum(_f(t.get("valor_trf")) for t in trfs_plano if t.get("situacao_contabil_trf") == "TRF004")

        # cap em 100%: execucao acumulada plurianual pode exceder o programado anual
        pct_execucao = round(min(total_executado / total_programado * 100, 100.0), 1) if total_programado > 0 else 0.0

        registros.append({
            "programa": prog.get("nome", "").strip(),
            "codigo": f"TG-{prog_id}",
            "status": prog.get("situacao", "").strip() or "Ativo",
            "valor_total": round(total_programado, 2),
            "valor_executado": round(total_executado, 2),
            "pct_execucao": pct_execucao,
            "repasses": repasses_count,
            "convenentes": len(set(p.get("unidade_descentralizada", "") for p in planos_prog)),
            "dt_inicio": "",
            "dt_fim_prevista": "",
        })

    return tuple(registros)


@lru_cache(maxsize=1)
def gerar_programas_transfere() -> tuple[dict, ...]:
    reais = _carregar_reais()
    if reais:
        return reais
    return _gerar_programas_sinteticos()


def _gerar_programas_sinteticos() -> tuple[dict, ...]:
    import random

    PROGRAMAS_TG = ["Capitalização da AEB", "Modernização do CLA", "Desenvolvimento de Satélites", "Programa Espacial Nacional", "Formação de Recursos Humanos", "Infraestrutura de Dados Espaciais"]
    STATUS_TG = ["Ativo", "Suspenso", "Concluído", "Em análise", "Cancelado"]

    rng = random.Random(99)
    registros: list[dict] = []
    for prog in PROGRAMAS_TG:
        repasses = rng.randint(1, 8)
        total = rng.uniform(5, 200) * 1_000_000
        executado = total * rng.uniform(0.3, 0.95)
        registros.append({
            "programa": prog,
            "codigo": f"TG-{rng.randint(1000,9999)}",
            "status": rng.choice(STATUS_TG),
            "valor_total": round(total, 2),
            "valor_executado": round(executado, 2),
            "pct_execucao": round(executado / total * 100, 1),
            "repasses": repasses,
            "convenentes": rng.randint(2, 10),
            "dt_inicio": f"{rng.randint(2020,2024)}-01-01",
            "dt_fim_prevista": f"{rng.randint(2024,2028)}-12-31",
        })
    return tuple(registros)


@lru_cache(maxsize=1)
def gerar_repasses() -> tuple[dict, ...]:
    """Repasses ainda sintéticos (requer join mais complexo com notas_credito)."""
    import random

    PROGRAMAS_TG = ["Capitalização da AEB", "Modernização do CLA", "Desenvolvimento de Satélites", "Programa Espacial Nacional", "Formação de Recursos Humanos", "Infraestrutura de Dados Espaciais"]
    REPASSES = ["AEB -> INPE", "AEB -> Censipam", "AEB -> UFSC", "AEB -> ITA", "AEB -> UFRJ", "AEB -> MCTI"]

    rng = random.Random(100)
    registros: list[dict] = []
    for i in range(40):
        val = rng.uniform(0.5, 30) * 1_000_000
        registros.append({
            "id": f"REP-{i+1:04d}",
            "programa": rng.choice(PROGRAMAS_TG),
            "repasse": rng.choice(REPASSES),
            "valor": round(val, 2),
            "data": f"2024-{rng.randint(1,12):02d}-{rng.randint(1,28):02d}",
            "status": rng.choice(["Efetivado", "Pendente", "Cancelado", "Bloqueado"]),
        })
    return tuple(registros)
