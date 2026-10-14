"""Operações escolares com frações e explicações passo a passo."""

from fractions import Fraction
from math import gcd, lcm
import re


class ErroEscolar(ValueError):
    """Erro de entrada ou operação matemática escolar."""


def _ler_fracao(texto):
    """Converte um inteiro ou fração 'a/b' em Fraction."""
    if not isinstance(texto, str):
        raise ErroEscolar("Informe a fração como texto, por exemplo: '2/3'.")
    texto = texto.strip().replace(" ", "")
    if not re.fullmatch(r"[+-]?\d+(?:/[+-]?\d+)?", texto):
        raise ErroEscolar("Use uma fração no formato a/b, por exemplo: 2/3.")
    try:
        if "/" in texto:
            numerador, denominador = map(int, texto.split("/"))
            return Fraction(numerador, denominador)
        return Fraction(int(texto), 1)
    except ZeroDivisionError as exc:
        raise ErroEscolar("O denominador de uma fração não pode ser zero.") from exc


def _texto(fracao):
    if fracao.denominator == 1:
        return str(fracao.numerator)
    return f"{fracao.numerator}/{fracao.denominator}"


def calcular_fracoes(primeira, operador, segunda=None):
    """Retorna {'resultado', 'etapas', 'observacao'} com explicação didática.

    Operadores: '+', '-', '*', '/', 'simplificar'.
    Entradas: inteiros ou frações escritos como strings, por exemplo '2/4'.
    """
    a = _ler_fracao(primeira)
    etapas = []

    if operador == "simplificar":
        if "/" in primeira.replace(" ", ""):
            n, d = map(int, primeira.replace(" ", "").split("/"))
        else:
            n, d = int(primeira.strip()), 1
        divisor = gcd(abs(n), abs(d))
        etapas.append(f"Identificamos a fração {n}/{d}.")
        etapas.append(f"O MDC de {abs(n)} e {abs(d)} é {divisor}.")
        etapas.append(f"Dividimos numerador e denominador por {divisor}.")
        etapas.append(f"Obtemos a forma simplificada: {_texto(a)}.")
        return {"resultado": _texto(a), "etapas": etapas, "observacao": "Uma fração está simplificada quando numerador e denominador não têm divisor comum maior que 1."}

    if segunda is None:
        raise ErroEscolar("Informe as duas frações para realizar a operação.")
    b = _ler_fracao(segunda)
    etapas.append(f"Identificamos as frações: {_texto(a)} e {_texto(b)}.")

    if operador in ("+", "-"):
        comum = lcm(a.denominator, b.denominator)
        na = a.numerator * (comum // a.denominator)
        nb = b.numerator * (comum // b.denominator)
        etapas.append(f"Calculamos o MMC dos denominadores {a.denominator} e {b.denominator}: {comum}.")
        etapas.append(f"Reescrevemos com o mesmo denominador: {na}/{comum} e {nb}/{comum}.")
        numerador = na + nb if operador == "+" else na - nb
        simbolo = "+" if operador == "+" else "−"
        etapas.append(f"Operamos os numeradores: {na} {simbolo} {nb} = {numerador}.")
        resultado = Fraction(numerador, comum)
        etapas.append(f"Simplificamos, se necessário: {_texto(resultado)}.")
    elif operador in ("*", "×"):
        etapas.append("Na multiplicação, multiplicamos numerador por numerador e denominador por denominador.")
        etapas.append(f"Numeradores: {a.numerator} × {b.numerator} = {a.numerator * b.numerator}.")
        etapas.append(f"Denominadores: {a.denominator} × {b.denominator} = {a.denominator * b.denominator}.")
        resultado = a * b
        etapas.append(f"Simplificamos, se necessário: {_texto(resultado)}.")
    elif operador in ("/", "÷"):
        if b == 0:
            raise ErroEscolar("Não é possível dividir por zero.")
        etapas.append("Para dividir frações, multiplicamos a primeira pelo inverso da segunda.")
        etapas.append(f"O inverso de {_texto(b)} é {b.denominator}/{b.numerator}.")
        resultado = a / b
        etapas.append(f"Multiplicamos e simplificamos: {_texto(resultado)}.")
    else:
        raise ErroEscolar("Operação inválida. Use +, -, *, / ou simplificar.")

    return {"resultado": _texto(resultado), "etapas": etapas, "observacao": "O resultado é apresentado como fração exata e simplificada."}
