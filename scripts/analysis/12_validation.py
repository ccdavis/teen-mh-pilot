"""Step 3 validation gates: (a) national timing ACS vs NSDUH MDE vs NHANES PHQ-9 vs YRBS; (b) state NSDUH MDE vs ACS 12-17; (c) sex pattern in YRBS/NHANES vs ACS."""
import pandas as pd, numpy as np, pathlib, pyfixest as pf
ROOT = pathlib.Path(__file__).resolve().parents[2]; T = ROOT/"results/tables"; EXT = ROOT/"data/external"
pd.set_option("display.width", 220)
rows = []
# --- NSDUH SAE
d = pd.read_sas(EXT/"nsduh/sae-datasets/NSDUH_99_19_state_saes_final.sas7bdat", format="sas7bdat", encoding="latin1")
m = d[(d.outcome=="MDE")&(d.agegrp==1)&(~d.pyearnm.str.contains("published"))].copy()
m["year"] = m.pyearnm.str[:4].astype(int) + 0.5  # midpoint of 2-yr period
nat = m[m.area==0]; rows += [dict(source="NSDUH MDE 12-17", year=r.year, sex="all", value=100*r.BSAE, se=100*r.ste_sae) for r in nat.itertuples()]
d2 = pd.read_sas(EXT/"nsduh/sae-datasets/state_saes_final_2124.sas7bdat", format="sas7bdat", encoding="latin1")
m2 = d2[(d2.outcome=="MDEYR")&(d2.agegrp==1)&(d2.pyearnm.str.contains("-"))].copy(); m2["year"] = m2.pyearnm.str[:4].astype(int)+0.5
rows += [dict(source="NSDUH MDE 12-17 (2021+ mode)", year=r.year, sex="all", value=100*r.BSAE, se=100*r.ste_sae) for r in m2[m2.area==0].itertuples()]
st = m[m.area==2][["state","year","BSAE","ste_sae"]].rename(columns={"state":"statefip","BSAE":"nsduh","ste_sae":"nsduh_se"})
# --- NHANES PHQ-9 >= 10, ages 18-24, by sex (the public-use NHANES files carry the PHQ-9 only for adults)
cyc = {"D":(2005,"2005-2006"),"E":(2007,"2007-2008"),"F":(2009,"2009-2010"),"G":(2011,"2011-2012"),"H":(2013,"2013-2014"),"I":(2015,"2015-2016"),"J":(2017,"2017-2018"),"L":(2021,"2021-2023")}
nh = []
for k,(y0,lab) in cyc.items():
    dpq = pd.read_sas(EXT/f"nhanes/DPQ_{k}.xpt" if (EXT/f"nhanes/DPQ_{k}.xpt").exists() else next((EXT/"nhanes").glob(f"*DPQ_{k}*")), format="xport")
    demo = pd.read_sas(next((EXT/"nhanes").glob(f"*DEMO_{k}*")), format="xport")
    x = dpq.merge(demo[["SEQN","RIAGENDR","RIDAGEYR","WTMEC2YR"]], on="SEQN"); x = x[x.RIDAGEYR.between(18,24)]
    items = [f"DPQ0{i}0" for i in range(1,10)]; v = x[items].where(x[items] <= 3); x = x[v.notna().all(axis=1)]; x["phq"] = v.sum(axis=1)
    x["dep"] = (x.phq >= 10).astype(float); x["yr"] = y0 + 0.5 if k != "L" else 2022
    for sx, lab2 in [(1,"boys"),(2,"girls"),(None,"all")]:
        s = x if sx is None else x[x.RIAGENDR==sx]; w = s.WTMEC2YR; p = np.average(s.dep, weights=w); neff = w.sum()**2/(w**2).sum()
        rows.append(dict(source="NHANES PHQ-9 ≥10, 18-24", year=s.yr.iloc[0], sex=lab2, value=100*p, se=100*np.sqrt(p*(1-p)/neff), n=len(s)))
# --- YRBS national, fixed width
# The national combined (SADC) file: the 2025 release (1991-2025, 900-character records; sad/hopeless q26 at column 266 and considered
# suicide q27 at 267) is used when present, otherwise the 2023 release (776-character records; q26 at 281, q27 at 282). Positions from the
# SADC SAS input programs; see data/external/yrbs/README.md.
names = ["sitecode","year","weight","age","sex","grade","q26","q27"]
REL = {"sadc_2025": [(0,5),(113,121),(124,134),(158,161),(161,164),(164,167),(265,266),(266,267)],
       "sadc_2023": [(0,5),(113,121),(124,134),(158,161),(161,164),(164,167),(280,281),(281,282)]}
def read_yrbs(release):
    path = EXT/f"yrbs/{release}/{release}_national.dat"
    y = pd.read_fwf(path, colspecs=REL[release], names=names, dtype={"sitecode":str,"age":str,"sex":str,"grade":str,"q26":str,"q27":str}, na_values=[" ",""]); return y
