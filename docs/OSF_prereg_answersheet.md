# OSF Preregistration — copy-paste answer sheet
Paste each block into the matching field of the **OSF Preregistration** template. Headings below
match the template's field names.

---

## Title
Erased at the margins: how small-count suppression biases county-level cancer disparities estimates

## Description (Study Information)
Area-level cancer disparities are routinely estimated from public data (NCI State Cancer Profiles) in which rates based on small counts are suppressed (period count < 16). In the bulk data, suppressed county–site–stratum cells are absent entirely, so a standard complete-case disparities analysis silently drops them. Because suppression depends on case count — a function of population size, rurality, and racial/economic composition — the missingness is informative (not-missing-at-random), and complete-case disparity estimates are expected to be biased in a characterizable direction and magnitude. This study quantifies that bias across three cancer sites spanning a rarity gradient, characterizes which communities are erased, and uses simulation against known ground truth to map bias as a function of the data-generating process.

## Hypotheses
H1 (empirical bias): The estimated disparity (most- vs least-deprived quintile) under complete-case analysis differs systematically from estimates that account for suppressed counties (bounding and model-based), with divergence increasing with site rarity (breast < stomach < cervix).
H2 (erasure profile): Suppressed counties are disproportionately rural, smaller-population, and higher-minority; the rural and high-minority population share erased under complete-case increases with site rarity.
H3 (simulation): With known true rates correlated with deprivation, complete-case estimates are biased relative to truth; bias magnitude increases as base incidence falls, as the deprivation–rate association strengthens, and as the suppression threshold rises. Direction is conditional on whether suppression preferentially removes high- or low-rate deprived counties (quantified in Aim 2 and simulation), and is therefore characterized rather than fixed a priori.

---
## Design Plan

### Study type
Observational (ecological). Secondary analysis of public, de-identified, aggregate data.

### Blinding
No blinding (secondary data analysis).

### Study design
Cross-sectional ecological study at the US county level. Exposure = area deprivation quintile; outcome = age-adjusted cancer incidence (and mortality) rate per 100,000. Disparity contrasts most- vs least-deprived quintile, evaluated under four suppression-handling methods, for three cancer sites, complemented by a Monte Carlo simulation.

### Randomization
Not applicable.

---
## Sampling Plan

### Existing data
Registration prior to analysis of the data.

### Explanation of existing data
The cancer rate data are public (NCI State Cancer Profiles, mirror `seandavi/state-cancer-profile-scraper`, release tag 2026-06-01) and the ACS covariates are public. Prior to registration we performed descriptive reconnaissance only: we confirmed the schema, the suppression rule (count < 16), and counted the number of suppressed counties per site (breast 10.8%, stomach 62.5%, cervix 76.4% of 3,143 counties). **No disparity estimand (rate ratio, rate difference, or gradient) has been computed for any site under any method, and no simulation results have been generated.** All analyses in Section "Analysis Plan" are unrun at registration.

### Data collection procedures
County-level age-adjusted incidence and mortality rates ("Latest 5-year average") from the frozen release; ACS 2018–2022 5-year estimates via tidycensus for ICE(race+income) and total population; USDA Rural-Urban Continuum Codes 2023. Merged on county FIPS.

### Sample size
All US counties and county-equivalents (N = 3,143). No sampling; full population of areal units.

### Sample size rationale
Census of counties; not a sample. Precision is addressed via nonparametric bootstrap (B = 2,000) over counties.

### Stopping rule
Not applicable (fixed, frozen dataset).

---
## Variables

### Manipulated variables
None (observational).

### Measured variables
Exposure — PRIMARY: ICE(race+income), household-based (Krieger 2016), ACS 2018–2022: A = White non-Hispanic households ≥ $100k (B19001H 014–017); P = households of color < $25k (B19001 002–005 minus B19001H 002–005); T = total households; ICE = (A − P)/T. SENSITIVITY: self-contained deprivation index = mean of five z-scored ACS marginals (−median household income, % below poverty, % < 9th-grade education, −% bachelor's+, % crowding); robustness: CDC/ATSDR SVI overall.
Outcome — county age-adjusted incidence rate per 100,000 (primary) and mortality rate (parallel), stratum All Races / All Stages / All Ages; sex = Female (breast, cervix), Both Sexes (stomach).
Covariates (Aim 2) — RUCC rurality, county population, % minority, persistent-poverty flag.

### Indices
Quintiles are population-weighted (each ≈ 20% of population), cutpoints computed on the full county universe before any outcome is examined; county total population (ACS B01003) is the weight. Sites: Breast (Female), Stomach, Cervix.

---
## Analysis Plan

### Statistical models
For each site × measure, three estimands: Rate Ratio = rate(most-deprived Q)/rate(least-deprived Q); Rate Difference = rate(most) − rate(least) per 100,000; population-weighted gradient = OLS slope of quintile mean rate on quintile rank (1–5). Quintile rate = population-weighted mean of county age-adjusted rates. Each recomputed under four suppression-handling methods: (1) complete-case; (2) available-case with retention accounting; (3) bounding (impute suppressed county rates from 0 to (threshold−1) cases → worst/best-case bounds); (4) model-based small-area estimation (hierarchical Poisson/negative-binomial with county random effects and state-level prior; empirical-Bayes state-prior shrinkage if the full hierarchical fit is not feasible, labeled as such). 95% CIs via nonparametric bootstrap over counties (B = 2,000, seed pre-set).

### Transformations
ICE and deprivation index converted to population-weighted quintiles. Rates analyzed on the natural scale (RD) and ratio scale (RR). Log scale used for bootstrap of RR.

### Inference criteria
Estimation, not null-hypothesis testing: point estimates with 95% bootstrap/credible intervals. Pre-defined "non-trivial bias" = relative change in the disparity estimate ≥ 10% between complete-case and the model-based (or bounding-midpoint) estimate.

### Data exclusion
Counties missing the exposure covariate are reported and handled by exposure availability, not by outcome, preserving the informative-missingness logic. No outcome-based exclusions.

### Missing data
Outcome suppression (count < 16) is the object of study and is handled by the four methods above; it is explicitly treated as informative/NMAR missingness. Complete-case is the comparator, not the preferred analysis.

### Exploratory analysis
Stratified/late-stage outcomes, mortality replication, and SVI-based exposure are robustness/exploratory.

---
## Other

Aim 3 simulation (pre-specified): synthetic county universe with populations from a log-normal calibrated to empirical US county sizes (log-mean 10.27, log-sd 1.50); true rate log-linear in a latent deprivation score (known); expected counts = rate × population × 5 years; observed counts ~ Poisson; suppress when simulated period count < threshold. Compare complete-case disparity to the true disparity. Fully crossed seeded grid (1,000 reps/cell): base incidence {5, 15, 50, 150 per 100k} × deprivation–rate association {RR per SD = 1.0, 1.3, 1.7} × deprivation–county-size correlation {0, −0.3, −0.6} × suppression threshold {10, 16, 25}. Outcome: bias (estimate − truth) and relative bias for RR, RD, and gradient as a function of the data-generating parameters.

Analytic discipline (pre-committed): suppression treated as informative/NMAR; ecological design → contextual/structural interpretation only, no individual inference; MAUP acknowledged (county fixed unit); any BRFSS-derived covariates are model-based and labeled. Environment: Python 3 + DuckDB (executed reference) with an R + DuckDB port; all steps seeded, version-pinned, scripted, committed; release tag and ACS vintage frozen.
