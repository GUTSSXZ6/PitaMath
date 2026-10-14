"""Verifica se as 15 operações devolvem explicações legíveis."""
import pytest
from matematica.cientifica import calcular_cientifica

CASOS = [
    ('sen', {'valor': 30, 'modo': 'DEG'}, '1/2'),
    ('cos', {'valor': 60, 'modo': 'DEG'}, '1/2'),
    ('tan', {'valor': 45}, 'seno / cosseno'),
    ('arcsen', {'valor': 0.5}, 'inversa trigonométrica'),
    ('arccos', {'valor': 0.5}, 'inversa trigonométrica'),
    ('arctan', {'valor': 1}, 'inversa trigonométrica'),
    ('log', {'valor': 100}, 'mudança de base'),
    ('ln', {'valor': 2}, 'logaritmo'),
    ('exp', {'valor': 2}, 'constante e'),
    ('potencia', {'base': 2, 'expoente': 3}, 'multiplicamos'),
    ('raiz', {'valor': 81, 'indice': 4}, 'elevado a 4'),
    ('fatorial', {'valor': 5}, 'multiplica'),
    ('abs', {'valor': -8}, 'distância'),
    ('notacao', {'valor': 4500}, 'coeficiente'),
    ('potencia10', {'valor': 3}, 'Expoente positivo'),
]

@pytest.mark.parametrize('operacao,parametros,trecho', CASOS)
def test_explicacao_por_operacao(operacao, parametros, trecho):
    r = calcular_cientifica(operacao, **parametros)
    assert r['resultado']
    assert len(r['etapas']) >= 3
    assert trecho.lower() in ' '.join(r['etapas']).lower()


def test_seno_30_mostra_conceito_e_conversao():
    r = calcular_cientifica('sen', valor=30, modo='DEG')
    texto = ' '.join(r['etapas'])
    assert 'cateto oposto' in texto
    assert 'π/180' in texto
    assert '1/2' in texto
    assert r['resultado'] == '0.5'


def test_angulo_nao_notavel_nao_inventa_resultado_exato():
    r = calcular_cientifica('sen', valor=37, modo='DEG')
    assert 'aproximado' in ' '.join(r['etapas']).lower()
