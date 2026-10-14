"""Verificações de segurança HTTP sem alterar as operações matemáticas."""
import pytest
from app import app


@pytest.fixture
def cliente():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


def test_cabecalhos(cliente):
    resposta = cliente.get('/')
    assert resposta.status_code == 200
    assert resposta.headers['X-Content-Type-Options'] == 'nosniff'
    assert resposta.headers['X-Frame-Options'] == 'DENY'
    assert "script-src 'self'" in resposta.headers['Content-Security-Policy']


def test_json_obrigatorio(cliente):
    resposta = cliente.post('/api/calcular', data='expressao=1+2')
    assert resposta.status_code == 415


def test_limite_de_corpo(cliente):
    resposta = cliente.post('/api/calcular', data='x' * 9000, content_type='application/json')
    assert resposta.status_code == 413


def test_calculo_continua_funcionando(cliente):
    resposta = cliente.post('/api/calcular', json={'expressao': '2+3'})
    assert resposta.status_code == 200
    assert str(resposta.json['resultado']) == '5'
    assert resposta.headers['Cache-Control'] == 'no-store'


def test_erro_nao_revela_detalhes(cliente):
    resposta = cliente.post('/api/calcular', json={'expressao': '1/0'})
    assert resposta.status_code == 400
    assert 'erro' in resposta.json
