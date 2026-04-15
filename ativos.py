#%% Bibliotecas
from bcb import sgs
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
#%% Definição do período analisado
start = "2024-12-31"
end = "2026-01-12"
#%% CDI
cdi = sgs.get(4389, start, end)
cdi["dia"] = ((1 + cdi["4389"]/100)**(1/252)-1)*100
cdi["fator"] = (1 + cdi["dia"]/100)
cdi["CDI Acum"] = (cdi["fator"].cumprod()-1)*100 
cdi = cdi["CDI Acum"].astype(float).round(2)
cdi = pd.DataFrame(cdi)
# %% Lista de ativos do yahoo finance
ativos = ["^BVSP", "^GSPC", "BTC-USD", "GC=F", "BRL=X", "EURBRL=X", "IMAB11.SA"]
data = yf.download(ativos, start, end)["Close"].dropna()
data = data.rename(columns = {"BRL=X": "Dólar",
                              "BTC-USD": "Bitcoin",
                              "EURBRL=X": "Euro",
                              "GC=F": "Ouro",
                              "^BVSP": "Ibovespa",
                              "^GSPC": "S&P500",
                              "IMAB11.SA": "ETF IMA-B"
                              })
data_perf = ((data / data.iloc[0] - 1) * 100).astype(float).round(2) #normaliza a performance
# %% Cria os gráficos
fig, axes = plt.subplots(ncols=2, nrows=4, figsize=(24,12))
# Gráfico 1 - CDI
axes[0,0].plot(cdi, color="blue", label="CDI")
axes[0,0].annotate(f"{cdi.iloc[-1,0]}%",
                   xy=(0.97, 0.5), xycoords = "axes fraction",
                   va = "bottom", ha = "right", fontsize = 10, color = "blue",
                   bbox=dict(boxstyle= "round, pad=0.25", fc="lightgray", ec="blue", lw=0.8, alpha=0.75))
axes[0,0].legend()
# Gráfico 2 - IMA-B
axes[0,1].plot(data_perf["ETF IMA-B"], color="blue", label="IMA-B(proxy)")
axes[0,1].annotate(f"{data_perf["ETF IMA-B"].iloc[-1]}%",
                   xy=(0.97, 0.5), xycoords = "axes fraction",
                   va = "bottom", ha = "right", fontsize = 10, color = "blue",
                   bbox=dict(boxstyle= "round, pad=0.25", fc="lightgray", ec="blue", lw=0.8, alpha=0.75))
axes[0,1].legend()
# Gráfico 3 - Ibov
axes[1,0].plot(data_perf["Ibovespa"], color="blue", label="Ibovespa")
axes[1,0].annotate(f"{data_perf["Ibovespa"].iloc[-1]}%",
                   xy=(0.97, 0.5), xycoords = "axes fraction",
                   va = "bottom", ha = "right", fontsize = 10, color = "blue",
                   bbox=dict(boxstyle= "round, pad=0.25", fc="lightgray", ec="blue", lw=0.8, alpha=0.75))
axes[1,0].annotate(f"Ibov: {data["Ibovespa"].iloc[-1]:.0f}",
                   xy=(0.97, 0.3), xycoords = "axes fraction",
                   va = "bottom", ha = "right", fontsize = 10, color = "blue",
                   bbox=dict(boxstyle="round,pad=0.25", fc="lightgray", ec="blue", lw=0.8, alpha=0.75))
axes[1,0].legend()
# Gráfico 4 - S&P500
axes[1,1].plot(data_perf["S&P500"], color="blue", label="S&P500")
axes[1,1].annotate(f"{data_perf["S&P500"].iloc[-1]}%",
                   xy=(0.97, 0.5), xycoords = "axes fraction",
                   va = "bottom", ha = "right", fontsize = 10, color = "blue",
                   bbox=dict(boxstyle="round,pad=0.25", fc="lightgray", ec="blue", lw=0.8, alpha=0.75))
axes[1,1].annotate(f"SP500: {data["S&P500"].iloc[-1]:.0f}",
                   xy=(0.97, 0.3), xycoords = "axes fraction",
                   va = "bottom", ha = "right", fontsize = 10, color = "blue",
                   bbox=dict(boxstyle="round,pad=0.25", fc="lightgray", ec="blue", lw=0.8, alpha=0.75))
