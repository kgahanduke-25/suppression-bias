# Get the data (run on YOUR machine, then the files sync to this folder)

The sandbox can't reach GitHub's release CDN, so download locally into THIS folder.

## Option A — GitHub CLI (cleanest)
    cd "<this data/raw folder>"
    gh release download 2026-06-01 -p "*" -R seandavi/state-cancer-profile-scraper

## Option B — curl (no gh needed)
    cd "<this data/raw folder>"
    BASE=https://github.com/seandavi/state-cancer-profile-scraper/releases/download/2026-06-01
    for f in state_cancer_profiles_incidence.csv.gz state_cancer_profiles_mortality.csv.gz \
             state_cancer_profiles_demographics.csv.gz state_cancer_profiles_risk.csv.gz \
             select_options.json scrape_catalog.jsonl gh_hash.txt; do
      curl -L -O "$BASE/$f"
    done

Then tell me "files are in" and I'll verify + finish Phase 0.
