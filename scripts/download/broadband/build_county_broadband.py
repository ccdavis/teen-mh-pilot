"""Build the county broadband tables in data/compiled/broadband/ from the raw NTIA National Broadband Map (State Broadband Initiative,
2010-2014), FCC Form 477 (2014-2021) and Census/FCC block-population files in data/external/broadband/ (see README.md there).
Usage (repository root): uv run python scripts/download/broadband/build_county_broadband.py [--step blockpop|nbm2010|analyze|nbm_wireline|fcc_fixed|fcc_area|assemble] [--force]
Intermediate block-level aggregates are cached as parquet in data/extracts/broadband/ (gitignored); the big CSVs are read with duckdb.

Outputs
  county_broadband_panel.csv   one row per county x data round (June 2010 ... June 2021): population-weighted shares of county
                               population with broadband available, by technology class and advertised download tier. source codes:
                               SBI-blocks-2000 = NTIA SBI block files on 2000 blocks weighted by Census 2000 block population; NBM-analyze = NTIA
                               Analyze table county rows (population metric); NBM-analyze+SBI-blocks-2010 = Analyze rows with wireline/fixed tiers
                               recomputed from the SBI small-block + road-segment files on 2010 blocks (FCC pop2010); FCC477-blocks = Form 477
                               fixed block file, consumer records, FCC 2015 block population; FCC477-area = Form 477 Area Table county rows.
  county_att_mobile_2010.csv   the AT&T 2010 footprint: share of county population in 2000 Census blocks with any AT&T Mobility
                               mobile-wireless coverage (TRANSTECH 80) in the June 2010 and December 2010 SBI releases, plus Verizon,
                               Sprint and T-Mobile for comparison, Myers & Hooper's block-group variant and treated/control classes.
Technology classes. NBM TRANSTECH: 10/20/30 DSL and copper, 40/41 cable, 50 fiber, 90 power line = "wireline"; 70/71 terrestrial fixed
wireless; 80 terrestrial mobile wireless; 60 satellite; 0 other. FCC 477 techcode: 10-12 DSL, 20, 30, 40-43 cable, 50 fiber, 90 BPL =
wireline; 70 fixed wireless; 60 satellite; 0 other. "fixed" = wireline + fixed wireless (the FCC's fixed terrestrial definition).
Speed tiers. NBM MAXADDOWN codes: 2 = 200-768 kbps, 3 = 768k-1.5M, 4 = 1.5-3M, 5 = 3-6M, 6 = 6-10M, 7 = 10-25M, 8 = 25-50M, 9 = 50-100M,
10 = 100M-1G, 11 = 1G+; so ">=3 Mbps" is code >= 5, ">=10" is >= 7, ">=25" is >= 8. FCC 477: maxaddown/maxadup in Mbps; >=10/1 and >=25/3.
A block counts as covered if any provider reports the technology at or above the tier anywhere in the block (the NBM wireless files
also give PCT_BLK_IN_SHAPE, the area share of the block under the coverage polygon, kept as an area-weighted variant for AT&T).
"""
import argparse, io, pathlib, re, subprocess, sys, time, zipfile
import duckdb, pandas as pd, numpy as np
ROOT = pathlib.Path(__file__).resolve().parents[3]; EXT = ROOT/"data/external/broadband"; X = ROOT/"data/extracts/broadband"; OUT = ROOT/"data/compiled/broadband"
X.mkdir(parents=True, exist_ok=True); OUT.mkdir(parents=True, exist_ok=True)
con = duckdb.connect(); con.sql(f"SET threads=8; SET memory_limit='6GB'; SET preserve_insertion_order=false; SET temp_directory='{X}/duckdb_tmp';")  # the build machine has 15 GB RAM; run stages one at a time
WIRELINE_NBM = "('10','20','30','40','41','50','90')"; FIXEDW_NBM = "('70','71')"
WIRELINE_FCC = "(10,11,12,20,30,40,41,42,43,50,90)"
CARRIERS = {"att": r"^AT&T", "verizon": r"^Verizon", "sprint": r"^Sprint", "tmobile": r"^(T-Mobile|Deutsche Telekom)"}  # hoconame (FCC holding-company roll-up), checked against the provider list
def log(*a): print(*a, flush=True)
def parts(d, pattern="part*.csv"): return sorted(str(p) for p in pathlib.Path(d).glob(pattern))
def read_parts(files, delim, cols):
    """UNION ALL of header-homogeneous CSV parts, keeping only `cols` (lower-cased names); columns missing in a part become NULL."""
    sel = []
    for f in files:
        hdr = [c.strip().strip('"').lower() for c in open(f, encoding="utf-8").readline().rstrip("\r\n").split(delim)]
        sel.append("SELECT " + ", ".join((f'"{c}"' if c in hdr else "NULL") + f" AS {c}" for c in cols) + f" FROM read_csv('{f}', header=false, skip=1, delim='{delim}', quote='\"', all_varchar=true, ignore_errors=true, sample_size=100000, names={[*hdr]})")
    return " UNION ALL ".join(sel)
