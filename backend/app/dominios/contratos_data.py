"""Dados sintéticos - domínio Contratos (COAD/DCONT/DIAP/DIPA/DSG)."""
from __future__ import annotations
import random
from functools import lru_cache
from datetime import date, timedelta

STATUS = ["Em execução", "Concluído", "Rescisão", "Cadastrado", "Aditado"]
MODALIDADES = ["Pregão", "Dispensa", "Inexigibilidade", "Concorrência", "Convite", "Tomada de Preços"]
AREAS = ["DGSE", "DIEN", "COF", "DPOA", "DGEP", "AUDIN", "CGP", "COAD", "DGTEC"]
FORNECEDORES = [
    "SERPRO", "EMBRAER", "AEL Sistemas", "Thales", "Leonardo", "INVAP",
    " Orbital", "SpaceX", "Airbus", "Boeing", "Lockheed Martin", "ISA",
    "Telespazio", "Viasat", "Harris", "Ball Aerospace", "OHB", "SENER",
]


@lru_cache(maxsize=1)
def gerar_contratos() -> tuple[dict, ...]:
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
