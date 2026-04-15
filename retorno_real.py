#%% Bibliotecas
from bcb import sgs
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
import datetime as dt
import numpy as np
#%% Janela em meses
start="1993-04-27"
janela=int(input("Escreva a quantidade de meses que deseja na janela de análise: "))
#%% Dataframe CDI
cdi=sgs.get(4391, start, dt.datetime.today())
cdi=cdi.rename(columns={"4391": "CDI"})
cdi=cdi/100
cdi=cdi.rolling(window=janela).apply(lambda x:(np.prod(1+x)-1)*100).dropna()
print(cdi)
# %% Dataframe IPCA
ipca=sgs.get(433, start, dt.datetime.today())
ipca=ipca.rename(columns={"433": "IPCA"})
ipca=ipca/100
ipca=ipca.rolling(window=janela).apply(lambda x:(np.prod(1+x)-1)*100).dropna()
print(ipca)
# %% Dataframe IBOV
ibov_nominal = yf.download("^BVSP", start, dt.datetime.today())["Close"]
ibov_mensal=ibov_nominal.resample("BMS").first()
ibov=ibov_mensal.pct_change().dropna()
ibov=ibov.rolling(window=janela).apply(lambda x:(np.prod(1+x)-1)*100).dropna()
ibov=ibov.rename(columns={"^BVSP": "Ibovespa"})
print(ibov)
# %%
df=pd.concat([cdi, ibov, ipca], axis=1).dropna().round(2)
df["CDI real"]=((1+df["CDI"]/100) / (1+df["IPCA"]/100) - 1) * 100
df["Ibov real"]=((1+df["Ibovespa"]/100) / (1+df["IPCA"]/100) - 1) * 100
print(df)
# %%
plt.figure(figsize=(16,12))
plt.plot(df["CDI real"], label="Retorno Real CDI", color="blue", linestyle="-.")
plt.plot(df["Ibov real"], label="Retorno Real Ibovespa", color="darkgrey", linestyle="--")
plt.legend(loc="best")
plt.title(f"Retorno real em janela móvel de {janela} meses", loc="left")
plt.annotate("Fonte: IBGE / Banco Central do Brasil / Yahoo Finance", xy=(0.1,0.03),
             va="bottom", ha="left", xycoords="figure fraction",
             color="black", fontsize=10)
#plt.annotate("Elaborado por: Fabricio Orlandin, CFP®", xy=(0.8,0.03),
#             va="bottom", ha="right", xycoords="figure fraction",
#             color="black", fontsize=10)
# %%
maior_ibov = len(df.loc[df["Ibov real"] > df["CDI real"]]) / len(df) * 100
maior_cdi = len(df.loc[df["CDI real"] > df["Ibov real"]]) / len(df) * 100
print(f"{maior_ibov:.2f}%")
print(f"{maior_cdi:.2f}%")
# %%
