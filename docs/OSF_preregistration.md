# OSF Pre-Registration

## Title
Erased at the margins: how small-count suppression biases county-level cancer disparities estimates

## Authors / Contributors
Kamalakanta Gahan (Duke University, Population Health Sciences); co-authors TBD.

## Date of registration
To be set at submission (must precede generation of any Aim 1 empirical disparity result).

---

## 1. Study information

### 1.1 Background & rationale
Area-level cancer disparities are routinely estimated from public datasets (e.g., NCI State Cancer Profiles) in which rates based on small counts are **suppressed** (period count < 16) for statistical stability and patient confidentiality. In the State Cancer Profiles bulk data, suppressed county–site–stratum cells are **absent entirely** (no row), so a standard complete-case disparities analysis silently drops them. Because suppression is determined by case count — itself a function of population size, rurality, and racial/economic composition — the missingness is **informative (not-missing-at-random, NMAR)**, and complete-case estimates of disparity are expected to be biased in a characterizable direction and magnitude. This study quantifies that bias empirically across three cancer sites spanning a rarity gradient, characterizes which communities are erased, and uses simulation against known ground truth to map bias as a function of the data-generating process.

### 1.2 Hypotheses
- **H1 (empirical bias).** The estimated disparity (most- vs least-deprived quintile) under complete-case analysis differs systematically from estimates that account for suppressed counties (bounding and model-based), and the divergence increases with site rarity (breast < stomach < cervix).
- **H2 (erasure profile).** Suppressed counties are disproportionately rural, smaller-population, and higher-minority; the share of rural and high-minority population erased under complete-case analysis increases with site rarity.
- **H3 (simulation).** In a synthetic county universe with known true rates correlated with deprivation, complete-case estimates of the disparity are biased relative to truth; bias magnitude increases as base incidence falls, as the deprivation–rate association strengthens, and as the suppression threshold rises.

We pre-specify the *existence and direction-characterization* of bias as the test; we do **not** pre-commit to a sign for every site, because direction depends on whether suppression preferentially removes high- or low-rate deprived counties — itself an empirical quantity reported in Aim 2.

---

## 2. Data

### 2.1 Source & release
- NCI **State Cancer Profiles**, accessed via the public bulk mirror `github.com/seandavi/state-cancer-profile-scraper`, **release tag `2026-06-01`** (frozen; exact tag recorded in Data Availability).
- County-level age-adjusted **incidence** and **mortality** rates (per 100,000), "Latest 5-year average."
- Area covariates: ACS 5-year (vintage **2018–2022**, i.e., `2022` ACS5) for the **primary exposure**; the release's ACS/SVI demographics file for the **sensitivity exposure**.
- USDA **Rural-Urban Continuum Codes (RUCC) 2023** for rurality (full 1–9 codes; the release also carries a collapsed Rural/Urban flag).

### 2.2 Units & universe
County (and county-equivalent) FIPS. Universe = **3,143** counties (confirmed via demographics rank field). Puerto Rico / territories handled per availability and noted.

### 2.3 Suppression rule (as implemented in the data)
A county–site–stratum rate is suppressed when the period case/death count < 16. In the bulk data this manifests as an **absent row**. Empirically the minimum non-suppressed `average_annual_count` ≈ 3.0, consistent with a 5-year-period threshold of 16 (16 / 5 ≈ 3.2 annual). We treat **absence of a usable rate** as the suppression indicator.

---

## 3. Variables

### 3.1 Exposure (area deprivation) — pre-specified
- **PRIMARY: ICE(race+income)** — Index of Concentration at the Extremes for racialized economic segregation (Krieger et al., AJPH 2016), household-based, from ACS5 2018–2022:
  - A = White non-Hispanic households with income ≥ $100,000 (B19001H, brackets 014–017)
  - P = households of color (all races minus White NH) with income < $25,000 (B19001 minus B19001H, brackets 002–005)
  - T = total households (B19001_001)
  - ICE = (A − P) / T, range [−1, +1]; lower = more deprived.
- **SENSITIVITY: self-contained deprivation index** — mean of five equally weighted z-scored ACS marginals from the release demographics file, oriented so higher = more deprived: (−)median household income, % below poverty, % less than 9th-grade education, (−)% bachelor's+, % crowded housing. (A secondary robustness check uses CDC/ATSDR **SVI overall** as a single validated alternative.)
- **Quintiles:** population-weighted quintiles (each quintile ≈ 20% of the relevant population), cutpoints computed on the full county universe **before** any outcome is examined. County total population (ACS B01003) is the weight.

### 3.2 Outcomes
County age-adjusted incidence rate per 100,000 (primary); mortality rate (parallel). Stratum: All Races, All Stages, All Ages; sex = Female (breast, cervix), Both Sexes (stomach).

