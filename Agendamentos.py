import tkinter as tk
from tkinter import ttk, messagebox
import csv
import os
import re
from datetime import datetime
import sys


# Arquivo CSV

if getattr(sys, 'frozen', False):
    # Quando for executável
    pasta_atual = os.path.dirname(sys.executable)
else:
    # Quando estiver rodando como script Python
    pasta_atual = os.path.dirname(__file__)

CSV_FILE = os.path.join(pasta_atual, "agendamentos.csv")



def validar_email(email):
    padrao = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return re.match(padrao, email) is not None

def validar_data(data):
    try:
        return datetime.strptime(data, "%d/%m/%Y")
    except ValueError:
        return None

def validar_hora(hora):
    try:
        return datetime.strptime(hora, "%H:%M")
    except ValueError:
        return None

# ------------------- Formatação automática de data e hora -------------------
def formatar_data(event=None):
    texto = entry_data.get().replace("/", "")[:8]
    novo = ""
    if len(texto) >= 2:
        novo += texto[:2] + "/"
        if len(texto) >= 4:
            novo += texto[2:4] + "/"
            novo += texto[4:]
        else:
            novo += texto[2:]
    else:
        novo = texto
    entry_data.delete(0, tk.END)
    entry_data.insert(0, novo)

def formatar_hora(event=None):
    texto = entry_hora.get().replace(":", "")[:4]
    novo = ""
    if len(texto) >= 2:
        novo += texto[:2] + ":"
        novo += texto[2:]
    else:
        novo = texto
    entry_hora.delete(0, tk.END)
    entry_hora.insert(0, novo)


def validar_data_hora(data, hora):
    d = validar_data(data)
    h = validar_hora(hora)
    if not d or not h:
        return False, None
    # Combina data + hora
    dt = datetime.combine(d.date(), h.time())
    if dt < datetime.now():
        return False, None
    return True, dt

