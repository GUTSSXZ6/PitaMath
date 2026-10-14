"""MMC e MDC didáticos para listas de 2 a 10 inteiros positivos."""
from math import gcd
from functools import reduce


def _fatores(n):
    fatores = []
    divisor = 2
    while divisor * divisor <= n:
        while n % divisor == 0:
            fatores.append(divisor)
            n //= divisor
        divisor += 1 if divisor == 2 else 2
    if n > 1:
        fatores.append(n)
    return fatores


def calcular_mmc_mdc(numeros, operacao):
    """Retorna resultado, etapas e observação para MMC ou MDC."""
    if not isinstance(numeros, list) or not 2 <= len(numeros) <= 10:
        raise ValueError('Informe de 2 a 10 números.')
    if any(type(n) is not int or n <= 0 or n > 1_000_000 for n in numeros):
        raise ValueError('Use apenas números inteiros positivos de até 1.000.000.')
    if operacao not in ('mmc', 'mdc'):
        raise ValueError('Escolha mmc ou mdc.')

    fatoracoes = [_fatores(n) for n in numeros]
    etapas = [f'Números informados: {", ".join(map(str, numeros))}.']
    for numero, fatores in zip(numeros, fatoracoes):
        etapas.append(f'Decomposição de {numero} em fatores primos: {" × ".join(map(str, fatores)) if fatores else "1 (não possui fatores primos)"}.')

    expoentes = {}
    for fatores in fatoracoes:
        contagem = {}
        for primo in fatores:
            contagem[primo] = contagem.get(primo, 0) + 1
        for primo in contagem:
            expoentes.setdefault(primo, []).append(contagem[primo])

    if operacao == 'mmc':
        resultado = 1
        partes = []
        for primo in sorted(expoentes):
            maior = max(expoentes[primo])
            resultado *= primo ** maior
            partes.append(f'{primo}^{maior}')
        etapas.append('Para o MMC, usamos cada fator primo com seu MAIOR expoente.')
    else:
        resultado = reduce(gcd, numeros)
        partes = []
        for primo in sorted(expoentes):
            if len(expoentes[primo]) == len(numeros):
                menor = min(expoentes[primo])
                partes.append(f'{primo}^{menor}')
        etapas.append('Para o MDC, usamos apenas os fatores presentes em TODOS os números, com seu MENOR expoente.')

    etapas.append(f'Produto dos fatores escolhidos: {" × ".join(partes) if partes else "1"}.')
    etapas.append(f'{operacao.upper()}({", ".join(map(str, numeros))}) = {resultado}.')
    return {
        'resultado': str(resultado),
        'etapas': etapas,
        'observacao': 'MMC significa mínimo múltiplo comum; MDC significa máximo divisor comum.'
    }
