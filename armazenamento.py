
import json
from pathlib import Path

# Encontra a pasta onde este arquivo está localizado.
PASTA = Path(__file__).parent

# Nome do arquivo que guardará os dados.
ARQUIVO = PASTA / "dados.json"


# Esta função carrega as informações salvas.
def carregar_dados():

    # Se o arquivo ainda não existir, cria uma estrutura vazia.
    if not ARQUIVO.exists():
        return {
            "movimentacoes": [],
            "orcamentos": {}
        }

    # Abre o arquivo para leitura.
    try:
        with open(ARQUIVO, "r", encoding="utf-8") as arquivo:

            dados = json.load(arquivo)

        return dados

    except (json.JSONDecodeError, OSError):
        return {
            "movimentacoes": [],
            "orcamentos": {}
        }


# Esta função salva as informações no arquivo JSON.
def salvar_dados(dados):

    with open(ARQUIVO, "w", encoding="utf-8") as arquivo:

        json.dump(
            dados,
            arquivo,
            indent=4,
            ensure_ascii=False
        )
