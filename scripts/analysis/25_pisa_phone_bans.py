"""PISA 2022: school-level phone ban (SC190Q02JA) vs student well-being and in-school phone use, within country."""
import pandas as pd, numpy as np, pyfixest as pf, pathlib
ROOT = pathlib.Path(__file__).resolve().parents[2]
T = ROOT/"results/tables"; pd.set_option("display.width", 220)
st = pd.read_parquet(ROOT/"data/extracts/pisa2022/pisa2022_student.parquet"); sc = pd.read_parquet(ROOT/"data/extracts/pisa2022/pisa2022_school.parquet")
sc = sc[["CNT","CNTSCHID","SC190Q02JA","PRIVATESCH"]].copy(); sc["ban"] = sc.SC190Q02JA.map({1:1.0, 2:0.0})  # SC190Q02JA: 1 = yes (phones banned on school grounds), 2 = no
d = st.merge(sc, on=["CNT","CNTSCHID"], how="inner"); d = d[d.ban.notna()]
v = lambda s, lo, hi: s.where(s.between(lo, hi))
d["girl"] = (d.ST004D01T==1).astype(int); d["lonely"] = (v(d.ST034Q06TA,1,4) <= 2).astype(float).where(v(d.ST034Q06TA,1,4).notna()); d["belong"] = (v(d.ST034Q03TA,1,4) <= 2).astype(float).where(v(d.ST034Q03TA,1,4).notna())
d["nervous_nodevice"] = (v(d.ST322Q07JA,1,5) >= 4).astype(float).where(v(d.ST322Q07JA,1,5).notna()); d["distracted"] = (v(d.ST273Q06JA,1,4) <= 2).astype(float).where(v(d.ST273Q06JA,1,4).notna())  # ST273Q06JA: 1 every lesson, 2 most lessons, 3 some lessons, 4 never or almost never
d["phone_school_daily"] = (v(d.IC170Q02JA,1,5) >= 4).astype(float).where(v(d.IC170Q02JA,1,6).notna()); d.loc[d.IC170Q02JA==6, "phone_school_daily"] = 0.0
d["leisure_school_1h"] = (v(d.ST326Q04JA,1,9) >= 3).astype(float).where(v(d.ST326Q04JA,1,9).notna()); d["leisure_home_3h"] = (v(d.ST326Q05JA,1,9) >= 5).astype(float).where(v(d.ST326Q05JA,1,9).notna())
d["lifesat"] = d.LIFESAT.where(d.LIFESAT.between(-5,5)); d["belong_idx"] = d.BELONG.where(d.BELONG.between(-5,5)); d["expwb"] = d.EXPWB.where(d.EXPWB.between(-5,5))
d["stress"] = d.STRESAGR.where(d.STRESAGR.between(-5,5))
d["escs"] = d.ESCS.where(d.ESCS.between(-6,6)); # PRIVATESCH is a string column in the SPSS file (public/private/missing/invalid); schools with unknown type get 0 and the ban coefficient is conditional on the known-type indicator
d["private"] = d.PRIVATESCH.astype(str).str.strip().str.lower().map({"private": 1.0, "public": 0.0}).fillna(0.0)
d["wt"] = d.W_FSTUWT; d["sch"] = d.CNT+"_"+d.CNTSCHID.astype(str)
print("students", len(d), "schools", d.sch.nunique(), "countries", d.CNT.nunique(), "ban share (students):", round(d.ban.mean(),3))
# country-level ban share vs mean outcomes (descriptive)
def wavg(x, w):
    m = x.notna() & w.notna(); return np.average(x[m], weights=w[m]) if w[m].sum() > 0 else np.nan
cl = d.groupby("CNT").apply(lambda g: pd.Series({"ban": wavg(g.ban, g.wt), "lonely": 100*wavg(g.lonely, g.wt), "phone_daily": 100*wavg(g.phone_school_daily, g.wt)}), include_groups=False).reset_index(); cl.to_csv(T/"pisa_country_ban_summary.csv", index=False)
rows = []
outs = {"phone_school_daily":"Uses smartphone at school daily+ (ICT module)","leisure_school_1h":"Leisure digital use at school >1 h/day","leisure_home_3h":"Leisure digital use after school >3 h/day (placebo)","distracted":"Distracted by digital devices in most/every lesson","nervous_nodevice":"Nervous/anxious without device (more than half the time)","lonely":"Feels lonely at school (agree)","belong":"Feels they belong at school (agree)","belong_idx":"Belonging index (SD units)","lifesat":"Life satisfaction index, WB module (SD units)","expwb":"Experienced well-being yesterday, WB module (SD units)","stress":"Stress resistance index (SD units)"}
for y, lab in outs.items():
    for sx, sl in [(None,"all"),(1,"girls"),(0,"boys")]:
        dd = d if sx is None else d[d.girl==sx]; dd = dd[dd[y].notna()&dd.escs.notna()]
        if len(dd) < 5000: continue
        m = pf.feols(f"{y} ~ ban + escs + girl + private + C(GRADE) | CNT", data=dd, weights="wt", vcov={"CRV1":"sch"})
        scale = 100 if dd[y].dropna().isin([0,1]).all() else 1
        rows.append(dict(outcome=lab, sex=sl, coef=scale*m.coef()["ban"], se=scale*m.se()["ban"], n=m._N, countries=dd.CNT.nunique(), mean=scale*np.average(dd[y], weights=dd.wt), unit="pp" if scale==100 else "SD"))
R = pd.DataFrame(rows); R.to_csv(T/"pisa_phone_ban_results.csv", index=False)
print(R.pivot_table(index="outcome", columns="sex", values=["coef","se"], sort=False).round(3).to_string()); print(R[R.sex=="all"][["outcome","n","countries","mean","unit"]].to_string())
