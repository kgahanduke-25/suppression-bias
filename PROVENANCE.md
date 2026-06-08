# PROVENANCE — lab notebook (reproducibility log)

Update whenever a script is re-run. Every manuscript number must trace to a file listed here.

## 1. Data sources (frozen)
- **Cancer rates:** NCI State Cancer Profiles via public mirror `seandavi/state-cancer-profile-scraper`,
  **release tag `2026-06-01`**. Assets used:
  `state_cancer_profiles_incidence.csv`, `state_cancer_profiles_mortality.csv`,
  `state_cancer_profiles_demographics.csv` (incidence/mortality arrived decompressed from `.csv.gz`).
  County rows = `locale_type='county'`. Rate field = `age_adjusted_rate_per_100_000` (per 100k, age-adjusted).
  Counts = `average_annual_count`. Null token `\N`.
- **ACS (primary ICE exposure):** ACS **2018–2022 5-year** (year=2022), U.S. Census Bureau API via `tidycensus`.
  Tables: `B19001` (household income, all), `B19001H` (household income, White non-Hispanic), `B01003_001` (total population).
- **Rurality:** embedded Rural/Urban flag (`2023_rural_urban_continuum_codesrural_urban_note`); full USDA RUCC 2023 (future merge).

## 2. ICE(race+income) — definition & quintiles
- A = White-NH households with income ≥ $100,000 = B19001H brackets 014–017.
- P = households of color (all − White-NH) with income < $25,000 = (B19001 002–005) − (B19001H 002–005), floored at 0.
- T = total households = B19001_001.  **ICE = (A − P) / T**, range [−1, +1]; lower = more deprived.
- **Quintiles:** population-weighted (county pop = B01003_001 as weight), cut on the U.S. county universe
  (excl. PR/territories: state FIPS 72/78/60/66/69) BEFORE outcomes examined.
  ICE quintile coded 1 = most deprived (lowest ICE); the analysis flips to dep_q where **5 = most deprived**.
- **Self-contained sensitivity exposure:** mean of five z-scored ACS marginals from the demographics file
  (−median household income, % below poverty, % <9th-grade, −% bachelor's+, % crowding); higher = more deprived; pop-weighted quintiles (5 = most deprived). Robustness: CDC/ATSDR SVI overall.

## 3. Scripts (run order, purpose, seed)
1. `R/pull_acs_ice.R` (or `python/pull_acs_ice.py`) — ACS pull → `data/raw/county_ice.csv`. (no RNG)
2. `python/01_build_pipeline.py` — ingest rates+demographics, build exposures + pop-weighted quintiles
   → `data/processed/scp.duckdb`, `exposure_master.csv`. (no RNG)
3. `python/run_aims_1_2.py` — Aim 1 disparities (4 methods) + Aim 2 erasure. **Bootstrap seed = 20260604**, B = 2000.
   → `results/aim1_disparities.csv`, `results/aim2_erasure.csv`.
4. `python/run_aim3.py` — full simulation grid. **Seeds = 20260604 + cell index.** reps = 1000/cell.
   → `results/aim3_simulation.csv`.
5. `python/calib_sim.py` — calibrated sensitivity (real corr, Poisson + overdispersed, weighted + unweighted).
   reps = 800. → `results/aim3_calibrated_sensitivity.csv`.
6. `python/make_figures.py` — figures → `figures/fig1_erasure.png`, `fig2_disparity_methods.png`, `fig3_simulation.png`.
- Engine: `python/analysis_engine.py` (executed reference) / `R/analysis_engine.R` (canonical port).
- Versions: Python 3.10; duckdb 1.5.3, pandas 2.3.3, numpy 2.2.6, matplotlib 3.10.8 (`requirements.txt`).

## 4. Calibrated simulation parameters (fit to release 2026-06-01 + ACS)
- County size: `pop_meanlog = 10.272`, `pop_sdlog = 1.50` (empirical log county population).
- Deprivation–size relationship (`dep_pop_shift`): **corr(log pop, deprivation index) = −0.30**; corr(log pop, ICE) = −0.18.
  Median population Q1 (least deprived) = 146,684 vs Q5 (most deprived) = 18,580 (Q5/Q1 = 0.24×).
- Overdispersion (`od_sd`): gamma-Poisson with extra-variance parameter 0.0 (Poisson) and 0.5 (overdispersed sensitivity); rough — reported as sensitivity, not an estimate.
- Suppression threshold: **period count < 16** (NCI rule); ≈ 3.2 on `average_annual_count` (16 / 5-year period). Simulation grid thresholds {10, 16, 25}.
- Grid: base rate {5, 15, 50, 150}/100k × deprivation–rate RR/SD {1.0, 1.3, 1.7} × corr {0, −0.3, −0.6} × threshold {10, 16, 25}.

### Empirical suppression-by-quintile (validation target; incidence, ICE quintiles)
| Site | % suppressed (overall) | Q5 most-deprived suppressed | Q1 least-deprived suppressed |
|---|---|---|---|
| Breast (Female) | 7.4 | 9.9 | 5.9 |
| Stomach | 61.3 | 67.7 | 45.9 |
| Cervix | 75.7 | 81.8 | 63.8 |

## 5. Results / figures manifest
- `results/aim1_disparities.csv` — RR/RD/gradient under complete-case, model-based, bounding (+ bootstrap CI), per site × measure × exposure.
- `results/aim2_erasure.csv` — % counties/population/rural/Q5 suppressed by site.
- `results/aim3_simulation.csv` — 108-cell grid; RR/RD/gradient true vs complete-case + relative bias + mean suppression.
- `results/aim3_calibrated_sensitivity.csv` — calibrated cells (corr −0.30; Poisson/overdispersed; weighted/unweighted).
- `results/REPORT.md` — plain-language results summary.
- `figures/fig1_erasure.png` — erasure by site (counties/pop/rural/Q5).
- `figures/fig2_disparity_methods.png` — RR by method, faceted incidence/mortality (fragility).
- `figures/fig3_simulation.png` — calibrated bias vs suppression; bias direction vs corr.

## 6. Pre-registration
OSF DOI **10.17605/OSF.IO/BJZR5** (direction registered as conditional/characterized). No amendments.
