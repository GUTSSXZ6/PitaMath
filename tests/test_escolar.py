import pytest
from matematica.escolar import calcular_fracoes

@pytest.mark.parametrize("primeira,operador,segunda,esperado", [
    ("1/2", "+", "1/3", "5/6"),
    ("3/4", "-", "1/2", "1/4"),
    ("2/3", "*", "3/5", "2/5"),
    ("3/4", "/", "2/5", "15/8"),
    ("2/4", "+", "0/1", "1/2"),
    ("1/2", "-", "3/2", "-1"),
])
def test_operacoes_com_fracoes(primeira, operador, segunda, esperado):
    resposta = calcular_fracoes(primeira, operador, segunda)
    assert resposta["resultado"] == esperado
    assert resposta["etapas"]
    assert resposta["observacao"]

def test_explicacao_da_soma():
    resposta = calcular_fracoes("1/2", "+", "1/3")
    assert any("MMC" in etapa for etapa in resposta["etapas"])
