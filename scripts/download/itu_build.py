"""Build tidy ITU country x year dataset of mobile-broadband adoption/coverage.

Primary source: ITU DataHub v3 CSV API, one raw file per SeriesID under
data/external/itu/datahub/ (downloaded with curl; see data/external/itu/README.md).
Supplementary source: GSMA Mobile Connectivity Index 2022 workbook (3G/4G coverage,
GSMA Intelligence) under data/external/itu/gsma_mci/.

Output: data/compiled/itu/itu_country_year.csv with columns
    iso3, country, year, indicator, value, source
plus data/compiled/itu/itu_coverage_table.csv (indicator x year -> n countries).

Run from the repository root:  uv run python scripts/download/itu_build.py
"""
from __future__ import annotations

import io
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / "data" / "external" / "itu"
OUT = ROOT / "data" / "compiled" / "itu"
OUT.mkdir(parents=True, exist_ok=True)

YEAR_MIN, YEAR_MAX = 2005, 2024

# SeriesID -> (SeriesCode expected, tidy indicator name)
SERIES = {
    12066: ("i911mw", "mbb_subs_per100"),           # Active mobile-broadband subscriptions per 100 inhabitants
    430: ("i271G", "pop_covered_3g_pct"),           # Population covered by at least a 3G mobile network (%)
    19306: ("i271GA", "pop_covered_4g_pct"),        # Population covered by at least an LTE/WiMAX (4G) mobile network (%)
    11624: ("i99H", "internet_users_pct"),          # Individuals using the Internet (%)
    9224: ("HHU4212-%_POP-15TO24-", "internet_users_pct_age15_24"),
    9225: ("HHU4212-%_POP-15TO24-FEMALE", "internet_users_pct_age15_24_female"),
    9226: ("HHU4212-%_POP-15TO24-MALE", "internet_users_pct_age15_24_male"),
    9230: ("HHU4212-%_POP-FEMALE-", "internet_users_pct_female"),
    9276: ("HHU4212-%_POP-MALE-", "internet_users_pct_male"),
    392: ("i911", "mobile_subs_per100"),            # Mobile-cellular subscriptions per 100 inhabitants
    12047: ("xHH6_IDI", "hh_internet_access_pct"),  # Estimated proportion of households with Internet access at home (%)
}

# Non-ISO area codes used by ITU for regional / income aggregates (kept out of the country file).
AGG_CODES = {"WLD", "AFR", "AMS", "ARB", "ASP", "CIS", "EUR", "HI", "UMI", "LMI", "LI", "LDC", "LLDC", "SIDS"}


def read_datahub(path: Path) -> pd.DataFrame:
    txt = path.read_text(encoding="utf-8-sig")
    try:
        df = pd.read_csv(io.StringIO(txt), dtype=str, keep_default_na=False)
    except pd.errors.ParserError:
        df = pd.read_csv(io.StringIO(txt), dtype=str, keep_default_na=False, engine="python")
    return df