### 3.3 Sites (pre-specified rarity gradient)
Breast (Female) [common], Stomach [rarer], Cervix [rarest]. Observed Phase 0 suppression (incidence, headline stratum): breast 10.8%, stomach 62.5%, cervix 76.4% of counties.

### 3.4 Covariates for Aim 2 characterization
RUCC (rurality), county population, % minority (ACS), persistent-poverty flag.

---

## 4. Estimands & analysis plan

### 4.1 Disparity estimands (per site × measure)
1. **Rate Ratio (RR):** rate in most-deprived (Q5) ÷ rate in least-deprived (Q1) quintile.
2. **Rate Difference (RD):** rate(Q5) − rate(Q1), per 100,000.
3. **Population-weighted gradient:** slope across all five quintiles (population-weighted least-squares of quintile mean rate on quintile rank), the "slope index of inequality"-style summary.

Quintile-level rate = population-weighted mean of county age-adjusted rates within quintile (weights = county population). Confidence intervals via nonparametric bootstrap over counties (B = 2,000; seed pre-set).

### 4.2 Aim 1 — disparity under four suppression-handling methods
For each site × measure, recompute RR, RD, gradient under:
1. **Complete-case** — use only counties with a non-suppressed rate (de facto standard).
2. **Available-case** — same estimate, but explicitly report counties and population retained vs lost per quintile.
3. **Bounding / sensitivity** — impute suppressed county rates at plausible extremes (count = 0 up to count = threshold − 1 = 15, giving rate from 0 to 15/population), producing worst-/best-case bounds on RR, RD, gradient.
4. **Model-based** — borrow strength via a hierarchical (small-area) model: a Bayesian Poisson/negative-binomial model with county random effects and a state-level prior, predicting rates for suppressed counties from population, deprivation, and rurality; disparity recomputed on the completed surface. (If the hierarchical fit is not feasible for a site, the state-rate-prior shrinkage estimator is used and labeled as such.)

**Primary comparison:** magnitude and direction of change in RR, RD, and gradient between complete-case (method 1) and (a) the bounding interval (method 3) and (b) the model-based estimate (method 4).

### 4.3 Aim 2 — who is erased
For each site × measure: share of US counties suppressed; share of total population in suppressed counties; share of the **rural** (RUCC ≥ 4 / "Rural") population erased; share of the **high-minority** population (top quintile of % minority) erased; cross-tab of suppression by deprivation quintile. Choropleth maps of suppressed counties per site.

### 4.4 Aim 3 — simulation vs ground truth
Synthetic universe of N counties with populations drawn from a realistic county-size distribution (calibrated to the empirical distribution). True age-adjusted rate per county generated as log-linear in a latent deprivation score (known by construction); expected counts = rate × population; observed counts ~ Poisson. Apply the suppression rule (suppress when simulated period count < threshold). Compute complete-case disparity (RR, RD, gradient) and compare to the **true** disparity (computed on the full synthetic universe). 

**Scenario grid (fully crossed, seeded):**
- Base incidence: rare ↔ common (e.g., 5, 15, 50, 150 per 100k).
- County-size distribution: empirical, plus shifted-smaller and shifted-larger variants.
- Deprivation–rate association strength: null, moderate, strong (rate ratio per SD of deprivation ∈ {1.0, 1.3, 1.7}).
- Suppression threshold: {10, 16, 25} period count.
Replications: 1,000 per cell. Outcome: bias (estimate − truth) and relative bias for RR, RD, gradient, summarized as a function of the data-generating parameters.

### 4.5 Inference criteria
Primary reporting is estimation (point estimates with 95% bootstrap/credible intervals), not null-hypothesis testing. "Non-trivial bias" is pre-defined as a relative change in the disparity estimate ≥ 10% between complete-case and the model-based (or bounding-midpoint) estimate.

---

## 5. Framing constraints (analytic discipline, pre-committed)
- Suppression is treated as **informative / NMAR** missingness; complete-case bias is non-ignorable and stated as such.
- **Ecological design**: contextual/structural interpretation only; no individual-level inference. ICE interpreted as area-level racialized economic segregation.
- **MAUP** (modifiable areal unit problem) acknowledged; county is the fixed unit.
- BRFSS-derived covariates (if used) are **model-based** estimates and labeled accordingly.

## 6. Exclusions & contingencies
- Counties missing the exposure covariate are reported and handled by exposure availability (not outcome), preserving the NMAR logic.
- If a site×measure has too few non-suppressed counties in a quintile to bootstrap, that cell is reported descriptively and flagged.
- Any deviation from this plan will be reported in the manuscript with rationale.

## 7. Analysis environment
Python 3 + DuckDB (primary, executed); an R + DuckDB port is provided in the repository for reproducibility. All steps seeded, version-pinned, scripted, and committed; intermediate artifacts saved to disk. Release tag and ACS vintage frozen.
