#%% importações
from bcb import sgs
import pandas as pd
import numpy as np
import datetime as dt
import matplotlib.pyplot as plt
import yfinance as yf
#%% Definindo as janelas
janela = int(input("Escreva quantos dias úteis terá a janela analisada: "))
#%% dataframe IBOV
ibov = yf.download(tickers="^BVSP", start="1998-01-01", end="2026-02-04")["Close"].astype(int)
ibov = ibov.pct_change().dropna()*100
ibov = ibov.rolling(window=janela).apply(lambda x:(np.prod(1+x/100)-1)*100, raw=True).dropna()
print(ibov)
#%% Dataframe CDI
cdi1 = sgs.get(12, "1998-01-01", "2006-01-01")
cdi2 = sgs.get(12, "2006-01-02", "2014-01-01")
cdi3 = sgs.get(12, "2014-01-02", "2022-01-01")
cdi4 = sgs.get(12, "2022-01-02", "2026-02-04")
cdi = pd.concat([cdi1, cdi2, cdi3, cdi4], axis=0)
cdi= cdi.rolling(window=janela).apply(lambda x:((1+x/100).prod()-1)*100, raw=True).dropna()
print(cdi)
#%% Unificando os Dataframes
ibov_cdi = pd.concat([ibov, cdi], axis=1).dropna()
print(ibov_cdi)
#%%
plt.figure(figsize=(16,10))
plt.plot(ibov_cdi["^BVSP"], color="gray", label="Ibovespa 2 anos", linestyle="--")
plt.plot(ibov_cdi["12"], color="blue", label="CDI 2 anos", linestyle="--")
plt.title("CDI x Ibovespa", fontsize=12, loc="left")
plt.annotate("Fonte: Banco Central do Brasil (BCB) e Yahoo Finance", xy=(0.06,0.0),
             va="bottom", ha="left", xycoords="figure fraction",
             color="black", fontsize=10)
plt.annotate("Elaborado por: Fabricio Orlandin, CFP®", xy=(0.84,0.0),
             va="bottom", ha="right", xycoords="figure fraction",
             color="black", fontsize=10)
plt.axhline(y=0, color="red", linestyle="--")
# %%
total = len(ibov_cdi)
ibov_vence = len(ibov_cdi.loc[ibov_cdi["^BVSP"] > ibov_cdi["12"]])
cdi_vence = len(ibov_cdi.loc[ibov_cdi["12"] > ibov_cdi["^BVSP"]])
print(f"Desde {ibov_cdi.index[1].strftime("%d-%m-%Y")}, o Ibovespa apresentou maior rentabilidade em janelas\n"
      f"de {janela} em {ibov_vence / total * 100 :.2f}% das vezes, enquanto o CDI\n"
      f"apresentou maior rentabilidade na mesma janela em {cdi_vence / total * 100 :.2f}% das vezes")
# %%