rel = "sadc_2025" if (EXT/"yrbs/sadc_2025/sadc_2025_national.dat").exists() else "sadc_2023"; print("YRBS national release:", rel)
yn = read_yrbs(rel)
yn["sad"] = yn.q26.map({"1":1.0,"2":0.0}); yn["consider"] = yn.q27.map({"1":1.0,"2":0.0})
def wprop(s, col):
    s = s[s[col].notna() & s.weight.notna()]
    if len(s) < 50: return np.nan, np.nan, len(s)
    w = s.weight; p = np.average(s[col], weights=w); neff = w.sum()**2/(w**2).sum(); pc = min(max(p, 0.5/len(s)), 1-0.5/len(s))
    return p, np.sqrt(pc*(1-pc)/neff), len(s)
for (yr, sx), s in yn.groupby(["year","sex"]):
    lab = {"1":"girls","2":"boys"}.get(str(sx).strip());
    if lab is None: continue
    for col, nm in [("sad","YRBS sad/hopeless"),("consider","YRBS considered suicide")]:
        p, se, n = wprop(s, col)
        if not np.isnan(p): rows.append(dict(source=nm, year=yr, sex=lab, value=100*p, se=100*se, n=n))
for yr, s in yn.groupby("year"):
    for col, nm in [("sad","YRBS sad/hopeless"),("consider","YRBS considered suicide")]:
        p, se, n = wprop(s, col)
        if not np.isnan(p): rows.append(dict(source=nm, year=yr, sex="all", value=100*p, se=100*se, n=n))
# --- ACS national
a = pd.read_csv(T/"acs_national_year_sex_1217.csv"); a = a[a.year>=2008]
rows += [dict(source="ACS cognitive difficulty 12-17", year=r.year, sex={1:"boys",2:"girls"}[r.sex], value=100*r.rate, se=100*r.se) for r in a.itertuples()]
a2 = pd.read_csv(T/"acs_national_year_age.csv"); a2 = a2[(a2.year>=2008)&(a2.agegrp.isin(["12-14","15-17"]))]
a2 = a2.groupby("year").apply(lambda g: pd.Series({"value":100*np.average(g.rate, weights=g["pop"]), "se":100*np.sqrt(np.sum((g["pop"]/g["pop"].sum())**2*g.se**2))}), include_groups=False).reset_index()
rows += [dict(source="ACS cognitive difficulty 12-17", year=r.year, sex="all", value=r.value, se=r.se) for r in a2.itertuples()]
V = pd.DataFrame(rows); V.to_csv(T/"validation_national_timing.csv", index=False)
piv = V[V.sex=="all"].pivot_table(index="year", columns="source", values="value"); print(piv.round(2).to_string())
# sex pattern summary
def chg(src, sex, y0, y1):
    s = V[(V.source==src)&(V.sex==sex)]; b = s[s.year.between(*y0)].value.mean(); e = s[s.year.between(*y1)].value.mean(); return b, e, 100*(e/b-1)
print("\nSex pattern, relative change 2009-2011 -> 2017-2019:")
for src in ["ACS cognitive difficulty 12-17","YRBS sad/hopeless","YRBS considered suicide","NHANES PHQ-9 ≥10, 18-24"]:
    for sex in ["boys","girls"]:
        b,e,r = chg(src, sex, (2009,2011.9), (2017,2019.9)); print(f"  {src:35s} {sex:5s} {b:5.2f} -> {e:5.2f}  ({r:+.0f}%)")
# --- state NSDUH vs ACS: pooled two-year ACS to match NSDUH periods
s = pd.read_csv(T/"acs_state_year_1217.csv")
rows2 = []
for (sf, yr), g in st.groupby(["statefip","year"]):
    y0 = int(yr-0.5); aa = s[(s.statefip==sf)&(s.year.isin([y0,y0+1]))]
    if len(aa)<2: continue
    w = aa["pop"]/aa["pop"].sum(); rows2.append(dict(statefip=sf, year=yr, nsduh=100*g.nsduh.iloc[0], nsduh_se=100*g.nsduh_se.iloc[0], acs=100*np.sum(w*aa.rate), acs_se=100*np.sqrt(np.sum(w**2*aa.se**2))))
P = pd.DataFrame(rows2); P.to_csv(T/"validation_state_nsduh_vs_acs.csv", index=False)
P["wt"] = 1/(P.nsduh_se**2)
print("\nState x period panel:", P.shape, "periods", sorted(P.year.unique()))
print("cross-section (pooled):", pf.feols("nsduh ~ acs", data=P, weights="wt", vcov={"CRV1":"statefip"}).summary())
print("within-state (state + period FE):"); print(pf.feols("nsduh ~ acs | statefip + year", data=P, weights="wt", vcov={"CRV1":"statefip"}).summary())
# two NSDUH two-year periods at each end (2008-09 and 2009-10 vs 2017-18 and 2018-19), so the ACS and NSDUH windows cover the same years
b = P[P.year.between(2008.4,2009.6)].groupby("statefip")[["nsduh","acs"]].mean(); e = P[P.year.between(2017.4,2018.6)].groupby("statefip")[["nsduh","acs"]].mean()
C = (e-b).dropna(); C.columns=["d_nsduh","d_acs"]; print("\nlong change 2008-10 -> 2017-19 across states: corr =", round(C.corr().iloc[0,1],3)); print(pf.feols("d_nsduh ~ d_acs", data=C.reset_index(), vcov="hetero").summary())
C.reset_index().to_csv(T/"validation_state_change.csv", index=False)
