"""DHS-8 Nepal 2022: self-reported PHQ-9 / GAD-7 (women 15-49, mental-health subsample) vs own internet frequency and smartphone; cluster FE. Kenya 2022: diagnosis items."""
import pandas as pd, numpy as np, pyfixest as pf, pathlib
T = pathlib.Path("results/tables"); pd.set_option("display.width", 200)
d = pd.read_parquet("data/extracts/dhs/np2022ir_slim.parquet"); d = d[d.DEPRESSIONSCORE.le(27)&d.GADSCORE.le(21)].copy()
d["w"] = d.PERWEIGHT/1e6; d["phq10"] = (d.DEPRESSIONSCORE>=10).astype(float); d["gad10"] = (d.GADSCORE>=10).astype(float); d["phq"] = d.DEPRESSIONSCORE.astype(float); d["gad"] = d.GADSCORE.astype(float)
d["net_daily"] = (d.INTERNETMO==3).astype(float); d["net_weekly"] = d.INTERNETMO.ge(2).astype(float); d["smart"] = (d.CELLPHONESMART==1).astype(float); d["urban"] = (d.URBAN==1).astype(int); d["cl"] = d.CLUSTERNO
d["agegrp"] = pd.cut(d.AGE, [14,19,24,49], labels=["15-19","20-24","25-49"])
print("MH-module women:", len(d)); print(d.groupby("agegrp", observed=True).apply(lambda g: pd.Series({"n":len(g), "phq10":100*np.average(g.phq10, weights=g.w), "gad10":100*np.average(g.gad10, weights=g.w), "net_daily":100*np.average(g.net_daily, weights=g.w), "smart":100*np.average(g.smart, weights=g.w)}), include_groups=False).round(1).to_string())
rows = []
for ag in ["15-19","20-24","25-49"]:
    s = d[d.agegrp==ag]
    for x in ["net_daily","net_weekly","smart"]:
        for y in ["phq10","gad10","phq","gad"]:
            for fe, lab in [("urban","none"),("cl","cluster FE")]:
                f = f"{y} ~ {x} + C(WEALTHQ) + C(EDUCLVL) + C(AGE)" + (" | cl" if fe=="cl" else " + urban")
                m = pf.feols(f, data=s, weights="w", vcov={"CRV1":"cl"}); rows.append(dict(ages=ag, exposure=x, outcome=y, fe=lab, coef=m.coef()[x]*(100 if y in ("phq10","gad10") else 1), se=m.se()[x]*(100 if y in ("phq10","gad10") else 1), n=m._N))
R = pd.DataFrame(rows); R.to_csv(T/"dhs_nepal_2022.csv", index=False)
print(R[R.fe=="cluster FE"].pivot_table(index=["ages","exposure"], columns="outcome", values=["coef","se"]).round(2).to_string())
k = pd.read_parquet("data/extracts/dhs/ke2022ir_slim.parquet"); k = k[k.DEPRESSIONDIAG.isin([0,1])].copy(); k["w"] = k.PERWEIGHT/1e6; k["smart"] = (k.CELLPHONESMART==1).astype(float); k["cl"] = k.CLUSTERNO; k["agegrp"] = pd.cut(k.AGE, [14,19,24,49], labels=["15-19","20-24","25-49"])
print("\nKenya 2022 (diagnosed depression/anxiety, women with the item):", len(k)); print(k.groupby("agegrp", observed=True).apply(lambda g: pd.Series({"n":len(g), "depdiag":100*np.average(g.DEPRESSIONDIAG, weights=g.w), "anxdiag":100*np.average(g.ANXIETYDIAG.clip(0,1), weights=g.w), "smart":100*np.average(g.smart, weights=g.w)}), include_groups=False).round(1).to_string())
for ag in ["15-19","20-24"]:
    s = k[k.agegrp==ag]; m = pf.feols("DEPRESSIONDIAG ~ smart + C(WEALTHQ) + C(EDUCLVL) + C(AGE) | cl", data=s, weights="w", vcov={"CRV1":"cl"}); print(f"  Kenya {ag}: dep diag on smartphone, cluster FE: {100*m.coef()['smart']:+.2f} pp (se {100*m.se()['smart']:.2f}) n={m._N}")
