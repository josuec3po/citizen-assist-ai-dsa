import io
import os
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from unittest.mock import patch

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import gerir
from base_conhecimento import BaseConhecimento
from lista_encadeada import ListaEncadeada
from ordenacao import insertion_sort
from orientacao import Orientacao


def criar(id, categoria="Saúde", titulo="Título", chaves=None):
    return Orientacao(id, categoria, titulo, chaves or ["chave"], "resp",
                      ["doc"], "local", "https://exemplo.gov.br", "2026-11-07")


def ids(lista):
    return [o.id for o in lista]


def base_com(*orientacoes):
    """Base em arquivo temporário, já com as orientações dadas."""
    pasta = tempfile.mkdtemp()
    base = BaseConhecimento(os.path.join(pasta, "base.json"))
    for o in orientacoes:
        base.cadastrar(o)
    return base


class TestListaEncadeada(unittest.TestCase):
    def test_lista_vazia(self):
        lista = ListaEncadeada()
        self.assertTrue(lista.esta_vazia())
        self.assertEqual(len(lista), 0)
        self.assertEqual(list(lista), [])
        self.assertIsNone(lista.buscar(lambda x: True))
        self.assertFalse(lista.remover(lambda x: True))

    def test_inserir_fim_mantem_ordem(self):
        lista = ListaEncadeada()
        for n in (1, 2, 3):
            lista.inserir_fim(n)
        self.assertEqual(list(lista), [1, 2, 3])
        self.assertEqual(len(lista), 3)

    def test_inserir_inicio(self):
        lista = ListaEncadeada()
        for n in (1, 2, 3):
            lista.inserir_inicio(n)
        self.assertEqual(list(lista), [3, 2, 1])
        self.assertEqual(lista.final.dado, 1)

    def test_remover_cabeca_meio_cauda_e_unico(self):
        lista = ListaEncadeada()
        for n in (1, 2, 3, 4):
            lista.inserir_fim(n)
        self.assertTrue(lista.remover(lambda x: x == 1))   # cabeça
        self.assertTrue(lista.remover(lambda x: x == 3))   # meio
        self.assertTrue(lista.remover(lambda x: x == 4))   # cauda
        self.assertEqual(list(lista), [2])
        self.assertTrue(lista.remover(lambda x: x == 2))   # único nó
        self.assertTrue(lista.esta_vazia())
        self.assertIsNone(lista.final)

    def test_inserir_depois_de_remover_cauda(self):
        lista = ListaEncadeada()
        for n in (1, 2, 3):
            lista.inserir_fim(n)
        lista.remover(lambda x: x == 3)
        lista.inserir_fim(9)
        self.assertEqual(list(lista), [1, 2, 9])

    def test_remover_inexistente(self):
        lista = ListaEncadeada()
        lista.inserir_fim(1)
        self.assertFalse(lista.remover(lambda x: x == 99))
        self.assertEqual(len(lista), 1)

    def test_buscar_e_buscar_todos(self):
        lista = ListaEncadeada()
        for n in (1, 2, 3, 4):
            lista.inserir_fim(n)
        self.assertEqual(lista.buscar(lambda x: x > 2), 3)
        self.assertEqual(lista.buscar_todos(lambda x: x % 2 == 0), [2, 4])
        self.assertEqual(lista.buscar_todos(lambda x: x > 10), [])


class TestOrdenacao(unittest.TestCase):
    def test_merge_sort_varios(self):
        lista = ListaEncadeada()
        for n in (5, 2, 9, 1, 7, 3):
            lista.inserir_fim(n)
        lista.ordenar(lambda x: x)
        self.assertEqual(list(lista), [1, 2, 3, 5, 7, 9])
        self.assertEqual(lista.final.dado, 9)
        lista.inserir_fim(10)  # cauda correta depois de ordenar
        self.assertEqual(list(lista)[-1], 10)

    def test_merge_sort_reverso(self):
        lista = ListaEncadeada()
        for n in (5, 2, 9):
            lista.inserir_fim(n)
        lista.ordenar(lambda x: x, reverso=True)
        self.assertEqual(list(lista), [9, 5, 2])

    def test_merge_sort_vazia_e_um_elemento(self):
        vazia = ListaEncadeada()
        vazia.ordenar(lambda x: x)
        self.assertEqual(list(vazia), [])
        um = ListaEncadeada()
        um.inserir_fim(1)
        um.ordenar(lambda x: x)
        self.assertEqual(list(um), [1])

    def test_merge_sort_estavel(self):
        lista = ListaEncadeada()
        for par in [("b", 1), ("a", 1), ("c", 0), ("d", 1)]:
            lista.inserir_fim(par)
        lista.ordenar(lambda p: p[1])
        self.assertEqual(list(lista), [("c", 0), ("b", 1), ("a", 1), ("d", 1)])

    def test_insertion_sort(self):
        self.assertEqual(insertion_sort([3, 1, 2], lambda x: x), [1, 2, 3])
        self.assertEqual(insertion_sort([3, 1, 2], lambda x: x, reverso=True), [3, 2, 1])
        self.assertEqual(insertion_sort([], lambda x: x), [])


