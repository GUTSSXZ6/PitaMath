# PitaMath

Plataforma matemática educacional em Flask, HTML, CSS e JavaScript.

## Funcionalidades
- Calculadora básica com resolução passo a passo
- Frações: soma, subtração, multiplicação e divisão
- MMC e MDC para 2 a 10 números inteiros positivos (até 1.000.000 cada)
- Histórico de cálculos durante a sessão

## Executar
```powershell
python -m pip install -r requirements.txt
python app.py
```
Acesse http://127.0.0.1:5000

## Testes
```powershell
python -m pytest tests -v
```


## Novos conteúdos escolares
Na aba escolar, use **Potências, raízes e equações**. Os cálculos são realizados no Python por `/api/escolar/conteudos`. A radiciação não exata é exibida em forma radical.

## Equações do 2º grau
Na aba Escolar > Potências, raízes e equações, selecione **Equação de 2º grau (Bhaskara)** e informe a, b e c. O Python calcula o discriminante, identifica raízes reais ou não reais e explica a fórmula de Bhaskara.
