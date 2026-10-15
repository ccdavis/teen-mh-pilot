# IPUMS International scan (pilot step 9), 2026-09-16
IPUMS International samples used: ke2009a, ke2019a, mx2010a, mx2020a, za2011a, za2016a, pe2007a, pe2017a, br2010a, gh2010a (no gh2021a, no za2022a).

Harmonized: DISMNTL (mental disability; ke2009a, ke2019a, mx2010a, mx2020a, za2016a, br2010a, gh2010a, pe2017a), DISPSYC (mx2020a only),
CELL (household cell phone; ke2009a, ke2019a, mx2010a, mx2020a, za*, pe*, br2010a), INTERNET (ke2019a, mx2010a, mx2020a, ...), COMPUTER.

Source variables (per person unless noted):
- Kenya 2019: KE2019A_0450 difficulty remembering/concentrating (WG), 0447-0452 other WG items; 0469 owned mobile phone last 3 months, 0470 used mobile,
  0471 used internet any location, 0472 used computer/tablet; household: 0121 member owns mobile/modem with internet, 0122 fixed internet, 0123 computer.
- Kenya 2009: 0061 household mobile phone, 0440 mobile phone service, 0443 internet use, 0444 main internet location; DISMNTL; 0431 difficulty working.
- Mexico 2020: MX2020A_0421 difficulty remembering/concentrating (WG), 0424 mental problem/condition, 0428 reason; household 0069 computer, 0071 cell phone, 0072 internet.
- Mexico 2010: MX2010A_0422 mental limitation (different wording from 2020 WG item); household 0056 computer, 0058 cell phone, 0059 internet.
Geography: GEO2_KE (district, consistent 1969-2019), GEO2_MX (municipality, consistent 1960-2020), GEOLEV2 world-consistent; URBAN; PERWT.
Verdict: Kenya pair is the best two-point design (same WG-style item? verify 2009 wording); Mexico 2020 gives a cross-sectional dose-response by municipality.

## Results (scripts/analysis/11_ipumsi_census.py, results/tables/ipumsi_*.csv)
- Prevalence 12-17 of "difficulty remembering/concentrating" (any): Kenya 2019 0.8-1.0% (boys > girls); Mexico 2020 1.0-1.8% (boys > girls). Severe (a lot/cannot): 0.2-0.7%.
  2009/2010 "mental disability" items: Kenya 0.4-0.5%, Mexico 0.5-0.9%. Wording change dominates any 2010-round vs 2020-round comparison.
- Sex pattern: boys > girls at all child ages in both countries (a disability/developmental item, like ACS DIFFREM), reversing only at 65+.
- Dose: Kenya 2019 per-person phone ownership 15-17 = 18% boys / 14% girls (internet use 14% / 11%); 18-24 = 67%. Mexico 2020 household internet 12-17 ≈ 45%, cell ≈ 90%.
- District dose-response (12-17, district x sex cells, urban control, sex FE, SE clustered by district): Kenya phone/internet coefficients ≈ 0 (within ±0.01 pp per pp of dose); Mexico household internet +0.007 pp/pp (SE 0.001), household cell +0.007 pp/pp (SE 0.002) on "any" (tiny: a one-SD rise in municipal household internet, 21 pp, moves a 1.4% rate by 0.14 pp).
- Data caveat: ke2019a household CELL_H (11%) is implausibly low relative to the source items and is not used as a dose; the per-person items KE2019A_0469/0471 are used for Kenya. (An earlier note that INTERNET_H was 97% was an artifact of reading code 1 as "yes"; INTERNET is 1 = no, 2 = yes, and the corrected household-internet shares are 2% for Kenya 2019 and 53-56% for Mexico 2020 at ages 12-17. Fixed 2026-10-15.)
- Verdict: the census cognitive item is not sensitive to adolescent distress; keep this arm as corroborating only, as the plan anticipated. A better census outcome does not exist; MICS/GSHS remain the developing-country outcomes.
