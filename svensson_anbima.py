#%% Bibliotecas
import datetime as dt
import re
import requests
import numpy as np
import pandas as pd
#%% ENTRADA DE DADOS
while True:
    modalidade = int(input("Informe a modalidade:\n"
                        "[1] - % do CDI\n"
                        "[2] - CDI + Taxa Fixa\n"
                        "Modalidade: "
    ))
    if modalidade in (1,2):
        break
    else:
        print("Digite uma opção válida:\n"
              "[1] - % do CDI\n"
              "[2] - CDI + Taxa Fixa")
while True:
    prazo = int(input("Informe o prazo em dias corridos de 1 a 3600 dias: "))
    if 1 <= prazo <= 3600:
        break
    else:
        print("Informe um prazo de 1 a 3600 dias")
taxa = float(input("Informe a taxa negociada: "))
#%% CONFIG
url = "https://www.anbima.com.br/informacoes/est-termo/CZ-down.asp"
max = 3600
base_ano = 360
tipo_curva = "PREFIXADOS"
#%% DATABASE
hoje = pd.Timestamp.today() # Obtém a data atual como um objeto Timestamp do Pandas
data_util = hoje - pd.tseries.offsets.BDay(1) # Subtrai 1 dia útil (Business Day) pulando sábados e domingos
data = data_util.strftime("%d%m%Y")# Converte de volta para a string de texto no formato "DDMMAAAA"
#%% EXTRAÇÃO DOS PARÂMETROS
data_formatada = f"{data[:2]}/{data[2:4]}/{data[4:]}" # Formatação da data exigida pelo formulário (DD/MM/AAAA)
payload = {
    'Idioma': 'PT',
    'Dt_Ref': data_formatada,
    'saida': 'csv'
}
response = requests.post(url, data=payload)# Realiza a requisição POST
linhas_csv = response.text.splitlines()# Transformação do texto em lista iterável separada por quebras de linha
linha_alvo = [linha for linha in linhas_csv if linha.startswith(tipo_curva)][0]# Busca linearmente a linha que começa com o tipo de curva desejado ("PREFIXADOS")
colunas = linha_alvo.split(';')# Divide o texto da linha usando o ponto-e-vírgula como separador
# Extrai e converte cada parâmetro (trocando vírgula decimal por ponto)
b1 = float(colunas[1].replace(',', '.'))
b2 = float(colunas[2].replace(',', '.'))
b3 = float(colunas[3].replace(',', '.'))
b4 = float(colunas[4].replace(',', '.'))
l1 = float(colunas[5].replace(',', '.'))
l2 = float(colunas[6].replace(',', '.'))
#%% CÁLCULO DA CURVA DE SVENSSON (LINEAR)
vertices = np.arange(1, max + 1)# Cria o vetor de vértices (de 1 até max) e converte para base anual
t = vertices / base_ano
# Aplicação da fórmula de Nelson-Siegel-Svensson diretamente (sem def)
termo1 = (1 - np.exp(-l1 * t)) / (l1 * t)
termo2 = termo1 - np.exp(-l1 * t)
termo3 = ((1 - np.exp(-l2 * t)) / (l2 * t)) - np.exp(-l2 * t)
# Cálculo das taxas aplicando os betas sobre os termos calculados
taxas = b1 + b2 * termo1 + b3 * termo2 + b4 * termo3
#%% CONSOLIDA DATAFRAME
df_curva = pd.DataFrame({'Vertice': vertices, 'Taxa': taxas})
df_curva = df_curva.set_index("Vertice")
df_curva["Taxa"] = df_curva["Taxa"] * 100
#%% 
print(df_curva)
#%% ENCONTRA O PRAZO NA CURVA 
if prazo in df_curva.index:
    di_aa = df_curva.loc[prazo]
else:
    di_aa = df_curva.loc[df_curva.index <= prazo].iloc[-1]
#%% CÁLCULOS
if modalidade == 1:
    prazo_selecionado = int(di_aa.name)
    taxa_di = float(di_aa.values[0])
    taxa_di_dia = ((1 + taxa_di / 100) ** (1/360) - 1) * 100
    fator_di = (1 + taxa_di_dia / 100) ** prazo_selecionado
    resultado_di = round(((fator_di - 1) * 100), 2)
    taxa_contratada_dia = (taxa_di_dia * taxa / 100)
    taxa_contratada_ano = (((1 + taxa_contratada_dia / 100) ** 360) - 1) * 100
    fator_contratado = (1 + taxa_contratada_dia / 100) ** prazo_selecionado
    resultado = round(((fator_contratado - 1) * 100) , 2)
elif modalidade == 2:
    prazo_selecionado = int(di_aa.name)
    taxa_di = float(di_aa.values[0])
    taxa_di_dia = ((1 + taxa_di / 100) ** (1/360) - 1) * 100
    fator_di = (1 + taxa_di_dia / 100) ** prazo_selecionado
    resultado_di = round(((fator_di - 1) * 100), 2)
    spread_dia = ((1 + taxa / 100) ** (1 / 360) - 1) * 100
    taxa_dia = ((1 + taxa_di_dia / 100) * (1 + spread_dia / 100) - 1) * 100
    taxa_ano = (((1 + taxa_dia / 100) ** 360) - 1) * 100
    fator_spread = (1 + taxa_dia / 100) ** prazo_selecionado
    resultado = round(((fator_spread - 1) * 100), 2)
print("-*" * 25)
print("RESULTADO")
print("-*" * 25)
print(" ")
print(f"Data Base utilizada: {data[:2]}/{data[2:4]}/{data[4:]}")
print(f"Vértice utilizado: {prazo_selecionado} dias\n" )
print(f"DI a.a. estimado: {taxa_di:.2f}% a.a.")
print(f"Resultado do DI estimado: {resultado_di}%\n")
if modalidade == 1:
    print(f"Retorno anual estimado: {taxa_contratada_ano:.2f}% a.a.")
elif modalidade == 2:
    print(f"Retorno anual estimado: {taxa_ano:.2f}% a.a.")
print(f"Resultado estimado da aplicação: {resultado}%")
print(" ")
print("-*" * 25)
print("elaborado por: Fabricio Orlandin, CFP® | matrícula: c074311\n"
      "fonte: B3\n\n")
print("Disclaimer: Disclaimer: Os resultados apresentados\n"
      "constituem meras projeções matemáticas baseadas na\n"
      "Estrutura a Termo da Taxa de Juros (ETTJ) vigente\n"
      "na data-base consultada. Tratando-se de estimativas\n"
      "fundamentadas em expectativas de mercado, os retornos\n"
      "reais apurados no vencimento poderão divergir das taxas\n"
      "aqui demonstradas devido à volatilidade econômica e às\n"
      "flutuações diárias da taxa CDI. Este cálculo possui caráter\n"
      "estritamente informativo e não configura promessa, recomendação\n"
      "de investimento ou garantia de rentabilidade futura."
)


# %%
