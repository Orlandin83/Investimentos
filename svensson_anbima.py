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
    prazo = int(input("Informe o prazo em dias corridos de 1 a 10000 dias: "))
    if 1 <= prazo <= 10000:
        break
    else:
        print("Informe um prazo de 1 a 10000 dias")
taxa = float(input("Informe a taxa negociada: "))
#%% CONFIG
url = "https://www.anbima.com.br/informacoes/est-termo/CZ-down.asp"
max = 10000
tipo_curva = "PREFIXADOS"
#%% DATABASE + EXTRAÇÃO DOS PARÂMETROS
data_teste = pd.Timestamp.today().normalize()

while True:
    data = data_teste.strftime("%d%m%Y")
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
#%% CÁLCULO DA CURVA DE SVENSSON (LINEAR)
# Como a Anbima trabalha com dias úteis, o usuário agora digitará dias úteis no terminal.
# Criamos um vetor que vai do dia 1 até o máximo de dias úteis projetados
vertices_uteis = np.arange(1, max + 1)

# O tempo (t) na fórmula de Svensson deve ser parametrizado como anos. 
# A base do ano na Anbima é 252 dias úteis.
t = vertices_uteis / 252

# Aplicação da fórmula de Nelson-Siegel-Svensson diretamente
termo1 = (1 - np.exp(-l1 * t)) / (l1 * t)
termo2 = termo1 - np.exp(-l1 * t)
termo3 = ((1 - np.exp(-l2 * t)) / (l2 * t)) - np.exp(-l2 * t)

# Cálculo das taxas aplicando os betas sobre os termos calculados
taxas = b1 + b2 * termo1 + b3 * termo2 + b4 * termo3

#%% CONSOLIDA DATAFRAME
# Agora o "Vertice" do DataFrame significa Dias Úteis
df_curva = pd.DataFrame({'Vertice': vertices_uteis, 'Taxa': taxas})
df_curva = df_curva.set_index("Vertice")
df_curva["Taxa"] = df_curva["Taxa"] * 100

#%% ENCONTRA O PRAZO NA CURVA 
# A variável "prazo" (que o usuário digitou no terminal) agora significa prazo em DIAS ÚTEIS
if prazo in df_curva.index:
    di_aa = df_curva.loc[prazo]
else:
    di_aa = df_curva.loc[df_curva.index <= prazo].iloc[-1]
#%% CÁLCULOS
if modalidade == 1:
    prazo_selecionado = int(di_aa.name) # Prazo em dias úteis
    taxa_di = float(di_aa.values[0])
    # 1. Taxa DI diária (fator de 1 dia)
    fator_di_diario = (1 + taxa_di / 100) ** (1 / 252)
    
    # 2. Resultado Acumulado do DI puro (só para exibição)
    resultado_di = round((((fator_di_diario) ** prazo_selecionado) - 1) * 100, 2)
    
    # 3. Taxa Contratada Diária (Aqui aplicamos o percentual do usuário - ex: 110%)
    fator_contratado_diario = (fator_di_diario - 1) * (taxa / 100) + 1
    
    # 4. Taxa Contratada Anualizada (projetada para 252 dias)
    taxa_contratada_ano = ((fator_contratado_diario ** 252) - 1) * 100
    
    # 5. Resultado final do período do investimento
    resultado = round((((fator_contratado_diario) ** prazo_selecionado) - 1) * 100, 2)
elif modalidade == 2:
    prazo_selecionado = int(di_aa.name)
    taxa_di = float(di_aa.values[0])
    
    fator_di_diario = (1 + taxa_di / 100) ** (1 / 252)
    resultado_di = round((((fator_di_diario) ** prazo_selecionado) - 1) * 100, 2)
    
    # Descapitaliza o spread fixo do usuário (ex: + 1.5% a.a.) para spread diário
    fator_spread_diario = (1 + taxa / 100) ** (1 / 252)
    
    # O produto CDI + Taxa é a multiplicação dos fatores diários
    fator_misto_diario = fator_di_diario * fator_spread_diario
    
    taxa_ano = ((fator_misto_diario ** 252) - 1) * 100
    resultado = round((((fator_misto_diario) ** prazo_selecionado) - 1) * 100, 2)
print("-*" * 25)
print("RESULTADO")
print("-*" * 25)
print(" ")
print(f"Data Base utilizada: {data[:2]}/{data[2:4]}/{data[4:]}")
print(f"Vértice utilizado: {prazo_selecionado} dias\n" )
print(f"DI a.a. estimado: {taxa_di:.2f}% a.a.")
print(f"Resultado do DI estimado: {resultado_di}%\n")
if modalidade == 1:
    print(f"Retorno anual estimado: {taxa_contratada_ano:.3f}% a.a.")
elif modalidade == 2:
    print(f"Retorno anual estimado: {taxa_ano:.3f}% a.a.")
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
