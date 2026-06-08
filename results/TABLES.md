# Results tables (auto-generated; numbers from scp.duckdb)

## Table 1. Characteristics of US counties (n=3,143) by ICE Race+Income quintile, ACS 2018–2022.
Unit = county. Population-weighted ICE quintiles (unequal county counts). Std. diff = standardized difference, Q1 vs Q5.

| Characteristic                                           | Overall                | Q1 most deprived (n=549)   | Q2 (n=657)             | Q3 (n=645)             | Q4 (n=742)             | Q5 least deprived (n=425)   |   Std. diff (Q1 vs Q5) |
|:---------------------------------------------------------|:-----------------------|:---------------------------|:-----------------------|:-----------------------|:-----------------------|:----------------------------|-----------------------:|
| Population, median [IQR]                                 | 26,704 [11,597–70,194] | 18,890 [9,483–41,986]      | 23,023 [10,839–56,351] | 25,709 [12,498–62,723] | 32,294 [11,957–79,398] | 53,381 [19,794–167,567]     |                   0.16 |
| Urban (SCP designation), n (%)                           | 1,157 (38.3)           | 146 (26.6)                 | 196 (29.8)             | 220 (34.1)             | 293 (39.5)             | 302 (71.1)                  |                   0.89 |
| % Black, mean (SD)                                       | 9.0 (14.3)             | 26.9 (22.2)                | 8.5 (10.3)             | 4.3 (6.2)              | 3.4 (5.0)              | 3.2 (4.1)                   |                   1.48 |
| % Hispanic, mean (SD)                                    | 10.2 (13.9)            | 18.4 (24.3)                | 11.1 (12.8)            | 7.9 (8.5)              | 7.1 (7.0)              | 7.6 (6.5)                   |                   0.6  |
| Median household income ($), median [IQR]                | 65,691 [56,520–75,854] | 51,424 [45,363–58,018]     | 58,239 [52,018–65,387] | 63,501 [59,450–68,464] | 72,637 [67,590–77,992] | 89,975 [81,136–103,670]     |                   2.79 |
| ICE Race+Income, median [IQR]                            | 0.2 [0.1–0.3]          | -0.0 [-0.1–0.0]            | 0.1 [0.1–0.2]          | 0.2 [0.2–0.2]          | 0.3 [0.2–0.3]          | 0.3 [0.3–0.4]               |                   5.04 |
| Breast incidence /100k (reported counties), median [IQR] | 126.9 [114.3–138.9]    | 123.1 [107.4–135.6]        | 122.3 [108.5–133.9]    | 123.9 [113.0–134.7]    | 129.6 [118.7–139.9]    | 137.8 [127.0–146.2]         |                   0.68 |
| Cervix incidence /100k (reported counties), median [IQR] | 7.9 [6.5–9.9]          | 9.9 [8.1–11.8]             | 8.8 [7.4–11.5]         | 8.4 [7.1–9.9]          | 7.4 [6.4–8.9]          | 6.0 [5.1–7.3]               |                   1.52 |

## Table 2A. Estimated breast-cancer incidence disparity by suppression-handling method (most- vs least-deprived ICE quintile).

| Handling method                                   | Rate ratio (95% CI)   |   Rate difference (/100k) | Counties included   |   % most-deprived counties retained |
|:--------------------------------------------------|:----------------------|--------------------------:|:--------------------|------------------------------------:|
| Complete-case (population-weighted)               | 0.87 (0.85–0.89)      |                     -18.4 | 2,794               |                                  90 |
| Complete-case (unweighted county-mean)            | 0.90 (0.88–0.92)      |                     -13.8 | 2,794               |                                  90 |
| Available-case (= complete-case; retention shown) | 0.87 (0.85–0.89)      |                     -18.4 | 2,794 of 3,018      |                                  90 |
| Bounding — impute 0                               | 0.87                  |                     -18.8 | 3,018               |                                 100 |
| Bounding — impute threshold                       | 0.87                  |                     -18.4 | 3,018               |                                 100 |
| Model-based (small-area)                          | 0.87 (0.85–0.89)      |                     -18.4 | 3,018               |                                 100 |

## Table 2B. Estimated cervix-cancer incidence disparity by suppression-handling method.

| Handling method                                   | Rate ratio (95% CI)   |   Rate difference (/100k) | Counties included   |   % most-deprived counties retained |
|:--------------------------------------------------|:----------------------|--------------------------:|:--------------------|------------------------------------:|
| Complete-case (population-weighted)               | 1.56 (1.46–1.67)      |                       3.3 | 732                 |                                  18 |
| Complete-case (unweighted county-mean)            | 1.61 (1.49–1.73)      |                       3.9 | 732                 |                                  18 |
| Available-case (= complete-case; retention shown) | 1.56 (1.46–1.67)      |                       3.3 | 732 of 3,018        |                                  18 |
| Bounding — impute 0                               | 1.24                  |                       1.5 | 3,018               |                                 100 |
| Bounding — impute threshold                       | 2.03                  |                       5.2 | 3,018               |                                 100 |
| Model-based (small-area)                          | 1.50 (1.42–1.59)      |                       3   | 3,018               |                                 100 |

## Table 3A. Suppression diagnostics by ICE quintile — breast incidence.

| ICE quintile      |   Counties, n | Suppressed, n (%)   |   % population in suppressed counties |   % rural population erased |   % minority population erased |
|:------------------|--------------:|:--------------------|--------------------------------------:|----------------------------:|-------------------------------:|
| Q1 most deprived  |           549 | 55 (10.0)           |                                   0.3 |                         2.1 |                            0.3 |
| Q2                |           657 | 47 (7.2)            |                                   0.2 |                         1.2 |                            0.1 |
| Q3                |           645 | 46 (7.1)            |                                   0.2 |                         1.1 |                            0.1 |
| Q4                |           742 | 51 (6.9)            |                                   0.2 |                         0.9 |                            0.1 |
| Q5 least deprived |           425 | 25 (5.9)            |                                   0.1 |                         1.9 |                            0.1 |

## Table 3B. Suppression diagnostics by ICE quintile — cervix incidence.

| ICE quintile      |   Counties, n | Suppressed, n (%)   |   % population in suppressed counties |   % rural population erased |   % minority population erased |
|:------------------|--------------:|:--------------------|--------------------------------------:|----------------------------:|-------------------------------:|
| Q1 most deprived  |           549 | 449 (81.8)          |                                  15   |                        78.3 |                           11.9 |
| Q2                |           657 | 505 (76.9)          |                                  14.5 |                        80.9 |                            7   |
| Q3                |           645 | 502 (77.8)          |                                  19.9 |                        82.4 |                            8.6 |
| Q4                |           742 | 559 (75.3)          |                                  22.9 |                        81.1 |                           10.4 |
| Q5 least deprived |           425 | 271 (63.8)          |                                  14.7 |                        88.7 |                            8   |

Abbreviations: ICE, Index of Concentration at the Extremes; RR, rate ratio; RD, rate difference; CI, confidence interval; IQR, interquartile range; SCP, State Cancer Profiles. Source: NCI State Cancer Profiles release 2026-06-01; ACS 2018–2022 5-year. Suppression rule: rates with period count <16 not reported.