# ---------------------------------------------------------------- block populations
def blockpop(force=False):
    p2000 = X/"blockpop2000.parquet"
    if force or not p2000.exists():
        rows = []
        for z in sorted((EXT/"census2000").glob("*geo_uf1.zip")):
            raw = zipfile.ZipFile(z).read(zipfile.ZipFile(z).namelist()[0])
            for l in raw.split(b"\n"):
                if l[8:11] == b"101": rows.append(((l[29:31] + l[31:34] + l[55:61] + l[62:66]).decode(), int(l[292:301])))
        d = pd.DataFrame(rows, columns=["block", "pop"]); d["county"] = d.block.str[:5]; d.to_parquet(p2000, index=False); log(f"blockpop2000: {len(d):,} blocks, pop {d['pop'].sum():,}")
    p2010 = X/"blockpop2010.parquet"
    if force or not p2010.exists():
        con.sql(f"COPY (SELECT block_fips AS block, substr(block_fips,1,5) AS county, pop2010::BIGINT AS pop2010, pop2015::DOUBLE AS pop2015 FROM read_csv('{EXT}/blockpop/us2015/us2015.csv', header=true, all_varchar=true)) TO '{p2010}' (FORMAT PARQUET)")
        log("blockpop2010:", con.sql(f"SELECT count(*), sum(pop2010), sum(pop2015) FROM '{p2010}'").fetchall())
