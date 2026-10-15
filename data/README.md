# data/

- `compiled/` (committed): tables built for this project from public sources. See `DATA_SOURCES.md` for provenance and the `scripts/download/` script that produced each.
- `external/` (not committed): raw public downloads (NSDUH, YRBS, NHANES, NTIA/Census supplement files, GSHS, HBSC reports, PISA 2022, ITU, state survey reports, policy sources). The download scripts recreate this directory.
- `extracts/` (not committed): slim microdata files produced by `scripts/extract/` and `scripts/download/` (ACS cells and person files, ATUS activity records, CPS supplement, MICS, IPUMS International, DHS, GSHS stacked file, NTIA person file, PISA student and school files). They derive from microdata whose terms do not allow redistribution.
- `ipums/` (not committed): where IPUMS extracts go after conversion to parquet, one file per sample, e.g. `ipums/usa/us2015a.parquet`, `ipums/atus/at2015_A.parquet` and `at2015_P.parquet`, `ipums/cps/cps2013_07s.parquet`, `ipums/ipumsi/ke2019a.parquet`, `ipums/dhs/np2022ir.parquet`. See `scripts/extract/README.md`.
- `raw/` (not committed): IPUMS MICS fixed-width files and their layouts.
