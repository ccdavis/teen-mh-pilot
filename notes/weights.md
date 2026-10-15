# ACS extract conventions
- Source: IPUMS USA 1-year ACS samples us2005a-us2024a (usa.ipums.org). In the internal file layout used here, household variables are carried on the person record with an `_H` suffix; a standard IPUMS extract delivers them on each person record without the suffix.
- PERWT and HHWT_H have 2 implied decimals (PERWT/100 = person weight). REPWTP1-80 are integral (same scale as PERWT/100). Verified: sum(PERWT)/100 = sum(REPWTP1) = US population.
- DIFFREM: 0 N/A (age<5), 1 no, 2 yes. Pre-2008 wording differs (2005-07 rates ~1.4pp higher for 12-17); series starts 2008.
- CIDATAPLN, CISMRTPHN: 0 N/A(GQ), 1 yes, 2 no, 8 suppressed (2023-24 select PUMAs). CINETHH: 1 yes w/ subscription, 2 yes w/o, 3 no. CIHISPEED: 10-17 yes, 20 no.
- MET2013: 0 = not in identifiable metro; market key = met2013 if >0 else statefip*100000 (state non-metro remainder).
- SEs: successive-difference replication, var = 4/80 * sum_r (theta_r - theta)^2.
- 2020 1-year ACS is the experimental release (nonresponse bias); flag in all plots.
