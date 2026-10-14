"""Servidor Flask do PitaMath — básica, frações e MMC/MDC."""
from flask import Flask, jsonify, render_template, request
from matematica.basica import resolver as resolver_basica, ErroMatematico
from matematica.escolar import calcular_fracoes
from matematica.mmc_mdc import calcular_mmc_mdc

from matematica.avancada_escolar import calcular_escolar
from matematica.segundo_grau import calcular_segundo_grau

app = Flask(__name__)
app.json.ensure_ascii = False

@app.get('/')
def inicio():
    return render_template('index.html')

@app.post('/api/calcular')
def calcular():
    dados = request.get_json(silent=True)
    if not isinstance(dados, dict):
        return jsonify(erro='Envie um JSON com o campo "expressao".'), 400
    try:
        return jsonify(resolver_basica(dados.get('expressao'))), 200
    except ErroMatematico as erro:
        return jsonify(erro=str(erro)), 400

@app.post('/api/escolar/fracoes')
def calcular_fracoes_api():
    dados = request.get_json(silent=True)
    if not isinstance(dados, dict):
        return jsonify(erro='Envie os dados das frações em JSON.'), 400
    primeira, operador, segunda = (dados.get(chave) for chave in ('primeira', 'operador', 'segunda'))
    if not all(isinstance(v, str) and v.strip() for v in (primeira, operador, segunda)):
        return jsonify(erro='Informe as duas frações e a operação.'), 400
    if operador not in ('+', '-', '*', '/'):
        return jsonify(erro='Operação inválida.'), 400
    try:
        return jsonify(calcular_fracoes(primeira, operador, segunda)), 200
    except (ValueError, ZeroDivisionError) as erro:
        return jsonify(erro=str(erro)), 400

@app.post('/api/escolar/mmc-mdc')
def calcular_mmc_mdc_api():
    dados = request.get_json(silent=True)
    if not isinstance(dados, dict):
        return jsonify(erro='Envie os números e a operação em JSON.'), 400
    try:
        return jsonify(calcular_mmc_mdc(dados.get('numeros'), dados.get('operacao'))), 200
    except ValueError as erro:
        return jsonify(erro=str(erro)), 400

@app.post('/api/escolar/conteudos')
def calcular_conteudos_api():
    dados = request.get_json(silent=True)
    if not isinstance(dados, dict):
        return jsonify(erro='Envie os dados em JSON.'), 400
    try:
        if dados.get('tipo') == 'equacao2':
            return jsonify(calcular_segundo_grau(dados.get('a'), dados.get('b'), dados.get('c'))), 200
        return jsonify(calcular_escolar(dados.get('tipo'), dados)), 200
    except ValueError as erro:
        return jsonify(erro=str(erro)), 400

if __name__ == '__main__':
    app.run(debug=True)
