"""Harmonize the PISA 2012, 2015, 2018 and 2022 student extracts into one stacked student file for scripts/analysis/32_pisa_panel.py.
Run from the repository root after extract_2012.py, extract_sav.py 2015, extract_sav.py 2018 (and scripts/download/pisa2022/*):
  uv run python scripts/download/pisa_panel/build_panel.py
Inputs: data/extracts/pisa_panel/pisa{2012,2015,2018}_{student,school}.parquet, data/extracts/pisa2022/pisa2022_{student,school}.parquet.
Outputs: data/extracts/pisa_panel/pisa_panel_student.parquet (one row per student, harmonized columns; see CROSSWALK below and
notes/pisa_panel.md) and data/extracts/pisa_panel/pisa_panel_items.csv (source item, wording and value labels per wave).
Hours categories: 2012-2018 'Internet use on a typical weekday at school / outside school' (IC05/IC06 in 2012, IC005/IC006 in 2015/2018;
identical 7 categories: no time, 1-30 min, 31-60 min, 1-2 h, 2-4 h, 4-6 h, >6 h) are mapped to midpoints 0, .25, .75, 1.5, 3, 5, 7 hours.
2022 asked hours/day on digital resources separately for learning and leisure, at school and before/after school (ST326Q01/Q04 and
Q02/Q05; 9 categories: none, <=1 h, 1-2, 2-3, 3-4, 4-5, 5-6, 6-7, >7 h -> midpoints 0, .5, 1.5, ..., 6.5, 7.5); the harmonized 2022 hours
are the sum of the learning and leisure midpoints (total device hours), with leisure-only versions kept as *_leis. Bands: none, <=1 h,
1-2 h, 2-4 h, 4-6 h, >6 h apply to the category (2012-18) or to the summed midpoints (2022).
"""
import pathlib, pandas as pd, numpy as np
ROOT = pathlib.Path(__file__).resolve().parents[3]; EX = ROOT/"data/extracts/pisa_panel"; EX22 = ROOT/"data/extracts/pisa2022"
MID7 = {1: 0.0, 2: 0.25, 3: 0.75, 4: 1.5, 5: 3.0, 6: 5.0, 7: 7.0}
MID9 = {1: 0.0, 2: 0.5, 3: 1.5, 4: 2.5, 5: 3.5, 6: 4.5, 7: 5.5, 8: 6.5, 9: 7.5}
BAND7 = {1: "none", 2: "<=1 h", 3: "<=1 h", 4: "1-2 h", 5: "2-4 h", 6: "4-6 h", 7: ">6 h"}
BANDS = ["none", "<=1 h", "1-2 h", "2-4 h", "4-6 h", ">6 h"]

def rng(s, lo, hi):
    s = pd.to_numeric(s, errors="coerce").astype("float64"); return s.where(s.between(lo, hi))
def agree(s):  # 1 strongly agree, 2 agree, 3 disagree, 4 strongly disagree -> 1 if agree/strongly agree
    s = rng(s, 1, 4); return (s <= 2).astype(float).where(s.notna())
def band_hours(h):
    h = pd.to_numeric(h, errors="coerce")
    return pd.cut(h, [-0.01, 0.0, 1.0, 2.0, 4.0, 6.0, 99], labels=BANDS).astype("object").where(h.notna())
