"""Pilot step 9: IPUMS International census arm. Kenya 2009/2019, Mexico 2010/2020.
Outcome: ages 12-17 difficulty remembering/concentrating (2019/2020 WG item: any difficulty; a lot/cannot), and 2009/2010 mental-disability item.
Dose: 2019 Kenya per-person phone ownership / internet use (ages 12-17 and 18-34); household cell/internet in all rounds.
Unit: GEO2 (district / municipality). Cross-sectional dose-response with urban share control; sex and age gradient by dose tercile.
Caveat: wording differs between rounds, so change-over-time comparisons are descriptive only."""
import duckdb, pandas as pd, numpy as np, pyfixest as pf, pathlib
OUT = pathlib.Path("results/tables"); pd.set_option("display.width", 220)
con = duckdb.connect()
spec = {
 "ke2019a": dict(any="KE2019A_0450 in (2,3,4)", severe="KE2019A_0450 in (3,4)", valid="KE2019A_0450 in (1,2,3,4)", phone="KE2019A_0469=1", phone_valid="KE2019A_0469 in (1,2)", net="KE2019A_0471=1", net_valid="KE2019A_0471 in (1,2)", hhcell="CELL_H=1", hhnet="INTERNET_H=1"),
 "ke2009a": dict(any="DISMNTL=1", severe="DISMNTL=1", valid="DISMNTL in (1,2)", phone="false", phone_valid="false", net="KE2009A_0443 in (1,2,3,4)", net_valid="KE2009A_0443 in (1,2,3,4,5)", hhcell="CELL_H=1", hhnet="false"),
 "mx2020a": dict(any="MX2020A_0421 in (2,3,4)", severe="MX2020A_0421 in (3,4)", valid="MX2020A_0421 in (1,2,3,4)", phone="false", phone_valid="false", net="false", net_valid="false", hhcell="CELL_H=1", hhnet="INTERNET_H=1"),
 "mx2010a": dict(any="DISMNTL=1", severe="DISMNTL=1", valid="DISMNTL in (1,2)", phone="false", phone_valid="false", net="false", net_valid="false", hhcell="CELL_H=1", hhnet="INTERNET_H=1"),
}
frames = []
for s, c in spec.items():
    q = f"""select '{s}' as smp, GEO2 as geo2, SEX as sex,
      case when AGE between 5 and 11 then '05-11' when AGE between 12 and 14 then '12-14' when AGE between 15 and 17 then '15-17' when AGE between 18 and 24 then '18-24'
           when AGE between 25 and 49 then '25-49' when AGE >= 65 then '65+' else 'other' end agegrp,
      count(*) n, sum(PERWT) pop,
      sum(case when {c['valid']} then PERWT end) pop_valid, sum(case when {c['any']} then PERWT end) dif_any, sum(case when {c['severe']} then PERWT end) dif_sev,
      sum(case when {c['phone_valid']} then PERWT end) phone_valid, sum(case when {c['phone']} then PERWT end) phone,
      sum(case when {c['net_valid']} then PERWT end) net_valid, sum(case when {c['net']} then PERWT end) net,
      sum(case when {c['hhcell']} then PERWT end) hhcell, sum(case when {c['hhnet']} then PERWT end) hhnet, sum(case when URBAN_H=2 then PERWT end) urban
      from read_parquet('data/extracts/ipumsi/{s}_slim.parquet') group by 1,2,3,4"""
    frames.append(con.sql(q).df())
d = pd.concat(frames); d.to_csv(OUT/"ipumsi_geo2_cells.csv", index=False)
# national rates by age/sex
nat = d.groupby(["smp","agegrp","sex"]).sum(numeric_only=True); nat["any_pct"] = 100*nat.dif_any/nat.pop_valid; nat["sev_pct"] = 100*nat.dif_sev/nat.pop_valid
nat["phone_pct"] = 100*nat.phone/nat.phone_valid; nat["net_pct"] = 100*nat.net/nat.net_valid; nat["hhcell_pct"] = 100*nat.hhcell/nat["pop"]; nat["hhnet_pct"] = 100*nat.hhnet/nat["pop"]
print(nat[["any_pct","sev_pct","phone_pct","net_pct","hhcell_pct","hhnet_pct"]].round(2).to_string()); nat.to_csv(OUT/"ipumsi_national_age_sex.csv")
# district-level cross-section, ages 12-17, latest round
for s, dose in [("ke2019a","phone_pct"),("ke2019a","net_pct"),("ke2019a","hhcell_pct"),("mx2020a","hhnet_pct"),("mx2020a","hhcell_pct")]:
    t = d[(d["smp"]==s)&(d.agegrp.isin(["12-14","15-17"]))].groupby(["geo2","sex"]).sum(numeric_only=True).reset_index()
    t["any_pct"] = 100*t.dif_any/t.pop_valid; t["sev_pct"] = 100*t.dif_sev/t.pop_valid; t["urban_pct"] = 100*t.urban/t["pop"]
    t["phone_pct"] = 100*t.phone/t.phone_valid; t["net_pct"] = 100*t.net/t.net_valid; t["hhcell_pct"] = 100*t.hhcell/t["pop"]; t["hhnet_pct"] = 100*t.hhnet/t["pop"]
    t = t[t.n >= 200]
    # adult dose in same district (18-34) to instrument teen access? just report both
    for y in ["any_pct","sev_pct"]:
        m = pf.feols(f"{y} ~ {dose} + urban_pct | sex", data=t, weights="n", vcov="hetero")
        print(f"{s} {y} on {dose} (+urban, sex FE, n={len(t)} district-sex cells): coef={m.coef()[dose]:.4f} se={m.se()[dose]:.4f}  [dose mean {t[dose].mean():.1f}, sd {t[dose].std():.1f}; outcome mean {t[y].mean():.2f}]")
    t.assign(dose=dose).to_csv(OUT/f"ipumsi_{s}_geo2_1217_{dose}.csv", index=False)
