"""Testes unitários para o módulo de auditoria (saldos alongados)."""
from datetime import date

import pytest

from app.auditoria import (
    ContaAlongada,
    SaldoMensal,
    calcular_alongamento,
    gerar_dados_sinteticos,
    obter_saldos_alongados_sinteticos,
    _parse_mes_ano,
)


class TestParseMesAno:
    def test_valido(self):
        assert _parse_mes_ano("JAN/2024") == date(2024, 1, 1)
        assert _parse_mes_ano("DEZ/2025") == date(2025, 12, 1)

    def test_invalido(self):
        assert _parse_mes_ano("JAN-2024") is None
        assert _parse_mes_ano("13/2024") is None
        assert _parse_mes_ano("") is None


class TestCalcularAlongamento:
    def test_alongamento_simples(self):
        """Saldo igual por 3 meses consecutivos -> 3 meses alongados."""
        registros = [
            SaldoMensal(date(2024, 1, 1), "24205", "AEB", "11111001", "Caixa", "100", 1000.0),
            SaldoMensal(date(2024, 2, 1), "24205", "AEB", "11111001", "Caixa", "100", 1000.0),
            SaldoMensal(date(2024, 3, 1), "24205", "AEB", "11111001", "Caixa", "100", 1000.0),
        ]
        result = calcular_alongamento(registros)
        assert len(result) == 1
        assert result[0].meses_alongados == 3
        assert result[0].saldo_atual == 1000.0

    def test_mudanca_de_saldo(self):
        """Saldo muda no meio -> conta como alongamento separado."""
        registros = [
            SaldoMensal(date(2024, 1, 1), "24205", "AEB", "11111001", "Caixa", "100", 1000.0),
            SaldoMensal(date(2024, 2, 1), "24205", "AEB", "11111001", "Caixa", "100", 1000.0),
            SaldoMensal(date(2024, 3, 1), "24205", "AEB", "11111001", "Caixa", "100", 2000.0),
            SaldoMensal(date(2024, 4, 1), "24205", "AEB", "11111001", "Caixa", "100", 2000.0),
        ]
        result = calcular_alongamento(registros)
        assert len(result) == 1
        assert result[0].meses_alongados == 2  # Maior sequência
        assert result[0].saldo_atual == 2000.0  # Último saldo

    def test_sem_alongamento(self):
        """Saldo muda todo mês -> não reporta (precisa >= 2 meses)."""
        registros = [
            SaldoMensal(date(2024, 1, 1), "24205", "AEB", "11111001", "Caixa", "100", 1000.0),
            SaldoMensal(date(2024, 2, 1), "24205", "AEB", "11111001", "Caixa", "100", 2000.0),
            SaldoMensal(date(2024, 3, 1), "24205", "AEB", "11111001", "Caixa", "100", 3000.0),
        ]
        result = calcular_alongamento(registros)
        assert len(result) == 0

    def test_tolerancia(self):
        """Diferença menor que tolerância conta como igual."""
        registros = [
            SaldoMensal(date(2024, 1, 1), "24205", "AEB", "11111001", "Caixa", "100", 1000.0),
            SaldoMensal(date(2024, 2, 1), "24205", "AEB", "11111001", "Caixa", "100", 1000.0005),
        ]
        result = calcular_alongamento(registros)
        assert len(result) == 1
        assert result[0].meses_alongados == 2

    def test_multiplas_contas(self):
        """Múltiplas contas -> resultados separados."""
        registros = [
            SaldoMensal(date(2024, 1, 1), "24205", "AEB", "11111001", "Caixa", "100", 1000.0),
            SaldoMensal(date(2024, 2, 1), "24205", "AEB", "11111001", "Caixa", "100", 1000.0),
            SaldoMensal(date(2024, 1, 1), "24205", "AEB", "11111002", "Banco", "100", 5000.0),
            SaldoMensal(date(2024, 2, 1), "24205", "AEB", "11111002", "Banco", "100", 5000.0),
        ]
        result = calcular_alongamento(registros)
        assert len(result) == 2


class TestDadosSinteticos:
    def test_geracao(self):
        dados = gerar_dados_sinteticos(meses=3, seed=42)
        assert len(dados) > 0
        # Verificar que todas as UGs estão presentes
        ugs = {d.ug for d in dados}
        assert len(ugs) == 3  # 3 UGs no fixture

    def test_sinteticos_alongados(self):
        alongados = obter_saldos_alongados_sinteticos(meses=6, min_meses=2)
        assert len(alongados) > 0
        for a in alongados:
            assert a.meses_alongados >= 2
            assert a.saldo_atual != 0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