# ---------------------------------------------------------------- NBM June/Dec 2010 (2000 blocks): wireless by carrier, wireline tiers
def nbm2010(force=False):
    for rnd, delim, blk, wdir, cdirs in [("2010-06", ",", "fullfipsid", EXT/"ntia_nbm/jun2010/parts_wireless", [EXT/"ntia_nbm/jun2010/parts_cblock"]),
                                           ("2010-12", "|", "censusblock_fips", EXT/"ntia_nbm/dec2010/parts_wireless", [EXT/"ntia_nbm/dec2010/parts_cblock", EXT/"ntia_nbm/dec2010/parts_address"])]:
        pw = X/f"nbm_{rnd}_mobile_blocks.parquet"
        if force or not pw.exists():
            t = time.time(); src = read_parts(parts(wdir), delim, ["hoconum", "hoconame", "provname", blk, "pct_blk_in_shape", "transtech", "maxaddown"])
            car = ", ".join(f"max(CASE WHEN regexp_matches(hoconame, '{pat}') THEN 1 ELSE 0 END) AS {k}" for k, pat in CARRIERS.items())
            con.sql(f"""COPY (SELECT trim({blk}) AS block, {car},
                        max(CASE WHEN regexp_matches(hoconame, '{CARRIERS['att']}') THEN least(try_cast(pct_blk_in_shape AS DOUBLE), 1.0) ELSE 0 END) AS att_area,
                        max(CASE WHEN try_cast(maxaddown AS INT) >= 5 THEN 1 ELSE 0 END) AS ge3, max(CASE WHEN try_cast(maxaddown AS INT) >= 7 THEN 1 ELSE 0 END) AS ge10, 1 AS any
                        FROM ({src}) WHERE transtech = '80' AND length(trim({blk})) = 15 GROUP BY 1) TO '{pw}' (FORMAT PARQUET)""")
            log(f"{rnd} mobile blocks: {con.sql(f'SELECT count(*) FROM {chr(39)}{pw}{chr(39)}').fetchone()[0]:,} ({time.time()-t:.0f}s)")
            hc = con.sql(f"SELECT hoconame, count(*) n FROM ({src}) WHERE transtech='80' GROUP BY 1 ORDER BY n DESC LIMIT 40").df(); log(hc.to_string())
        pl = X/f"nbm_{rnd}_wireline_blocks.parquet"
        if force or not pl.exists():
            t = time.time(); files = sum((parts(d) for d in cdirs), [])
            src = read_parts(files, delim, ["fullfipsid", "transtech", "maxaddown"])
            con.sql(f"""COPY (SELECT trim(fullfipsid) AS block,
                        max(CASE WHEN transtech IN {WIRELINE_NBM} THEN try_cast(maxaddown AS INT) END) AS wl_down,
                        max(CASE WHEN transtech IN {WIRELINE_NBM} OR transtech IN {FIXEDW_NBM} THEN try_cast(maxaddown AS INT) END) AS fx_down
                        FROM ({src}) WHERE length(trim(fullfipsid)) = 15 GROUP BY 1) TO '{pl}' (FORMAT PARQUET)""")
            log(f"{rnd} wireline blocks: {con.sql(f'SELECT count(*) FROM {chr(39)}{pl}{chr(39)}').fetchone()[0]:,} ({time.time()-t:.0f}s)")
def county_from_blocks_2000(rnd):
    """County shares (2000 block populations) for a 2010 round; returns a DataFrame indexed by county."""
    pw, pl, bp = X/f"nbm_{rnd}_mobile_blocks.parquet", X/f"nbm_{rnd}_wireline_blocks.parquet", X/"blockpop2000.parquet"
    car = ", ".join(f"sum(b.pop * coalesce(m.{k},0))/sum(b.pop) AS {k}_share" for k in CARRIERS)
    d = con.sql(f"""SELECT b.county, count(*) AS n_blocks, sum(b.pop) AS population, {car},
                 sum(b.pop * coalesce(m.att_area,0))/sum(b.pop) AS att_area_share, sum(b.pop * coalesce(m.any,0))/sum(b.pop) AS mobile_any,
                 sum(b.pop * coalesce(m.ge3,0))/sum(b.pop) AS mobile_ge3, sum(b.pop * coalesce(m.ge10,0))/sum(b.pop) AS mobile_ge10,
                 sum(b.pop * CASE WHEN w.wl_down >= 2 THEN 1 ELSE 0 END)/sum(b.pop) AS wireline_any, sum(b.pop * CASE WHEN w.wl_down >= 5 THEN 1 ELSE 0 END)/sum(b.pop) AS wireline_ge3,
                 sum(b.pop * CASE WHEN w.wl_down >= 7 THEN 1 ELSE 0 END)/sum(b.pop) AS wireline_ge10, sum(b.pop * CASE WHEN w.wl_down >= 8 THEN 1 ELSE 0 END)/sum(b.pop) AS wireline_ge25,
                 sum(b.pop * CASE WHEN w.fx_down >= 2 THEN 1 ELSE 0 END)/sum(b.pop) AS fixed_any, sum(b.pop * CASE WHEN w.fx_down >= 7 THEN 1 ELSE 0 END)/sum(b.pop) AS fixed_ge10,
                 sum(b.pop * CASE WHEN w.fx_down >= 8 THEN 1 ELSE 0 END)/sum(b.pop) AS fixed_ge25
                 FROM '{bp}' b LEFT JOIN '{pw}' m USING (block) LEFT JOIN '{pl}' w USING (block) GROUP BY 1 HAVING sum(b.pop) > 0""").df()
    bg = con.sql(f"""WITH g AS (SELECT substr(b.block,1,12) AS bg, b.county, sum(b.pop) AS pop, avg(coalesce(m.att,0)) AS cov FROM '{bp}' b LEFT JOIN '{pw}' m USING (block) GROUP BY 1,2)
                 SELECT county, sum(pop*cov)/sum(pop) AS att_share_bg FROM g GROUP BY 1 HAVING sum(pop) > 0""").df()
    return d.merge(bg, on="county", how="left").set_index("county")