class TestBase(unittest.TestCase):
    def test_cadastrar_e_id_duplicado(self):
        base = base_com()
        self.assertTrue(base.cadastrar(criar(1)))
        self.assertFalse(base.cadastrar(criar(1)))
        self.assertEqual(len(base), 1)

    def test_id_invalido(self):
        base = base_com()
        for invalido in (0, -3, "a", None, True):
            self.assertFalse(base.cadastrar(criar(invalido)))
        self.assertEqual(len(base), 0)

    def test_consulta_por_id(self):
        base = base_com(criar(1, titulo="A"), criar(2, titulo="B"))
        self.assertEqual(base.buscar_por_id(2).titulo, "B")
        self.assertIsNone(base.buscar_por_id(99))

    def test_atualizar(self):
        base = base_com(criar(1, titulo="A"))
        self.assertTrue(base.atualizar(1, titulo="Novo", id=50))  # id é ignorado
        self.assertEqual(base.buscar_por_id(1).titulo, "Novo")
        self.assertFalse(base.atualizar(99, titulo="X"))

    def test_excluir(self):
        base = base_com(criar(1), criar(2), criar(3))
        self.assertTrue(base.excluir(2))
        self.assertEqual(ids(base.orientacoes), [1, 3])
        self.assertFalse(base.excluir(2))

    def test_pesquisa_titulo_categoria_e_sem_resultado(self):
        base = base_com(criar(1, "Saúde", "Vacinas para idosos"),
                        criar(2, "Transporte", "Ônibus gratuito"))
        self.assertEqual(ids(base.pesquisar_por_titulo("VACINA")), [1])
        self.assertEqual(ids(base.pesquisar_por_titulo("onibus")), [2])
        self.assertEqual(ids(base.pesquisar_por_categoria("saude")), [1])
        self.assertEqual(base.pesquisar_por_titulo("xyz"), [])
        self.assertEqual(base.pesquisar_por_titulo("   "), [])

    def test_ordenar_por_criterios(self):
        base = base_com(criar(3, "B", "Zebra"), criar(1, "C", "ábaco"), criar(2, "A", "Mesa"))
        base.ordenar("id")
        self.assertEqual(ids(base.orientacoes), [1, 2, 3])
        base.ordenar("titulo")   # 'ábaco' vem antes de 'Mesa' (ignora acento)
        self.assertEqual(ids(base.orientacoes), [1, 2, 3])
        base.ordenar("categoria", reverso=True)
        self.assertEqual(ids(base.orientacoes), [1, 3, 2])
        self.assertFalse(base.ordenar("criterio_inexistente"))

    def test_lista_vazia_operacoes(self):
        base = base_com()
        self.assertEqual(base.categorias(), [])
        self.assertEqual(base.buscar("sus"), [])
        self.assertEqual(base.sugerir("sus"), [])
        self.assertEqual(base.analise()["total"], 0)
        self.assertEqual(base.proximo_id(), 1)
        self.assertTrue(base.ordenar("id"))

    def test_analise(self):
        base = base_com(criar(1, "A"), criar(2, "B"), criar(3, "A"))
        resumo = base.analise()
        self.assertEqual(resumo["total"], 3)
        self.assertEqual(resumo["por_categoria"], [("A", 2), ("B", 1)])

    def test_persistencia_salvar_e_recarregar(self):
        base = base_com(criar(1, titulo="Á"), criar(2))
        self.assertTrue(base.salvar())
        outra = BaseConhecimento(base.caminho)
        outra.carregar()
        self.assertEqual(ids(outra.orientacoes), [1, 2])
        self.assertEqual(outra.buscar_por_id(1).titulo, "Á")

    def test_carregar_arquivo_inexistente_ou_corrompido(self):
        pasta = tempfile.mkdtemp()
        base = BaseConhecimento(os.path.join(pasta, "nao_existe.json"))
        with redirect_stdout(io.StringIO()):
            base.carregar()
        self.assertEqual(len(base), 0)
        caminho = os.path.join(pasta, "ruim.json")
        with open(caminho, "w", encoding="utf-8") as f:
            f.write("{ isto não é json")
        base = BaseConhecimento(caminho)
        with redirect_stdout(io.StringIO()):
            base.carregar()
        self.assertEqual(len(base), 0)

    def test_carregar_ignora_registro_incompleto_e_id_repetido(self):
        pasta = tempfile.mkdtemp()
        caminho = os.path.join(pasta, "base.json")
        valido = criar(1).para_dict()
        incompleto = {"id": 2, "titulo": "sem os outros campos"}
        with open(caminho, "w", encoding="utf-8") as f:
            import json
            json.dump([valido, incompleto, valido], f)
        base = BaseConhecimento(caminho)
        with redirect_stdout(io.StringIO()):
            base.carregar()
        self.assertEqual(ids(base.orientacoes), [1])

    def test_busca_por_pontuacao(self):
        base = base_com(criar(1, "Saúde", "Cartão SUS", ["sus", "cartao sus"]),
                        criar(2, "Saúde", "Vacinas", ["vacina"]))
        resultados = base.buscar("onde consigo meu cartão sus?")
        self.assertEqual(resultados[0][1].id, 1)
        self.assertGreaterEqual(resultados[0][0], 3)
        self.assertEqual(base.buscar("zzz qqq"), [])


