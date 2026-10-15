# IPUMS extracts

The analyses read slim parquet files in `data/extracts/`. They were produced here from IPUMS data with duckdb; a user with a standard IPUMS extract can produce the same files by converting the extract to parquet (one file per sample, IPUMS variable names as columns, for example with `ipumspy` reading the DDI and data file, then `DataFrame.to_parquet`) into `data/ipums/<product>/<sample>.parquet` and running the SQL here. Weights in IPUMS extracts are delivered with decimals already applied; the scripts note where the internal files used implied decimals (`notes/weights.md`).

## IPUMS USA (ACS 1-year, us2005a–us2024a)
Person-level variables: YEAR, SERIAL, PERNUM, PERWT, HHWT, AGE, SEX, RACE, HISPAN, BPL, CITIZEN, LANGUAGE, SCHOOL, GRADEATT, SCHLTYPE, EDUC, MIGRATE1, DIFFREM, DIFFCARE, DIFFSENS, DIFFEYE, DIFFHEAR, DIFFPHYS, DIFFMOB, POVERTY, FTOTINC, HHINCOME, HCOVANY, RELATE, MOMLOC, POPLOC, NCHILD, STATEFIP, COUNTYFIP, PUMA, CPUMA0010, MET2013, MET2013ERR, METRO, DENSITY, CINETHH, CIHISPEED, CIDATAPLN, CISMRTPHN, CIHAND, CILAPTOP, CIBRDBND, OWNERSHP, MULTGEN, and the replicate weights REPWTP1–REPWTP80. `acs_extract_sql.py` writes one SQL file per sample into `build/sql/` and a runner script; the internal files carried household variables with an `_H` suffix, so edit the column list in that script to drop the suffix when working from a standard extract.

## IPUMS CPS (Computer and Internet Use Supplement months)
`cps_internet_supplement.sql`: CI* supplement items, WTFINL, HWTFINL, CISUPPWT, CIPWT, STATEFIP, METFIPS, COUNTY, AGE, SEX, MISH, for the ten supplement samples listed in `DATA_SOURCES.md`.

## IPUMS ATUS (at2003–at2024)
`atus_extract.sql.template`: joins the activity file (ACTIVITY, DURATION, WHERE, START, ACTLINE, CASEID) to the respondent record (AGE, SEX, RACE, HISPAN, EDUC, SCHLCOLL, FULLPART, EMPSTAT, DAY, HOLIDAY, MONTH, DIFFREM, STATEFIP, METRO, METFIPS, HH_CHILD, FAMINCOME, WT06; WT20 for 2020). Substitute the sample name for `{sample}`.

## IPUMS International (ke2009a, ke2019a, mx2010a, mx2020a)
`ipumsi_extract.sql`: AGE, SEX, SCHOOL, EDATTAIN, DISABLED, DISMNTL, the source-variable Washington Group and ICT items named in the file, URBAN, GEOLEV2, GEO2_KE / GEO2_MX, CELL, INTERNET, COMPUTER, PERWT, HHWT.

## IPUMS DHS (np2022ir, ke2022ir)
`dhs_extract.sql`: the mental-health module scores and diagnosis items, internet and phone items, wealth, education, cluster, and PERWEIGHT.

## IPUMS MICS (fixed-width)
`mics_reader.py` reads IPUMS MICS fixed-width files with their layout files (space-separated: name, record type, start column, width, type) and `mics_extract.py` builds the children 5–17, women, men, and household extracts for every MICS6/MICS7 sample carrying the Child Functioning Module. Value labels are in the IPUMS MICS documentation; the codes used are listed in `notes/` and in the analysis script.
