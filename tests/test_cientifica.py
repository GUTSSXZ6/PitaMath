import math
import pytest
from matematica.cientifica import (ErroMatematico, calcular_cientifica, trigonometria,
    trigonometria_inversa, logaritmo, log_natural, exponencial, potencia,
    raiz, fatorial, valor_absoluto, notacao_cientifica, potencia_dez)

@pytest.mark.parametrize('op,angulo,esperado', [
    ('sen',30,0.5),('cos',60,0.5),('tan',45,1),('sen',-30,-0.5),('cos',180,-1)])
def test_trigonometria(op,angulo,esperado):
    assert float(trigonometria(op,angulo)['resultado']) == pytest.approx(esperado)

def test_radianos():
    assert float(trigonometria('sen',math.pi/2,'RAD')['resultado']) == pytest.approx(1)

def test_tangente_indefinida():
    with pytest.raises(ErroMatematico): trigonometria('tan',90)

def test_inversas():
    assert float(trigonometria_inversa('arcsen',0.5)['resultado']) == pytest.approx(30)
    assert float(trigonometria_inversa('arccos',0.5)['resultado']) == pytest.approx(60)
    assert float(trigonometria_inversa('arctan',1)['resultado']) == pytest.approx(45)

def test_logaritmos():
    assert float(logaritmo(100)['resultado']) == pytest.approx(2)
    assert float(logaritmo(8,2)['resultado']) == pytest.approx(3)
    assert float(log_natural(math.e)['resultado']) == pytest.approx(1)

def test_exponenciais():
    assert float(exponencial(1)['resultado']) == pytest.approx(math.e)
    assert float(potencia(2,5)['resultado']) == 32
    assert float(potencia_dez(3)['resultado']) == 1000

def test_outras():
    assert float(raiz(27,3)['resultado']) == pytest.approx(3)
    assert float(raiz(-27,3)['resultado']) == pytest.approx(-3)
    assert fatorial(5)['resultado'] == '120'
    assert float(valor_absoluto(-9)['resultado']) == 9
    assert notacao_cientifica(4500)['resultado'] == '4.5 × 10^3'

def test_explica():
    r=calcular_cientifica('sen',valor='30',modo='DEG')
    assert r['etapas'] and r['resultado'] == '0.5'
    assert 'observacao' in r

@pytest.mark.parametrize('operacao,parametros', [
    ('sen',{'valor':'__import__("os")'}),('log',{'valor':-1}),
    ('log',{'valor':10,'base':1}),('arcsen',{'valor':2}),
    ('raiz',{'valor':-4,'indice':2}),('fatorial',{'valor':200}),
    ('potencia',{'base':2,'expoente':10000}),('tan',{'valor':90}),
    ('sen',{'valor':'nan'}),('potencia',{'base':-2,'expoente':0.5}),
    ('exp',{'valor':500}),('sen',{}),('inexistente',{'valor':1})])
def test_invalidos(operacao,parametros):
    with pytest.raises(ErroMatematico): calcular_cientifica(operacao,**parametros)