class TestInterface(unittest.TestCase):
    def rodar(self, funcao, base, entradas):
        saida = io.StringIO()
        with patch("builtins.input", side_effect=entradas), redirect_stdout(saida):
            funcao(base)
        return saida.getvalue()

    def test_pedir_id_invalido(self):
        saida = io.StringIO()
        with patch("builtins.input", side_effect=["abc", "-1", "", "²", "5"]), \
                redirect_stdout(saida):
            self.assertEqual(gerir.pedir_id("ID: "), 5)
        self.assertEqual(saida.getvalue().count("ID inválido"), 4)

    def test_cadastrar_id_duplicado_e_campos_vazios(self):
        base = base_com(criar(1))
        entradas = ["1",            # id duplicado -> recusa
                    "2",            # id válido
                    "1",            # categoria existente (Saúde)
                    "", "Título novo",       # título vazio -> repete
                    "", "a, b",              # palavras-chave vazias -> repete
                    "Resposta",
                    "", "Doc 1", "",         # documentos: vazio -> repete; depois termina
                    "Posto",
                    "ftp://errado", "https://gov.br/x"]  # fonte inválida -> repete
        with patch("gerir.hoje", return_value="2026-11-13"):
            saida = self.rodar(gerir.cadastrar, base, entradas)
        self.assertIn("Já existe uma orientação com o ID 1", saida)
        self.assertIn("não pode ficar vazio", saida)
        self.assertIn("Informe pelo menos uma palavra-chave", saida)
        self.assertIn("deve ser um link", saida)
        self.assertEqual(len(base), 2)
        self.assertEqual(base.buscar_por_id(2).palavras_chave, ["a", "b"])
        self.assertTrue(os.path.exists(base.caminho))  # salvou em arquivo

    def test_cadastrar_cancelado(self):
        base = base_com()
        saida = self.rodar(gerir.cadastrar, base, ["0"])
        self.assertIn("cancelado", saida)
        self.assertEqual(len(base), 0)

    def test_operacoes_com_lista_vazia(self):
        base = base_com()
        for funcao in (gerir.consultar_id, gerir.pesquisar,
                       gerir.atualizar, gerir.excluir,
                       gerir.listar_ordenado, gerir.analise):
            saida = self.rodar(funcao, base, [])
            self.assertIn("base está vazia", saida, funcao.__name__)

    def test_consulta_inexistente(self):
        base = base_com(criar(1))
        saida = self.rodar(gerir.consultar_id, base, ["99"])
        self.assertIn("Nenhuma orientação com o ID 99", saida)

    def test_pesquisa_sem_resultado(self):
        base = base_com(criar(1))
        saida = self.rodar(gerir.pesquisar, base, ["1", "inexistente"])
        self.assertIn("Nenhuma orientação encontrada", saida)

    def test_excluir_com_confirmacao(self):
        base = base_com(criar(1), criar(2))
        self.rodar(gerir.excluir, base, ["1", "n"])    # cancela
        self.assertEqual(len(base), 2)
        self.rodar(gerir.excluir, base, ["1", "talvez", "s"])  # resposta inválida e depois sim
        self.assertEqual(ids(base.orientacoes), [2])

    def test_atualizar_pela_interface(self):
        base = base_com(criar(1, titulo="Antigo"))
        with patch("gerir.hoje", return_value="2026-11-13"):
            self.rodar(gerir.atualizar, base, ["1", "2", "Novo título"])
        self.assertEqual(base.buscar_por_id(1).titulo, "Novo título")
        self.assertEqual(base.buscar_por_id(1).verificado_em, "2026-11-13")

    def test_opcao_inexistente_no_menu(self):
        from assistente import pedir_opcao
        saida = io.StringIO()
        with patch("builtins.input", side_effect=["99", "x", "", "3"]), redirect_stdout(saida):
            self.assertEqual(pedir_opcao("Opção: ", 0, 11), 3)
        self.assertEqual(saida.getvalue().count("Opção inválida"), 3)


if __name__ == "__main__":
    unittest.main(module=None, argv=[sys.argv[0], "testes.test_dsa", "-v"])
