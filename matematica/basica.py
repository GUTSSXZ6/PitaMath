"""Interpretador restrito e operações da calculadora básica."""
import ast
import math
import re
from matematica.explicacoes import (explicar_operacao, explicar_fatorial, explicar_raiz, explicar_porcentagem)

class ErroMatematico(ValueError):
    pass


def formatar(numero):
    if isinstance(numero, float) and not math.isfinite(numero):
        raise ErroMatematico('Resultado fora dos limites suportados.')
    if abs(numero) > 1e100:
        raise ErroMatematico('Resultado grande demais para esta versão.')
    if numero == int(numero):
        return str(int(numero))
    return f'{numero:.12g}'


def normalizar(expressao):
    texto = expressao.replace(' ', '').replace('×', '*').replace('÷', '/')
    texto = texto.replace('−', '-').replace(',', '.').replace('^', '**')
    # Operadores pós-fixados: número ou parênteses seguidos de ! ou %.
    operando = r'(?:\d+(?:\.\d+)?|\([^()]*\))'
    for _ in range(15):
        novo = re.sub(r'(' + operando + r')!', r'fat(\1)', texto)
        novo = re.sub(r'(' + operando + r')%', r'(\1/100)', novo)
        if novo == texto:
            break
        texto = novo
    texto = texto.replace('√(', 'sqrt(')
    if '!' in texto or '%' in texto or '√' in texto:
        raise ErroMatematico('Use fatorial, porcentagem e raiz com números ou parênteses válidos.')
    return texto


def resolver(expressao):
    if not isinstance(expressao, str) or not expressao.strip():
        raise ErroMatematico('Digite uma expressão.')
    if len(expressao) > 200:
        raise ErroMatematico('A expressão deve ter no máximo 200 caracteres.')
    texto = normalizar(expressao)
    try:
        arvore = ast.parse(texto, mode='eval')
    except (SyntaxError, ValueError) as exc:
        raise ErroMatematico('Expressão inválida. Confira os números e operadores.') from exc
    if sum(1 for _ in ast.walk(arvore)) > 100:
        raise ErroMatematico('Expressão complexa demais.')
    etapas = []

    def avaliar(no, profundidade=0):
        if profundidade > 25:
            raise ErroMatematico('Expressão com muitos níveis de parênteses.')
        if isinstance(no, ast.Constant) and type(no.value) in (int, float):
            valor = no.value
        elif isinstance(no, ast.UnaryOp) and isinstance(no.op, (ast.UAdd, ast.USub)):
            a = avaliar(no.operand, profundidade + 1)
            valor = a if isinstance(no.op, ast.UAdd) else -a
            etapas.append(f'Aplicamos o sinal: {formatar(valor)}.')
        elif isinstance(no, ast.BinOp):
            a = avaliar(no.left, profundidade + 1)
            b = avaliar(no.right, profundidade + 1)
            if isinstance(no.op, ast.Add):
                valor, simbolo = a + b, '+'
            elif isinstance(no.op, ast.Sub):
                valor, simbolo = a - b, '−'
            elif isinstance(no.op, ast.Mult):
                valor, simbolo = a * b, '×'
            elif isinstance(no.op, ast.Div):
                if b == 0:
                    raise ErroMatematico('Não é possível dividir por zero.')
                valor, simbolo = a / b, '÷'
            elif isinstance(no.op, ast.Pow):
                if abs(b) > 1000 or abs(a) > 1e20:
                    raise ErroMatematico('Potência grande demais.')
                try:
                    valor = a ** b
                except (OverflowError, ZeroDivisionError) as exc:
                    raise ErroMatematico('Potência fora do domínio suportado.') from exc
                if isinstance(valor, complex):
                    raise ErroMatematico('Resultados complexos ainda não são suportados.')
                simbolo = '^'
            else:
                raise ErroMatematico('Operador não permitido.')
            etapas.extend(explicar_operacao(a, b, simbolo, valor, formatar))
        elif isinstance(no, ast.Call) and isinstance(no.func, ast.Name) and not no.keywords and len(no.args) == 1:
            a = avaliar(no.args[0], profundidade + 1)
            if no.func.id == 'sqrt':
                if a < 0:
                    raise ErroMatematico('A raiz quadrada de número negativo não é real.')
                valor = math.sqrt(a)
                etapas.extend(explicar_raiz(a, valor, formatar))
            elif no.func.id == 'fat':
                if a < 0 or a != int(a) or a > 170:
                    raise ErroMatematico('Fatorial exige inteiro de 0 a 170.')
                valor = math.factorial(int(a))
                etapas.extend(explicar_fatorial(int(a), valor, formatar))
            else:
                raise ErroMatematico('Função não permitida.')
        else:
            raise ErroMatematico('Expressão contém símbolos ou funções não permitidos.')
        formatar(valor)
        return valor

    try:
        resultado = avaliar(arvore.body)
    except (OverflowError, RecursionError) as exc:
        raise ErroMatematico('Cálculo excedeu os limites suportados.') from exc
    if re.fullmatch(r'\s*\d+(?:[.,]\d+)?%\s*', expressao):
        numero = float(expressao.strip()[:-1].replace(',', '.'))
        etapas = explicar_porcentagem(numero, resultado, formatar)
    if not etapas:
        etapas.append('A expressão já é um número; não há operações para resolver.')
    etapas.append(f'Resultado final: {formatar(resultado)}.')
    return {'resultado': formatar(resultado), 'etapas': etapas,
            'observacao': 'Nesta versão, % significa dividir por 100 (ex.: 20% = 0,2).'}


