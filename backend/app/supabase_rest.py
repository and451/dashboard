"""Cliente Supabase via API REST (HTTP/443) — alternativa quando psycopg2 não consegue conectar.

Usa a chave anon do Supabase para ler dados publicamente (RLS já configurada no schema.sql).
Mais lento que psycopg2, mas passa por firewalls corporativos.
"""
from __future__ import annotations

import os
from urllib.request import Request, urlopen
from urllib.parse import urlencode
import json

_SUPABASE_URL = os.getenv("SUPABASE_URL", "").strip().rstrip("/")
_SUPABASE_KEY = os.getenv("SUPABASE_KEY", "").strip()


def _tem_supabase_rest() -> bool:
    return bool(_SUPABASE_URL and _SUPABASE_KEY)


def _req(path: str, params: dict | None = None, paginate: bool = False) -> list[dict]:
    url = f"{_SUPABASE_URL}/rest/v1/{path}"
    base_params = dict(params) if params else {}
    
    if not paginate:
        # Aumenta limite para 1000 (maximo default do Supabase)
        base_params["limit"] = 1000
        if base_params:
            url += "?" + urlencode(base_params)
        req = Request(
            url,
            headers={
                "apikey": _SUPABASE_KEY,
                "Authorization": f"Bearer {_SUPABASE_KEY}",
                "Accept": "application/json",
                "Prefer": "count=exact",
            },
        )
        with urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode("utf-8"))
    
    # Paginacao para ler tudo
    all_rows = []
    offset = 0
    batch = 1000
    while True:
        page_params = dict(base_params)
        page_params["limit"] = batch
        page_params["offset"] = offset
        page_url = f"{_SUPABASE_URL}/rest/v1/{path}?" + urlencode(page_params)
        req = Request(
            page_url,
            headers={
                "apikey": _SUPABASE_KEY,
                "Authorization": f"Bearer {_SUPABASE_KEY}",
                "Accept": "application/json",
            },
        )
        with urlopen(req, timeout=30) as resp:
            rows = json.loads(resp.read().decode("utf-8"))
        if not rows:
            break
        all_rows.extend(rows)
        if len(rows) < batch:
            break
        offset += batch
    return all_rows


def consultar_orcamento(filtros: dict | None = None) -> list[dict]:
    """Lê public.orcamento via REST API do Supabase.
    
    Usa a view orcamento_por_acao (ja agregada) para evitar baixar
    11 mil linhas e agregar no Python.
    """
    if not _tem_supabase_rest():
        return []

    params = {"select": "*"}
    if filtros:
        for k, v in filtros.items():
            # Mapeia campos do schema Registro para os da view
            campo_map = {
                "id_ano_lanc": "id_ano_lanc",
                "id_uo": "id_uo",
                "id_programa_pt": None,  # nao existe na view por_acao
                "id_acao_pt": "id_acao_pt",
                "id_funcao_pt": None,
                "id_grupo_despesa_nade": None,
                "id_in_resultado_lei_ceor": None,
            }
            campo = campo_map.get(k, k)
            if campo:
                params[campo] = f"eq.{v}"

    rows = _req("orcamento_por_acao", params, paginate=False)
    # Converte para o formato do schema Registro
    return [
        {
            "ano": r.get("id_ano_lanc", 0),
            "mes": 12,
            "uo": r.get("id_uo", "24205"),
            "programa": r.get("no_programa_pt", ""),
            "acao": r.get("no_acao_pt", ""),
            "ptres": r.get("id_acao_pt", ""),
            "funcao": "Não informado",
            "grupo_despesa": "",
            "fonte": "",
            "dotacao_inicial": round(r.get("loa_atualizada") or 0, 2),
            "dotacao_atual": round(r.get("loa_atualizada") or 0, 2),
            "empenhado": round(r.get("empenhado") or 0, 2),
            "liquidado": round(r.get("liquidado") or 0, 2),
            "pago": round(r.get("pago") or 0, 2),
        }
        for r in rows
    ]


