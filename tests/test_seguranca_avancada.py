
import pytest
from app import app


@pytest.fixture
def cliente():
    app.config["TESTING"] = True
    with app.test_client() as cliente:
        yield cliente


def test_json_invalido(cliente):
    resposta = cliente.post(
        "/api/calcular",
        data='{"expressao":',
        content_type="application/json"
    )
    assert resposta.status_code == 400


def test_tipo_incorreto(cliente):
    resposta = cliente.post(
        "/api/calcular",
        json={"expressao": ["2+2"]}
    )
    assert resposta.status_code == 400


def test_codigo_python_bloqueado(cliente):
    resposta = cliente.post(
        "/api/calcular",
        json={"expressao": "__import__('os')"}
    )
    assert resposta.status_code == 400


def test_requisicao_muito_grande(cliente):
    resposta = cliente.post(
        "/api/calcular",
        data="x" * 9000,
        content_type="application/json"
    )
    assert resposta.status_code == 413


def test_cabecalhos_seguranca(cliente):
    resposta = cliente.get("/")
    assert resposta.headers.get("X-Content-Type-Options") == "nosniff"
    assert resposta.headers.get("X-Frame-Options") in ("DENY", "SAMEORIGIN")


def test_calculo_normal(cliente):
    resposta = cliente.post(
        "/api/calcular",
        json={"expressao": "2+2"}
    )
    assert resposta.status_code == 200
    assert str(resposta.json["resultado"]) == "4"
