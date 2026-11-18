import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime

from financeiro import ControleFinanceiro


class SistemaFinanceiro:
    """Monta a interface e conecta os elementos visuais às funções financeiras."""

    def __init__(self, janela):
        self.janela = janela
        self.janela.title("Finance Control - Controle Financeiro")
        self.janela.geometry("1000x700")
        self.janela.configure(bg="#F1F5F9")

        self.controle_financeiro = ControleFinanceiro()
        self.mes_atual = datetime.now().strftime("%m/%Y")

        self.criar_interface()

    # ---------- Métodos auxiliares: evitam repetir configurações ----------
    def rotulo(self, pai, texto, **opcoes):
        """Cria um Label com as cores padrão da interface."""
        return tk.Label(pai, text=texto, bg=opcoes.pop("bg", "white"), **opcoes)

    def entrada(self, pai, largura=20):
        """Cria um campo de texto com largura padrão."""
        return tk.Entry(pai, width=largura)

    def botao(self, pai, texto, comando, cor="#2563EB", **opcoes):
        """Cria um botão padronizado."""
        return tk.Button(
            pai, text=texto, command=comando, bg=cor, fg="white",
            relief="flat", font=("Arial", 10, "bold"), **opcoes
        )

    @staticmethod
    def validar_mes(mes):
        """Confere se o mês está no formato MM/AAAA."""
        datetime.strptime(mes, "%m/%Y")

    # ---------- Estrutura principal e abas ----------
    def criar_interface(self):
        self.rotulo(
            self.janela, "FINANCE CONTROL", font=("Arial", 24, "bold"),
            bg="#172554", fg="white", pady=20
        ).pack(fill="x")

        self.rotulo(
            self.janela, "Sistema de Controle Financeiro Pessoal",
            font=("Arial", 12), bg="#F1F5F9", fg="#334155"
        ).pack(pady=10)

        self.abas = ttk.Notebook(self.janela)
        self.abas.pack(fill="both", expand=True, padx=20, pady=20)

        # Cada Frame é uma página do sistema.
        self.dashboard, self.lancamentos, self.orcamento, self.relatorios = [
            tk.Frame(self.abas, bg="white") for _ in range(4)
        ]
        for pagina, nome in zip(
            (self.dashboard, self.lancamentos, self.orcamento, self.relatorios),
            ("Dashboard", "Lançamentos", "Orçamento", "Relatórios")
        ):
            self.abas.add(pagina, text=nome)

        self.criar_dashboard()
        self.criar_lancamentos()
        self.criar_orcamento()
        self.criar_relatorios()
        self.atualizar_tabela()
        self.atualizar_dashboard()

    # ---------- Dashboard: resumo do mês ----------
    def criar_dashboard(self):
        self.rotulo(
            self.dashboard, "Visão geral financeira",
            font=("Arial", 18, "bold"), fg="#172554"
        ).pack(pady=20)
        self.resumo = self.rotulo(
            self.dashboard, "", font=("Arial", 14), justify="left"
        )
        self.resumo.pack(pady=20)

    def atualizar_dashboard(self):
        resultado = self.controle_financeiro.calcular_resumo(self.mes_atual)
        texto = (
            f"Mês: {self.mes_atual}\n\n"
            f"Receitas: {self.moeda(resultado['receitas'])}\n\n"
            f"Despesas: {self.moeda(resultado['despesas'])}\n\n"
            f"Saldo: {self.moeda(resultado['saldo'])}"
        )
        self.resumo.config(text=texto)

    # ---------- Lançamentos: formulário e tabela ----------
    def criar_lancamentos(self):
        self.rotulo(
            self.lancamentos, "Cadastrar movimentação",
            font=("Arial", 17, "bold"), fg="#172554"
        ).pack(pady=15)

        formulario = tk.Frame(self.lancamentos, bg="white")
        formulario.pack(padx=20, pady=10)

        # Os campos são criados em sequência para reduzir código repetido.
        campos = [
            ("Tipo:", "tipo"),
            ("Descrição:", "descricao"),
            ("Categoria:", "categoria"),
            ("Valor (R$):", "valor"),
            ("Mês (MM/AAAA):", "mes"),
        ]
        for linha, (texto, atributo) in enumerate(campos):
            self.rotulo(formulario, texto).grid(
                row=linha, column=0, padx=5, pady=5, sticky="e"
            )
            if atributo == "tipo":
                campo = ttk.Combobox(
                    formulario, values=["receita", "despesa"],
                    state="readonly", width=18
                )
                campo.set("despesa")
            elif atributo == "categoria":
                campo = ttk.Combobox(
                    formulario,
                    values=["Alimentação", "Moradia", "Transporte", "Saúde",
                            "Educação", "Lazer", "Salário", "Outros"],
                    width=18
                )
            else:
                campo = self.entrada(formulario, 22)
            campo.grid(row=linha, column=1, padx=5)
            setattr(self, atributo, campo)

        self.mes.insert(0, self.mes_atual)
        self.botao(
            formulario, "CADASTRAR MOVIMENTAÇÃO", self.cadastrar
        ).grid(row=5, column=0, columnspan=2, pady=15, sticky="ew")

        self.rotulo(
            self.lancamentos, "Movimentações cadastradas",
            font=("Arial", 14, "bold"), fg="#172554"
        ).pack(pady=10)

        colunas = ("tipo", "descricao", "categoria", "valor", "mes")
        self.tabela = ttk.Treeview(
            self.lancamentos, columns=colunas, show="headings"
        )
        nomes = {
            "tipo": "Tipo", "descricao": "Descrição", "categoria": "Categoria",
            "valor": "Valor", "mes": "Mês"
        }
        for coluna, nome in nomes.items():
            self.tabela.heading(coluna, text=nome)
            self.tabela.column(coluna, width=140, anchor="center")
        self.tabela.pack(fill="both", expand=True, padx=15, pady=10)

    def cadastrar(self):
        try:
            tipo = self.tipo.get()
            descricao = self.descricao.get().strip()
            categoria = self.categoria.get().strip()
            mes = self.mes.get().strip()

            if not descricao:
                raise ValueError("Informe a descrição.")
            if not categoria:
                raise ValueError("Informe a categoria.")
            self.validar_mes(mes)
            valor = self.converter_valor(self.valor.get().strip())

            self.controle_financeiro.cadastrar(
                tipo, descricao, categoria, valor, mes
            )
            self.mes_atual = mes
            messagebox.showinfo("Sucesso", "Movimentação cadastrada com sucesso!")

            # Limpa os campos após o cadastro e atualiza as telas dependentes.
            self.descricao.delete(0, tk.END)
            self.categoria.set("")
            self.valor.delete(0, tk.END)
            self.atualizar_tabela()
            self.atualizar_dashboard()
            self.atualizar_orcamento()
        except ValueError as erro:
            messagebox.showerror("Erro", str(erro))

    def atualizar_tabela(self):
        for item in self.tabela.get_children():
            self.tabela.delete(item)

        for item in self.controle_financeiro.obter_movimentacoes():
            sinal = "+" if item["tipo"] == "receita" else "-"
            self.tabela.insert("", "end", values=(
                item["tipo"].capitalize(), item["descricao"], item["categoria"],
                sinal + self.moeda(item["valor"]), item["mes"]
            ))

    # ---------- Orçamento: limite mensal e acompanhamento ----------
    def criar_orcamento(self):
        self.rotulo(
            self.orcamento, "CONTROLE DE ORÇAMENTO",
            font=("Arial", 20, "bold"), fg="#172554"
        ).pack(pady=25)

        formulario = tk.Frame(self.orcamento, bg="white")
        formulario.pack(pady=15)

        self.rotulo(formulario, "Mês (MM/AAAA):", font=("Arial", 11)).grid(
            row=0, column=0, padx=10, pady=10
        )
        self.mes_orcamento = self.entrada(formulario)
        self.mes_orcamento.insert(0, self.mes_atual)
        self.mes_orcamento.grid(row=0, column=1)

        self.rotulo(formulario, "Limite de gastos (R$):", font=("Arial", 11)).grid(
            row=1, column=0, padx=10, pady=10
        )
        self.valor_orcamento = self.entrada(formulario)
        self.valor_orcamento.grid(row=1, column=1)

        self.botao(
            formulario, "DEFINIR ORÇAMENTO", self.definir_orcamento
        ).grid(row=2, column=0, columnspan=2, pady=15)

        self.info_orcamento = self.rotulo(
            self.orcamento, "Defina um orçamento para visualizar seus gastos.",
            font=("Arial", 13), justify="center"
        )
        self.info_orcamento.pack(pady=25)

        self.progresso = ttk.Progressbar(
            self.orcamento, length=400, mode="determinate", maximum=100
        )
        self.progresso.pack(pady=15)
        self.atualizar_orcamento()

    def definir_orcamento(self):
        try:
            mes = self.mes_orcamento.get().strip()
            self.validar_mes(mes)
            valor = self.converter_valor(self.valor_orcamento.get())
            self.controle_financeiro.definir_orcamento(mes, valor)
            messagebox.showinfo("Sucesso", "Orçamento definido com sucesso!")
            self.atualizar_orcamento()
        except ValueError as erro:
            messagebox.showerror("Erro", str(erro))

    def atualizar_orcamento(self):
        mes = self.mes_orcamento.get().strip()
        try:
            self.validar_mes(mes)
        except ValueError:
            self.info_orcamento.config(
                text="Informe um mês válido no formato MM/AAAA."
            )
            self.progresso["value"] = 0
            return

        resultado = self.controle_financeiro.verificar_orcamento(mes)
        limite, despesas = resultado["orcamento"], resultado["despesas"]
        if limite == 0:
            self.info_orcamento.config(text=f"Nenhum orçamento definido para {mes}.")
            self.progresso["value"] = 0
            return

        restante = limite - despesas
        percentual = despesas / limite * 100
        self.progresso["value"] = min(percentual, 100)

        if resultado["ultrapassou"]:
            situacao = (
                "ATENÇÃO! ORÇAMENTO ULTRAPASSADO!\n"
                f"Você gastou {self.moeda(despesas - limite)} além do limite."
            )
            cor = "#DC2626"
        elif percentual >= 80:
            situacao, cor = "CUIDADO! Você está próximo do limite.", "#D97706"
        else:
            situacao, cor = "Orçamento dentro do limite.", "#16A34A"

        texto = (
            f"Mês: {mes}\n\nOrçamento: {self.moeda(limite)}\n\n"
            f"Total de despesas: {self.moeda(despesas)}\n\n"
            f"Valor restante: {self.moeda(restante)}\n\n"
            f"Utilização do orçamento: {percentual:.1f}%\n\n{situacao}"
        )
        self.info_orcamento.config(text=texto, fg=cor)

    # ---------- Relatórios: consulta mensal e comparação ----------
    def criar_relatorios(self):
        self.rotulo(
            self.relatorios, "RELATÓRIOS FINANCEIROS",
            font=("Arial", 20, "bold"), fg="#172554"
        ).pack(pady=20)

        self.rotulo(
            self.relatorios, "Consultar despesas de um mês",
            font=("Arial", 13, "bold")
        ).pack(pady=5)
        self.mes_relatorio = self.entrada(self.relatorios)
        self.mes_relatorio.insert(0, self.mes_atual)
        self.mes_relatorio.pack(pady=5)
        self.botao(
            self.relatorios, "GERAR RELATÓRIO", self.gerar_relatorio
        ).pack(pady=10)
        self.resultado_relatorio = self.rotulo(
            self.relatorios, "Informe um mês para consultar.",
            font=("Arial", 12), justify="left"
        )
        self.resultado_relatorio.pack(pady=10)

        self.rotulo(
            self.relatorios, "Comparação entre dois meses",
            font=("Arial", 14, "bold"), fg="#172554"
        ).pack(pady=15)
        comparacao = tk.Frame(self.relatorios, bg="white")
        comparacao.pack(pady=5)

        for linha, texto, atributo in (
            (0, "Primeiro mês:", "mes_comparacao1"),
            (1, "Segundo mês:", "mes_comparacao2")
        ):
            self.rotulo(comparacao, texto).grid(
                row=linha, column=0, padx=5, pady=5
            )
            campo = self.entrada(comparacao, 15)
            if linha == 0:
                campo.insert(0, self.mes_atual)
            campo.grid(row=linha, column=1)
            setattr(self, atributo, campo)

        self.botao(
            comparacao, "COMPARAR MESES", self.comparar_relatorios,
            cor="#16A34A"
        ).grid(row=2, column=0, columnspan=2, pady=15)

        self.resultado_comparacao = self.rotulo(
            self.relatorios, "Informe os dois meses para comparar.",
            font=("Arial", 12), justify="left"
        )
        self.resultado_comparacao.pack(pady=10)

    def gerar_relatorio(self):
        try:
            mes = self.mes_relatorio.get().strip()
            self.validar_mes(mes)
            resumo = self.controle_financeiro.calcular_resumo(mes)
            categoria, valor_categoria = self.controle_financeiro.maior_categoria(mes)
            maior_gasto = (
                "Nenhuma despesa cadastrada." if categoria is None
                else f"{categoria}: {self.moeda(valor_categoria)}"
            )
            texto = (
                f"RELATÓRIO DE {mes}\n\n"
                f"Total de receitas: {self.moeda(resumo['receitas'])}\n\n"
                f"Total de despesas: {self.moeda(resumo['despesas'])}\n\n"
                f"Saldo do mês: {self.moeda(resumo['saldo'])}\n\n"
                f"Categoria com maior gasto:\n{maior_gasto}"
            )
            self.resultado_relatorio.config(text=texto, fg="#172554")
        except ValueError:
            messagebox.showerror(
                "Erro", "Informe um mês válido no formato MM/AAAA."
            )

    def comparar_relatorios(self):
        try:
            mes1 = self.mes_comparacao1.get().strip()
            mes2 = self.mes_comparacao2.get().strip()
            self.validar_mes(mes1)
            self.validar_mes(mes2)
            if mes1 == mes2:
                raise ValueError("Informe dois meses diferentes.")

            resultado = self.controle_financeiro.comparar_meses(mes1, mes2)
            texto = (
                "COMPARAÇÃO FINANCEIRA\n\n"
                f"Primeiro mês ({mes1}): {self.moeda(resultado['mes1'])}\n\n"
                f"Segundo mês ({mes2}): {self.moeda(resultado['mes2'])}\n\n"
            )
            if resultado["variacao"] is None:
                texto += resultado["mensagem"]
            else:
                texto += (
                    f"Variação: {abs(resultado['variacao']):.2f}%\n\n"
                    f"Resultado: {resultado['mensagem']}"
                )

            cor = (
                "#DC2626" if resultado["variacao"] is not None
                and resultado["variacao"] > 0 else "#16A34A"
            )
            self.resultado_comparacao.config(text=texto, fg=cor)
        except ValueError as erro:
            messagebox.showerror("Erro", str(erro))

    # ---------- Conversão e apresentação de valores monetários ----------
    def converter_valor(self, texto):
        """Converte valores digitados em reais para número decimal."""
        texto = texto.replace("R$", "").replace(" ", "")
        if "," in texto:
            texto = texto.replace(".", "").replace(",", ".")
        valor = float(texto)
        if valor <= 0:
            raise ValueError("O valor deve ser maior que zero.")
        return valor

    @staticmethod
    def moeda(valor):
        """Formata um número no padrão monetário brasileiro."""
        return "R$ " + f"{valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def iniciar_interface():
    """Cria a janela principal e inicia o loop de eventos do Tkinter."""
    janela = tk.Tk()
    SistemaFinanceiro(janela)
    janela.mainloop()
