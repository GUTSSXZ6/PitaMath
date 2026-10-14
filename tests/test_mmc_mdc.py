import pytest
from matematica.mmc_mdc import calcular_mmc_mdc


@pytest.mark.parametrize('numeros,operacao,esperado', [
    ([12, 18], 'mmc', '36'),
    ([12, 18], 'mdc', '6'),
    ([4, 6, 8], 'mmc', '24'),
    ([4, 6, 8], 'mdc', '2'),
    ([6, 12, 18, 24], 'mmc', '72'),
    ([6, 12, 18, 24], 'mdc', '6'),
    ([2, 3, 4, 5, 6], 'mmc', '60'),
    ([2, 3, 4, 5, 6], 'mdc', '1'),
    ([1, 1], 'mmc', '1'),
    ([1, 1], 'mdc', '1'),
])
def test_resultados(numeros, operacao, esperado):
    resposta = calcular_mmc_mdc(numeros, operacao)
    assert resposta['resultado'] == esperado
    assert len(resposta['etapas']) >= 4


@pytest.mark.parametrize('numeros,operacao', [
    ([2], 'mmc'),
    (list(range(1, 12)), 'mdc'),
    ([0, 2], 'mmc'),
    ([-1, 2], 'mdc'),
    ([2.5, 3], 'mmc'),
    ([True, 2], 'mmc'),
    ([2, 3], 'soma'),
    ([1_000_001, 2], 'mmc'),
])
def test_entradas_invalidas(numeros, operacao):
    with pytest.raises(ValueError):
        calcular_mmc_mdc(numeros, operacao)
