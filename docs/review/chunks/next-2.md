<!-- Generated review chunk: next-2 -->

[Index](../README.md) · [Full paper](../../Teen_Distress_Pilot.md#review-next-2)

Context: Teen Distress Pilot → Conclusions and next steps

Editable source entry points: [scripts/report/90_build_report.py:713](../../../scripts/report/90_build_report.py#L713)

---

- **Done from public files or IPUMS copies:** NHIS Sample Child 2021–2024 against the published NHIS-Teen estimates; NSCH 2016–2025; the DHS-8 mental-health modules pooled across Nepal, Mozambique, and Bangladesh with the module inventory of all 31 DHS-8 reports; NVSS monthly suicide seasonality 1999–2024; the PISA 2012–2022 four-wave panel with the 2015 test-anxiety interaction; Monitoring the Future's published 12th-grade series 1996–2012; county broadband coverage 2010–2021 and the AT&T 2010 footprint; the Pennsylvania 2025 and California 2019–25 county waves; the 2025 YRBS state files with the pre-specified phone-ban difference-in-differences; and the ATUS 2025 and Bangladesh MICS 2025 releases.
- **Blocked, with the pipeline written and waiting for access:** the NHIS-Teen microdata (Research Data Center only), the Monitoring the Future microdata (ICPSR login; `scripts/analysis/31_mtf.py` runs its student-level homework × social-media models once the files are placed), the DHS-8 men's files, Zambia 2024 and Lesotho's PHQ-9 (DHS Program data request), county youth-suicide counts under 10 (restricted NVSS), and Minnesota's 2022 and 2025 county tables (bot-manager CAPTCHA; the request specification is in `notes/state_surveys.md`).
- **To add as released:** NSCH 2026 (first full post-mandate year for the 19 states of the 2025–26 wave), YRBS 2025 and 2027 (the pre-specified ban difference-in-differences in `scripts/analysis/33_yrbs_ban_did.py`), the 2026–27 county waves around the Minnesota, Maine, California, and Illinois mandates, and PISA 2025 (the first wave with both the phone-ban item and hours).
- **Licensed data still worth requesting:** GSMA mobile-coverage polygons with MICS and DHS cluster coordinates; student-level HBSC microdata (schoolwork pressure × social-media use × school phone rules); NCHS Research Data Center access to NHIS-Teen linked to the Sample Child. Further extensions of the ACS market event study or the IPUMS International census item are not warranted.

Reproducibility: analysis scripts are in `scripts/` and output tables are in `results/tables/` of the project repository. Data sources: IPUMS USA (ACS 1-year 2005–2024), IPUMS ATUS 2003–2025, IPUMS MICS (69 surveys), IPUMS International (Kenya 2009/2019, Mexico 2010/2020), IPUMS DHS (Nepal, Mozambique, Bangladesh, Kenya, Madagascar) with 31 DHS-8 final reports, Census CPS Computer and Internet Use Supplements (2009–2023), OECD PISA 2012, 2015, 2018 and 2022, WHO GSHS (165 country-rounds), WHO HBSC, NCHS NHIS Sample Child 2021–2024 and NHIS-Teen published estimates, HRSA/Census NSCH 2016–2025, CDC WONDER/NVSS mortality 1999–2024, Monitoring the Future data volumes 1996–2012, the NTIA National Broadband Map and FCC Form 477, and public NSDUH, NHANES, YRBS, NCES SSOCS/School Pulse, and state youth survey files as documented in each section.