# ---------------------------------------------------------------- NBM Analyze tables (county rows, population metric), Jun 2011 - Jun 2014
ANALYZE = {"2011-06": "analyze/june2011_analyze_table.csv", "2011-12": "analyze/All-NBM-Analyze-Table-December-2011/Dec2011_analyze_table.county.csv",
           "2012-06": "analyze/All-NBM-Analyze-Table-June-2012/Jun2012_analyze_master.county.csv", "2012-12": "analyze/All-NBM-Analyze-Table-December-2012/Dec2012_analyze_master.xlsx",
           "2013-06": "analyze/All-NBM-Analyze-Table-June-2013/Analyze_Table_Jun2013.xlsx", "2013-12": "analyze/All-NBM-Analyze-Table-December-2013/Analyze_Table_Dec2013.xlsx",
           "2014-06": "analyze/All-NBM-Analyze-Table-June-2014/Analyze_Table_Jun2014.xlsx"}
ACOLS = {"anywline": "wireline_any", "terrmobilewless": "mobile_any", "anywless_nosat": "wireless_nosat_any", "any_tech_nosat": "anytech_nosat", "advdl_gr3000k": "anytech_ge3",
         "advdl_gr10000k": "anytech_ge10", "advdl_gr25000k": "anytech_ge25", "wline_prov_gr2": "wireline_2plus", "population": "population"}
def analyze(force=False):
    p = X/"nbm_analyze_county.parquet"
    if not force and p.exists(): return pd.read_parquet(p)
    con.sql("INSTALL excel; LOAD excel;"); out = []
    for rnd, f in ANALYZE.items():
        f = EXT/"ntia_nbm"/f; rd = f"read_xlsx('{f}', all_varchar=true)" if f.suffix == ".xlsx" else f"read_csv('{f}', header=true, all_varchar=true, sample_size=-1)"
        d = con.sql(f"SELECT geography_id, {', '.join(ACOLS)} FROM {rd} WHERE upper(geography_type) = 'COUNTY' AND metric_type = 'POP'").df()
        d["fips"] = d.geography_id.str.zfill(5); d = d.drop(columns="geography_id").rename(columns=ACOLS); d["round"] = rnd
        for c in ACOLS.values(): d[c] = pd.to_numeric(d[c], errors="coerce")
        log(f"analyze {rnd}: {len(d)} counties; mean wireline_any {d.wireline_any.mean():.3f}, mobile_any {d.mobile_any.mean():.3f}, anytech_ge10 {d.anytech_ge10.mean():.3f}"); out.append(d)
    d = pd.concat(out); d.to_parquet(p, index=False); return d
