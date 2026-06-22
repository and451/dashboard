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


def _req(path: str, params: dict | None = None) -> list[dict]:
    url = f"{_SUPABASE_URL}/rest/v1/{path}"
    if params:
        url += "?" + urlencode(params)
    req = Request(
        url,
        headers={
            "apikey": _SUPABASE_KEY,
            "Authorization": f"Bearer {_SUPABASE_KEY}",
            "Accept": "application/json",
        },
    )
    with urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode("utf-8"))


def consultar_orcamento(filtros: dict | None = None) -> list[dict]:
    """Lê public.orcamento via REST API do Supabase."""
    if not _tem_supabase_rest():
        return []

    # Para queries complexas (group by, sum), usamos uma função RPC
    # ou fazemos a agregação no Python (menos eficiente, mas funciona)
    params = {"select": "*", "limit": 10000}
    if filtros:
        for k, v in filtros.items():
            params[f"{k}"] = f"eq.{v}"

    rows = _req("orcamento", params)
    return _agregar_por_fase(rows)


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
    rows = consultar_orcamento({"id_ano_lanc": ano} if ano else None)
    dot = sum(r["dotacao_atual"] for r in rows)
    emp = sum(r["empenhado"] for r in rows)
    liq = sum(r["liquidado"] for r in rows)
    pag = sum(r["pago"] for r in rows)
    return {
        "dotacao_atual": round(dot, 2),
        "empenhado": round(emp, 2),
        "liquidado": round(liq, 2),
        "pago": round(pag, 2),
        "pct_empenhado": round(emp / dot * 100, 1) if dot else 0,
        "pct_liquidado": round(liq / dot * 100, 1) if dot else 0,
        "pct_pago": round(pag / dot * 100, 1) if dot else 0,
        "registros": len(rows),
    }


def dimensoes_orcamento() -> dict:
    if not _tem_supabase_rest():
        return {}
    rows = _req("orcamento", {"select": "id_programa_pt,no_programa_pt", "id_uo": "eq.24205"})
    programas = []
    vistos = set()
    for r in rows:
        p = r.get("id_programa_pt", "")
        n = r.get("no_programa_pt", "")
        if p and p not in vistos:
            programas.append({"programa": p, "programa_nome": n})
            vistos.add(p)
    return {"programas": programas}