def finish(d, year):
    d["year"] = year; d["oecd"] = (pd.to_numeric(d["oecd"], errors="coerce") == 1).astype(int)
    d["sch"] = d["CNT"].astype(str) + "_" + d["schid"].astype(str); d["stu"] = d["sch"] + "_" + d["stuid"].astype(str)
    d["lifesat_low"] = (d["lifesat"] <= 4).astype(float).where(d["lifesat"].notna()); d["lifesat_high"] = (d["lifesat"] >= 9).astype(float).where(d["lifesat"].notna())
    d["sch_1h"] = (d["hrs_school"] > 1).astype(float).where(d["hrs_school"].notna()); d["out_2h"] = (d["hrs_out"] > 2).astype(float).where(d["hrs_out"].notna()); d["out_4h"] = (d["hrs_out"] > 4).astype(float).where(d["hrs_out"].notna())
    d["band_school"] = band_hours(d["hrs_school"]); d["band_out"] = band_hours(d["hrs_out"])
    cov = d.groupby("CNT", observed=True)["hrs_out"].transform(lambda s: s.notna().mean()); d["ict_country"] = (cov > 0.5).astype(int)
    keep = ["year", "CNT", "oecd", "sch", "stu", "girl", "grade", "age", "escs", "immig", "wt", "private", "ict_country", "lonely", "outsider", "belong", "awkward", "belong_idx", "lifesat", "lifesat_low", "lifesat_high",
            "hrs_school", "hrs_out", "hrs_wkend", "hrs_school_leis", "hrs_out_leis", "sch_1h", "out_2h", "out_4h", "band_school", "band_out", "first_net_lt7", "first_net_lt10", "socnet_daily", "chat_school_daily", "phone_school_daily",
            "anxtest", "anx1", "anx2", "anx3", "anx4", "anx5", "anxmat", "sch_policy", "ban"]
    for k in keep:
        if k not in d: d[k] = np.nan
    return d[keep]

def wave2012():
    d = pd.read_parquet(EX/"pisa2012_student.parquet"); s = pd.read_parquet(EX/"pisa2012_school.parquet")[["CNT", "SCHOOLID", "SC01Q01"]]
    d = d.merge(s, on=["CNT", "SCHOOLID"], how="left")
    o = pd.DataFrame({"CNT": d.CNT.astype(str), "oecd": d.OECD, "schid": d.SCHOOLID.astype(str), "stuid": d.StIDStd.astype(str), "girl": (rng(d.ST04Q01, 1, 2) == 1).astype(float).where(rng(d.ST04Q01, 1, 2).notna()),
                      "grade": rng(d.GRADE, -4, 4), "age": rng(d.AGE, 14, 17), "escs": rng(d.ESCS, -8, 5), "immig": rng(d.IMMIG, 1, 3), "wt": d.W_FSTUWT.astype(float), "private": rng(d.SC01Q01, 1, 2).map({1: 0.0, 2: 1.0}),
                      "lonely": agree(d.ST87Q06), "outsider": agree(d.ST87Q01), "belong": agree(d.ST87Q03), "awkward": agree(d.ST87Q04), "belong_idx": rng(d.BELONG, -6, 6), "lifesat": np.nan,
                      "hrs_school": rng(d.IC05Q01, 1, 7).map(MID7), "hrs_out": rng(d.IC06Q01, 1, 7).map(MID7), "hrs_wkend": rng(d.IC07Q01, 1, 7).map(MID7),
                      "first_net_lt7": (rng(d.IC04Q01, 1, 5) == 1).astype(float).where(rng(d.IC04Q01, 1, 5).notna()), "first_net_lt10": (rng(d.IC04Q01, 1, 5) <= 2).astype(float).where(rng(d.IC04Q01, 1, 5).notna()),
                      "socnet_daily": (rng(d.IC08Q05, 1, 5) >= 4).astype(float).where(rng(d.IC08Q05, 1, 5).notna()), "chat_school_daily": (rng(d.IC10Q01, 1, 5) >= 4).astype(float).where(rng(d.IC10Q01, 1, 5).notna()),
                      "anxmat": rng(d.ANXMAT, -6, 6)})
    return finish(o, 2012)

