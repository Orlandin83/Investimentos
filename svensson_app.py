#%% Bibliotecas
import sys
import tkinter as tk
from tkinter import messagebox
import datetime as dt
import requests
import numpy as np
import pandas as pd

#%% POP-UP 1: ENTRADA DE DADOS
# Cria a janela principal invisível e a janela de formulário
root = tk.Tk()
root.title("Simulador CDI Futuro")
root.geometry("400x370")
root.eval('tk::PlaceWindow . center') # Centraliza a janela na tela

# Variáveis do Tkinter para capturar os inputs
modalidade_var = tk.IntVar(value=1)
prazo_var = tk.StringVar()
taxa_var = tk.StringVar()
dados_validos = False

# Função exclusiva para o botão da interface gráfica validar os dados
def submeter():
    global dados_validos
    try:
        p = int(prazo_var.get())
        t = float(taxa_var.get().replace(',', '.'))
        if not (1 <= p <= 3600):
            messagebox.showwarning("Aviso", "O prazo deve ser entre 1 e 3600 dias.")
            return
        dados_validos = True
        root.quit() # Interrompe a pausa da janela e libera o código para seguir
    except ValueError:
        messagebox.showerror("Erro", "Por favor, digite valores numéricos válidos.\nExemplo: 110 ou 1.5")

# Desenho dos botões e campos do Pop-up 1
tk.Label(root, text="Selecione a Modalidade:", font=("Arial", 10, "bold")).pack(pady=(15,5))
tk.Radiobutton(root, text="% do CDI", variable=modalidade_var, value=1).pack()
tk.Radiobutton(root, text="CDI + Taxa Fixa", variable=modalidade_var, value=2).pack()

tk.Label(root, text="Prazo em dias corridos (1 a 3600):", font=("Arial", 10, "bold")).pack(pady=(10,5))
tk.Entry(root, textvariable=prazo_var, justify="center").pack()

tk.Label(root, text="Taxa negociada (ex: 110 ou 1.5):", font=("Arial", 10, "bold")).pack(pady=(10,5))
tk.Entry(root, textvariable=taxa_var, justify="center").pack()

tk.Button(root, text="Simular", command=submeter, bg="blue", fg="black", font=("Arial", 10, "bold"), width=15).pack(pady=20)

# Créditos exigidos no Pop-up de Entrada
tk.Label(root, text="elaborado por: Fabricio Orlandin, CFP® | matrícula: c074311", font=("Arial", 10, "italic"), fg="gray").pack(side="bottom", pady=10)

root.mainloop() # O código fica travado aqui até o usuário clicar em "Simular"

# Se o usuário fechar a janela no "X" sem preencher, encerra o script inteiro
if not dados_validos:
    root.destroy()
    sys.exit()

# Extrai os dados em formato Python tradicional
modalidade = modalidade_var.get()
prazo = int(prazo_var.get())
taxa = float(taxa_var.get().replace(',', '.'))
root.destroy() # Destrói o pop-up 1

#%% DATABASE (Garante que a data consultada será dia útil)
hoje = pd.Timestamp.today()
data_util = hoje - pd.tseries.offsets.BDay(1)
data_formatada = data_util.strftime("%d/%m/%Y")

#%% CONFIG
url = "https://www.anbima.com.br/informacoes/est-termo/CZ-down.asp"
max_dias = 3600
base_ano = 360
tipo_curva = "PREFIXADOS"

#%% EXTRAÇÃO DOS PARÂMETROS
payload = {
    'Idioma': 'PT',
    'Dt_Ref': data_formatada,
    'saida': 'csv'
}
response = requests.post(url, data=payload)
linhas_csv = response.text.splitlines()
linha_alvo = [linha for linha in linhas_csv if linha.startswith(tipo_curva)][0]
colunas = linha_alvo.split(';')

b1 = float(colunas[1].replace(',', '.'))
b2 = float(colunas[2].replace(',', '.'))
b3 = float(colunas[3].replace(',', '.'))
b4 = float(colunas[4].replace(',', '.'))
l1 = float(colunas[5].replace(',', '.'))
l2 = float(colunas[6].replace(',', '.'))

#%% CÁLCULO DA CURVA DE SVENSSON (LINEAR)
vertices = np.arange(1, max_dias + 1)
t = vertices / base_ano
termo1 = (1 - np.exp(-l1 * t)) / (l1 * t)
termo2 = termo1 - np.exp(-l1 * t)
termo3 = ((1 - np.exp(-l2 * t)) / (l2 * t)) - np.exp(-l2 * t)
taxas = b1 + b2 * termo1 + b3 * termo2 + b4 * termo3

