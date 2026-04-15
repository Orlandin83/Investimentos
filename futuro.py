#%% Bibliotecas
from pyettj import ettj
import datetime as dt
#%% Database automática
data_ref = dt.date.today() - dt.timedelta(days=1)
while True:
    data_base = data_ref.strftime("%d/%m/%Y")
    try:
        df_ettj = ettj.get_ettj(data_base)
        break
    except ValueError:
        data_ref = data_ref - dt.timedelta(days=1)
#%% Entrada de dados
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
prazo = int(input("Informe o prazo em dias corridos: "))
taxa = float(input("Informe a taxa negociada: "))
#%% Encontra o Vértice
vertice = df_ettj
vertice = vertice[["Dias Corridos", "DI x pré 360"]].copy()
vertice["Dias Corridos"] = vertice["Dias Corridos"].astype(int)
vertice = vertice.set_index("Dias Corridos").sort_index()
if prazo in vertice.index:
    di_aa = vertice.loc[prazo]
else:
    di_aa = vertice.loc[vertice.index <= prazo].iloc[-1]
#%% Cálculos
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
#%% Resultado
print("-*" * 25)
print("RESULTADO")
print("-*" * 25)
print(" ")
print(f"Data Base utilizada: {data_base}")
print(f"Vértice utilizado: {prazo_selecionado} dias\n" )
print(f"DI a.a. estimado: {taxa_di}% a.a.")
print(f"Resultado do DI estimado: {resultado_di}%\n")
if modalidade == 1:
    print(f"Retorno anual estimado: {taxa_contratada_ano:.2f}% a.a.")
elif modalidade == 2:
    print(f"Retorno anual estimado: {taxa_ano:.2f}% a.a.")
print(f"Resultado estimado da aplicação: {resultado}%")
print(" ")
print("-*" * 25)
print("elaborado por: Fabricio Orlandin, CFP® / fonte: B3\n\n")
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