def wave_1518(year):
    d = pd.read_parquet(EX/f"pisa{year}_student.parquet"); s = pd.read_parquet(EX/f"pisa{year}_school.parquet")
    scols = ["CNT", "CNTSCHID", "SC013Q01TA"] + (["SC156Q01HA"] if "SC156Q01HA" in s else []); d = d.merge(s[scols], on=["CNT", "CNTSCHID"], how="left")
    first = rng(d["IC004Q01TA" if year == 2015 else "IC004Q01HA"], 1, 6)
    lt7 = (first == 1) if year == 2015 else (first <= 2); lt10 = (first <= 2) if year == 2015 else (first <= 3)   # 2015: 1 '<=6', 2 '7-9'; 2018: 1 '<=3', 2 '4-6', 3 '7-9'
    o = pd.DataFrame({"CNT": d.CNT.astype(str), "oecd": d.OECD, "schid": d.CNTSCHID.astype(str), "stuid": d.CNTSTUID.astype(str), "girl": (rng(d.ST004D01T, 1, 2) == 1).astype(float).where(rng(d.ST004D01T, 1, 2).notna()),
                      "grade": rng(d.GRADE, -4, 4), "age": rng(d.AGE, 14, 17), "escs": rng(d.ESCS, -9, 5), "immig": rng(d.IMMIG, 1, 3), "wt": d.W_FSTUWT.astype(float), "private": rng(d.SC013Q01TA, 1, 2).map({1: 0.0, 2: 1.0}),
                      "lonely": agree(d.ST034Q06TA), "outsider": agree(d.ST034Q01TA), "belong": agree(d.ST034Q03TA), "awkward": agree(d.ST034Q04TA), "belong_idx": rng(d.BELONG, -6, 6), "lifesat": rng(d.ST016Q01NA, 0, 10),
                      "hrs_school": rng(d.IC005Q01TA, 1, 7).map(MID7), "hrs_out": rng(d.IC006Q01TA, 1, 7).map(MID7), "hrs_wkend": rng(d.IC007Q01TA, 1, 7).map(MID7),
                      "first_net_lt7": lt7.astype(float).where(first.notna()), "first_net_lt10": lt10.astype(float).where(first.notna()),
                      "socnet_daily": (rng(d.IC008Q05TA, 1, 5) >= 4).astype(float).where(rng(d.IC008Q05TA, 1, 5).notna()), "chat_school_daily": (rng(d.IC011Q01TA, 1, 5) >= 4).astype(float).where(rng(d.IC011Q01TA, 1, 5).notna())})
    if year == 2015:
        o["anxtest"] = rng(d.ANXTEST, -6, 6)
        for i in range(1, 6): o[f"anx{i}"] = rng(d[f"ST118Q0{i}NA"], 1, 4)   # 1 strongly disagree .. 4 strongly agree
    if year == 2018: o["sch_policy"] = rng(d.SC156Q01HA, 1, 2).map({1: 1.0, 2: 0.0})
    return finish(o, year)

def wave2022():
    cols = ["CNT", "OECD", "CNTSCHID", "CNTSTUID", "ST004D01T", "GRADE", "AGE", "ESCS", "IMMIG", "W_FSTUWT", "ST016Q01NA", "ST034Q01TA", "ST034Q03TA", "ST034Q04TA", "ST034Q06TA", "BELONG", "ST326Q01JA", "ST326Q02JA", "ST326Q04JA", "ST326Q05JA", "ST326Q06JA", "IC170Q02JA", "ANXMAT"]
    d = pd.read_parquet(EX22/"pisa2022_student.parquet", columns=cols); s = pd.read_parquet(EX22/"pisa2022_school.parquet", columns=["CNT", "CNTSCHID", "PRIVATESCH", "SC190Q02JA"])
    d = d.merge(s, on=["CNT", "CNTSCHID"], how="left")
    m = lambda c: rng(d[c], 1, 9).map(MID9)
    tot = lambda a, b: (m(a) + m(b)).where(m(a).notna() & m(b).notna())
    ph = rng(d.IC170Q02JA, 1, 6); phone = (ph.between(4, 5)).astype(float).where(ph.notna())
    o = pd.DataFrame({"CNT": d.CNT.astype(str), "oecd": d.OECD, "schid": d.CNTSCHID.astype(str), "stuid": d.CNTSTUID.astype(str), "girl": (rng(d.ST004D01T, 1, 2) == 1).astype(float).where(rng(d.ST004D01T, 1, 2).notna()),
                      "grade": rng(d.GRADE, -4, 4), "age": rng(d.AGE, 14, 17), "escs": rng(d.ESCS, -9, 5), "immig": rng(d.IMMIG, 1, 3), "wt": d.W_FSTUWT.astype(float),
                      "private": d.PRIVATESCH.astype(str).str.strip().str.lower().map({"private": 1.0, "public": 0.0}),
                      "lonely": agree(d.ST034Q06TA), "outsider": agree(d.ST034Q01TA), "belong": agree(d.ST034Q03TA), "awkward": agree(d.ST034Q04TA), "belong_idx": rng(d.BELONG, -6, 6), "lifesat": rng(d.ST016Q01NA, 0, 10),
                      "hrs_school": tot("ST326Q01JA", "ST326Q04JA"), "hrs_out": tot("ST326Q02JA", "ST326Q05JA"), "hrs_wkend": tot("ST326Q03JA", "ST326Q06JA") if "ST326Q03JA" in d else m("ST326Q06JA"),
                      "hrs_school_leis": m("ST326Q04JA"), "hrs_out_leis": m("ST326Q05JA"), "phone_school_daily": phone, "anxmat": rng(d.ANXMAT, -6, 6), "ban": rng(d.SC190Q02JA, 1, 2).map({1: 1.0, 2: 0.0})})
    return finish(o, 2022)

