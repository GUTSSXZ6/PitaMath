"""Servidor Flask do PitaMath — básica, frações e MMC/MDC."""
from flask import Flask, jsonify, render_template, request
from werkzeug.exceptions import RequestEntityTooLarge
from collections import defaultdict, deque
from threading import Lock
from time import monotonic
import os
from matematica.basica import resolver as resolver_basica, ErroMatematico
from matematica.escolar import calcular_fracoes
from matematica.mmc_mdc import calcular_mmc_mdc

from matematica.avancada_escolar import calcular_escolar
from matematica.segundo_grau import calcular_segundo_grau

app = Flask(__name__)
app.json.ensure_ascii = False
# Limite para requisições: cada operação usa apenas poucos números.
app.config['MAX_CONTENT_LENGTH'] = 8 * 1024
app.config['MAX_FORM_MEMORY_SIZE'] = 8 * 1024
app.config['JSON_SORT_KEYS'] = False

# Limitação simples por IP: adequada a execução local / instância única.
# Para várias instâncias ou atrás de proxy, usar rate limit compartilhado (Redis).
_acessos = defaultdict(deque)
_bloqueio = Lock()

@app.before_request
def proteger_api():
    if not request.path.startswith('/api/'):
        return None
    if request.method != 'POST':
        return None
    if request.content_length is not None and request.content_length > app.config['MAX_CONTENT_LENGTH']:
        return jsonify(erro='Requisição muito grande.'), 413
    if not request.is_json:
        return jsonify(erro='Envie os dados como JSON (application/json).'), 415
    # Não confiar em X-Forwarded-For vindo diretamente do cliente.
    endereco = request.remote_addr or 'desconhecido'
    agora = monotonic()
    with _bloqueio:
        fila = _acessos[endereco]
        while fila and agora - fila[0] > 60:
            fila.popleft()
        if len(fila) >= 60:
            return jsonify(erro='Muitas requisições. Tente novamente em instantes.'), 429
        fila.append(agora)
        # Evita crescimento ilimitado de chaves em processos duradouros.
        if len(_acessos) > 4096:
            for chave in list(_acessos):
                if not _acessos[chave] or agora - _acessos[chave][-1] > 60:
                    del _acessos[chave]
    return None

@app.after_request
def cabecalhos_seguranca(resposta):
    resposta.headers['X-Content-Type-Options'] = 'nosniff'
    resposta.headers['X-Frame-Options'] = 'DENY'
    resposta.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
    resposta.headers['Permissions-Policy'] = 'camera=(), microphone=(), geolocation=()'
    resposta.headers['Content-Security-Policy'] = (
        "default-src 'self'; script-src 'self'; style-src 'self'; "
        "img-src 'self' data:; font-src 'self'; connect-src 'self'; "
        "object-src 'none'; base-uri 'self'; form-action 'self'; frame-ancestors 'none'"
    )
    if request.path.startswith('/api/'):
        resposta.headers['Cache-Control'] = 'no-store'
    return resposta

@app.errorhandler(RequestEntityTooLarge)
def tamanho_excedido(_erro):
    return jsonify(erro='Requisição muito grande (limite: 8 KB).'), 413

@app.errorhandler(404)
def pagina_inexistente(_erro):
    if request.path.startswith('/api/'):
        return jsonify(erro='Rota não encontrada.'), 404
    return 'Página não encontrada.', 404

@app.errorhandler(500)
def falha_interna(_erro):
    if request.path.startswith('/api/'):
        return jsonify(erro='Erro interno ao processar o cálculo.'), 500
    return 'Erro interno do servidor.', 500


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

from matematica.cientifica import calcular_cientifica, ErroMatematico as ErroCientifico

@app.post('/api/cientifica')
def calcular_cientifica_api():
    dados = request.get_json(silent=True)
    if not isinstance(dados, dict):
        return jsonify(erro='Envie um objeto JSON válido.'), 400
    operacao = dados.get('operacao')
    if not isinstance(operacao, str):
        return jsonify(erro='Escolha uma operação científica.'), 400
    parametros = {chave: dados[chave] for chave in ('valor', 'base', 'expoente', 'indice', 'modo') if chave in dados}
    try:
        return jsonify(calcular_cientifica(operacao, **parametros)), 200
    except (ErroCientifico, ValueError, OverflowError) as erro:
        return jsonify(erro=str(erro)), 400

if __name__ == '__main__':
    app.run(debug=False, host='127.0.0.1', port=int(os.environ.get('PORT', '5000')))
