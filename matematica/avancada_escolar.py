"""Potências, raízes exatas e equações lineares com explicações."""
from math import isqrt
from fractions import Fraction


def _inteiro(valor, nome):
    if type(valor) is not int or abs(valor) > 1000000:
        raise ValueError(f'{nome}: informe um número inteiro entre -1.000.000 e 1.000.000.')
    return valor


def calcular_escolar(tipo, dados):
    if not isinstance(dados, dict):
        raise ValueError('Dados inválidos.')
    if tipo == 'potencia':
        base = _inteiro(dados.get('base'), 'Base')
        expoente = _inteiro(dados.get('expoente'), 'Expoente')
        if abs(expoente) > 100 or (abs(base) > 10000 and abs(expoente) > 20):
            raise ValueError('Expoente ou base muito grande para esta demonstração.')
        if base == 0 and expoente < 0:
            raise ValueError('Zero não pode ter expoente negativo.')
        if base == 0 and expoente == 0:
            raise ValueError('0 elevado a 0 é indeterminado neste contexto.')
        resultado = Fraction(base, 1) ** expoente
        if len(str(abs(resultado.numerator))) > 500 or len(str(resultado.denominator)) > 500:
            raise ValueError('Resultado muito grande.')
        passos = [f'Identificamos a base {base} e o expoente {expoente}.']
        if expoente == 0:
            passos.append('Toda base diferente de zero elevada a 0 é igual a 1.')
        elif expoente < 0:
            passos.append(f'Expoente negativo: invertemos a potência, 1/({base}^{-expoente}).')
        elif expoente <= 8:
            passos.append('Multiplicamos a base por ela mesma: ' + ' × '.join([f'({base})'] * expoente) + '.')
        else:
            passos.append(f'Multiplicamos {base} por ele mesmo {expoente} vezes.')
        passos.append(f'Resultado: {resultado}.')
        return {'resultado': str(resultado), 'etapas': passos, 'observacao': 'Expoentes negativos produzem o inverso da potência.'}
    if tipo == 'raiz':
        numero = _inteiro(dados.get('numero'), 'Radicando')
        indice = _inteiro(dados.get('indice'), 'Índice')
        if not 2 <= indice <= 10:
            raise ValueError('O índice da raiz deve estar entre 2 e 10.')
        if numero < 0 and indice % 2 == 0:
            raise ValueError('Raiz de índice par de número negativo não é real.')
        alvo = abs(numero)
        lo, hi = 0, min(alvo + 1, 1000001)
        while lo + 1 < hi:
            meio = (lo + hi) // 2
            if meio ** indice <= alvo: lo = meio
            else: hi = meio
        exata = lo ** indice == alvo
        raiz = -lo if numero < 0 else lo
        etapas = [f'Queremos encontrar um número que elevado a {indice} resulte em {numero}.']
        if exata:
            etapas += [f'Verificamos: ({raiz})^{indice} = {numero}.', f'Logo, a raiz é {raiz}.']
            resultado = str(raiz)
        else:
            sinal = '-' if numero < 0 else ''
            etapas += [f'{lo}^{indice} = {lo ** indice} e {(lo + 1)}^{indice} = {(lo + 1) ** indice}.', 'A raiz não é inteira; mantemos a forma radical exata.']
            resultado = f'{sinal}raiz({numero if numero >= 0 else -numero}, {indice})'
        return {'resultado': resultado, 'etapas': etapas, 'observacao': 'Para raízes não exatas, o resultado é apresentado na forma radical, sem arredondamento.'}
    if tipo == 'equacao':
        a = _inteiro(dados.get('a'), 'Coeficiente a')
        b = _inteiro(dados.get('b'), 'Coeficiente b')
        c = _inteiro(dados.get('c'), 'Coeficiente c')
        etapas = [f'Equação informada: {a}x + ({b}) = {c}.', f'Subtraímos {b} dos dois lados: {a}x = {c} - ({b}).', f'Calculamos: {a}x = {c-b}.']
        if a == 0:
            if b == c:
                return {'resultado':'Infinitas soluções','etapas':[f'{b} = {c}: qualquer valor de x satisfaz a igualdade.'],'observacao':'Esta equação é uma identidade.'}
            return {'resultado':'Sem solução','etapas':[f'{b} ≠ {c}: não existe x que satisfaça a igualdade.'],'observacao':'Esta equação é impossível.'}
        resultado = Fraction(c-b,a)
        etapas += [f'Dividimos os dois lados por {a}: x = ({c-b}) / ({a}).', f'Simplificamos: x = {resultado}.']
        return {'resultado':str(resultado),'etapas':etapas,'observacao':'Uma equação do 1º grau tem a forma ax + b = c, com a diferente de zero.'}
    raise ValueError('Escolha potencia, raiz ou equacao.')
