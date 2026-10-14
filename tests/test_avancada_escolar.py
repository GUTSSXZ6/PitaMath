import pytest
from matematica.avancada_escolar import calcular_escolar

@pytest.mark.parametrize('tipo,dados,esperado', [
 ('potencia', {'base':2,'expoente':5}, '32'),
 ('potencia', {'base':2,'expoente':-2}, '1/4'),
 ('potencia', {'base':5,'expoente':0}, '1'),
 ('raiz', {'numero':81,'indice':2}, '9'),
 ('raiz', {'numero':-27,'indice':3}, '-3'),
 ('equacao', {'a':2,'b':3,'c':11}, '4'),
 ('equacao', {'a':3,'b':0,'c':1}, '1/3'),
 ('equacao', {'a':0,'b':2,'c':2}, 'Infinitas soluções'),
 ('equacao', {'a':0,'b':2,'c':3}, 'Sem solução'),
])
def test_conteudos(tipo,dados,esperado):
    r = calcular_escolar(tipo,dados)
    assert r['resultado'] == esperado
    assert r['etapas']

@pytest.mark.parametrize('tipo,dados', [
 ('potencia',{'base':0,'expoente':-1}),
 ('raiz',{'numero':-16,'indice':2}),
 ('equacao',{'a':1.5,'b':2,'c':3}),
 ('invalido',{}),
])
def test_erros(tipo,dados):
    with pytest.raises(ValueError): calcular_escolar(tipo,dados)