#%% CONSOLIDA DATAFRAME
df_curva = pd.DataFrame({'Vertice': vertices, 'Taxa': taxas})
df_curva = df_curva.set_index("Vertice")
df_curva["Taxa"] = df_curva["Taxa"] * 100

if prazo in df_curva.index:
    di_aa = df_curva.loc[prazo]
else:
    di_aa = df_curva.loc[df_curva.index <= prazo].iloc[-1]

#%% CÁLCULOS
prazo_selecionado = int(di_aa.name)
taxa_di = float(di_aa.values[0])
taxa_di_dia = ((1 + taxa_di / 100) ** (1/360) - 1) * 100
fator_di = (1 + taxa_di_dia / 100) ** prazo_selecionado
resultado_di = round(((fator_di - 1) * 100), 2)

if modalidade == 1:
    taxa_contratada_dia = (taxa_di_dia * taxa / 100)
    taxa_contratada_ano = (((1 + taxa_contratada_dia / 100) ** 360) - 1) * 100
    fator_contratado = (1 + taxa_contratada_dia / 100) ** prazo_selecionado
    resultado = round(((fator_contratado - 1) * 100) , 2)
    txt_anual = f"Retorno anual estimado: {taxa_contratada_ano:.2f}% a.a."
elif modalidade == 2:
    spread_dia = ((1 + taxa / 100) ** (1 / 360) - 1) * 100
    taxa_dia_mista = ((1 + taxa_di_dia / 100) * (1 + spread_dia / 100) - 1) * 100
    taxa_ano = (((1 + taxa_dia_mista / 100) ** 360) - 1) * 100
    fator_spread = (1 + taxa_dia_mista / 100) ** prazo_selecionado
    resultado = round(((fator_spread - 1) * 100), 2)
    txt_anual = f"Retorno anual estimado: {taxa_ano:.2f}% a.a."

#%% POP-UP 2: RESULTADOS
res = tk.Tk()
res.title("Resultado da Simulação")
res.geometry("500x480")
res.eval('tk::PlaceWindow . center')

tk.Label(res, text="📊 RESULTADO DA SIMULAÇÃO", font=("Arial", 14, "bold")).pack(pady=(15, 10))

# Grade de Informações calculadas
frame_info = tk.Frame(res)
frame_info.pack(pady=10)

tk.Label(frame_info, text=f"Data Base utilizada: {data_formatada}", font=("Arial", 11)).grid(row=0, column=0, sticky="w", pady=2)
tk.Label(frame_info, text=f"Vértice utilizado: {prazo_selecionado} dias", font=("Arial", 11)).grid(row=1, column=0, sticky="w", pady=2)
tk.Label(frame_info, text=f"DI a.a. estimado: {taxa_di:.2f}% a.a.", font=("Arial", 11)).grid(row=2, column=0, sticky="w", pady=2)
tk.Label(frame_info, text=f"Resultado do DI estimado: {resultado_di}%", font=("Arial", 11)).grid(row=3, column=0, sticky="w", pady=2)
tk.Label(frame_info, text=txt_anual, font=("Arial", 11, "bold")).grid(row=4, column=0, sticky="w", pady=(10, 2))
tk.Label(frame_info, text=f"Resultado estimado da aplicação: {resultado}%", font=("Arial", 12, "bold"), fg="darkblue").grid(row=5, column=0, sticky="w", pady=2)

# Fontes e Disclaimer exigidos no Pop-up de Resultado
tk.Label(res, text="fonte: B3 / Metodologia Nelson-Siegel-Svensson (ANBIMA)", font=("Arial", 9, "bold")).pack(pady=(15, 5))

disclaimer = ("Disclaimer: Os resultados apresentados constituem meras projeções matemáticas baseadas na "
              "Estrutura a Termo da Taxa de Juros (ETTJ) vigente na data-base consultada. Tratando-se de estimativas "
              "fundamentadas em expectativas de mercado, os retornos reais apurados no vencimento poderão divergir das taxas "
              "aqui demonstradas devido à volatilidade econômica e às flutuações diárias da taxa CDI. Este cálculo possui caráter "
              "estritamente informativo e não configura promessa, recomendação de investimento ou garantia de rentabilidade futura.\n"
              "FAVOR NÃO IMPRIMIR")

tk.Message(res, text=disclaimer, width=450, font=("Arial", 8, "italic"), fg="dimgray", justify="center").pack()

tk.Button(res, text="Sair", command=res.destroy, bg="red", fg="black", font=("Arial", 10, "bold"), width=15).pack(pady=15)

res.mainloop()