CROSSWALK = [  # harmonized variable, wave, source item(s), recode
    ("lonely", "2012", "ST87Q06 'I feel lonely at school'", "1 = strongly agree/agree"), ("lonely", "2015/2018/2022", "ST034Q06TA 'I feel lonely at school'", "1 = strongly agree/agree"),
    ("belong", "2012", "ST87Q03 'I feel like I belong at school'", "1 = agree"), ("belong", "2015/2018/2022", "ST034Q03TA", "1 = agree"),
    ("outsider", "2012", "ST87Q01 'I feel like an outsider (or left out of things) at school'", "1 = agree"), ("outsider", "2015/2018/2022", "ST034Q01TA", "1 = agree"),
    ("awkward", "2012", "ST87Q04 'I feel awkward and out of place in my school'", "1 = agree"), ("awkward", "2015/2018/2022", "ST034Q04TA", "1 = agree"),
    ("belong_idx", "all", "BELONG (WLE)", "as published; scaled separately each wave (OECD mean 0, SD 1 in the scaling wave), not comparable across waves"),
    ("lifesat", "2015", "ST016Q01NA (file CY6_MS_CMB_STU_QQ2) 'Overall, how satisfied are you with your life as a whole these days?' 0-10", "as is"), ("lifesat", "2018/2022", "ST016Q01NA 0-10", "as is"),
    ("hrs_school", "2012", "IC05Q01 'Internet at school' (typical weekday)", "midpoints 0/.25/.75/1.5/3/5/7 h"), ("hrs_school", "2015/2018", "IC005Q01TA 'During a typical weekday, for how long do you use the Internet at school?'", "same midpoints"),
    ("hrs_school", "2022", "ST326Q01JA + ST326Q04JA hours/day on digital resources at school for learning + for leisure", "sum of 9-category midpoints 0/.5/1.5/.../7.5"),
    ("hrs_out", "2012", "IC06Q01 'Internet out-of-school - weekday'", "midpoints"), ("hrs_out", "2015/2018", "IC006Q01TA 'During a typical weekday, for how long do you use the Internet outside of school?'", "midpoints"),
    ("hrs_out", "2022", "ST326Q02JA + ST326Q05JA hours/day on digital resources before and after school for learning + leisure", "sum of midpoints"),
    ("hrs_wkend", "2012/2015/2018", "IC07Q01 / IC007Q01TA weekend day outside school", "midpoints"), ("hrs_wkend", "2022", "ST326Q03JA + ST326Q06JA weekend learning + leisure", "sum of midpoints"),
    ("sch_1h / out_2h / out_4h", "all", "hrs_school > 1; hrs_out > 2; hrs_out > 4", "category boundaries shared by all waves"),
    ("band_out / band_school", "all", "none, <=1 h, 1-2 h, 2-4 h, 4-6 h, >6 h", "2012-18 from the 7 categories; 2022 from summed midpoints"),
    ("first_net_lt7 / lt10", "2012/2015", "IC04Q01 / IC004Q01TA age first accessed the Internet (<=6, 7-9, 10-12, 13+, never)", "lt7 = '<=6'; lt10 = '<=6' or '7-9'"), ("first_net_lt7 / lt10", "2018", "IC004Q01HA (<=3, 4-6, 7-9, 10-12, 13+, never)", "lt7 = '<=3' or '4-6'; lt10 adds '7-9'"),
    ("socnet_daily", "2012/2015/2018", "IC08Q05 / IC008Q05TA social networks outside school", "1 = almost every day / every day"), ("chat_school_daily", "2012/2015/2018", "IC10Q01 / IC011Q01TA chatting online at school", "1 = almost every day / every day"),
    ("phone_school_daily", "2022", "IC170Q02JA smartphone use at school", "1 = every day / several times a day; 'not available' = 0"),
    ("anxtest, anx1-anx5", "2015", "ANXTEST (WLE); ST118Q01NA-Q05NA (1 strongly disagree .. 4 strongly agree)", "as is"), ("anxmat", "2012/2022", "ANXMAT (WLE)", "as is, wave-specific scaling"),
    ("sch_policy", "2018", "school SC156Q01HA 'At school: its own written statement about the use of digital devices'", "1 yes, 0 no"), ("ban", "2022", "school SC190Q02JA cell phones not allowed on school premises", "1 yes, 0 no"),
    ("private", "2012", "school SC01Q01", "1 private"), ("private", "2015/2018", "school SC013Q01TA", "1 private"), ("private", "2022", "school PRIVATESCH", "1 private"),
    ("girl", "2012", "ST04Q01", "1 female"), ("girl", "2015-2022", "ST004D01T", "1 female"), ("wt", "all", "W_FSTUWT final student weight", "as is"), ("oecd", "all", "OECD flag", "1 = OECD member (2015 code 2 'not applicable' -> 0)"),
    ("ict_country", "all", "derived", "1 if >50% of the country's students answered the out-of-school hours item (ICT familiarity module administered)")]