def build_datahub() -> tuple[pd.DataFrame, pd.DataFrame]:
    frames, aggs, log = [], [], []
    for sid, (code, name) in SERIES.items():
        f = RAW / "datahub" / f"datahub_v3_codesid_{sid}.csv"
        df = read_datahub(f)
        # the API returns the whole indicator family; keep only the requested SeriesID
        df = df[df["SeriesID"] == str(sid)].copy()
        codes = set(df["SeriesCode"])
        assert codes == {code}, (sid, codes)
        series_label = df["Series"].iloc[0].strip()
        unit = df["Unit"].iloc[0]
        df["year"] = pd.to_numeric(df["Year"], errors="coerce").astype("Int64")
        df["value"] = pd.to_numeric(df["Value"], errors="coerce")
        n_blank = df["value"].isna().sum()
        df = df[df["value"].notna()]
        df = df.sort_values("LastModifiedOn")
        n_dup = df.duplicated(["AreaCode", "year"], keep="last").sum()
        df = df.drop_duplicates(["AreaCode", "year"], keep="last")
        is_agg = df["AreaCode"].isin(AGG_CODES) | (df["DisaggregationGroup"] == "Total")
        tidy = pd.DataFrame({
            "iso3": df["AreaCode"],
            "country": df["AreaName"].str.strip(),
            "year": df["year"],
            "indicator": name,
            "value": df["value"],
            "source": "ITU DataHub v3 (WTID) SeriesID " + str(sid) + " " + code,
        })
        frames.append(tidy[~is_agg.values])
        aggs.append(tidy[is_agg.values])
        log.append({
            "series_id": sid, "series_code": code, "indicator": name, "itu_label": series_label, "unit": unit,
            "rows_raw": len(df) + n_blank, "blank_values_dropped": int(n_blank), "dups_resolved": int(n_dup),
            "n_iso3": int(tidy[~is_agg.values]["iso3"].nunique()),
            "year_min": int(tidy["year"].min()), "year_max": int(tidy["year"].max()),
        })
    return pd.concat(frames, ignore_index=True), pd.concat(aggs, ignore_index=True), pd.DataFrame(log)


def build_gsma() -> pd.DataFrame:
    f = RAW / "gsma_mci" / "MCI_Data_2022.xlsx"
    d = pd.read_excel(f, sheet_name="Index Scores", header=2)
    d = d.rename(columns={"ISO Code": "iso3", "Country": "country", "Year": "year"})
    rows = []
    for col, name in [("3G Coverage", "pop_covered_3g_pct"), ("4G Coverage", "pop_covered_4g_pct")]:
        t = d[["iso3", "country", "year", col]].rename(columns={col: "value"}).dropna(subset=["value"])
        t["indicator"] = name
        t["source"] = "GSMA Mobile Connectivity Index 2022 (GSMA Intelligence), Index Scores sheet, '" + col + "' (normalised 0-100 score = % population covered)"
        rows.append(t)
    g = pd.concat(rows, ignore_index=True)
    g["year"] = g["year"].astype(int)
    return g[["iso3", "country", "year", "indicator", "value", "source"]]


def main() -> None:
    itu, agg, log = build_datahub()
    gsma = build_gsma()

    tidy = pd.concat([itu, gsma], ignore_index=True)
    tidy = tidy[(tidy["year"] >= YEAR_MIN) & (tidy["year"] <= YEAR_MAX)]
    tidy["year"] = tidy["year"].astype(int)
    tidy = tidy.sort_values(["indicator", "source", "iso3", "year"]).reset_index(drop=True)
    assert not tidy.duplicated(["iso3", "year", "indicator", "source"]).any()
    tidy.to_csv(OUT / "itu_country_year.csv", index=False)

    agg = agg[(agg["year"] >= YEAR_MIN) & (agg["year"] <= YEAR_MAX)]
    agg.to_csv(OUT / "itu_aggregates_year.csv", index=False)
    log.to_csv(OUT / "itu_series_log.csv", index=False)

    # coverage: indicator x year -> number of ISO3 countries with a value (ITU DataHub rows only)
    cov = (itu[(itu["year"] >= YEAR_MIN) & (itu["year"] <= YEAR_MAX)]
           .groupby(["indicator", "year"])["iso3"].nunique().unstack("year").fillna(0).astype(int))
    cov.to_csv(OUT / "itu_coverage_table.csv")
    gcov = (gsma.groupby(["indicator", "year"])["iso3"].nunique().unstack("year").fillna(0).astype(int))

    pd.set_option("display.width", 250)
    print("wrote", OUT / "itu_country_year.csv", tidy.shape)
    print(log.to_string(index=False))
    print("\nITU DataHub coverage (n ISO3 countries with a value):")
    print(cov.to_string())
    print("\nGSMA MCI 2022 coverage:")
    print(gcov.to_string())
    print("\nsources:", tidy["source"].value_counts().to_dict())


if __name__ == "__main__":
    main()