def _agregar_por_fase(rows: list[dict]) -> list[dict]:
    """Agrega o formato EAV (longo) do Supabase no formato do schema Registro."""
    from collections import defaultdict

    grupos: dict = defaultdict(
        lambda: {
            "ano": 0, "mes": 12, "uo": "24205",
            "programa": "", "acao": "", "ptres": "",
            "funcao": "", "grupo_despesa": "", "fonte": "",
            "dotacao_inicial": 0.0, "dotacao_atual": 0.0,
            "empenhado": 0.0, "liquidado": 0.0, "pago": 0.0,
        }
    )

    FASES = {9: "dotacao_inicial", 13: "dotacao_atual", 29: "empenhado", 31: "liquidado", 34: "pago"}

    for r in rows:
        ano = r.get("id_ano_lanc", 0)
        mes = r.get("id_mes_lanc", 12)
        chave = (
            ano, mes,
            r.get("id_programa_pt", ""),
            r.get("id_acao_pt", ""),
            r.get("id_ptres", ""),
            r.get("id_funcao_pt", ""),
            r.get("id_grupo_despesa_nade", ""),
            r.get("id_in_resultado_lei_ceor", ""),
        )
        reg = grupos[chave]
        reg["ano"] = ano
        reg["mes"] = mes if 1 <= mes <= 12 else 12
        reg["programa"] = r.get("no_programa_pt") or r.get("id_programa_pt", "")
        reg["acao"] = r.get("no_acao_pt") or r.get("id_acao_pt", "")
        reg["ptres"] = r.get("id_ptres", "")
        reg["funcao"] = r.get("id_funcao_pt", "") or "Não informado"
        reg["grupo_despesa"] = r.get("no_grupo_despesa_nade") or r.get("id_grupo_despesa_nade", "")
        reg["fonte"] = r.get("no_in_resultado_lei_ceor") or r.get("id_in_resultado_lei_ceor", "")

        co = r.get("co_item_informacao")
        if co in FASES:
            reg[FASES[co]] = round(reg[FASES[co]] + float(r.get("saldo_item_informacao") or 0), 2)

    return list(grupos.values())


def kpi_orcamento(ano: int | None = None) -> dict:
    """Usa a view orcamento_cards (1 linha por ano/UO) — muito mais rapido."""
    from datetime import datetime
    ano_padrao = ano or datetime.now().year
    params = {
        "id_uo": "eq.24205",
        "id_ano_lanc": f"eq.{ano_padrao}",
    }
    rows = _req("orcamento_cards", params, paginate=False)
    if not rows:
        return {
            "dotacao_atual": 0, "empenhado": 0, "liquidado": 0, "pago": 0,
            "pct_empenhado": 0, "pct_liquidado": 0, "pct_pago": 0, "registros": 0,
        }
    r = rows[0]  # 1 linha = 1 ano/UO
    dot = float(r.get("loa_atualizada") or 0)
    emp = float(r.get("empenhado") or 0)
    liq = float(r.get("liquidado") or 0)
    pag = float(r.get("pago") or 0)
    return {
        "dotacao_atual": round(dot, 2),
        "empenhado": round(emp, 2),
        "liquidado": round(liq, 2),
        "pago": round(pag, 2),
        "pct_empenhado": round(emp / dot * 100, 1) if dot else 0,
        "pct_liquidado": round(liq / dot * 100, 1) if dot else 0,
        "pct_pago": round(pag / dot * 100, 1) if dot else 0,
        "registros": 1,
    }


def dimensoes_orcamento() -> dict:
    if not _tem_supabase_rest():
        return {}
    # Usa view orcamento_por_acao (ja agregada)
    rows = _req("orcamento_por_acao", {"select": "no_programa_pt", "id_uo": "eq.24205"})
    programas = []
    vistos = set()
    for r in rows:
        p = r.get("no_programa_pt", "")
        if p and p not in vistos:
            programas.append({"programa": p, "programa_nome": p})
            vistos.add(p)
    return {"programas": programas}
