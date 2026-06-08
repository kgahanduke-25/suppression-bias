# Results summary — Erased at the margins

Release `2026-06-01`; ACS 2018–2022 5-year; county universe 3,143 (3,222 with ACS incl. territories,
3,017 with both exposures in 50 states + DC). Primary exposure ICE(race+income); sensitivity = self-
contained deprivation index. Estimand = most- vs least-deprived quintile rate ratio (RR), rate
difference (RD), population-weighted gradient. Numbers below are produced by the scripts in `python/`
and stored in this folder (`aim1_disparities.csv`, `aim2_erasure.csv`, `aim3_simulation.csv`,
`aim3_calibrated_sensitivity.csv`).

## Headline
Small-count suppression (period count < 16) **erases most rural and most-deprived counties** for
less-common cancers, yet the **population-weighted disparity point estimate is robust**; the harm is to
**representation** and to the **fragility of inference** (wide bounds, method sensitivity), not to the
headline ratio. Calibrated simulation shows population-weighted bias < 2% even at ~70% suppression,
with a direction that is conditional on the deprivation–county-size relationship.

## Aim 2 — erasure (incidence, ICE universe)
| Site | % counties erased | % population erased | % rural counties erased | % most-deprived Q5 erased |
|---|---|---|---|---|
| Breast (Female) | 7.4 | 0.2 | 11.4 | 9.9 |
| Stomach | 61.3 | 9.7 | 80.3 | 67.7 |
| Cervix | 75.7 | 17.4 | 94.4 | 81.8 |

Structural driver: most-deprived counties have median population **18,580** vs **146,684** in the least-
deprived (Q5/Q1 = 0.24×); deprivation–log(population) correlation = **−0.30**.

## Aim 1 — disparity under four methods (RR, ICE quintiles)
| Measure | Site | % suppressed | RR complete-case (95% CI) | RR model-based | RR bounding interval | Δ model vs CC |
|---|---|---|---|---|---|---|
| Incidence | Breast | 7.4 | 0.87 (0.85–0.89) | 0.87 | 0.87–0.87 | 0% |
| Incidence | Stomach | 61.3 | 1.37 (1.29–1.47) | 1.35 | 1.14–1.68 | −1.6% |
| Incidence | Cervix | 75.7 | 1.56 (1.46–1.66) | 1.50 | 1.24–2.03 | −3.6% |
| Mortality | Breast | 42.2 | 1.13 (1.07–1.18) | 1.13 | 1.06–1.18 | +0.1% |
| Mortality | Stomach | 80.4 | 1.58 (1.51–1.67) | 1.51 | 0.94–2.88 | −4.6% |
| Mortality | Cervix | 90.7 | 1.86 (1.65–2.09) | 1.56 | 0.81–6.05 | −16.0% |

Method sensitivity and bounding-interval width grow with suppression; at the extreme (cervix mortality,
91% suppressed) the disparity is weakly identified. (Breast incidence RR < 1 reflects the known higher
breast-cancer incidence in less-deprived areas.) Self-contained-index results parallel these (see CSV).

## Aim 3 — simulation vs ground truth (calibrated)
At the empirical deprivation–size correlation (−0.30), population-weighted complete-case RR bias is
**≈ 0 to −1% across base rates** (≤ 2% with overdispersion); unweighted county-unit analysis ≈ 2×.
Across the full grid, |relative bias| in RR reaches ~6% only at strong correlation (−0.6) + low threshold.
Direction is conditional: complete-case *over*-estimates when deprived counties are smaller (realistic),
*under*-estimates when county size is independent of deprivation. Magnitude scales with rarity/suppression
as pre-registered (OSF.IO/BJZR5).

## Pre-registration
OSF DOI 10.17605/OSF.IO/BJZR5. Direction was registered as conditional/characterized, consistent with
findings; no deviations requiring amendment.
