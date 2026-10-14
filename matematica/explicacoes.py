"""Explicações didáticas para operações efetivamente calculadas pelo PitaMath."""


def explicar_operacao(a, b, simbolo, resultado, formatar):
    x, y, r = formatar(a), formatar(b), formatar(resultado)
    descricoes = {
        '+': 'Somamos os dois valores.',
        '−': 'Subtraímos o segundo valor do primeiro.',
        '×': 'Multiplicamos os dois fatores.',
        '÷': 'Dividimos o primeiro valor pelo segundo.',
        '^': 'Elevamos a base ao expoente.',
    }
    etapas = [descricoes[simbolo]]
    if simbolo == '^' and b == int(b) and 2 <= b <= 10:
        etapas.append(f'Desenvolvendo a potência: {" × ".join([x] * int(b))}.')
    etapas.append(f'Calculamos: {x} {simbolo} {y} = {r}.')
    return etapas


def explicar_fatorial(n, resultado, formatar):
    etapas = [f'O símbolo ! indica o fatorial de {n}: multiplicamos todos os inteiros positivos de {n} até 1.']
    if n == 0:
        etapas.append('Por definição, 0! = 1.')
    elif n <= 12:
        etapas.append(f'Desenvolvemos: {n}! = {" × ".join(str(i) for i in range(n, 0, -1))}.')
        acumulado = n
        for i in range(n - 1, 0, -1):
            novo = acumulado * i
            etapas.append(f'{formatar(acumulado)} × {i} = {formatar(novo)}.')
            acumulado = novo
    else:
        etapas.append(f'Desenvolvimento: {n} × {n-1} × ... × 2 × 1 (resumido para evitar uma explicação excessivamente longa).')
    etapas.append(f'Portanto, {n}! = {formatar(resultado)}.')
    return etapas


def explicar_raiz(a, resultado, formatar):
    return [
        f'Procuramos o número não negativo que, multiplicado por ele mesmo, resulta em {formatar(a)}.',
        f'Como {formatar(resultado)} × {formatar(resultado)} = {formatar(a)}, a raiz quadrada principal é {formatar(resultado)}.'
    ]


def explicar_porcentagem(a, resultado, formatar):
    return [
        'Porcentagem significa “por cento”, isto é, dividir por 100.',
        f'{formatar(a)}% = {formatar(a)} ÷ 100 = {formatar(resultado)}.'
    ]
