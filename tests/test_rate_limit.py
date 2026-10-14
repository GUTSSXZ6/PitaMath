
import pytest
from app import app, _acessos, _bloqueio


@pytest.fixture
def cliente():
    app.config["TESTING"] = True

    with _bloqueio:
        _acessos.clear()

    with app.test_client() as cliente:
        yield cliente

    with _bloqueio:
        _acessos.clear()


def test_limite_de_requisicoes(cliente):
    endereco = {"REMOTE_ADDR": "192.0.2.10"}

    for numero in range(60):
        resposta = cliente.post(
            "/api/calcular",
            json={"expressao": "2+2"},
            environ_overrides=endereco
        )
        assert resposta.status_code == 200, (
            f"Falhou na requisicao {numero + 1}: "
            f"HTTP {resposta.status_code}"
        )

    resposta = cliente.post(
        "/api/calcular",
        json={"expressao": "2+2"},
        environ_overrides=endereco
    )

    assert resposta.status_code == 429


def test_site_continua_acessivel(cliente):
    resposta = cliente.get("/")
    assert resposta.status_code == 200
