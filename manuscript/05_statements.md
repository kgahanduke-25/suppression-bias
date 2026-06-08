# Title page and statements

## Title
Bias from small-count suppression in county-level cancer disparity estimates: a calibrated simulation study

## Author
Kamalakanta Gahan¹

¹ Department of Population Health Sciences, Duke University, Durham, NC, USA

**Corresponding author:** Kamalakanta Gahan, Department of Population Health Sciences, Duke University, Durham, NC, USA. Email: kamalakanta.gahan@duke.edu. ORCID: 0000-0002-4880-6228.

## Author contributions (CRediT)
K.G.: Conceptualization; Methodology; Software; Formal analysis; Investigation; Data curation; Validation; Visualization; Writing – original draft; Writing – review & editing.

## Competing interests
The author declares no competing interests.

## Funding
This research received no specific grant from any funding agency in the public, commercial, or not-for-profit sectors.

## Ethics / IRB
This study is a secondary analysis of publicly available, de-identified, aggregate data and does not constitute human-subjects research; it was therefore exempt from institutional review board review.

## Data and code availability
All inputs are public and de-identified; no restricted or identifiable data were used.
- **Cancer data:** NCI State Cancer Profiles (a joint NCI/CDC resource), obtained from the public scraped release `seandavi/state-cancer-profile-scraper`, **release tag 2026-06-01** (county-level incidence and mortality).
- **Covariates:** U.S. Census Bureau American Community Survey **2018–2022 5-year** estimates, tables **B19001, B19001H** (household income, overall and White non-Hispanic) and **B01003** (total population) for ICE; USDA **Rural-Urban Continuum Codes 2023** for rurality.
- **Code:** analysis, simulation, and figure scripts are openly available at **https://github.com/kgahanduke-25/suppression-bias** (commit/tag to cite at submission). Executed reference: Python 3.10 (duckdb 1.5.3, pandas 2.3.3, numpy 2.2.6, matplotlib 3.10.8); canonical R port included.
- **Pre-registration:** OSF, **https://doi.org/10.17605/OSF.IO/BJZR5**. A provenance log (`PROVENANCE.md`) records the exact run order, seeds, and calibrated parameters.

## Acknowledgments
The author thanks the National Cancer Institute and CDC for the State Cancer Profiles resource, the U.S. Census Bureau for the American Community Survey, and the maintainer of the public data release used here.

## Reporting guidelines
The observational analysis is reported in accordance with STROBE (cross-sectional studies); the simulation study is reported following the ADEMP framework (Morris et al., 2019). A completed STROBE checklist is provided as a supplement.
