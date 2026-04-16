#%% Bibliotecas
import sys
import tkinter as tk
from tkinter import messagebox
import requests
import numpy as np
import pandas as pd

#%% POP-UP 1: ENTRADA DE DADOS
root = tk.Tk()
root.title("Simulador CDI Futuro")
root.geometry("400x370")
root.eval('tk::PlaceWindow . center')

modalidade_var = tk.IntVar(value=1)
prazo_var = tk.StringVar()
taxa_var = tk.StringVar()
dados_validos = False

def submeter():
    global dados_validos
    try:
        p = int(prazo_var.get())
        float(taxa_var.get().replace(',', '.'))
        if not (1 <= p <= 10000):
            messagebox.showwarning("Aviso", "O prazo deve ser entre 1 e 10000 dias úteis.")
            return
        dados_validos = True
        root.quit()
    except ValueError:
        messagebox.showerror("Erro", "Por favor, digite valores numéricos válidos.\nExemplo: 110 ou 1,5")

tk.Label(root, text="Selecione a Modalidade:", font=("Arial", 10, "bold")).pack(pady=(15,5))
tk.Radiobutton(root, text="% do CDI", variable=modalidade_var, value=1).pack()
tk.Radiobutton(root, text="CDI + Taxa Fixa", variable=modalidade_var, value=2).pack()

tk.Label(root, text="Prazo em dias úteis (1 a 3600):", font=("Arial", 10, "bold")).pack(pady=(10,5))
tk.Entry(root, textvariable=prazo_var, justify="center").pack()

tk.Label(root, text="Taxa negociada (ex: 110 ou 1.5):", font=("Arial", 10, "bold")).pack(pady=(10,5))
tk.Entry(root, textvariable=taxa_var, justify="center").pack()

tk.Button(root, text="Simular", command=submeter, bg="blue", fg="black", font=("Arial", 10, "bold"), width=15).pack(pady=20)

tk.Label(root, text="elaborado por: Fabricio Orlandin, CFP® | matrícula: c074311", font=("Arial", 10, "italic"), fg="gray").pack(side="bottom", pady=10)

root.mainloop()

if not dados_validos:
    root.destroy()
    sys.exit()

modalidade = modalidade_var.get()
prazo = int(prazo_var.get())
taxa = float(taxa_var.get().replace(',', '.'))
root.destroy()

#%% CONFIG
url = "https://www.anbima.com.br/informacoes/est-termo/CZ-down.asp"
max_dias = 10000
tipo_curva = "PREFIXADOS"

#%% DATABASE + EXTRAÇÃO DOS PARÂMETROS
data_teste = pd.Timestamp.today().normalize()

while True:
    data_formatada = data_teste.strftime("%d/%m/%Y")

    payload = {
        'Idioma': 'PT',
        'Dt_Ref': data_formatada,
        'saida': 'csv'
    }

    response = requests.post(url, data=payload)
    linhas_csv = response.text.splitlines()
    linhas_filtradas = [linha for linha in linhas_csv if linha.startswith(tipo_curva)]

    if len(linhas_filtradas) > 0:
        linha_alvo = linhas_filtradas[0]
        break
    else:
        data_teste = data_teste - pd.tseries.offsets.BDay(1)

colunas = linha_alvo.split(';')

b1 = float(colunas[1].replace(',', '.'))
b2 = float(colunas[2].replace(',', '.'))
b3 = float(colunas[3].replace(',', '.'))
b4 = float(colunas[4].replace(',', '.'))
l1 = float(colunas[5].replace(',', '.'))
l2 = float(colunas[6].replace(',', '.'))

#%% CÁLCULO DA CURVA DE SVENSSON
vertices = np.arange(1, max_dias + 1)
t = vertices / 252

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

fator_di_diario = (1 + taxa_di / 100) ** (1 / 252)
resultado_di = round(((fator_di_diario ** prazo_selecionado) - 1) * 100, 2)

if modalidade == 1:
    fator_contratado_diario = ((fator_di_diario - 1) * (taxa / 100)) + 1
    taxa_contratada_ano = ((fator_contratado_diario ** 252) - 1) * 100
    resultado = round(((fator_contratado_diario ** prazo_selecionado) - 1) * 100, 2)
    txt_anual = f"Retorno anual estimado: {taxa_contratada_ano:.2f}% a.a."

elif modalidade == 2:
    fator_spread_diario = (1 + taxa / 100) ** (1 / 252)
    fator_misto_diario = fator_di_diario * fator_spread_diario
    taxa_ano = ((fator_misto_diario ** 252) - 1) * 100
    resultado = round(((fator_misto_diario ** prazo_selecionado) - 1) * 100, 2)
    txt_anual = f"Retorno anual estimado: {taxa_ano:.2f}% a.a."

#%% POP-UP 2: RESULTADOS
res = tk.Tk()
res.title("Resultado da Simulação")
res.geometry("500x480")
res.eval('tk::PlaceWindow . center')

tk.Label(res, text="📊 RESULTADO DA SIMULAÇÃO", font=("Arial", 14, "bold")).pack(pady=(15, 10))

frame_info = tk.Frame(res)
frame_info.pack(pady=10)

tk.Label(frame_info, text=f"Data Base utilizada: {data_formatada}", font=("Arial", 11)).grid(row=0, column=0, sticky="w", pady=2)
tk.Label(frame_info, text=f"Vértice utilizado: {prazo_selecionado} dias úteis", font=("Arial", 11)).grid(row=1, column=0, sticky="w", pady=2)
tk.Label(frame_info, text=f"DI a.a. estimado: {taxa_di:.2f}% a.a.", font=("Arial", 11)).grid(row=2, column=0, sticky="w", pady=2)
tk.Label(frame_info, text=f"Resultado do DI estimado: {resultado_di}%", font=("Arial", 11)).grid(row=3, column=0, sticky="w", pady=2)
tk.Label(frame_info, text=txt_anual, font=("Arial", 11, "bold")).grid(row=4, column=0, sticky="w", pady=(10, 2))
tk.Label(frame_info, text=f"Resultado estimado da aplicação: {resultado}%", font=("Arial", 12, "bold"), fg="darkblue").grid(row=5, column=0, sticky="w", pady=2)

tk.Label(res, text="fonte: B3 / Metodologia Nelson-Siegel-Svensson (ANBIMA)", font=("Arial", 9, "bold")).pack(pady=(15, 5))

disclaimer = (
    "Disclaimer: Os resultados apresentados constituem meras projeções matemáticas baseadas na "
    "Estrutura a Termo da Taxa de Juros (ETTJ) vigente na data-base consultada. Tratando-se de estimativas "
    "fundamentadas em expectativas de mercado, os retornos reais apurados no vencimento poderão divergir das taxas "
    "aqui demonstradas devido à volatilidade econômica e às flutuações diárias da taxa CDI. Este cálculo possui caráter "
    "estritamente informativo e não configura promessa, recomendação de investimento ou garantia de rentabilidade futura.\n"
    "FAVOR NÃO IMPRIMIR"
)

tk.Message(res, text=disclaimer, width=450, font=("Arial", 8, "italic"), fg="dimgray", justify="center").pack()

tk.Button(res, text="Sair", command=res.destroy, bg="red", fg="black", font=("Arial", 10, "bold"), width=15).pack(pady=15)

res.mainloop()