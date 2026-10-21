#%% Biblioteas
from bcb import sgs
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
# %% Montando Dataframe
windows = [12, 24, 36, 48, 60]
cdi = sgs.get(4392, "1994-01-01", "2026-04-01")
cdi["Month"] = ((1 + cdi / 100) ** (20 / 252) - 1) * 100
ipca = sgs.get(433)
ipca = ipca.rename(columns = {"433": "Month"})
ipca["12m"] = sgs.get(13522)
df = pd.DataFrame()
for w in windows:
    if w == 12:
        df[f"CDI{w}m"] = cdi["Month"].rolling(window=w).apply(
            lambda x:(np.prod(1 + x / 100) - 1) * 100
        ).round(2)
        df[f"IPCA{w}m"] = sgs.get(13522).round(2)
    else:
        df[f"CDI{w}m"] = cdi["Month"].rolling(window=w).apply(
            lambda x:(np.prod(1 + x / 100) - 1) * 100
        ).round(2)
        df[f"IPCA{w}m"] = ipca["Month"].rolling(window=w).apply(
            lambda x:(np.prod(1 + x / 100) - 1) * 100
        ).round(2)
print(df)
# %% Juro Real
for r in windows:
    juro_real = f"Juro Real {r}m"
    df[juro_real] = ((1 + df[f"CDI{r}m"] / 100) / (1 + df[f"IPCA{r}m"] / 100) - 1) * 100
print(df)
# %% calculando a media dos últimos 5 anos
media_df = dict()
for m in windows:
    col = f"Juro Real {m}m"
    media_df[f"{m}m"] = float(np.mean(df[col].iloc[-60:]).round(2))
print(media_df)
# %% Gráficos
fig, axes = plt.subplots(figsize=(18,12), nrows=5, ncols =1)
janelas = ["Juro Real 12m",
           "Juro Real 24m",
           "Juro Real 36m",
           "Juro Real 48m", 
           "Juro Real 60m"
]
for p, j in enumerate (janelas):
    axes[p].plot(df[f"{j}"], color = "red")
    axes[p].set_title(f"{j}", loc="left")
for w, m in enumerate(media_df):
    axes[w].axhline(y = media_df[m], linestyle = "--", color = "black")
#criar annotate para os juros reais 

#criar annotate para a média dos últimos 5 anos

plt.tight_layout()
plt.show()

# %%
