"""H3 refined: does the school phone ban matter more for students under high academic pressure? PISA 2022 within country:
ban x high math anxiety (ANXMAT, the only pressure-like index available to all students) and ban x 'nervous about exams' item."""
import pandas as pd, numpy as np, pyfixest as pf, pathlib
T = pathlib.Path("results/tables"); pd.set_option("display.width", 220)
st = pd.read_parquet("data/extracts/pisa2022/pisa2022_student.parquet"); sc = pd.read_parquet("data/extracts/pisa2022/pisa2022_school.parquet")[["CNT","CNTSCHID","SC190Q02JA","PRIVATESCH"]]
d = st.merge(sc, on=["CNT","CNTSCHID"]); d["ban"] = d.SC190Q02JA.map({1:1.0,2:0.0}); d = d[d.ban.notna()]
v = lambda s, lo, hi: s.where(s.between(lo, hi))
d["girl"] = (d.ST004D01T==1).astype(int); d["lonely"] = (v(d.ST034Q06TA,1,4)<=2).astype(float).where(v(d.ST034Q06TA,1,4).notna()); d["nervous_nodevice"] = (v(d.ST322Q07JA,1,5)>=4).astype(float).where(v(d.ST322Q07JA,1,5).notna())
d["belong_idx"] = d.BELONG.where(d.BELONG.between(-5,5)); d["lifesat"] = d.LIFESAT.where(d.LIFESAT.between(-5,5)); d["escs"] = d.ESCS.where(d.ESCS.between(-6,6)); d["wt"] = d.W_FSTUWT; d["sch"] = d.CNT+"_"+d.CNTSCHID.astype(str)
d["anxmat"] = d.ANXMAT.where(d.ANXMAT.between(-5,5)); d["hi_anx"] = (d.anxmat > d.groupby("CNT").anxmat.transform("median")).astype(float).where(d.anxmat.notna())
d["school_anx"] = d["hi_anx"]; d["phone_school_daily"] = (v(d.IC170Q02JA,1,5)>=4).astype(float).where(v(d.IC170Q02JA,1,6).notna()); d.loc[d.IC170Q02JA==6,"phone_school_daily"] = 0.0
print("students with ANXMAT:", d.anxmat.notna().sum())
rows = []
for y, lab, scale in [("lonely","Lonely at school",100),("nervous_nodevice","Nervous without device",100),("belong_idx","Belonging index",100),("lifesat","Life satisfaction index",100)]:
    for sx, sl in [(1,"girls"),(0,"boys")]:
        dd = d[(d.girl==sx)&d[y].notna()&d.hi_anx.notna()&d.escs.notna()]
        m = pf.feols(f"{y} ~ ban + hi_anx + ban:hi_anx + escs + C(GRADE) | CNT", data=dd, weights="wt", vcov={"CRV1":"sch"})
        rows.append(dict(outcome=lab, sex=sl, ban_lowanx=scale*m.coef()["ban"], se_low=scale*m.se()["ban"], ban_x_hianx=scale*m.coef()["ban:hi_anx"], se_int=scale*m.se()["ban:hi_anx"], hianx_main=scale*m.coef()["hi_anx"], n=m._N))
R = pd.DataFrame(rows); R["ban_hianx"] = R.ban_lowanx + R.ban_x_hianx; R.to_csv(T/"pisa_ban_x_pressure.csv", index=False); print(R.round(2).to_string())
# also: do high-anxiety students use phones at school more, and does the ban reduce their use more?
dd = d[d.phone_school_daily.notna()&d.hi_anx.notna()&d.escs.notna()]
m = pf.feols("phone_school_daily ~ ban + hi_anx + ban:hi_anx + escs + girl + C(GRADE) | CNT", data=dd, weights="wt", vcov={"CRV1":"sch"}); print("\nphone use at school: ban", round(100*m.coef()["ban"],2), "hi_anx", round(100*m.coef()["hi_anx"],2), "ban x hi_anx", round(100*m.coef()["ban:hi_anx"],2), "(se", round(100*m.se()["ban:hi_anx"],2), ")")
