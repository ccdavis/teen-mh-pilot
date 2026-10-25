<!-- Generated review chunk: what-the-student-level-mtf-literature-already-answers-2 -->

[Index](../README.md) · [Full paper](../../Teen_Distress_Pilot.md#review-what-the-student-level-mtf-literature-already-answers-2)

Context: Teen Distress Pilot → Part 3 · School pressure (H2) → Monitoring the Future: homework, socializing, screens and distress among 12th graders, 1996–2012, and the student-level test that still needs the microdata → What the student-level MTF literature already answers

Editable source entry points: [scripts/report/90_build_report.py:1](../../../scripts/report/90_build_report.py#L1)

---

Student-level MTF estimates as published (verified against the abstract, PMC full text or the paper where accessible; two entries flagged in the methods note could not be verified beyond the abstract). Full citations in `data/compiled/mtf/mtf_literature.csv`.

#### The prepared microdata test

`scripts/analysis/31_mtf.py` is written to run on the ICPSR files once they are placed in `data/external/mtf/icpsr/<study>/` (0 files found at this run). It locates variables through the MTF variable labels (the OSIRIS abbreviations printed in the volumes' cross-time index), with the 8th/10th-grade V-codes from Orben and Przybylski's public replication code as confirmed anchors, and estimates, by sex and grade with year fixed effects, race/ethnicity, parent education, region and the design weight, depressive affect, loneliness and happiness on homework hours, social-media hours and their product, followed by a year-effects decomposition of the change since 2012. The study numbers to request are listed in the script header; the 12th-grade files for 2013–2024 are the binding gap, since they carry the hours-per-day social-media item that the published volumes never reached.

**Assessment.** Nothing in the published MTF record supports the H2 premise for 12th graders: self-reported homework fell by about an hour a week from 1996 to 2012 (boys -0.78 (0.42), girls -1.04 (0.42)) and fell for 8th/10th graders from 1991 to 2014, while in-person socializing declined steadily through the whole period and TV time was flat; loneliness and depressive affect were lower in 2012 than in 1996 and self-derogation only slightly higher, with girls' self-derogation (+1.10 (0.62) points, 2010–2012) the one sign of the turn that Keyes et al. date to 2012. That ordering fits Haidt's and Gray's shared claim that face-to-face time was eroding before smartphones, and it leaves the H1 question to the 2013–2024 microdata. The literature answers the H1 main effect (a dose gradient in hours, a null at the daily-use margin) and shows homework as protective at the individual level, but the H3 interaction of homework with social-media hours has not been estimated by anyone; the pipeline here will estimate it as soon as the ICPSR files can be downloaded by an account holder.
