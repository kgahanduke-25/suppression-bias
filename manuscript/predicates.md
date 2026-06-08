# Predicate papers — structure & claim notes (PubMed-sourced)

Source: PubMed. DOIs are live links. Used to emulate Methods structure and to anchor citations.

## 1. Krieger et al. 2016, *Cancer Causes Control* — ICE + breast cancer (the template)
DOI: https://doi.org/10.1007/s10552-016-0793-7 (PMID 27503397)
- **Methods structure:** SEER cohort → append county-level income quintile + three ICE measures (income, race, race+income) → logistic regression of ER status on ICE quintile, adjusted for age/registry/tumor/race.
- **Claim & evidence:** Most- vs least-privileged ICE quintile → 1.1–1.3× odds ER+ (CIs exclude 1), robust to adjustment; ICE captures segregation that single-axis SES misses.
- **ICE / small-area cites:** introduces ICE(race+income) operationalization (≤20th vs ≥80th); cites Krieger AJPH 2016 for the metric.
- **For us:** template for ICE-quintile rate-contrast Methods and the privilege–deprivation framing.

## 2. Larrabee Sonderlund et al. 2022, *PLoS One* — ICE(race+income) systematic review
DOI: https://doi.org/10.1371/journal.pone.0262962 (PMID 35089963)
- **Methods structure:** PRISMA systematic review; 20 studies linking ICE(race+income) to birth, cancer, mortality, communicable disease.
- **Claim & evidence:** Strong, consistent association between ICE(race+income) and adverse health; income is the key mechanism of racialized health inequality.
- **ICE cites:** consolidates the ICE(race+income) evidence base — our citation for "ICE is a validated exposure."
- **For us:** Introduction support that ICE(race+income) is established and validated.

## 3. Houston et al. 2018, *J Thorac Oncol* — county/rural disparities missed by national estimates
DOI: https://doi.org/10.1016/j.jtho.2017.12.010 (PMID 29360512)
- **Methods structure:** SEER+NPCR population registry; age-adjusted histologic rates + rate ratios by race/ethnicity × residential county (metro/nonmetro); APC trends.
- **Claim & evidence:** "National cancer estimates may not always reflect the cancer burden… in small geographic areas"; the Black–White disparity *grows with rurality*.
- **For us:** the paper's own premise — small-area/rural burden is hidden in aggregates — is exactly the gap suppression worsens; key Discussion cite.

## 4. Schootman et al. 2010, *Cancer Epidemiol Biomarkers Prev* — Bayesian small-area smoothing
DOI: https://doi.org/10.1158/1055-9965.EPI-09-0966 (PMID 20354128)
- **Methods structure:** county SEER breast indicators 1988–2005; observed county rates **smoothed with hierarchical Bayesian spatiotemporal methods**; absolute/relative geographic disparity over time.
- **Claim & evidence:** quantifies trends in small-area geographic disparities using model-based smoothing to stabilize sparse county rates.
- **For us:** the methodological precedent for our **model-based (small-area) suppression-handling arm**.

## Method anchors (PubMed-verified)
- **ICE canonical:** Krieger et al. 2016, *Am J Public Health* — https://doi.org/10.2105/AJPH.2015.302955 (PMID 26691119). Defines ICE for public-health monitoring; ICE(race+income) gives largest RRs.
- **ICE + small-count count models:** Feldman et al. 2019, *Am J Public Health* — https://doi.org/10.2105/AJPH.2018.304851 (PMID 30676802). ICE with multilevel **negative-binomial** models for sparse event counts.
- **Rurality + county measurement discordance:** Kenzik et al. 2024, *JCO Oncol Pract* — https://doi.org/10.1200/OP.23.00626 (PMID 38560814). RUCC, ADI; 22–30% of counties "discordant"; rural designations mask high-need counties.
- **Missing-data / complete-case bias:** Sterne et al. 2009, *BMJ* — https://doi.org/10.1136/bmj.b2393 (PMID 19564179). Multiple imputation & the pitfalls of complete-case analysis under informative missingness.

## OPEN CITATION GAP (flagged per integrity rules)
A dedicated peer-indexed methods paper for **statistical cell-suppression / small-numbers confidentiality in cancer surveillance** was not cleanly retrievable from PubMed (the canonical sources are NCI State Cancer Profiles and CDC/NPCR–USCS *technical documentation*, not journal articles). Plan: cite the **NCI State Cancer Profiles suppression documentation and CDC USCS technical notes** as data-source/technical references (non-PubMed, appropriate for a methods description), and state the < 16 rule with that attribution. Do **not** invent a journal citation for it.
