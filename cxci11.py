
#%% bilbiotecas
import pandas as pd
import matplotlib.pyplot as plt
import yfinance as yf
from datetime import datetime as dt
#%% Posição do cliente
price = 100
value = 30000
units = value / price
#%% Dataframe do fundo
close = yf.download("CXCI11.SA", start="2022-01-01", end=dt.today(), auto_adjust=False)["Close"]
# %% dataframe de proventos
proventos_df = pd.read_excel("CXCI11.xlsx")
proventos_df = proventos_df.set_index("DATA DE PAGAMENTO")
proventos_df = proventos_df["VALOR POR COTA (R$)"]
df = pd.concat([close, proventos_df], axis=1, ).copy()
df = df.rename(columns=
               {"VALOR POR COTA (R$)": "rendimento_por_cota"})
df["rendimento_por_cota"] = df["rendimento_por_cota"].fillna(0)
print(df)
# %% cálculos cliente
df["quantidade"] = 0.0
df["rend_recebidos"] = 0.0
df["cotas_compradas"] = 0.0

quantidade_atual = units

for i in df.index:
    rendimento = quantidade_atual * df.loc[i, "rendimento_por_cota"]
    preco = df.loc[i, "CXCI11.SA"]
    cotas_novas = rendimento // preco
    quantidade_atual += cotas_novas
    df.at[i, "rend_recebidos"] = rendimento
    df.at[i, "cotas_compradas"] = cotas_novas
    df.at[i, "quantidade"] = quantidade_atual  
df["posicao"] = (df["quantidade"] * df["CXCI11.SA"]).round(2)
# %%
print(df.tail())
# %%
