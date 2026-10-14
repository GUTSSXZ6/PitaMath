import unittest
from matematica.basica import resolver, ErroMatematico

class TestCalculadoraBasica(unittest.TestCase):
    def test_operacoes(self):
        casos = {'2+3*4':'14', '(2+3)*4':'20', '5!':'120', '√(9)':'3', '2^3':'8', '20%':'0.2', '10÷2':'5'}
        for expressao, esperado in casos.items():
            with self.subTest(expressao=expressao):
                self.assertEqual(resolver(expressao)['resultado'], esperado)

    def test_divisao_por_zero(self):
        with self.assertRaises(ErroMatematico):
            resolver('1/0')

    def test_codigo_nao_permitido(self):
        with self.assertRaises(ErroMatematico):
            resolver('__import__("os")')

if __name__ == '__main__':
    unittest.main()
