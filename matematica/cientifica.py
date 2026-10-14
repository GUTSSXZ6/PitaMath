"""Motor matemático e explicações da calculadora científica PitaMath.

Sem eval(), sem dependências externas. Não inclui Flask nem interface.
"""
from __future__ import annotations

import math
from decimal import Decimal, InvalidOperation
from typing import Any

MAX_ABS = 1e100
MAX_FATORIAL = 170
MAX_EXPOENTE = 1000
TOL = 1e-12


class ErroMatematico(ValueError):
    """Entrada inválida ou operação fora do domínio real suportado."""


def _numero(valor: Any, nome: str = "valor") -> float:
    if isinstance(valor, bool) or not isinstance(valor, (str, int, float, Decimal)):
        raise ErroMatematico(f"{nome.capitalize()} deve ser um número real.")
    try:
        texto = str(valor).strip().replace(",", ".")
        if len(texto) > 120:
            raise ErroMatematico(f"{nome.capitalize()} é longo demais.")
        numero = float(texto)
    except (ValueError, OverflowError, InvalidOperation) as exc:
        raise ErroMatematico(f"{nome.capitalize()} deve ser um número real.") from exc
    if not math.isfinite(numero) or abs(numero) > MAX_ABS:
        raise ErroMatematico(f"{nome.capitalize()} está fora do limite permitido.")
    return numero


def _formatar(n: float) -> str:
    if abs(n) < TOL:
        return "0"
    return f"{n:.12g}"


def _retorno(resultado: float | int, etapas: list[str], observacao: str = "") -> dict:
    if not math.isfinite(resultado):
        raise ErroMatematico("O resultado não é um número real finito.")
    return {"resultado": _formatar(float(resultado)), "etapas": etapas, "observacao": observacao}


def _modo(modo: str) -> str:
    if not isinstance(modo, str) or modo.upper() not in {"DEG", "RAD"}:
        raise ErroMatematico("O modo angular deve ser DEG ou RAD.")
    return modo.upper()


def _angulo_notavel(funcao: str, graus: float) -> str | None:
    # Valores exatos para ângulos notáveis no círculo trigonométrico.
    valores = {
        0: ("0", "1"), 30: ("1/2", "√3/2"), 45: ("√2/2", "√2/2"),
        60: ("√3/2", "1/2"), 90: ("1", "0"), 120: ("√3/2", "-1/2"),
        135: ("√2/2", "-√2/2"), 150: ("1/2", "-√3/2"), 180: ("0", "-1"),
        210: ("-1/2", "-√3/2"), 225: ("-√2/2", "-√2/2"),
        240: ("-√3/2", "-1/2"), 270: ("-1", "0"),
        300: ("-√3/2", "1/2"), 315: ("-√2/2", "√2/2"),
        330: ("-1/2", "√3/2"),
    }
    ang = graus % 360
    for k, v in valores.items():
        if abs(ang - k) < 1e-10:
            return v[0 if funcao == "sen" else 1]
    return None


