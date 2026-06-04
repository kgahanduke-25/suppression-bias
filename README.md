# Erased at the margins
### How small-count suppression biases county-level cancer disparities estimates

Reproducible code and manuscript for a methods study quantifying how the suppression of
small-count cells (period count < 16) in NCI State Cancer Profiles distorts area-level
cancer disparity estimates. Suppressed counties are dropped entirely under complete-case
analysis; because suppression is informative (NMAR) missingness, the resulting disparity
estimates are biased in a characterizable direction and magnitude.

## Aims
1. **Empirical** — how the most- vs least-deprived quintile disparity (rate ratio, rate
   difference, population-weighted gradient) moves across four suppression-handling methods:
   complete-case, available-case, bounding/sensitivity, and model-based (small-area).
2. **Erasure** — who disappears under complete-case: share of counties, population, rural,
   and high-minority population lost, by site. Maps included.
3. **Simulation** — bias vs known ground truth across a grid of data-generating parameters
   (base incidence, county-size distribution, deprivation–rate association, threshold).

## Sites
Breast (Female), Stomach, Cervix — a common->rare gradient
(Phase 0 incidence suppression: 10.8% / 62.5% / 76.4% of counties).

## Exposure
- **Primary:** ICE(race+income) — Index of Concentration at the Extremes, ACS 2018–2022 5-year.
- **Sensitivity:** self-contained deprivation index from the release demographics (+ SVI robustness).

## Data
- Cancer rates: `seandavi/state-cancer-profile-scraper`, release tag **2026-06-01** (incidence,
  mortality; county level). Raw files are not committed — download from the release into `data/raw/`.
- Covariates: ACS 5-year via `tidycensus` (run `R/pull_acs_ice.R`); USDA RUCC 2023.

## Run order (executed reference: Python + DuckDB, all verified)
1. Download the release CSVs into `data/raw/` (see `data/raw/DOWNLOAD_INSTRUCTIONS.md`).
2. `Rscript R/pull_acs_ice.R` (or `python python/pull_acs_ice.py`) — county ICE + population -> `data/raw/county_ice.csv`.
3. `python python/01_build_pipeline.py` — ingest rates + demographics, build exposures/quintiles -> `data/processed/scp.duckdb` + `exposure_master.csv`.
4. `python python/run_aims_1_2.py` — Aim 1 disparities (4 methods) + Aim 2 erasure -> `results/`.
5. `python python/run_aim3.py` and `python python/calib_sim.py` — Aim 3 simulation grid + calibrated sensitivity -> `results/`.
6. `python python/make_figures.py` — main-text figures -> `figures/`.

Results are summarized in `results/REPORT.md`. The `R/` folder holds the canonical port:
`pull_acs_ice.R` (used in step 2) and `analysis_engine.R` (the estimator + four suppression
methods, mirroring `python/analysis_engine.py`); R driver scripts for steps 3–6 are in progress.
`manuscript/` will hold the medRxiv manuscript + supplement (in preparation).

## Reproducibility
Seeded, version-pinned, scripted, committed. Release tag and ACS vintage frozen.

## Status
Pre-registered (OSF, DOI 10.17605/OSF.IO/BJZR5). Analysis complete (Aims 1–3); manuscript in preparation.
Repository: https://github.com/REPLACE_ME_USERNAME/suppression-bias
<!-- after publishing, find-and-replace REPLACE_ME_USERNAME with your GitHub username -->


## License
Code: MIT. Data: see NCI State Cancer Profiles terms and the source release.