# ---------------------------------------------------------------- NBM Dec 2013 / Jun 2014 wireline tiers from the small-block + road-segment files (2010 blocks)
def nbm_wireline(force=False):
    for rnd, zname, inner in [("2013-12", "All-NBM-CSV-December-2013.zip", ["NBM-CBLOCK-CSV-December-2013.zip", "NBM-Address-Street-CSV-December-2013.zip"]),
                              ("2014-06", "All-NBM-CSV-June-2014.zip", ["NBM-CBLOCK-CSV-JUN-2014.zip", "NBM-Address-Street-CSV-JUN-2014.zip"])]:
        pl = X/f"nbm_{rnd}_wireline_blocks.parquet"
        if not force and pl.exists(): continue
        t = time.time(); work = EXT/"ntia_nbm"/f"work_{rnd}"; work.mkdir(exist_ok=True); files = []
        for i in inner:  # Info-ZIP unzip handles the Deflate64 members that Python's zipfile cannot
            subprocess.run(["unzip", "-o", "-q", "-j", str(EXT/"ntia_nbm"/zname), f"*/{i}", "-d", str(work)], check=True)
            subprocess.run(["unzip", "-o", "-q", "-j", str(work/i), "-d", str(work)], check=True)
        files = [f for f in work.iterdir() if f.suffix.lower() in (".csv", ".txt")]
        for f in files:  # split on repeated header lines (state exports concatenated), as for 2010
            pd_ = work/(f.stem + "_parts"); pd_.mkdir(exist_ok=True)
            subprocess.run(["awk", "-v", f"out={pd_}", "-v", "hdr=^(\"?objectid\"?[,|]|frn[,|])", "-f", str(EXT/"ntia_nbm/split_by_header.awk"), str(f)], check=True)
        pf = sum((parts(work/(f.stem + "_parts")) for f in files), []); delim = "|" if open(pf[0], encoding="utf-8").readline().count("|") > 3 else ","
        src = read_parts(pf, delim, ["fullfipsid", "transtech", "maxaddown"])
        con.sql(f"""COPY (SELECT trim(fullfipsid) AS block, max(CASE WHEN transtech IN {WIRELINE_NBM} THEN try_cast(maxaddown AS INT) END) AS wl_down,
                    max(CASE WHEN transtech IN {WIRELINE_NBM} OR transtech IN {FIXEDW_NBM} THEN try_cast(maxaddown AS INT) END) AS fx_down
                    FROM ({src}) WHERE length(trim(fullfipsid)) = 15 GROUP BY 1) TO '{pl}' (FORMAT PARQUET)""")
        log(f"{rnd} wireline blocks: {con.sql(f'SELECT count(*) FROM {chr(39)}{pl}{chr(39)}').fetchone()[0]:,} from {len(pf)} parts ({time.time()-t:.0f}s)")
        subprocess.run(["rm", "-rf", str(work)])
def county_wireline_2010blocks(rnd, popcol="pop2010"):
    pl, bp = X/f"nbm_{rnd}_wireline_blocks.parquet", X/"blockpop2010.parquet"
    return con.sql(f"""SELECT b.county, sum(b.{popcol}) AS population_blocks,
                 sum(b.{popcol} * CASE WHEN w.wl_down >= 2 THEN 1 ELSE 0 END)/sum(b.{popcol}) AS wireline_any, sum(b.{popcol} * CASE WHEN w.wl_down >= 5 THEN 1 ELSE 0 END)/sum(b.{popcol}) AS wireline_ge3,
                 sum(b.{popcol} * CASE WHEN w.wl_down >= 7 THEN 1 ELSE 0 END)/sum(b.{popcol}) AS wireline_ge10, sum(b.{popcol} * CASE WHEN w.wl_down >= 8 THEN 1 ELSE 0 END)/sum(b.{popcol}) AS wireline_ge25,
                 sum(b.{popcol} * CASE WHEN w.fx_down >= 2 THEN 1 ELSE 0 END)/sum(b.{popcol}) AS fixed_any, sum(b.{popcol} * CASE WHEN w.fx_down >= 7 THEN 1 ELSE 0 END)/sum(b.{popcol}) AS fixed_ge10,
                 sum(b.{popcol} * CASE WHEN w.fx_down >= 8 THEN 1 ELSE 0 END)/sum(b.{popcol}) AS fixed_ge25
                 FROM '{bp}' b LEFT JOIN '{pl}' w USING (block) GROUP BY 1 HAVING sum(b.{popcol}) > 0""").df().set_index("county")
