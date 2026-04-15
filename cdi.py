#%%
from bcb import sgs
# %%
start = "2026-03-01"
end = "2026-03-31"
cdi = sgs.get(12,start,end)
cdi = cdi.rename(columns={"12": "CDI"})
cdi = cdi * 0.9275
#cdi = cdi.round(4)
cdi["fator"] = 1 +cdi["CDI"] / 100
cdi["acum"] = cdi["fator"].cumprod()
cdi["retorno"] = (cdi["acum"] - 1) * 100
cdi = cdi.round(6)
print(cdi)
# %%
