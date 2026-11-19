
from base_conhecimento import BaseConhecimento
from orientacao import Orientacao


def cadeia(lista):
    # percorre os nós seguindo o proximo, como a lista faz por dentro
    partes = []
    no = lista.comeco
    while no is not None:
        partes.append(f"[{no.dado.id}]")
        no = no.proximo
    if not partes:
        return "comeco -> None   (lista vazia)"
    return "comeco -> " + " -> ".join(partes) + " -> None"


def mostrar(base, passo):
    lista = base.orientacoes
    print(f"\n=== {passo} ===")
    print(cadeia(lista))
    ultimo = lista.final.dado.id if lista.final else None
    print(f"tamanho: {len(lista)} | final aponta para o nó: {ultimo}")
    input("Enter para continuar...")


def nova(id):
    return Orientacao(id, "Teste", f"Orientação de teste {id}", ["teste"],
                      "resposta", ["nenhum"], "local", "https://gov.br", "2026-11-15")


base = BaseConhecimento("data/base_conhecimento.json")
base.carregar()
mostrar(base, "1. Lista carregada do JSON")

base.cadastrar(nova(99))
mostrar(base, "2. Inserir no fim (ID 99): o final passa a apontar para o 99")

repetido = base.cadastrar(nova(99))
print(f"\nCadastrar o ID 99 de novo devolveu: {repetido}")
mostrar(base, "3. ID duplicado recusado: a lista não mudou")
 
base.excluir(5)
mostrar(base, "4. Remover do meio (ID 5): o nó anterior passa a apontar para o seguinte")

base.excluir(99)
mostrar(base, "5. Remover o último (ID 99): o final volta para o nó anterior")

base.excluir(1)
mostrar(base, "6. Remover o primeiro (ID 1): o comeco passa a apontar para o ID 2")

base.ordenar("titulo")
mostrar(base, "7. Ordenada por título com Merge Sort (só os ponteiros mudaram)")
for o in base.orientacoes:
    print(f"   [{o.id}] {o.titulo[:55]}")
input("Enter para continuar...")

base.ordenar("id")
mostrar(base, "8. Ordenada por ID")

vazia = BaseConhecimento("data/vazia.json")
mostrar(vazia, "9. Lista vazia (nenhum nó)")
print(f"buscar_por_id(1) na lista vazia: {vazia.buscar_por_id(1)}")
print(f"excluir(1) na lista vazia: {vazia.excluir(1)}")
