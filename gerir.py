from datetime import date

from assistente import pedir_opcao, pedir_sim_ou_nao
from orientacao import Orientacao

MSG_LISTA_VAZIA = "\nA base está vazia. Cadastre uma orientação primeiro."


# ---------- entradas validadas por categoria ----------
def pedir_texto(texto, obrigatorio=True):
    # Pede um texto; se obrigatório, repete até não ser vazio
    while True:
        valor = " ".join(input(texto).split())
        if valor or not obrigatorio:
            return valor
        print("Este campo não pode ficar vazio.")


def pedir_id(texto):
    # Aqui pede um id inteiro positivo. Devolve None se a pessoa digitar 0
    while True:
        valor = input(texto).strip()
        if valor == "0":
            return None
        if valor.isdecimal() and int(valor) > 0:
            return int(valor)
        print("ID inválido. Digite um número inteiro maior que zero (ou 0 para cancelar).")


def pedir_url(texto):
    while True:
        valor = pedir_texto(texto)
        if valor.startswith(("http://", "https://")):
            return valor
        print("A fonte deve ser um link que comece com http:// ou https://.")


def pedir_palavras_chave():
    while True:
        bruto = input("Palavras-chave separadas por vírgula: ")
        palavras = [p.strip() for p in bruto.split(",") if p.strip()]
        if palavras:
            return palavras
        print("Informe pelo menos uma palavra-chave.")


def pedir_documentos():
    documentos = []
    while True:
        item = pedir_texto(f"Documento {len(documentos) + 1} (Enter vazio para terminar): ",
                           obrigatorio=False)
        if not item:
            if documentos:
                return documentos
            print("Informe pelo menos um item (ex.: 'Nenhum documento é necessário').")
            continue
        documentos.append(item)


def pedir_categoria(base):
    categorias = base.categorias()
    print("Categorias existentes:")
    for i, nome in enumerate(categorias, start=1):
        print(f"  {i}. {nome}")
    print(f"  {len(categorias) + 1}. Criar nova categoria")
    escolha = pedir_opcao("Escolha a categoria: ", 1, len(categorias) + 1)
    if escolha <= len(categorias):
        return categorias[escolha - 1]
    return pedir_texto("Nome da nova categoria: ")


def hoje():
    # Funcao para data sempre atualizada
    return date.today().isoformat()


def salvar_ou_avisar(base):
    if not base.salvar():
        print("Aviso: a alteração vale nesta execução, mas não foi possível gravar o arquivo.")