axes[1,1].legend()
# Gráfico 5 - Dólar
axes[2,0].plot(data_perf["Dólar"], color="red", label="Dólar")
axes[2,0].annotate(f"{data_perf["Dólar"].iloc[-1]}%",
                   xy=(0.97, 0.5), xycoords = "axes fraction",
                   va = "bottom", ha = "right", fontsize = 10, color = "red",
                   bbox=dict(boxstyle="round,pad=0.25", fc="lightgray", ec="red", lw=0.8, alpha=0.75))
axes[2,0].annotate(f"USD: {data["Dólar"].iloc[-1]:.2f}",
                   xy=(0.97, 0.3), xycoords = "axes fraction",
                   va = "bottom", ha = "right", fontsize = 10, color = "red",
                   bbox=dict(boxstyle="round,pad=0.25", fc="lightgray", ec="red", lw=0.8, alpha=0.75))
axes[2,0].legend()
# Gráfico 6 - Euro
axes[2,1].plot(data_perf["Euro"], color="blue", label="Euro")
axes[2,1].annotate(f"{data_perf["Euro"].iloc[-1]}%",
                   xy=(0.97, 0.5), xycoords = "axes fraction",
                   va = "bottom", ha = "right", fontsize = 10, color = "blue",
                   bbox=dict(boxstyle="round,pad=0.25", fc="lightgray", ec="blue", lw=0.8, alpha=0.75))
axes[2,1].annotate(f"Euro: {data["Euro"].iloc[-1]:.2f}",
                   xy=(0.97, 0.3), xycoords = "axes fraction",
                   va = "bottom", ha = "right", fontsize = 10, color = "blue",
                   bbox=dict(boxstyle="round,pad=0.25", fc="lightgray", ec="blue", lw=0.8, alpha=0.75))
axes[2,1].legend()
# Gráfico 7 - Ouro
axes[3,0].plot(data_perf["Ouro"], color="blue", label="Ouro")
axes[3,0].annotate(f"{data_perf["Ouro"].iloc[-1]}%",
                   xy=(0.97, 0.5), xycoords = "axes fraction",
                   va = "bottom", ha = "right", fontsize = 10, color = "blue",
                   bbox=dict(boxstyle="round,pad=0.25", fc="lightgray", ec="blue", lw=0.8, alpha=0.75))
axes[3,0].annotate(f"Ouro: {data["Ouro"].iloc[-1]:.2f}",
                   xy=(0.97, 0.3), xycoords = "axes fraction",
                   va = "bottom", ha = "right", fontsize = 10, color = "blue",
                   bbox=dict(boxstyle="round,pad=0.25", fc="lightgray", ec="blue", lw=0.8, alpha=0.75))
axes[3,0].legend()
# Gráfico 8 - Bitcoin
axes[3,1].plot(data_perf["Bitcoin"], color="red", label="Bitcoin")
axes[3,1].annotate(f"{data_perf["Bitcoin"].iloc[-1]}%",
                   xy=(0.97, 0.5), xycoords = "axes fraction",
                   va = "bottom", ha = "right", fontsize = 10, color = "red",
                   bbox=dict(boxstyle="round,pad=0.25", fc="lightgray", ec="red", lw=0.8, alpha=0.75))
axes[3,1].annotate(f"BTC: {data["Bitcoin"].iloc[-1]:.2f}",
                   xy=(0.97, 0.3), xycoords = "axes fraction",
                   va = "bottom", ha = "right", fontsize = 10, color = "red",
                   bbox=dict(boxstyle="round,pad=0.25", fc="lightgray", ec="red", lw=0.8, alpha=0.75))
axes[3,1].legend()
# Ajustes do Gráfico
fig.suptitle(f"{start} a {end}", fontsize=30)
plt.annotate("Fonte: Yahoo Finance", xy=(0.1,0.03),
             va="bottom", ha="left", xycoords="figure fraction",
             color="black", fontsize=10)
plt.annotate("Elaborado por: Fabricio Orlandin, CFP®", xy=(0.8,0.03),
             va="bottom", ha="right", xycoords="figure fraction",
             color="black", fontsize=10)
plt.subplots_adjust(wspace=0.2, hspace=0.2)
# %%
plt.savefig("Ativos")
# %%
