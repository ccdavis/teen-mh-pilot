"""Fetch World Bank WDI ICT indicators (internet users %, mobile subscriptions per 100, GDP per capita PPP, population), 2000-2024, all economies."""
import requests, pandas as pd, time, pathlib
OUT = pathlib.Path(__file__).resolve().parents[2]/"data/compiled/wdi"; OUT.mkdir(parents=True, exist_ok=True)
inds = {"IT.NET.USER.ZS":"internet_users_pct","IT.CEL.SETS.P2":"mobile_subs_per100","NY.GDP.PCAP.PP.KD":"gdp_pc_ppp","SP.POP.TOTL":"pop"}
frames = []
for code, name in inds.items():
    rows = []; page = 1
    while True:
        j = requests.get(f"https://api.worldbank.org/v2/country/all/indicator/{code}", params={"format":"json","per_page":20000,"page":page,"date":"2000:2024"}, timeout=60).json()
        rows += [dict(iso3=x["countryiso3code"], country=x["country"]["value"], year=int(x["date"]), value=x["value"]) for x in j[1] if x["countryiso3code"]]
        if page >= j[0]["pages"]: break
        page += 1; time.sleep(0.3)
    frames.append(pd.DataFrame(rows).rename(columns={"value": name}).set_index(["iso3","country","year"]))
pd.concat(frames, axis=1).reset_index().to_csv(OUT/"wdi_ict_2000_2024.csv", index=False); print("written", OUT/"wdi_ict_2000_2024.csv")