def salvar_agendamento():
    nome = entry_nome.get().strip()
    email = entry_email.get().strip()
    servico = combo_servico.get().strip()
    data = entry_data.get().strip()
    hora = entry_hora.get().strip()
    extra = ""

    # Validações
    if not nome or not email or not servico or not data or not hora:
        messagebox.showwarning("Campos obrigatórios", "Preencha todos os campos!")
        return

    if not validar_email(email):
        messagebox.showerror("Erro de validação", "Digite um e-mail válido.")
        return

    valido, _ = validar_data_hora(data, hora)
    if not valido:
        messagebox.showerror("Erro de validação", "Digite uma data/hora válida e que seja futura.")
        return

    # Salvar no CSV
    novo_registro = [nome, email, servico, data, hora, extra]
    arquivo_existe = os.path.isfile(CSV_FILE)

    try:
        with open(CSV_FILE, mode="a", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            if not arquivo_existe:
                writer.writerow(["Nome", "Email", "Serviço", "Data", "Hora", "Info Extra"])
            writer.writerow(novo_registro)
    except Exception as e:
        messagebox.showerror("Erro", f"Erro ao salvar no CSV: {e}")
        return

    messagebox.showinfo("Agendamento", "Agendamento salvo com sucesso!")

    # Limpar
    entry_nome.delete(0, tk.END)
    entry_email.delete(0, tk.END)
    combo_servico.current(0)
    entry_data.delete(0, tk.END)
    entry_hora.delete(0, tk.END)

def ver_agendamentos():
    if not os.path.isfile(CSV_FILE):
        messagebox.showinfo("Informação", "Nenhum agendamento encontrado.")
        return

    janela = tk.Toplevel(root)
    janela.title("Agendamentos Salvos")
    janela.geometry("800x500")

    colunas = ("Nome", "Email", "Serviço", "Data", "Hora", "Info Extra")
    tree = ttk.Treeview(janela, columns=colunas, show="headings")
    tree.pack(fill="both", expand=True, pady=10)

    for col in colunas:
        tree.heading(col, text=col)
        tree.column(col, width=120, anchor="center")

    def carregar_dados(filtro=None, termo=None):
        # Limpa tabela
        for i in tree.get_children():
            tree.delete(i)

        with open(CSV_FILE, mode="r", encoding="utf-8") as file:
            reader = csv.reader(file)
            next(reader, None)
            for row in reader:
                if filtro and termo:
                    idx = colunas.index(filtro)
                    if termo.lower() not in row[idx].lower():
                        continue
                tree.insert("", tk.END, values=row)

    carregar_dados()

    # 🔍 Filtro
    frame_filtro = tk.Frame(janela)
    frame_filtro.pack(pady=5)

    tk.Label(frame_filtro, text="Filtrar por:").pack(side="left", padx=5)
    filtro_opcao = ttk.Combobox(frame_filtro, values=["Nome", "Serviço", "Data"], state="readonly", width=12)
    filtro_opcao.current(0)
    filtro_opcao.pack(side="left")

    entry_filtro = tk.Entry(frame_filtro, width=30)
    entry_filtro.pack(side="left", padx=5)

    def aplicar_filtro():
        filtro = filtro_opcao.get()
        termo = entry_filtro.get().strip()
        if termo:
            carregar_dados(filtro=filtro, termo=termo)
        else:
            carregar_dados()

    btn_filtrar = tk.Button(frame_filtro, text="Filtrar", command=aplicar_filtro, bg="#2196F3", fg="white")
    btn_filtrar.pack(side="left", padx=5)

    # ⚡ Funções Excluir e Editar
    def excluir_selecionado():
        selecionado = tree.selection()
        if not selecionado:
            messagebox.showwarning("Seleção", "Selecione um agendamento para excluir.")
            return

        valores = tree.item(selecionado)["values"]

        confirmar = messagebox.askyesno("Confirmar Exclusão",
                                        f"Excluir agendamento de {valores[0]} em {valores[3]} às {valores[4]}?")
        if not confirmar:
            return

        with open(CSV_FILE, mode="r", encoding="utf-8") as file:
            linhas = list(csv.reader(file))

        cabecalho, registros = linhas[0], linhas[1:]
        novos_registros = [r for r in registros if r != valores]

        with open(CSV_FILE, mode="w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow(cabecalho)
            writer.writerows(novos_registros)

        tree.delete(selecionado)
        messagebox.showinfo("Exclusão", "Agendamento excluído com sucesso!")

    def editar_selecionado():
        selecionado = tree.selection()
        if not selecionado:
            messagebox.showwarning("Seleção", "Selecione um agendamento para editar.")
            return

        valores = tree.item(selecionado)["values"]

        edit_win = tk.Toplevel(janela)
        edit_win.title("Editar Agendamento")
        edit_win.geometry("400x500")

        tk.Label(edit_win, text="Nome:").pack(anchor="w", padx=20, pady=5)
        e_nome = tk.Entry(edit_win, width=40)
        e_nome.pack(padx=20)
        e_nome.insert(0, valores[0])

        tk.Label(edit_win, text="Email:").pack(anchor="w", padx=20, pady=5)
        e_email = tk.Entry(edit_win, width=40)
        e_email.pack(padx=20)
        e_email.insert(0, valores[1])

        tk.Label(edit_win, text="Serviço:").pack(anchor="w", padx=20, pady=5)
        e_servico = ttk.Combobox(edit_win, values=["Impressão 3D", "Corte a Laser", "Auxílio Geral"], state="readonly")
        e_servico.pack(padx=20)
        e_servico.set(valores[2])

        tk.Label(edit_win, text="Data (dd/mm/aaaa):").pack(anchor="w", padx=20, pady=5)
        e_data = tk.Entry(edit_win, width=20)
        e_data.pack(padx=20)
        e_data.insert(0, valores[3])

        tk.Label(edit_win, text="Hora (hh:mm):").pack(anchor="w", padx=20, pady=5)
        e_hora = tk.Entry(edit_win, width=20)
        e_hora.pack(padx=20)
        e_hora.insert(0, valores[4])

        # Campo extra dinâmico
        extra_label = tk.Label(edit_win, text="Info Extra:")
        extra_label.pack(anchor="w", padx=20, pady=5)
        e_extra = tk.Entry(edit_win, width=40)
        e_extra.pack(padx=20)
        e_extra.insert(0, valores[5] if len(valores) > 5 else "")

        def atualizar_campos(event=None):
            serv = e_servico.get()
            if serv == "Impressão 3D":
                extra_label.config(text="Tempo Impressão / Gramas Filamento:")
            elif serv == "Corte a Laser":
                extra_label.config(text="Dimensão / Espessura:")
            else:
                extra_label.config(text="Tipo de Auxílio:")

        e_servico.bind("<<ComboboxSelected>>", atualizar_campos)
        atualizar_campos()

        def salvar_edicao():
            valido, _ = validar_data_hora(e_data.get(), e_hora.get())
            if not valido:
                messagebox.showerror("Erro", "Digite uma data/hora válida e que seja futura.")
                return

            novo_valor = [
                e_nome.get(), e_email.get(), e_servico.get(),
                e_data.get(), e_hora.get(), e_extra.get()
            ]

            with open(CSV_FILE, mode="r", encoding="utf-8") as file:
                linhas = list(csv.reader(file))

            cabecalho, registros = linhas[0], linhas[1:]
            novos_registros = []
            for r in registros:
                if r == valores:
                    novos_registros.append(novo_valor)
                else:
                    novos_registros.append(r)

            with open(CSV_FILE, mode="w", newline="", encoding="utf-8") as file:
                writer = csv.writer(file)
                writer.writerow(cabecalho)
                writer.writerows(novos_registros)

            tree.item(selecionado, values=novo_valor)
            messagebox.showinfo("Edição", "Agendamento atualizado com sucesso!")
            edit_win.destroy()

        tk.Button(edit_win, text="Salvar Alterações", command=salvar_edicao,
                  bg="#4CAF50", fg="white").pack(pady=20)

    # Botões excluir e editar
    frame_btns = tk.Frame(janela)
    frame_btns.pack(pady=5)

    tk.Button(frame_btns, text="Excluir Selecionado", command=excluir_selecionado,
              bg="#E53935", fg="white").pack(side="left", padx=10)
    tk.Button(frame_btns, text="Editar Selecionado", command=editar_selecionado,
              bg="#FF9800", fg="white").pack(side="left", padx=10)

# ---------------- Janela Principal ----------------
root = tk.Tk()
root.title("Sistema de Agendamento")
root.geometry("500x460")
root.resizable(False, False)

tk.Label(root, text="Nome:").pack(anchor="w", padx=20, pady=5)
entry_nome = tk.Entry(root, width=40)
entry_nome.pack(padx=20)

tk.Label(root, text="Email:").pack(anchor="w", padx=20, pady=5)
entry_email = tk.Entry(root, width=40)
entry_email.pack(padx=20)

tk.Label(root, text="Serviço:").pack(anchor="w", padx=20, pady=5)
combo_servico = ttk.Combobox(root, values=["Impressão 3D", "Corte a Laser", "Auxílio Geral"], state="readonly")
combo_servico.pack(padx=20)
combo_servico.current(0)

tk.Label(root, text="Data (dd/mm/aaaa):").pack(anchor="w", padx=20, pady=5)
entry_data = tk.Entry(root, width=20)
entry_data.pack(padx=20)
entry_data.bind("<KeyRelease>", formatar_data) 

tk.Label(root, text="Hora (hh:mm):").pack(anchor="w", padx=20, pady=5)
entry_hora = tk.Entry(root, width=20)
entry_hora.pack(padx=20)
entry_hora.bind("<KeyRelease>", formatar_hora)


tk.Button(root, text="Salvar Agendamento", command=salvar_agendamento,
          bg="#4CAF50", fg="white").pack(pady=10)

tk.Button(root, text="Ver Agendamentos", command=ver_agendamentos,
          bg="#2196F3", fg="white").pack(pady=5)

root.mainloop()