if __name__ == "__main__":
    waves = [wave2012(), wave_1518(2015), wave_1518(2018), wave2022()]
    p = pd.concat(waves, ignore_index=True)
    for c in ["CNT", "sch", "band_school", "band_out"]: p[c] = p[c].astype("category")
    p.to_parquet(EX/"pisa_panel_student.parquet", index=False, compression="zstd")
    print("wrote", EX/"pisa_panel_student.parquet", p.shape)
    print(p.groupby("year").agg(n=("stu", "size"), countries=("CNT", "nunique"), ict_countries=("CNT", lambda s: p.loc[s.index].query("ict_country==1").CNT.nunique()),
                                lonely=("lonely", "mean"), belong=("belong", "mean"), lifesat=("lifesat", "mean"), hrs_school=("hrs_school", "mean"), hrs_out=("hrs_out", "mean"), girl=("girl", "mean"), private=("private", "mean")).round(3).to_string())
    rows = []
    metas = {y: pd.read_pickle(EX/f"_meta_{y}.pkl") for y in (2012, 2015, 2018) if (EX/f"_meta_{y}.pkl").exists()}
    def fmt(vl):
        if not isinstance(vl, dict): return ""
        return "; ".join(f"{k}={v}" for k, v in list(vl.items())[:12])
    for var, wave, src, rec in CROSSWALK:
        item = src.split()[0].replace("'", "")
        labs = []
        for y, m in metas.items():
            hit = m[m.variable == item]
            if len(hit): labs.append(f"{y}: {hit.iloc[0].label} [{fmt(hit.iloc[0].value_labels)}]")
        rows.append(dict(harmonized=var, waves=wave, source=src, recode=rec, source_labels=" | ".join(labs)))
    pd.DataFrame(rows).to_csv(EX/"pisa_panel_items.csv", index=False); print("wrote", EX/"pisa_panel_items.csv", len(rows), "rows")