def trigonometria(funcao: str, angulo: Any, modo: str = "DEG") -> dict:
    """sen, cos, tan. DEG recebe graus; RAD recebe radianos."""
    f = str(funcao).lower().strip()
    if f not in {"sen", "cos", "tan"}:
        raise ErroMatematico("Use sen, cos ou tan.")
    m = _modo(modo)
    x = _numero(angulo, "ângulo")
    rad = math.radians(x) if m == "DEG" else x
    graus = x if m == "DEG" else math.degrees(x)
    conceitos = {
        "sen": "No triângulo retângulo, seno = cateto oposto / hipotenusa; no círculo unitário, é a coordenada vertical (y).",
        "cos": "No triângulo retângulo, cosseno = cateto adjacente / hipotenusa; no círculo unitário, é a coordenada horizontal (x).",
        "tan": "Tangente = seno / cosseno (ou cateto oposto / cateto adjacente), quando o cosseno não é zero.",
    }
    etapas = [
        f"1. Queremos calcular {f}({_formatar(x)} {'graus' if m == 'DEG' else 'radianos'}).",
        f"2. Conceito: {conceitos[f]}",
    ]
    if m == "DEG":
        etapas.append(f"3. Converta para radianos: {_formatar(x)} × π/180 ≈ {_formatar(rad)} rad.")
    else:
        etapas.append(f"3. O ângulo já está em radianos: {_formatar(rad)} rad.")
    seno, cosseno = math.sin(rad), math.cos(rad)
    if f == "tan":
        if abs(cosseno) < TOL:
            raise ErroMatematico("Tangente indefinida: cosseno do ângulo é zero.")
        resultado = seno / cosseno
        etapas.append("4. Use a identidade tan(x) = sen(x) / cos(x).")
        etapas.append(f"5. tan(x) ≈ {_formatar(seno)} / {_formatar(cosseno)} = {_formatar(resultado)}.")
    else:
        resultado = seno if f == "sen" else cosseno
        exato = _angulo_notavel(f, graus)
        if exato:
            etapas.append(f"4. Este é um ângulo notável: {f}({_formatar(graus)}°) = {exato}.")
        else:
            etapas.append(f"4. Este ângulo não está na tabela de ângulos notáveis usada aqui; calculamos numericamente {f}({_formatar(rad)} rad).")
        if exato and exato.lstrip("-").count("/") == 1 and "√" not in exato:
            a, b = exato.split("/")
            etapas.append(f"5. Converta a fração para decimal: {a} ÷ {b} = {_formatar(resultado)}.")
        elif exato:
            etapas.append(f"5. Avalie o valor exato {exato} numericamente: {_formatar(resultado)}.")
        else:
            etapas.append(f"5. Resultado decimal aproximado: {_formatar(resultado)}.")
    return _retorno(resultado, etapas, "Resultado aproximado; valores exatos aparecem para ângulos notáveis." if f != "tan" else "Tangente é a razão entre seno e cosseno.")


def trigonometria_inversa(funcao: str, valor: Any, modo: str = "DEG") -> dict:
    """arcsen, arccos, arctan, com resultado em DEG ou RAD."""
    f = str(funcao).lower().strip()
    funcs = {"arcsen": math.asin, "arccos": math.acos, "arctan": math.atan}
    if f not in funcs:
        raise ErroMatematico("Use arcsen, arccos ou arctan.")
    m = _modo(modo)
    x = _numero(valor)
    if f in {"arcsen", "arccos"} and not -1 <= x <= 1:
        raise ErroMatematico(f"{f} exige entrada entre -1 e 1 no conjunto dos reais.")
    rad = funcs[f](x)
    resposta = math.degrees(rad) if m == "DEG" else rad
    etapas = [
        f"1. A função {f} é a inversa trigonométrica: procura o ângulo cujo { {'arcsen': 'seno', 'arccos': 'cosseno', 'arctan': 'tangente'}[f] } é {_formatar(x)}.",
        "2. Diferentemente de sen/cos/tan, a entrada é uma razão trigonométrica, não um ângulo.",
        f"3. Calcule o valor principal: {f}({_formatar(x)}) ≈ {_formatar(rad)} rad.",
        f"4. Expresse o ângulo em {('graus' if m == 'DEG' else 'radianos')}: {_formatar(resposta)} {('°' if m == 'DEG' else 'rad')}.",
    ]
    return _retorno(resposta, etapas, "A função inversa retorna o ângulo principal, não todos os ângulos possíveis.")


def logaritmo(valor: Any, base: Any = 10) -> dict:
    x, b = _numero(valor), _numero(base, "base")
    if x <= 0:
        raise ErroMatematico("Logaritmo real exige argumento maior que zero.")
    if b <= 0 or b == 1:
        raise ErroMatematico("A base do logaritmo deve ser positiva e diferente de 1.")
    r = math.log(x) / math.log(b)
    etapas = [
        f"1. Identifique log na base {_formatar(b)} de {_formatar(x)}.",
        f"2. Pela definição, procure y tal que {_formatar(b)}^y = {_formatar(x)}.",
        "3. A mudança de base permite calcular: log_b(x) = ln(x) / ln(b).",
        f"4. Substitua: ln({_formatar(x)}) / ln({_formatar(b)}) = {_formatar(r)}.",
        f"5. Portanto, log na base {_formatar(b)} de {_formatar(x)} = {_formatar(r)}.",
    ]
    return _retorno(r, etapas)