# ---------------------------------------------------------------- FCC Form 477 fixed deployment block files, Dec 2014 - Jun 2016 (2010 blocks, FCC 2015 block population)
FCC_FIXED = {"2014-12": "US-Fixed-with-Satellite-Dec2014.zip", "2015-06": "US-Fixed-with-Satellite-Jun2015.zip", "2015-12": "US-Fixed-with-Satellite-Dec2015.zip", "2016-06": "US-Fixed-with-Satellite-Jun2016.zip"}
def fcc_fixed(force=False):
    for rnd, zname in FCC_FIXED.items():
        pl = X/f"fcc_{rnd}_fixed_blocks.parquet"
        if not force and pl.exists(): continue
        t = time.time(); z = zipfile.ZipFile(EXT/"fcc477"/zname); inner = [n for n in z.namelist() if n.lower().endswith(".csv")][0]; tmp = X/f"tmp_{rnd}.csv"
        with open(tmp, "wb") as f: subprocess.run(["unzip", "-p", str(EXT/"fcc477"/zname), inner], stdout=f, check=True)
        log(f"{rnd}: extracted {inner} {tmp.stat().st_size/1e9:.1f} GB ({time.time()-t:.0f}s)")
        con.sql(f"""COPY (SELECT blockcode AS block,
                    max(CASE WHEN techcode IN {WIRELINE_FCC} THEN maxaddown END) AS wl_down, max(CASE WHEN techcode IN {WIRELINE_FCC} AND maxaddown >= 10 THEN maxadup END) AS wl_up10,
                    max(CASE WHEN techcode IN {WIRELINE_FCC} AND maxaddown >= 25 THEN maxadup END) AS wl_up25,
                    max(CASE WHEN techcode IN {WIRELINE_FCC} OR techcode = 70 THEN maxaddown END) AS fx_down, max(CASE WHEN (techcode IN {WIRELINE_FCC} OR techcode = 70) AND maxaddown >= 10 THEN maxadup END) AS fx_up10,
                    max(CASE WHEN (techcode IN {WIRELINE_FCC} OR techcode = 70) AND maxaddown >= 25 THEN maxadup END) AS fx_up25
                    FROM read_csv('{tmp}', header=true, types={{'blockcode':'VARCHAR','techcode':'INT','maxaddown':'DOUBLE','maxadup':'DOUBLE','consumer':'INT'}}, ignore_errors=true, sample_size=200000)
                    WHERE consumer = 1 GROUP BY 1) TO '{pl}' (FORMAT PARQUET)""")
        tmp.unlink(); log(f"{rnd} fixed blocks: {con.sql(f'SELECT count(*) FROM {chr(39)}{pl}{chr(39)}').fetchone()[0]:,} ({time.time()-t:.0f}s)")
def county_fcc_fixed(rnd):
    pl, bp = X/f"fcc_{rnd}_fixed_blocks.parquet", X/"blockpop2010.parquet"
    return con.sql(f"""SELECT b.county, sum(b.pop2015) AS population_blocks,
                 sum(b.pop2015 * CASE WHEN w.wl_down >= 0.2 THEN 1 ELSE 0 END)/sum(b.pop2015) AS wireline_any, sum(b.pop2015 * CASE WHEN w.wl_down >= 3 THEN 1 ELSE 0 END)/sum(b.pop2015) AS wireline_ge3,
                 sum(b.pop2015 * CASE WHEN w.wl_up10 >= 1 THEN 1 ELSE 0 END)/sum(b.pop2015) AS wireline_ge10, sum(b.pop2015 * CASE WHEN w.wl_up25 >= 3 THEN 1 ELSE 0 END)/sum(b.pop2015) AS wireline_ge25,
                 sum(b.pop2015 * CASE WHEN w.fx_down >= 0.2 THEN 1 ELSE 0 END)/sum(b.pop2015) AS fixed_any, sum(b.pop2015 * CASE WHEN w.fx_up10 >= 1 THEN 1 ELSE 0 END)/sum(b.pop2015) AS fixed_ge10,
                 sum(b.pop2015 * CASE WHEN w.fx_up25 >= 3 THEN 1 ELSE 0 END)/sum(b.pop2015) AS fixed_ge25
                 FROM '{bp}' b LEFT JOIN '{pl}' w USING (block) GROUP BY 1 HAVING sum(b.pop2015) > 0""").df().set_index("county")
