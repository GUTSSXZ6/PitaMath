import pytest
from matematica.segundo_grau import calcular_segundo_grau

@pytest.mark.parametrize('a,b,c,esperado', [
    (1,-5,6,'x₁ = 3; x₂ = 2'),
    (1,2,1,'x = -1'),
    (1,0,-4,'x₁ = 2; x₂ = -2'),
    (2,3,1,'x₁ = -1/2; x₂ = -1'),
    (1,0,1,'Sem raízes reais'),
])
def test_resultados(a,b,c,esperado):
    r=calcular_segundo_grau(a,b,c)
    assert r['resultado']==esperado
    assert r['etapas'] and r['observacao']

def test_raizes_irracionais():
    r=calcular_segundo_grau(1,1,-1)
    assert '√5' in r['resultado']
    assert any('Bhaskara' in passo for passo in r['etapas'])

@pytest.mark.parametrize('args', [(0,1,2),(True,2,3),(1.5,2,3),(1000001,2,3)])
def test_invalidos(args):
    with pytest.raises(ValueError): calcular_segundo_grau(*args)

def test_api():
    pytest.importorskip("flask")
    from app import app
    cliente=app.test_client()
    resp=cliente.post('/api/escolar/conteudos',json={'tipo':'equacao2','a':1,'b':-5,'c':6})
    assert resp.status_code==200
    assert resp.get_json()['resultado']=='x₁ = 3; x₂ = 2'
