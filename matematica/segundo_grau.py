"""Resolução didática de ax² + bx + c = 0 por Bhaskara."""
from fractions import Fraction
from math import isqrt


def calcular_segundo_grau(a, b, c):
    for nome, valor in (("a", a), ("b", b), ("c", c)):
        if type(valor) is not int or abs(valor) > 1_000_000:
            raise ValueError(f"Coeficiente {nome}: informe um inteiro entre -1.000.000 e 1.000.000.")
    if a == 0:
        raise ValueError("O coeficiente a não pode ser zero em uma equação do 2º grau.")
    delta = b * b - 4 * a * c
    etapas = [
        f"Equação: ({a})x² + ({b})x + ({c}) = 0.",
        f"Identificamos a = {a}, b = {b} e c = {c}.",
        "Calculamos o discriminante pela fórmula Δ = b² − 4ac.",
        f"Δ = ({b})² − 4 × ({a}) × ({c}) = {delta}.",
    ]
    if delta < 0:
        etapas.append("Como Δ < 0, a equação não possui raízes reais.")
        return {"resultado": "Sem raízes reais", "etapas": etapas,
                "observacao": "No conjunto dos números complexos, existem duas raízes conjugadas."}
    etapas.append("Aplicamos a fórmula de Bhaskara: x = (−b ± √Δ) / (2a).")
    raiz = isqrt(delta)
    if raiz * raiz == delta:
        x1 = Fraction(-b + raiz, 2 * a)
        x2 = Fraction(-b - raiz, 2 * a)
        etapas.append(f"√Δ = √{delta} = {raiz}.")
        etapas.append(f"x₁ = (−({b}) + {raiz}) / (2 × ({a})) = {x1}.")
        etapas.append(f"x₂ = (−({b}) − {raiz}) / (2 × ({a})) = {x2}.")
        if delta == 0:
            etapas.append("Como Δ = 0, as duas raízes são iguais (raiz dupla).")
            resultado = f"x = {x1}"
        else:
            resultado = f"x₁ = {x1}; x₂ = {x2}"
        observacao = "As raízes foram apresentadas na forma exata, com frações simplificadas."
    else:
        # Sem aproximação: preserva o radical e o denominador originais.
        etapas.append(f"Como √{delta} não é inteiro, conservamos a raiz em forma exata.")
        etapas.append(f"x₁ = ({-b} + √{delta}) / ({2*a}).")
        etapas.append(f"x₂ = ({-b} − √{delta}) / ({2*a}).")
        resultado = f"x₁ = ({-b} + √{delta})/({2*a}); x₂ = ({-b} − √{delta})/({2*a})"
        observacao = "Raízes irracionais mantidas em forma radical exata, sem arredondamento."
    return {"resultado": resultado, "etapas": etapas, "observacao": observacao}