# ---------------------------------------------------------------- FCC Area Tables, Dec 2016 - Jun 2021 (county rows pulled by fetch_fcc_area_tables.py)
def fcc_area():
    out = []
    for f in sorted((EXT/"fcc477/area_table").glob("area_table_*.csv")):
        rnd = f.stem.replace("area_table_", ""); d = pd.read_csv(f, dtype={"id": str}); d["id"] = d.id.str.zfill(5)
        for c in ["has_0", "has_1", "has_2", "has_3more"]: d[c] = pd.to_numeric(d[c], errors="coerce").fillna(0)
        g = d.groupby(["id", "tech", "speed"])[["has_0", "has_1", "has_2", "has_3more"]].sum(); g["tot"] = g.sum(axis=1); g["share"] = (g.tot - g.has_0) / g.tot
        w = g.share.unstack(["tech", "speed"]); pop = g.tot.groupby("id").max()
        r = pd.DataFrame({"population": pop, "wireline_any": w[("acfo", 0.2)], "wireline_ge10": w[("acfo", 10)], "wireline_ge25": w[("acfo", 25)],
                          "fixed_any": w[("acfow", 0.2)], "fixed_ge10": w[("acfow", 10)], "fixed_ge25": w[("acfow", 25)], "fixedwireless_any": w[("w", 0.2)]})
        r["round"] = rnd; r.index.name = "fips"; out.append(r.reset_index()); log(f"area table {rnd}: {len(r)} counties; mean fixed_ge25 {r.fixed_ge25.mean():.3f}")
    return pd.concat(out)