def log_natural(valor: Any) -> dict:
    x = _numero(valor)
    if x <= 0:
        raise ErroMatematico("ln(x) só existe nos reais para x > 0.")
    r = math.log(x)
    return _retorno(r, [f"1. ln({_formatar(x)}) é o logaritmo na base e.", f"2. Procuramos y tal que e^y = {_formatar(x)}, sendo e ≈ 2,718281828459.", f"3. Calculando, y ≈ {_formatar(r)}.", f"4. Conferência conceitual: e^{_formatar(r)} ≈ {_formatar(x)}."])


def exponencial(valor: Any) -> dict:
    x = _numero(valor, "expoente")
    if x > math.log(MAX_ABS):
        raise ErroMatematico("Expoente grande demais para o limite de cálculo.")
    r = math.exp(x)
    return _retorno(r, [f"1. Identifique e elevado a {_formatar(x)}.", "2. A constante e vale aproximadamente 2,718281828459 e é a base do logaritmo natural.", f"3. Elevamos e ao expoente {_formatar(x)}.", f"4. Resultado: e^{_formatar(x)} ≈ {_formatar(r)}."])


def potencia(base: Any, expoente: Any) -> dict:
    b, e = _numero(base, "base"), _numero(expoente, "expoente")
    if abs(e) > MAX_EXPOENTE:
        raise ErroMatematico("Expoente fora do limite permitido.")
    if b == 0 and e <= 0:
        raise ErroMatematico("Zero não pode ser elevado a expoente zero ou negativo nesta calculadora.")
    if b < 0 and not e.is_integer():
        raise ErroMatematico("Base negativa com expoente não inteiro não é suportada neste módulo real.")
    try:
        r = math.pow(b, e)
    except (ValueError, OverflowError) as exc:
        raise ErroMatematico("Potência fora do domínio ou limite suportado.") from exc
    if not math.isfinite(r) or abs(r) > MAX_ABS:
        raise ErroMatematico("Resultado excede o limite permitido.")
    return _retorno(r, [f"1. Identifique base {_formatar(b)} e expoente {_formatar(e)}.", "2. Se o expoente é inteiro positivo, multiplicamos a base por ela mesma essa quantidade de vezes; expoente negativo indica o inverso e expoente fracionário se relaciona a raízes.", f"3. Aplicando a regra: {_formatar(b)}^{_formatar(e)} = {_formatar(r)}."])


def raiz(valor: Any, indice: Any = 2) -> dict:
    x, n = _numero(valor, "radicando"), _numero(indice, "índice")
    if not n.is_integer() or n < 2 or n > 1000:
        raise ErroMatematico("O índice da raiz deve ser inteiro de 2 a 1000.")
    ni = int(n)
    if x < 0 and ni % 2 == 0:
        raise ErroMatematico("Raiz de índice par de número negativo não é real.")
    r = math.copysign(abs(x) ** (1 / ni), x)
    return _retorno(r, [f"1. Identifique a raiz de índice {ni} de {_formatar(x)}.", f"2. A raiz é o número y que, elevado a {ni}, produz {_formatar(x)}.", f"3. Portanto, procuramos y tal que y^{ni} = {_formatar(x)}.", f"4. O valor calculado é y ≈ {_formatar(r)}; verificando, y^{ni} ≈ {_formatar(x)}."], "Para radicando negativo, apenas índices ímpares são aceitos.")


def fatorial(valor: Any) -> dict:
    x = _numero(valor)
    if not x.is_integer() or x < 0 or x > MAX_FATORIAL:
        raise ErroMatematico(f"Fatorial exige inteiro entre 0 e {MAX_FATORIAL}.")
    n = int(x)
    r = math.factorial(n)
    if n == 0:
        detalhe = "Por definição, 0! = 1."
    elif n <= 8:
        detalhe = " × ".join(str(i) for i in range(n, 0, -1))
    else:
        detalhe = f"{n} × {n-1} × ... × 2 × 1"
    return {"resultado": str(r), "etapas": [f"1. O fatorial n! multiplica todos os inteiros positivos de n até 1 (e 0! = 1 por definição). Aqui, n = {n}.", f"2. {n}! = {detalhe}.", f"3. Resultado: {r}."], "observacao": "0! = 1 por definição."}


