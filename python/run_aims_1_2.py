"""
run_aims_1_2.py — Aim 1 (disparity under 4 suppression methods) + Aim 2 (erasure profile).
Executed reference. Reads scp.duckdb (built by the pipeline); writes results/ + figures/.
Exposure dep_q convention: 5 = MOST deprived. ICE quintile is flipped to match.
"""
import duckdb, numpy as np, pandas as pd, os, sys
sys.path.insert(0, os.path.dirname(__file__))
from analysis_engine import complete_case, available_case, bounding, model_based, bootstrap

DB = sys.argv[1] if len(sys.argv) > 1 else "scp.duckdb"
OUTR = sys.argv[2] if len(sys.argv) > 2 else "../results"
os.makedirs(OUTR, exist_ok=True)
con = duckdb.connect(DB, read_only=True)

SITES = [("Breast (Female)", "Female"), ("Cervix", "Female"), ("Stomach", "Both Sexes")]
BASE = "race='All Races (includes Hispanic)' AND stage='All Stages' AND age='All Ages' AND year='Latest 5-year average'"

# US county universe with exposures (exclude PR 72; keep 50 states + DC)
univ = con.execute("""
  SELECT fips, county_name, pop_total, ice_quintile_popwt, dep_quintile_popwt, ice_raceinc, dep_index
  FROM exposure_master
  WHERE substr(fips,1,2) NOT IN ('72','78','60','66','69')
    AND ice_quintile_popwt IS NOT NULL AND dep_quintile_popwt IS NOT NULL
""").df()
univ["state_fips"] = univ["fips"].str[:2]
print(f"county universe with both exposures: {len(univ)}")

def frame(measure, site, sex, exposure):
    tbl = "incidence" if measure == "incidence" else "mortality"
    obs = con.execute(f"""SELECT fips, rate, cnt FROM {tbl}
        WHERE {BASE} AND cancer=? AND sex=? AND rate IS NOT NULL""", [site, sex]).df()
    d = univ.merge(obs, on="fips", how="left")
    if exposure == "ice":
        d["dep_q"] = 6 - d["ice_quintile_popwt"]       # flip: 5 = most deprived (lowest ICE)
    else:
        d["dep_q"] = d["dep_quintile_popwt"]            # already 5 = most deprived
    return d

rows = []
for measure in ["incidence", "mortality"]:
    for site, sex in SITES:
        for exposure in ["ice", "dep"]:
            d = frame(measure, site, sex, exposure)
            n_univ = len(d); n_obs = d["rate"].notna().sum()
            cc = complete_case(d); mb = model_based(d); bd = bounding(d, 16, 5)
            ci = bootstrap(d, complete_case, B=2000, seed=20260604)
            rows.append({
                "measure": measure, "site": site, "exposure": exposure,
                "n_universe": n_univ, "n_observed": int(n_obs),
                "pct_suppressed": round(100*(1-n_obs/n_univ), 1),
                "RR_cc": cc["RR"], "RR_cc_lo": ci["RR"][0], "RR_cc_hi": ci["RR"][1],
                "RR_model": mb["RR"], "RR_bound_lo": bd["RR"][0], "RR_bound_hi": bd["RR"][1],
                "RD_cc": cc["RD"], "RD_model": mb["RD"], "RD_bound_lo": bd["RD"][0], "RD_bound_hi": bd["RD"][1],
                "grad_cc": cc["gradient"], "grad_model": mb["gradient"],
                "rate_most_cc": cc["rate_most"], "rate_least_cc": cc["rate_least"],
                "RR_relchange_model_vs_cc": (mb["RR"]-cc["RR"])/cc["RR"] if cc["RR"] else np.nan,
            })
res = pd.DataFrame(rows)
res.to_csv(f"{OUTR}/aim1_disparities.csv", index=False)
pd.set_option("display.width", 200, "display.max_columns", 30)
print(res[["measure","site","exposure","pct_suppressed","RR_cc","RR_cc_lo","RR_cc_hi","RR_model","RR_bound_lo","RR_bound_hi","RR_relchange_model_vs_cc"]].round(3).to_string(index=False))

# ---- Aim 2: erasure profile (incidence, ICE-universe; rurality from RUCC note + minority) ----
rumin = con.execute("""SELECT fips, any_value(rucc_note) AS rucc_note FROM incidence GROUP BY fips""").df()
a2rows = []
for site, sex in SITES:
    d = frame("incidence", site, sex, "ice").merge(rumin, on="fips", how="left")
    d["suppressed"] = d["rate"].isna()
    tot_pop = d["pop_total"].sum()
    rural = d["rucc_note"].eq("Rural")
    a2rows.append({
        "site": site,
        "counties_suppressed": int(d["suppressed"].sum()),
        "pct_counties_suppressed": round(100*d["suppressed"].mean(), 1),
        "pct_pop_suppressed": round(100*d.loc[d["suppressed"], "pop_total"].sum()/tot_pop, 1),
        "pct_rural_counties_suppressed": round(100*d.loc[rural, "suppressed"].mean(), 1) if rural.any() else np.nan,
        "pct_urban_counties_suppressed": round(100*d.loc[~rural, "suppressed"].mean(), 1),
        "suppressed_in_Q5_mostdeprived": int(d.loc[d["dep_q"]==5, "suppressed"].sum()),
        "pct_Q5_suppressed": round(100*d.loc[d["dep_q"]==5, "suppressed"].mean(), 1),
        "pct_Q1_suppressed": round(100*d.loc[d["dep_q"]==1, "suppressed"].mean(), 1),
    })
a2 = pd.DataFrame(a2rows); a2.to_csv(f"{OUTR}/aim2_erasure.csv", index=False)
print("\n=== Aim 2: erasure profile (incidence) ===")
print(a2.to_string(index=False))
con.close()
