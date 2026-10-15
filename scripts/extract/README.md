# IPUMS extracts

The analyses read slim parquet files in `data/extracts/`. They were produced from IPUMS data with duckdb; a user with a standard IPUMS extract can produce the same files by converting the extract to parquet (one file per sample, IPUMS variable names as columns, for example with `ipumspy` reading the DDI and data file, then `DataFrame.to_parquet`) into `data/ipums/<product>/<sample>.parquet` and running the generators and SQL here. The generated runners create the output directories; when running a `.sql` file directly, create `data/extracts/<product>/` first.

## Column-name conventions

The files used for the report came from IPUMS-internal copies whose column names differ from a standard extract. The slim files and the analysis scripts keep the internal names; the generators map a standard extract onto them.

| internal name (kept in the slim files) | standard extract name |
|---|---|
| `YEARP`, `SERIALP` (ACS, IPUMS International) | `YEAR`, `SERIAL` |
| household variables with `_H` (`STATEFIP_H`, `MET2013_H`, `HHWT_H`, `URBAN_H`, `CELL_H`, ...) | the same name without `_H` |
| ATUS `CASEIDA` (activity record), `CASEIDP` (person record) | `CASEID` |
| ATUS `PSERIALA`, `PSERIAL` | `LINENO` |
| ATUS `RESP` (1 = diary respondent) | not present; respondents are the rows with `WT06 > 0` |
| CPS `YEAR_H`, `SERIAL_H`, ... | `YEAR`, `SERIAL`, ... |

Weights. The internal ACS `PERWT` carries two implied decimals, and the slim files keep it in hundredths (the ACS scripts divide by 100); the generator multiplies a standard extract's `PERWT` by 100 to match. Internal CPS weights carry four implied decimals and the generator divides them by 10,000 (a standard extract's weights are already decimal). ATUS `WT06` is copied as delivered; the analysis uses weight ratios only. DHS `PERWEIGHT` is divided by 1e6 in the analysis script. See `notes/weights.md`.

## IPUMS USA (ACS 1-year, us2005a–us2024a)
`acs_extract_sql.py` writes one SQL file per sample into `build/sql/` plus `run_extract.sh`. Person-level variables: YEAR, SERIAL, PERNUM, PERWT, HHWT, AGE, SEX, RACE, HISPAN, BPL, CITIZEN, LANGUAGE, SCHOOL, GRADEATT, SCHLTYPE, EDUC, MIGRATE1, DIFFREM, DIFFCARE, DIFFSENS, DIFFEYE, DIFFHEAR, DIFFPHYS, DIFFMOB, POVERTY, FTOTINC, HHINCOME, HCOVANY, RELATE, MOMLOC, POPLOC, NCHILD, STATEFIP, COUNTYFIP, PUMA, CPUMA0010, CPUMA1020, MET2013, MET2013ERR, MET2023, METRO, DENSITY, CINETHH, CIHISPEED, CIDATAPLN, CISMRTPHN, CIHAND, CILAPTOP, CIBRDBND, OWNERSHP, MULTGEN; the cell file also needs the replicate weights REPWTP1–REPWTP80. Variables a sample does not carry (the CI* items before 2013, CPUMA1020 and MET2023 in older samples) are written as NULL.

## IPUMS CPS (Computer and Internet Use Supplement months)
`cps_extract_sql.py` writes `build/sql/cps_internet_supplement.sql` and `run_cps.sh` for the ten supplement samples (cps2009_10s, cps2010_10s, cps2011_07s, cps2012_10s, cps2013_07s, cps2015_07s, cps2017_11s, cps2019_11s, cps2021_11s, cps2023_11s): the CI* supplement items, WTFINL, HWTFINL, CISUPPWT, CIPWT, YEAR, MONTH, SERIAL, PERNUM, CPSID, CPSIDP, MISH, STATEFIP, COUNTY, METFIPS, METAREA, METRO, CBSASZ, INDIVIDCC, FAMINC, HHTENURE, AGE, SEX, RACE, HISPAN. Output: `data/extracts/cps/cps_ci_<sample>.parquet`.

## IPUMS ATUS (at2003–at2024)
`atus_extract.py` writes `build/sql/atus_<sample>.sql` and `run_atus.sh`. Each joins the activity records (ACTIVITY, DURATION, WHERE, START, ACTLINE, CASEID, LINENO) to the diary respondent's person record (YEAR, CASEID, LINENO, RESP, AGE, SEX, RACE, HISPAN, EDUC, SCHLCOLL, FULLPART, EMPSTAT, DAY, HOLIDAY, MONTH, DIFFREM, STATEFIP, METRO, METFIPS, HH_CHILD, FAMINCOME, POVERTY185, KIDBEDTIME, GENHEALTH, WBWT, WT06 written as WT, and WT20 for 2020). A hierarchical extract is split into `<sample>_A.parquet` and `<sample>_P.parquet` by record type before conversion.

## IPUMS International (ke2009a, ke2019a, mx2010a, mx2020a)
`ipumsi_extract.sql`: YEAR, SERIAL, PERWT, AGE, SEX, SCHOOL, LIT, EDATTAIN, DISABLED, DISMNTL, DISPSYC, the source-variable Washington Group and ICT items named in the file, HHWT, URBAN, GEOLEV2, GEO2_KE / GEO2_MX (written as GEO2), CELL, INTERNET, COMPUTER and the household source variables. The file uses the internal names (`YEARP`, `_H`); edit them for a standard extract as in the table above.

## IPUMS DHS (np2022ir, ke2022ir)
`dhs_extract.sql`: SAMPLE, COUNTRY, YEAR, IDHSPSU, CLUSTERNO, PERWEIGHT, AGE, URBAN, WEALTHQ, EDUCLVL, the mental-health module (DEPRESSIONSCORE, DEPRESSIONREFER, GADSCORE, DEPRESSIONDIAG, ANXIETYDIAG), and the internet and phone items (INTERNETEVYR, INTERNETMO, CELLPHONSELF, CELLPHONESMART, MOBPHONE).

## IPUMS MICS (fixed-width)
`mics_reader.py` reads IPUMS MICS fixed-width files with their layout files (space-separated: name, record type, start column, width, type) and `mics_extract.py` builds the children 5–17, women, men, and household extracts for every MICS6/MICS7 sample carrying the Child Functioning Module. Value labels are in the IPUMS MICS documentation; the codes used are listed in `notes/` and in the analysis script.