def valor_absoluto(valor: Any) -> dict:
    x = _numero(valor)
    r = abs(x)
    return _retorno(r, [f"1. O valor absoluto representa a distância de {_formatar(x)} até zero.", "2. Se o número for negativo, retiramos o sinal; se for positivo ou zero, mantemos o valor.", f"3. |{_formatar(x)}| = {_formatar(r)}."])


def notacao_cientifica(valor: Any) -> dict:
    x = _numero(valor)
    if x == 0:
        return {"resultado": "0 × 10^0", "etapas": ["1. O número é zero.", "2. Por convenção, podemos escrever 0 × 10^0."], "observacao": "Zero não tem mantissa normalizada não nula."}
    expoente = math.floor(math.log10(abs(x)))
    mantissa = x / 10 ** expoente
    # Corrigir eventual arredondamento de log10 próximo a potências exatas.
    if abs(mantissa) >= 10:
        mantissa /= 10
        expoente += 1
    elif abs(mantissa) < 1:
        mantissa *= 10
        expoente -= 1
    representacao = f"{_formatar(mantissa)} × 10^{expoente}"
    return {"resultado": representacao, "etapas": [f"1. Comece com {_formatar(x)}.", "2. Escreva o número como a × 10^n, com 1 ≤ |a| < 10.", f"3. O coeficiente é {_formatar(mantissa)} e o expoente é {expoente}; o expoente indica quantas casas a vírgula foi deslocada.", f"4. Forma científica: {representacao}."], "observacao": "O coeficiente fica entre -10 e -1 ou entre 1 e 10."}


def potencia_dez(valor: Any) -> dict:
    x = _numero(valor, "expoente")
    if x > 100 or x < -100:
        raise ErroMatematico("Expoente de base 10 fora do intervalo [-100, 100].")
    r = 10 ** x
    return _retorno(r, [f"1. Identifique 10 elevado a {_formatar(x)}.", "2. Expoente positivo multiplica por 10 repetidamente; negativo equivale a dividir por potências de 10; zero dá 1.", f"3. 10^{_formatar(x)} = {_formatar(r)}."])


OPERACOES = {
    "sen": lambda **kw: trigonometria("sen", kw["valor"], kw.get("modo", "DEG")),
    "cos": lambda **kw: trigonometria("cos", kw["valor"], kw.get("modo", "DEG")),
    "tan": lambda **kw: trigonometria("tan", kw["valor"], kw.get("modo", "DEG")),
    "arcsen": lambda **kw: trigonometria_inversa("arcsen", kw["valor"], kw.get("modo", "DEG")),
    "arccos": lambda **kw: trigonometria_inversa("arccos", kw["valor"], kw.get("modo", "DEG")),
    "arctan": lambda **kw: trigonometria_inversa("arctan", kw["valor"], kw.get("modo", "DEG")),
    "log": lambda **kw: logaritmo(kw["valor"], kw.get("base", 10)),
    "ln": lambda **kw: log_natural(kw["valor"]),
    "exp": lambda **kw: exponencial(kw["valor"]),
    "potencia": lambda **kw: potencia(kw["base"], kw["expoente"]),
    "raiz": lambda **kw: raiz(kw["valor"], kw.get("indice", 2)),
    "fatorial": lambda **kw: fatorial(kw["valor"]),
    "abs": lambda **kw: valor_absoluto(kw["valor"]),
    "notacao": lambda **kw: notacao_cientifica(kw["valor"]),
    "potencia10": lambda **kw: potencia_dez(kw["valor"]),
}


def calcular_cientifica(operacao: str, **parametros: Any) -> dict:
    """Ponto de entrada uniforme para integrar futuramente com Flask."""
    if not isinstance(operacao, str) or operacao not in OPERACOES:
        raise ErroMatematico("Operação científica não reconhecida.")
    try:
        return OPERACOES[operacao](**parametros)
    except (KeyError, TypeError) as exc:
        raise ErroMatematico("Parâmetros obrigatórios ausentes ou inválidos.") from exc
