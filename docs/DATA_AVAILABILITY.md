# Data & Code Availability

**Cancer rates.** NCI State Cancer Profiles county-level age-adjusted incidence and mortality
("Latest 5-year average"), obtained from the public bulk mirror
`github.com/seandavi/state-cancer-profile-scraper`, **release tag `2026-06-01`** (frozen).
Raw files are not redistributed in this repository (see `.gitignore`); download them from that
release into `data/raw/` using `data/raw/DOWNLOAD_INSTRUCTIONS.md`.

**Area covariates.** American Community Survey 2018–2022 5-year estimates (tables B19001, B19001H,
B01003) via the U.S. Census Bureau API, retrieved with `tidycensus` (`R/pull_acs_ice.R`); the
release's ACS/SVI demographics file (self-contained deprivation index and SVI robustness); USDA
Rural-Urban Continuum Codes 2023.

**Derived data.** `data/processed/exposure_master.csv` (county exposures + quintiles) and
`data/processed/dep_index.csv` are derived by `python/01_build_pipeline.py` and committed for
convenience.

**Code.** All analysis code is publicly available at
**https://github.com/kgahanduke-25/suppression-bias** (MIT license). The executed reference
implementation is in `python/`; a canonical R port is in `R/`. All steps are seeded and version-
pinned (`requirements.txt`). The DuckDB working database is rebuilt from raw by the build script
and is not committed.



**Pre-registration.** OSF, DOI **10.17605/OSF.IO/BJZR5**.

**Ethics.** Secondary analysis of publicly available, de-identified, aggregate data; not human-
subjects research (exempt).

**Competing interests / Funding.** [To complete before submission.]
