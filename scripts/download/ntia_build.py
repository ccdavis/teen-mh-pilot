"""Build harmonized NTIA Internet Use Survey (CPS Computer & Internet Use Supplement)
person-level file and state/CBSA aggregates of mobile internet adoption, 2009-2023.

Inputs : data/external/ntia/raw/<wave>pub.dat.gz   (Census fixed-width public-use files)
         data/external/ntia/dictionaries/<wave>-dictionary.csv (NTIA column layouts)
Outputs: data/extracts/ntia/ntia_person_all.parquet
         data/compiled/ntia/ntia_state_year.csv
         data/compiled/ntia/ntia_cbsa_year.csv
         data/compiled/ntia/ntia_national_sanity.csv

Run: uv run python scripts/09_ntia_build.py
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / "data/external/ntia/raw"
DICT = ROOT / "data/external/ntia/dictionaries"
OUT = ROOT / "data/extracts/ntia"
OUT.mkdir(parents=True, exist_ok=True)

WAVES = [  # (wave tag, year, month)
    ("oct09", 2009, 10), ("oct10", 2010, 10), ("jul11", 2011, 7), ("oct12", 2012, 10),
    ("jul13", 2013, 7), ("jul15", 2015, 7), ("nov17", 2017, 11), ("nov19", 2019, 11),
    ("nov21", 2021, 11), ("nov23", 2023, 11),
]

COMMON = ["hrhhid", "hrhhid2", "hrmonth", "hryear4", "hrintsta", "hrmis", "hrhtype", "qstnum",
          "occurnum", "pulineno", "gestfips", "gtcbsa", "gtco", "gtmetsta", "gtcbsast",
          "perrp", "prpertyp", "pesex", "pwsswgt", "hwhhwgt"]
PEIN = ["peinhome", "peinwork", "peinschl", "peincafe", "peintrav", "peinlico", "peinelho", "peinothr"]
HEIN = [c.replace("pe", "he", 1) for c in PEIN]

WAVE_VARS = {
    "oct09": ["peage", "pwsupwgt", "henet1", "penet2", "henet3", "henet4"],
    "oct10": ["peage", "pwsupwgt", "henet2a", "pen2who", "henet5a", "penet6", "heserv35", "hecomp12"],
    "jul11": ["peage", "pwprmwgt", "prhresp", "peperscr", "pecell", "petabl", "hesci75", "hesci5",
              "pesci1", "pesc2a7"],
    "oct12": ["prtage", "pwsupwgt", "pwprmwgt", "prhresp", "penet8", "penet10", "henet3", "henet9",
              "henet45", "penet1", "penet1a4", "penet1a5", "penet1a6", "penet1a8", "penet1a9"],
    "jul13": ["prtage", "pwsupwgt", "hwsupwgt", "pwprmwgt", "puelgflg", "peperscr", "pecell", "petabl",
              "henet45", "henet3", "hesc2a8"],
    "jul15": ["prtage", "pwprmwgt", "puelgflg", *PEIN, *HEIN, "pemphone", "petablet", "hehomte1",
              "heoutmob", "pesocial", "henetchk"],
}
for w in ("nov17", "nov19", "nov21", "nov23"):
    WAVE_VARS[w] = ["prtage", "pwprmwgt", "puelgflg", *PEIN, *HEIN, "pemphone", "petablet",
                    "hehomte1", "hemobdat", "pesocial", "henetchk", "penetck2"]


def read_wave(wave: str) -> pd.DataFrame:
    d = pd.read_csv(DICT / f"{wave}-dictionary.csv")
    d["name"] = d["name"].str.lower()
    want = COMMON + WAVE_VARS[wave]
    missing = sorted(set(want) - set(d["name"]))
    if missing:
        raise KeyError(f"{wave}: not in dictionary: {missing}")
    sel = d[d["name"].isin(want)].drop_duplicates("name")
    colspecs = [(s - 1, e) for s, e in zip(sel["start"], sel["end"])]
    dtypes = {n: (str if t == "char" else "Int64") for n, t in zip(sel["name"], sel["type"])}
    df = pd.read_fwf(RAW / f"{wave}pub.dat.gz", colspecs=colspecs, names=list(sel["name"]),
                     dtype=dtypes, compression="gzip", header=None)
    for c in df.columns:  # NTIA importer: all *wgt columns carry 4 implied decimals
        if c.endswith("wgt"):
            df[c] = df[c].astype("float64") / 10000.0
    return df


def yes(s: pd.Series) -> pd.Series:
    return (s == 1).fillna(False).astype(bool)


def build_wave(wave: str, year: int, month: int) -> pd.DataFrame:
    df = read_wave(wave)
    age = df["peage"] if "peage" in df else df["prtage"]
    out = pd.DataFrame({
        "year": year, "month": month, "wave": wave,
        "hrhhid": df["hrhhid"], "hrhhid2": df["hrhhid2"].astype("Int64"), "qstnum": df["qstnum"],
        "occurnum": df["occurnum"], "pulineno": df["pulineno"],
        "state": df["gestfips"], "cbsa": df["gtcbsa"], "county": df["gtco"],
        "metro_status": df["gtmetsta"], "cbsa_status": df["gtcbsast"],
        "hrintsta": df["hrintsta"], "hrmis": df["hrmis"], "hrhtype": df["hrhtype"],
        "perrp": df["perrp"], "prpertyp": df["prpertyp"], "age": age.astype("Int64"), "sex": df["pesex"],
        "pwsswgt": df["pwsswgt"], "hwhhwgt": df["hwhhwgt"],
        "pwsupwgt": df["pwsupwgt"] if "pwsupwgt" in df else np.nan,
        "hwsupwgt": df["hwsupwgt"] if "hwsupwgt" in df else np.nan,
        "pwprmwgt": df["pwprmwgt"] if "pwprmwgt" in df else np.nan,
    })
    # NTIA universe conventions
    interviewed = df["hrintsta"] == 1
    is_person = (interviewed & (df["prpertyp"] != 3) & (age >= 3)).fillna(False).astype(bool)
    if wave == "jul13":
        is_person &= ~df["hrmis"].isin([1, 5])  # supplement not asked of MIS 1 and 5 in July 2013
    if wave in ("nov21", "nov23"):
        is_hholder = df["perrp"].isin([40, 41])
    else:
        is_hholder = (df["perrp"] > 0) & (df["perrp"] < 3)
    is_hholder &= is_person & (df["hrhtype"] > 0) & (df["hrhtype"] < 9)
    if wave in ("jul11", "oct12"):
        is_resp = is_person & (df["prhresp"] == 1)        # primary respondent (weight pwprmwgt)
    elif wave in ("jul13", "jul15", "nov17", "nov19", "nov21", "nov23"):
        is_resp = is_person & (df["puelgflg"] == 20)      # random respondent (weight pwprmwgt)
    else:
        is_resp = pd.Series(False, index=df.index)
    out["in_universe"] = is_person
    out["is_householder"] = is_hholder
    out["is_respondent"] = is_resp
    # person-level analysis weight per NTIA guidance (PWSUPWGT only for July 2013)
    out["w_person"] = df["pwsupwgt"] if wave == "jul13" else df["pwsswgt"]
    out["w_hh"] = df["hwsupwgt"] if wave == "jul13" else df["hwhhwgt"]
    out["w_resp"] = df["pwprmwgt"] if "pwprmwgt" in df else np.nan

    def ind(cond, universe):
        """1/0 within universe, NA outside."""
        r = pd.Series(pd.NA, index=df.index, dtype="Int8")
        r[universe] = cond[universe].astype("int8")
        return r

    NA = pd.Series(pd.NA, index=df.index, dtype="Int8")

    # ---- person_internet_any -------------------------------------------------
    if wave == "oct09":
        inet = yes(df["penet2"])
    elif wave == "oct10":
        inet = yes(df["pen2who"]) | yes(df["penet6"])
    elif wave in ("jul11", "jul13"):
        inet = yes(df["peperscr"])
    elif wave == "oct12":
        inet = yes(df["penet8"]) | yes(df["penet10"])
    else:
        inet = df[PEIN].eq(1).fillna(False).any(axis=1)
    out["person_internet_any"] = ind(inet, is_person)

    # ---- household mobile items ----------------------------------------------
    if wave == "oct09":
        out["hh_mobile_data_plan"] = NA
        out["hh_mobile_internet_at_home"] = NA
    elif wave == "oct10":
        out["hh_mobile_data_plan"] = ind(yes(df["heserv35"]), is_person)
        out["hh_mobile_internet_at_home"] = ind(yes(df["heserv35"]), is_person)
    elif wave == "jul11":
        out["hh_mobile_data_plan"] = ind(yes(df["hesci75"]), is_person)
        out["hh_mobile_internet_at_home"] = ind(yes(df["hesci75"]), is_person)
    elif wave in ("oct12", "jul13"):
        out["hh_mobile_data_plan"] = ind(yes(df["henet45"]), is_person)
        out["hh_mobile_internet_at_home"] = ind(yes(df["henet45"]), is_person)
    elif wave == "jul15":
        out["hh_mobile_data_plan"] = ind(yes(df["hehomte1"]) | yes(df["heoutmob"]), is_person)
        out["hh_mobile_internet_at_home"] = ind(yes(df["hehomte1"]), is_person)
    else:
        out["hh_mobile_data_plan"] = ind(yes(df["hemobdat"]), is_person)
        out["hh_mobile_internet_at_home"] = ind(yes(df["hehomte1"]), is_person)

    # ---- person mobile phone / smartphone internet ---------------------------
    if wave in ("oct09", "oct10"):
        out["person_mobile_phone_user"] = NA
        out["person_uses_smartphone_internet"] = NA
        out["person_mobile_device_internet"] = NA
    elif wave in ("jul11", "jul13"):
        out["person_mobile_phone_user"] = NA   # 2011/2013 only ask about phones used for Internet
        out["person_uses_smartphone_internet"] = ind(yes(df["pecell"]), is_person)
        out["person_mobile_device_internet"] = ind(yes(df["pecell"]) | yes(df["petabl"]), is_person)
    elif wave == "oct12":
        phone_inet = yes(df["penet1"]) & df[["penet1a4", "penet1a5", "penet1a6", "penet1a8", "penet1a9"]].eq(1).any(axis=1)
        out["person_mobile_phone_user"] = ind(yes(df["penet1"]), is_resp)
        out["person_uses_smartphone_internet"] = ind(phone_inet, is_resp)
        out["person_mobile_device_internet"] = ind(phone_inet, is_resp)
    else:
        mob_plan = out["hh_mobile_data_plan"].fillna(0).astype(bool)
        out["person_mobile_phone_user"] = ind(yes(df["pemphone"]), is_person)
        out["person_uses_smartphone_internet"] = ind(yes(df["pemphone"]) & inet & mob_plan, is_person)
        out["person_mobile_device_internet"] = ind((yes(df["pemphone"]) | yes(df["petablet"])) & inet, is_person)

    # ---- social networking ---------------------------------------------------
    if wave in ("jul15", "nov17", "nov19", "nov21", "nov23"):
        asked = is_resp & df["pesocial"].isin([1, 2])
        out["person_social_network"] = ind(yes(df["pesocial"]), asked)
    else:
        out["person_social_network"] = NA
    if wave == "jul11":
        asked = is_resp & df["pesc2a7"].isin([1, 2]) | (is_resp & (df["pesci1"] == 2))
        out["person_phone_social_network"] = ind(yes(df["pesc2a7"]), asked)
    elif wave == "oct12":
        asked = is_resp & (df["penet1a8"].isin([1, 2]) | (df["penet1"] == 2))
        out["person_phone_social_network"] = ind(yes(df["penet1a8"]), asked)
    else:
        out["person_phone_social_network"] = NA
    out["hh_phone_social_network"] = ind(yes(df["hesc2a8"]), is_person) if wave == "jul13" else NA

    # ---- household contains a 12-17-year-old --------------------------------
    teen = ((age >= 12) & (age <= 17)).fillna(False).astype(bool)
    out["hh_has_teen_12_17"] = teen.groupby(df["qstnum"]).transform("max").astype("int8")
    out["hh_n_persons"] = df.groupby("qstnum")["qstnum"].transform("size").astype("int16")
    return out


INDICATORS = {
    # name: weight column
    "person_internet_any": "w_person",
    "hh_mobile_data_plan": "w_person",
    "hh_mobile_internet_at_home": "w_person",
    "person_mobile_phone_user": "w_person",
    "person_uses_smartphone_internet": "w_person",
    "person_mobile_device_internet": "w_person",
    "person_social_network": "w_resp",
    "person_phone_social_network": "w_resp",
    "hh_phone_social_network": "w_person",
}
RESP_WAVES = {"person_mobile_phone_user": ["oct12"], "person_uses_smartphone_internet": ["oct12"],
              "person_mobile_device_internet": ["oct12"]}


def weight_col(ind: str, wave: str) -> str:
    if wave in RESP_WAVES.get(ind, []):
        return "w_resp"
    return INDICATORS[ind]


def aggregate(df: pd.DataFrame, geo: str | None) -> pd.DataFrame:
    rows = []
    groups = {"all": pd.Series(True, index=df.index),
              "age15_24": df["age"].between(15, 24).fillna(False),
              "hh_teen12_17": df["hh_has_teen_12_17"] == 1}
    for (wave, year, month), sub in df.groupby(["wave", "year", "month"], sort=True):
        for ind in INDICATORS:
            wcol = weight_col(ind, wave)
            ok = sub[ind].notna() & sub[wcol].notna() & (sub[wcol] > 0)
            if not ok.any():
                continue
            for gname, gmask in groups.items():
                m = ok & gmask.loc[sub.index]
                s = sub[m]
                if geo is not None:
                    s = s[s[geo] > 0]
                    keys = [geo]
                else:
                    keys = []
                v = s[ind].astype(float) * s[wcol]
                g = s.assign(_wv=v, _w=s[wcol])
                agg = (g.groupby(keys)[["_wv", "_w"]].sum() if keys else
                       pd.DataFrame({"_wv": [v.sum()], "_w": [s[wcol].sum()]}))
                n = g.groupby(keys).size() if keys else pd.Series([len(g)])
                agg = agg.assign(n_unweighted=n.values, share=lambda x: x["_wv"] / x["_w"],
                                 weighted_pop=lambda x: x["_w"], weighted_yes=lambda x: x["_wv"])
                agg = agg.reset_index()
                agg.insert(0, "year", year); agg.insert(1, "month", month); agg.insert(2, "wave", wave)
                agg["group"] = gname; agg["indicator"] = ind; agg["weight"] = wcol
                rows.append(agg.drop(columns=["_wv", "_w"]))
    res = pd.concat(rows, ignore_index=True)
    cols = ["year", "month", "wave"] + ([geo] if geo else []) + ["group", "indicator", "weight",
                                                                 "share", "n_unweighted", "weighted_yes", "weighted_pop"]
    return res[cols].sort_values(cols[:6]).reset_index(drop=True)


if __name__ == "__main__":
    parts = []
    for wave, year, month in WAVES:
        p = build_wave(wave, year, month)
        parts.append(p)
        u = p[p["in_universe"]]
        print(f"{wave}: rows={len(p):,} in_universe={len(u):,} sum(w_person)={u['w_person'].sum()/1e6:,.1f}M "
              f"resp={int(p['is_respondent'].sum()):,} sum(w_resp)={p.loc[p['is_respondent'], 'w_resp'].sum()/1e6:,.1f}M")
    allp = pd.concat(parts, ignore_index=True)
    allp.to_parquet(OUT / "ntia_person_all.parquet", index=False)
    uni = allp[allp["in_universe"]].copy()

    nat = aggregate(uni, None)
    nat.to_csv(OUT / "ntia_national_sanity.csv", index=False)
    aggregate(uni, "state").to_csv(OUT / "ntia_state_year.csv", index=False)
    aggregate(uni, "cbsa").to_csv(OUT / "ntia_cbsa_year.csv", index=False)
    piv = nat[nat["group"] == "all"].pivot(index="year", columns="indicator", values="share")
    print(piv.round(3).to_string())