# ---------------------------------------------------------------- assemble
def assemble():
    rows = []
    for rnd in ["2010-06", "2010-12"]:
        d = county_from_blocks_2000(rnd).reset_index().rename(columns={"county": "fips"}); d["round"] = rnd; d["source"] = "SBI-blocks-2000"
        if rnd == "2010-06": d[["wireline_any", "wireline_ge3", "wireline_ge10", "wireline_ge25", "fixed_any", "fixed_ge10", "fixed_ge25"]] = np.nan  # June 2010 release lacks the large-block (road segment) file
        rows.append(d[["fips", "round", "source", "population", "wireline_any", "wireline_ge3", "wireline_ge10", "wireline_ge25", "fixed_any", "fixed_ge10", "fixed_ge25", "mobile_any", "mobile_ge3", "mobile_ge10", "att_share"]].rename(columns={"att_share": "att_mobile_any"}))
    a = analyze(); a["source"] = "NBM-analyze"
    W = pd.concat([county_wireline_2010blocks(rnd).reset_index().rename(columns={"county": "fips"}).drop(columns="population_blocks").assign(round=rnd) for rnd in ["2013-12", "2014-06"] if (X/f"nbm_{rnd}_wireline_blocks.parquet").exists()])
    if len(W):  # block-file wireline/fixed tiers replace the Analyze any-wireline share for those rounds (same source, finer tiers)
        a = a.merge(W, on=["fips", "round"], how="left", suffixes=("_an", ""))
        a["wireline_any"] = a.wireline_any.fillna(a.wireline_any_an); a = a.drop(columns="wireline_any_an"); a.loc[a["round"].isin(W["round"].unique()), "source"] = "NBM-analyze+SBI-blocks-2010"
    rows.append(a)
    for rnd in FCC_FIXED:
        if (X/f"fcc_{rnd}_fixed_blocks.parquet").exists():
            d = county_fcc_fixed(rnd).reset_index().rename(columns={"county": "fips", "population_blocks": "population"}); d["round"] = rnd; d["source"] = "FCC477-blocks"; rows.append(d)
    ar = fcc_area(); ar["source"] = "FCC477-area"; rows.append(ar)
    P = pd.concat(rows, ignore_index=True); P = P[P.fips.str.len() == 5]; P = P[P.fips.str[:2].astype(int) <= 56]
    P["year_frac"] = P["round"].str[:4].astype(int) + np.where(P["round"].str[-2:] == "06", 0.5, 1.0)
    cols = ["fips", "round", "year_frac", "source", "population", "wireline_any", "wireline_ge3", "wireline_ge10", "wireline_ge25", "fixed_any", "fixed_ge10", "fixed_ge25", "fixedwireless_any",
            "mobile_any", "mobile_ge3", "att_mobile_any", "anytech_ge3", "anytech_ge10", "anytech_ge25"]
    for c in cols:
        if c not in P: P[c] = np.nan
    P = P[cols].sort_values(["fips", "round"]); num = [c for c in cols if c not in ("fips", "round", "date", "source")]
    P[num] = P[num].astype(float).round(3); P["population"] = P.population.round(0)
    P.to_csv(OUT/"county_broadband_panel.csv", index=False); log(f"county_broadband_panel.csv: {len(P):,} rows, {P.fips.nunique()} counties, rounds {sorted(P['round'].unique())}")
    log(P.groupby("round")[["wireline_any", "wireline_ge10", "wireline_ge25", "fixed_ge25", "mobile_any", "mobile_ge3", "anytech_ge10"]].mean().round(3).to_string())
    # AT&T 2010 footprint table
    j, d = county_from_blocks_2000("2010-06"), county_from_blocks_2000("2010-12")
    A = pd.DataFrame({"att_share_dec2010": d.att_share, "att_share_bg_dec2010": d.att_share_bg, "att_area_share_dec2010": d.att_area_share, "att_share_jun2010": j.att_share,
                      "verizon_share_dec2010": d.verizon_share, "sprint_share_dec2010": d.sprint_share, "tmobile_share_dec2010": d.tmobile_share,
                      "any_mobile_share_dec2010": d.mobile_any, "any_mobile_share_jun2010": j.mobile_any, "mobile_ge3_share_dec2010": d.mobile_ge3, "n_blocks": d.n_blocks, "population_2000": d.population})
    A.index.name = "fips"; A = A.reset_index(); A = A[A.fips.str[:2].astype(int) <= 56]
    A["mh_group"] = np.select([A.att_share_bg_dec2010 > 0.9, A.att_share_bg_dec2010 < 0.1], ["treated", "control"], "intermediate")
    num = [c for c in A.columns if c.startswith(("att", "verizon", "sprint", "tmobile", "any_", "mobile_"))]; A[num] = A[num].astype(float).round(4)
    A.to_csv(OUT/"county_att_mobile_2010.csv", index=False)
    log(f"county_att_mobile_2010.csv: {len(A)} counties; mean att_share_dec2010 {A.att_share_dec2010.mean():.3f}; groups {A.mh_group.value_counts().to_dict()}")
    log(A.describe().T.round(3).to_string())
if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter); ap.add_argument("--step", action="append", choices=["blockpop", "nbm2010", "analyze", "nbm_wireline", "fcc_fixed", "fcc_area", "assemble"]); ap.add_argument("--force", action="store_true")
    a = ap.parse_args(); steps = a.step or ["blockpop", "nbm2010", "analyze", "nbm_wireline", "fcc_fixed", "assemble"]
    for s in steps:
        t = time.time(); log(f"==== {s}"); {"blockpop": blockpop, "nbm2010": nbm2010, "analyze": analyze, "nbm_wireline": nbm_wireline, "fcc_fixed": fcc_fixed, "fcc_area": fcc_area, "assemble": assemble}[s](**({"force": a.force} if s not in ("assemble", "fcc_area") else {})); log(f"     {s} done in {time.time()-t:.0f}s")
