<!-- Generated review chunk: mtf -->

[Index](../README.md) · [Full paper](../../Teen_Distress_Pilot.md#review-mtf)

Context: Teen Distress Pilot → Part 3 · School pressure (H2) → Monitoring the Future: homework, socializing, screens and distress among 12th graders, 1996–2012, and the student-level test that still needs the microdata

Editable source entry points: [scripts/report/90_build_report.py:1](../../../scripts/report/90_build_report.py#L1)

---

### Monitoring the Future: homework, socializing, screens and distress among 12th graders, 1996–2012, and the student-level test that still needs the microdata

Monitoring the Future (MTF) is the one U.S. survey that has asked the same adolescents about homework hours, evenings out, time with friends, screen use and a stable set of distress items every year since 1991, and it is the source behind most of the Twenge-side correlational evidence. Its public-use microdata (ICPSR/NAHDAP series 35, grades 8, 10 and 12) could not be obtained from this machine: icpsr.umich.edu answers a Cloudflare bot challenge (HTTP 403) to every non-interactive client tried, and downloads in any case require an ICPSR login with terms acceptance. We therefore use what MTF itself published: the annual *Questionnaire Responses from the Nation's High School Seniors* volumes, which print every item's weighted percentage distribution by sex, race, region and college plans. The volumes for the 1996–2012 surveys are the only ones ever posted as PDFs (the series ended with the 2012 volume) and were recovered from Internet Archive captures; each item is answered by one random sixth of the national sample (about 2,261 weighted cases for a single-form item, 12,130 for items on every form). The 17 volumes were parsed into 26 item series and pooled across forms weighting by the N answering. Standard errors use a design effect of 2, the midpoint of the volumes' own guidance.

![Chart: mtf_trends](../../figures/mtf_trends.png)

MTF 12th graders, 1996–2012, by sex (boys blue, girls orange, all dotted), with approximate 95% intervals. Homework and TV are means of category midpoints; the self-derogation and depressive-affect panels average the share endorsing the negative pole over four items each ("I feel I do not have much to be proud of", "Sometimes I think that I am no good at all", "I feel that I can't do anything right", "I feel that my life is not very useful"; "Life often seems meaningless", "The future often seems hopeless", disagree "I enjoy life as much as anyone", disagree "It feels good to be alive").

#### What moved before 2012, and what did not

Over 1996–2012, 12th graders' self-reported homework fell by roughly an hour a week (boys -0.78 (0.42) hours, girls -1.04 (0.42), from 6.9 to 5.9 hours for all students), so the MTF record does not show the rise in homework load that ATUS shows for school weekdays after 2003; MTF's weekly self-report is a different quantity from a diary, but Twenge and Park (2019) and Twenge, Spitzberg and Campbell (2019) read the same series as flat or declining back to 1976. In-person socializing, by contrast, fell steadily and well before smartphones: evenings out per week -0.19 (0.04) for boys and -0.25 (0.04) for girls, and the share getting together with friends informally almost every day -12.36 (2.09) and -8.82 (2.02) percentage points. Weekday television was flat (-0.05 (0.07) hours, all students), and the share getting seven or more hours of sleep most days rose by +4.71 (2.75) points for boys and +4.96 (2.68) for girls. Screen time did rise before the distress turn: personal internet use went from 6.6 to 11.0 hours a week between 2006 and 2012, daily social-networking from 49% to 71% (2008–2012; girls 78%), and electronic games from 6.6 to 9.9 hours a week. The distress items were, over the same sixteen years, essentially stable or improving: loneliness -2.80 (2.69) points for boys and -8.10 (2.76) for girls, self-derogation +1.79 (0.61) and +0.42 (0.62), depressive affect -1.55 (0.96) and -2.73 (0.93). The last two volumes catch at most the start of the post-2011 turn: between 2010 and 2012 girls' self-derogation rose +1.10 (0.62) points while their loneliness did not move (-1.40 (2.76)), and homework hours moved -0.33 (0.40) (girls) and -0.08 (0.41) (boys).

| Indicator (12th graders)                 | Boys 1996  | Boys 2012 | Δ 1996→2010            | Δ 2010→2012  | Girls 1996 | Girls 2012 | Δ 1996→2010            | Δ 2010→2012  |
|------------------------------------------|------------|-----------|------------------------|--------------|------------|------------|------------------------|--------------|
| Homework, hours/week (mean)              | 6.3        | 5.5       | -0.7 (0.4)             | -0.1 (0.4)   | 7.3        | 6.3        | -0.7 (0.4)             | -0.3 (0.4)   |
| Homework 10+ h/week, %                   | 22.3       | 17.0      | -3.8 (2.6)             | -1.5 (2.4)   | 27.6       | 20.8       | -5.8 (2.6)             | -1.0 (2.5)   |
| Evenings out per week (mean)             | 2.98       | 2.80      | -0.13 (0.04)           | -0.05 (0.04) | 2.60       | 2.35       | -0.17 (0.04)           | -0.08 (0.04) |
| Friends informally almost daily, %       | 55.4       | 43.0      | -9.2 (2.1)             | -3.1 (2.1)   | 44.3       | 35.5       | -3.3 (2.0)             | -5.5 (2.0)   |
| Dates weekly or more, %                  | 44.6       | 31.6      | -9.3 (1.2)             | -3.7 (1.2)   | 46.8       | 30.2       | -11.2 (1.2)            | -5.4 (1.2)   |
| TV on a weekday, hours (mean)            | 2.21       | 2.12      | -0.13 (0.10)           | +0.04 (0.10) | 2.08       | 2.05       | -0.14 (0.10)           | +0.11 (0.10) |
| Internet for personal use, h/week (mean) | 7.6 (2006) | 11.8      | +4.2 (0.8) (2006–2012) | +1.7 (0.8)   | 5.8 (2006) | 10.3       | +4.4 (0.7) (2006–2012) | +2.2 (0.7)   |
| Works during the school year, %          | 74.0       | 57.8      | -15.8 (1.2)            | -0.4 (1.2)   | 77.7       | 60.9       | -18.0 (1.1)            | +1.2 (1.2)   |
| 7+ hours of sleep most days, %           | 56.1       | 60.8      | +0.3 (2.8)             | +4.4 (2.1)   | 47.6       | 52.6       | +2.5 (2.7)             | +2.4 (2.1)   |
| Lonely: agree, %                         | 27.7       | 24.9      | -4.8 (2.7)             | +2.0 (2.6)   | 37.3       | 29.2       | -6.7 (2.8)             | -1.4 (2.8)   |
| Often feels left out, %                  | 23.4       | 27.1      | +1.5 (2.6)             | +2.2 (2.7)   | 34.8       | 33.4       | -4.9 (2.8)             | +3.5 (2.8)   |
| Self-derogation, mean % agree (4 items)  | 13.0       | 14.8      | +0.5 (0.6)             | +1.3 (0.6)   | 15.2       | 15.6       | -0.7 (0.6)             | +1.1 (0.6)   |
| Depressive affect, mean % (4 items)      | 11.9       | 10.3      | -1.1 (1.0)             | -0.5 (1.0)   | 12.5       | 9.8        | -2.8 (0.9)             | +0.1 (0.9)   |
| Very happy, %                            | 19.9       | 26.3      | +4.7 (1.1)             | +1.7 (1.2)   | 17.2       | 21.7       | +5.1 (1.0)             | -0.5 (1.1)   |
| Not too happy, %                         | 14.9       | 12.6      | -2.9 (0.9)             | +0.6 (0.9)   | 15.0       | 12.9       | -2.2 (0.9)             | +0.1 (0.9)   |
| Life satisfaction, mean (1-7)            | 5.01       | 5.14      | +0.08 (0.06)           | +0.06 (0.07) | 4.98       | 5.12       | +0.19 (0.05)           | -0.05 (0.06) |

Levels in 1996 and 2012 and changes with approximate SEs (design effect 2). Pooled across questionnaire forms; loneliness and the left-out item are on one form (n ≈ 2,270), happiness on all six.

At the year level the series that declined together over 1996–2012 (friends, evenings out, homework, loneliness, depressive affect) are positively correlated in levels, which is shared trend rather than evidence of anything; in first differences the correlations of the exposures with loneliness, self-derogation and depressive affect run from -0.67 (evenings out with self-derogation) to +0.50 (homework hours with loneliness) over seventeen points, with nothing in between that survives the number of pairs tried. Table: Pearson r in levels / in first differences (years).

| Year-level exposure  | Lonely             | Self-derogation    | Depressive affect  |
|----------------------|--------------------|--------------------|--------------------|
| Homework hours       | +0.63 / +0.50 (17) | +0.05 / +0.45 (17) | +0.45 / +0.22 (17) |
| Evenings out         | +0.46 / -0.43 (17) | -0.62 / -0.67 (17) | +0.42 / -0.14 (17) |
| Friends almost daily | +0.58 / -0.13 (17) | -0.58 / -0.47 (17) | +0.46 / +0.03 (17) |
| TV hours (weekday)   | +0.51 / +0.05 (17) | -0.20 / -0.06 (17) | +0.51 / +0.14 (17) |
| 7+ h sleep most days | -0.10 / -0.11 (17) | +0.20 / -0.25 (17) | -0.09 / +0.00 (17) |
| Works                | +0.54 / +0.09 (17) | -0.50 / +0.15 (17) | +0.27 / -0.18 (17) |

Year-level co-movement of 12th-grade means, all students. Seventeen annual points; these are descriptive, not estimates of an effect.

#### 8th and 10th graders, 1991–2014, from a published table
