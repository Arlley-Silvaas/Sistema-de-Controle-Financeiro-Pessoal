
from armazenamento import carregar_dados, salvar_dados


# Esta classe reúne as operações financeiras.
class ControleFinanceiro:

    # É executada automaticamente quando o sistema começa.
    def __init__(self):

        # Carrega as informações que já estavam salvas.
        self.dados = carregar_dados()

    # ---------------------------------
    # CADASTRAR RECEITAS E DESPESAS
    # ---------------------------------

    def cadastrar(self, tipo, descricao, categoria, valor, mes):

        if tipo not in ("receita", "despesa"):
            raise ValueError("Tipo de movimentação inválido.")

        if valor <= 0:
            raise ValueError("O valor deve ser maior que zero.")

        if not descricao.strip():
            raise ValueError("Informe uma descrição.")

        if not categoria.strip():
            raise ValueError("Informe uma categoria.")

        registro = {
            "tipo": tipo,
            "descricao": descricao,
            "categoria": categoria,
            "valor": valor,
            "mes": mes
        }

        # Adiciona a movimentação à lista.
        self.dados["movimentacoes"].append(registro)

        # Salva os dados atualizados.
        self.salvar()

    # ---------------------------------
    # DEFINIR ORÇAMENTO
    # ---------------------------------

    def definir_orcamento(self, mes, valor):

        if valor <= 0:
            raise ValueError("Orçamento inválido.")

        self.dados["orcamentos"][mes] = valor

        self.salvar()

    # ---------------------------------
    # BUSCAR MOVIMENTAÇÕES
    # ---------------------------------

    def obter_movimentacoes(self, mes=None):

        registros = self.dados["movimentacoes"]

        # Se um mês for informado, filtra os registros.
        if mes:
            return [
                item for item in registros
                if item["mes"] == mes
            ]

        # Se nenhum mês for informado, retorna tudo.
        return registros

    # ---------------------------------
    # CALCULAR SALDO
    # ---------------------------------

    def calcular_resumo(self, mes):

        registros = self.obter_movimentacoes(mes)

        receitas = sum(
            item["valor"] for item in registros
            if item["tipo"] == "receita"
        )

        despesas = sum(
            item["valor"] for item in registros
            if item["tipo"] == "despesa"
        )

        saldo = receitas - despesas

        return {
            "receitas": receitas,
            "despesas": despesas,
            "saldo": saldo
        }

    # ---------------------------------
    # IDENTIFICAR MAIOR CATEGORIA
    # ---------------------------------

    def maior_categoria(self, mes):

        categorias = {}

        for item in self.obter_movimentacoes(mes):

            if item["tipo"] == "despesa":

                categoria = item["categoria"]

                categorias[categoria] = (
                    categorias.get(categoria, 0)
                    + item["valor"]
                )

        if not categorias:
            return None, 0

        maior = max(categorias, key=categorias.get)

        return maior, categorias[maior]

    # ---------------------------------
    # VERIFICAR ORÇAMENTO
    # ---------------------------------

    def verificar_orcamento(self, mes):

        resumo = self.calcular_resumo(mes)

        orcamento = self.dados["orcamentos"].get(mes, 0)

        return {
            "orcamento": orcamento,
            "despesas": resumo["despesas"],
            "ultrapassou": (
                orcamento > 0
                and resumo["despesas"] > orcamento
            )
        }

    # ---------------------------------
    # COMPARAR DOIS MESES
    # ---------------------------------

    def comparar_meses(self, mes1, mes2):

        total1 = self.calcular_resumo(mes1)["despesas"]
        total2 = self.calcular_resumo(mes2)["despesas"]

        if total1 == 0:

            return {
                "mes1": total1,
                "mes2": total2,
                "variacao": None,
                "mensagem": "Não há base para calcular a variação."
            }

        variacao = ((total2 - total1) / total1) * 100

        if variacao > 0:
            mensagem = "Aumento das despesas"

        elif variacao < 0:
            mensagem = "Redução das despesas"

        else:
            mensagem = "Despesas sem alteração"

        return {
            "mes1": total1,
            "mes2": total2,
            "variacao": variacao,
            "mensagem": mensagem
        }

    # ---------------------------------
    # SALVAR INFORMAÇÕES
    # ---------------------------------

    def salvar(self):

        salvar_dados(self.dados)
