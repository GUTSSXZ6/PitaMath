"""Testes de explicações produzidas a partir dos cálculos reais."""
from matematica.basica import resolver


def test_fatorial_oito_desenvolvido():
    resposta = resolver('8!')
    assert resposta['resultado'] == '40320'
    texto = ' '.join(resposta['etapas'])
    assert '8 × 7 × 6 × 5 × 4 × 3 × 2 × 1' in texto
    assert '56 × 6 = 336' in texto


def test_expressao_com_fatorial_e_potencia():
    resposta = resolver('5!+2^3')
    assert resposta['resultado'] == '128'
    texto = ' '.join(resposta['etapas'])
    assert '5 × 4 × 3 × 2 × 1' in texto
    assert '2 × 2 × 2' in texto
    assert '120 + 8 = 128' in texto


def test_raiz():
    assert '3 × 3 = 9' in ' '.join(resolver('√(9)')['etapas'])


def test_porcentagem():
    assert '20 ÷ 100 = 0.2' in ' '.join(resolver('20%')['etapas'])


def test_fatorial_zero():
    assert '0! = 1' in ' '.join(resolver('0!')['etapas'])
