
"""
PitaMath — Plataforma Matemática Educacional.

Servidor Flask responsável por:
- Exibir a página principal.
- Receber expressões matemáticas.
- Enviar os cálculos ao módulo matematica.basica.
- Retornar resultados e explicações em JSON.
- Tratar erros matemáticos.
"""

from flask import Flask, jsonify, render_template, request

from matematica.basica import resolver as resolver_basica
from matematica.basica import ErroMatematico


# Inicialização do Flask
app = Flask(__name__)

# Preserva acentos e símbolos matemáticos no JSON
app.json.ensure_ascii = False


# ---------------------------------------
# PÁGINA PRINCIPAL
# ---------------------------------------

@app.get("/")
def inicio():
    """Exibe a interface principal do PitaMath."""
    return render_template("index.html")


# ---------------------------------------
# API DA CALCULADORA
# ---------------------------------------

@app.post("/api/calcular")
def calcular():
    """
    Recebe uma expressão matemática e retorna
    o resultado acompanhado das explicações.
    """

    dados = request.get_json(silent=True)

    # Verifica se a requisição contém um JSON válido
    if not isinstance(dados, dict):
        return jsonify(
            erro='Envie um JSON com o campo "expressao".'
        ), 400

    expressao = dados.get("expressao")

    try:
        # O Python realiza os cálculos e gera as explicações
        resposta = resolver_basica(expressao)

        # Devolve o resultado para o JavaScript
        return jsonify(resposta), 200

    except ErroMatematico as erro:
        # Exemplo: divisão por zero ou expressão inválida
        return jsonify(
            erro=str(erro)
        ), 400


# ---------------------------------------
# INICIALIZAÇÃO DO SERVIDOR
# ---------------------------------------

if __name__ == "__main__":
    app.run(debug=True)
