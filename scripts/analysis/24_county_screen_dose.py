"""County-level social-media / screen-time items vs sadness in WA (2023, 2025) and ME (2017-2021)."""
import pandas as pd, pyfixest as pf, pathlib
ROOT = pathlib.Path(__file__).resolve().parents[2]; T = ROOT/"results/tables"; S = pd.read_csv(T/"state_survey_county_series.csv"); S = S[S.sex=="all"]
W = S.pivot_table(index=["state","fips","year"], columns="item", values="value").reset_index(); rows = []
for st, x in [("WA","social_media_daily"),("WA","screen_time_3plus"),("ME","screen_time_3plus")]:
    for y in ["sad_hopeless","considered_suicide"]:
        d = W[(W.state==st)&W[x].notna()&W[y].notna()]
        m = pf.feols(f"{y} ~ {x} | year", data=d, vcov="hetero"); m2 = pf.feols(f"{y} ~ {x} | fips + year", data=d, vcov="hetero")
        rows.append(dict(state=st, dose=x, outcome=y, n=len(d), years=str(sorted(d.year.unique())), cross_coef=m.coef().iloc[0], cross_se=m.se().iloc[0], within_coef=m2.coef().iloc[0], within_se=m2.se().iloc[0]))
pd.DataFrame(rows).to_csv(T/"county_screen_dose.csv", index=False); print(pd.DataFrame(rows).round(2).to_string())
