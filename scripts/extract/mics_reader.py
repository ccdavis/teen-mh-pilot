"""Read IPUMS-MICS fixed-width .dat.gz files using the .layout.txt files (name, rectype, start, width, type)."""
import pandas as pd, gzip, pathlib
RAW = pathlib.Path(__file__).resolve().parents[2]/"data/raw/mics"
def layout(sample, rt):
    L = pd.read_csv(RAW/"layouts"/f"{sample}_{rt}.layout.txt", sep=r"\s+", header=None, names=["name","rectype","start","width","type"], dtype={"name":str,"rectype":str,"start":int,"width":int,"type":str})
    return L
def read(sample, rt, vars, chunksize=None):
    L = layout(sample, rt); L = L[L.name.isin(vars)].drop_duplicates("name")
    missing = [v for v in vars if v not in set(L.name)]
    colspecs = [(s-1, s-1+w) for s, w in zip(L.start, L.width)]
    df = pd.read_fwf(RAW/"data"/f"{sample}_{rt}_mics.dat.gz", colspecs=colspecs, names=list(L.name), compression="gzip", dtype=str)
    for n, t in zip(L.name, L.type):
        if t in ("integer","double"): df[n] = pd.to_numeric(df[n], errors="coerce")
    for m in missing: df[m] = pd.NA
    return df
if __name__ == "__main__":
    import time; t=time.time()
    d = read("gh2017a", "fs", ["SAMPLE","COUNTRY_ISO3","YEAR","SERIAL","CLUSTER","HHNO","LINECH","WEIGHTFS","URBAN","AGEFS","SEXFS","WINDEX5","EDCURR_FS","ANXIFREQ","DEPRESSFREQ","DIFFLEARN","DIFFREMEM","DIFFFRIEND","RESULTFS","PSU"])
    print(d.shape, round(time.time()-t,1), "s"); print(d.head(3).to_string()); print(d.ANXIFREQ.value_counts(dropna=False).sort_index().to_dict(), d.DEPRESSFREQ.value_counts(dropna=False).sort_index().to_dict()); print("weight mean", d.WEIGHTFS.mean(), "age", d.AGEFS.min(), d.AGEFS.max())
