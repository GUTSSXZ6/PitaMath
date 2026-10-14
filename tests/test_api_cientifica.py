from app import app

def test_cientifica_seno():
    resposta = app.test_client().post('/api/cientifica', json={'operacao':'sen','valor':'30','modo':'DEG'})
    assert resposta.status_code == 200
    dados = resposta.get_json()
    assert abs(float(dados['resultado']) - 0.5) < 1e-10
    assert len(dados['etapas']) >= 3

def test_cientifica_log():
    resposta = app.test_client().post('/api/cientifica', json={'operacao':'log','valor':'100','base':'10'})
    assert resposta.status_code == 200
    assert abs(float(resposta.get_json()['resultado']) - 2) < 1e-10

def test_cientifica_invalida():
    resposta = app.test_client().post('/api/cientifica', json={'operacao':'sen','valor':'abc'})
    assert resposta.status_code == 400
