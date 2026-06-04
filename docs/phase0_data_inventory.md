# Phase 0 — Data Inventory (COMPLETE)

**Project:** Erased at the margins — small-count suppression bias in county-level cancer disparities
**Release used:** `2026-06-01` (latest tag) | **Source:** github.com/seandavi/state-cancer-profile-scraper
**Sites:** Breast (Female), Cervix, Stomach | **Pipeline:** Python+DuckDB now, R port for repo

## Files acquired (data/raw/, arrived decompressed)
- `state_cancer_profiles_incidence.csv` — 601 MB, 1,476,853 rows (1,351,271 county rows)
- `state_cancer_profiles_mortality.csv` — 426 MB
- `state_cancer_profiles_demographics.csv` — 1.4 GB (ACS/SVI, long format by topic)
- `state_cancer_profiles_risk.csv` — 32 MB (BRFSS, model-based covariates only)

## Schema (incidence/mortality, 29 cols)
Key: `fips`, `state_fips`; strata: `cancer`, `sex`, `race`, `stage`, `age`, `year`(=Latest 5-year average), `measurement`, `locale_type`(county/state/national). Rate: `age_adjusted_rate_per_100_000` (+ `lower_ci_rate`,`upper_ci_rate`), `average_annual_count`, trend cols. Rural flag embedded: `2023_rural_urban_continuum_codesrural_urban_note` (Rural/Urban only — full 1-9 RUCC still to be merged from USDA). `\N` = null token.

## Strata available (county)
- sex: Both Sexes / Male / Female
- race: All Races (incl. Hispanic), White NH, Black NH, Hispanic, Asian/PI NH, AI/AN NH
- stage: All Stages / Late Stage
- age: All Ages (+ age bands)
- County universe: 3,143 (confirmed by demographics `rank` = "1 of 3143"); 3,029 counties appear at least once.

## Suppression rule — CONFIRMED
- **Threshold: period count < 16 -> suppressed** (NCI State Cancer Profiles; CDC USCS). Stability (SE >= ~25% of rate) + confidentiality.
- **Manifestation: suppressed counties are ABSENT** (no row), not null-flagged. Empirically, min non-null `average_annual_count` ~ 3.0 => boundary ~ 16/5 = 3.2 annual. This is informative (NMAR) missingness -> complete-case bias is non-ignorable.

## HEADLINE Phase 0 result (incidence; All Races, All Stages, All Ages)
| Site | Counties w/ rate | Suppressed (of 3143) | % suppressed |
|---|---|---|---|
| Breast (Female) | 2,805 | 338 | 10.8% |
| Stomach | 1,178 | 1,965 | 62.5% |
| Cervix | 741 | 2,402 | 76.4% |

Strong rarity gradient => the bias gradient will be visible. Among counties that *retain* a rate, rare sites skew urban (e.g., Cervix retains only 106 rural vs 635 urban) — the Aim 2 erasure story, directionally confirmed.

## Deprivation/ICE inputs (demographics file, county-level, self-contained)
Income (median household & family $), Poverty (% below, % <150%, persistent-poverty flag), Education, Crowding, Food insecurity, Insurance (by poverty band), Racial composition (% Black/Hispanic/AI-AN/API/White), **SVI overall + 4 subdomains** (Socioeconomic, Household, Housing/Transport, Racial/Ethnic Minority).
- NOTE: file has income **medians only**, not ACS income brackets => canonical Krieger **ICE(race+income) requires external ACS** (Census API, blocked in sandbox -> needs user key + local pull). Decision pending (see chat).

## Environment
Python 3.10 + DuckDB (working DB kept in sandbox-local storage; cloud-synced Drive blocks DuckDB WAL). No R in sandbox; R+DuckDB port to be written for the published repo. Census API + GitHub release CDN both blocked in sandbox (data pulled locally by user).
