"""
01_build_pipeline.py — reproducible build of the analysis database from raw inputs.
Reads data/raw/*.csv (release 2026-06-01) + data/raw/county_ice.csv (from pull_acs_ice.R/.py),
writes data/processed/scp.duckdb and exposure_master.csv. Executed reference for the pipeline.

Run order: download release CSVs -> pull_acs_ice -> this script -> run_aims_1_2.py -> run_aim3.py.
"""
import duckdb, os, sys
RAW = sys.argv[1] if len(sys.argv) > 1 else "../data/raw"
PROC = sys.argv[2] if len(sys.argv) > 2 else "../data/processed"
os.makedirs(PROC, exist_ok=True)
DB = os.path.join(PROC, "scp.duckdb")
if os.path.exists(DB):
    os.remove(DB)
con = duckdb.connect(DB)
con.execute("PRAGMA threads=4")
NULL = "nullstr='\\N'"

def ingest_rates(name, fname):
    con.execute(f"""CREATE OR REPLACE TABLE {name} AS
      SELECT fips, state_fips, cancer, sex, race, stage, age, year,
        age_adjusted_rate_per_100_000 AS rate, lower_ci_rate, upper_ci_rate,
        average_annual_count AS cnt,
        "2023_rural_urban_continuum_codesrural_urban_note" AS rucc_note
      FROM read_csv_auto('{RAW}/{fname}', {NULL}, sample_size=-1, ignore_errors=true)
      WHERE locale_type='county'""")
    print(name, con.execute(f"SELECT count(*) FROM {name}").fetchone()[0])

ingest_rates("incidence", "state_cancer_profiles_incidence.csv")
ingest_rates("mortality", "state_cancer_profiles_mortality.csv")

# demographics (long, by topic) -> wide exposure components (All Races/Both Sexes/All Ages)
con.execute(f"""CREATE OR REPLACE TABLE demo AS
  SELECT * FROM read_csv_auto('{RAW}/state_cancer_profiles_demographics.csv', {NULL},
    sample_size=-1, ignore_errors=true) WHERE locale_type='county'""")

def comp(topic, dl, col):
    dl = dl.replace("'", "''")
    return (f"SELECT area_code AS fips, TRY_CAST({col} AS DOUBLE) v FROM demo "
            f"WHERE topic='{topic}' AND demo_label='{dl}' AND race='All Races (includes Hispanic)' "
            f"AND sex='Both Sexes' AND age='All Ages'")
parts = {
 'median_hh_income': comp('inc', 'Median household income ($)', 'value_dollars'),
 'pct_below_poverty': comp('pov', 'Persons below poverty', 'percent'),
 'pct_lt9th': comp('ed', 'Less than 9th grade', 'percent'),
 'pct_bachelors': comp('ed', "At least bachelor's degree", 'percent'),
 'pct_crowding': comp('crowd', 'Households with >1 person per room', 'percent'),
 'svi_overall': comp('svi', 'Overall (SVI)', 'value_index'),
 'svi_ses': comp('svi', 'Socioeconomic Status', 'value_index'),
}
for n, sql in parts.items():
    con.execute(f"CREATE OR REPLACE TEMP VIEW t_{n} AS {sql}")
con.execute("""CREATE OR REPLACE TABLE exposures AS
  SELECT a.fips, a.v median_hh_income, b.v pct_below_poverty, c.v pct_lt9th, d.v pct_bachelors,
         e.v pct_crowding, f.v svi_overall, g.v svi_ses
  FROM t_median_hh_income a LEFT JOIN t_pct_below_poverty b USING(fips)
  LEFT JOIN t_pct_lt9th c USING(fips) LEFT JOIN t_pct_bachelors d USING(fips)
  LEFT JOIN t_pct_crowding e USING(fips) LEFT JOIN t_svi_overall f USING(fips)
  LEFT JOIN t_svi_ses g USING(fips)""")

# self-contained deprivation index (z-scored; higher = more deprived)
con.execute("""CREATE OR REPLACE TABLE dep AS
  WITH z AS (SELECT fips,
    -(median_hh_income-avg(median_hh_income)OVER())/stddev_pop(median_hh_income)OVER() z_inc,
     (pct_below_poverty-avg(pct_below_poverty)OVER())/stddev_pop(pct_below_poverty)OVER() z_pov,
     (pct_lt9th-avg(pct_lt9th)OVER())/stddev_pop(pct_lt9th)OVER() z_ed9,
    -(pct_bachelors-avg(pct_bachelors)OVER())/stddev_pop(pct_bachelors)OVER() z_bach,
     (pct_crowding-avg(pct_crowding)OVER())/stddev_pop(pct_crowding)OVER() z_crowd
    FROM exposures)
  SELECT fips, (z_inc+z_pov+z_ed9+z_bach+z_crowd)/5.0 AS dep_index FROM z""")

# ICE from ACS pull (pull_acs_ice)
ice_csv = os.path.join(RAW, "county_ice.csv")
if not os.path.exists(ice_csv):
    raise SystemExit("Missing data/raw/county_ice.csv — run R/pull_acs_ice.R (or python/pull_acs_ice.py) first.")
con.execute(f"""CREATE OR REPLACE TABLE ice AS
  SELECT lpad(CAST(fips AS VARCHAR),5,'0') fips, county_name, pop_total, ice_raceinc
  FROM read_csv_auto('{ice_csv}', sample_size=-1)""")

# population-weighted quintiles for both exposures, over the US county universe (excl PR/territories)
def popwt_quintiles(src_tbl, val_col, out_tbl, qcol):
    con.execute(f"""CREATE OR REPLACE TABLE {out_tbl} AS
      WITH u AS (SELECT s.fips, s.{val_col} AS v, i.pop_total FROM {src_tbl} s JOIN ice i USING(fips)
                 JOIN (SELECT DISTINCT fips FROM incidence) c ON c.fips=s.fips
                 WHERE s.{val_col} IS NOT NULL AND i.pop_total>0
                   AND substr(s.fips,1,2) NOT IN ('72','78','60','66','69')),
      cum AS (SELECT fips, v, pop_total, sum(pop_total) OVER (ORDER BY v)/sum(pop_total) OVER () cw FROM u)
      SELECT fips, v, pop_total,
        CASE WHEN cw<=0.2 THEN 1 WHEN cw<=0.4 THEN 2 WHEN cw<=0.6 THEN 3 WHEN cw<=0.8 THEN 4 ELSE 5 END AS {qcol}
      FROM cum""")
popwt_quintiles("ice", "ice_raceinc", "ice_q", "ice_quintile_popwt")     # 1 = most deprived (lowest ICE)
popwt_quintiles("dep", "dep_index", "dep_qpw", "dep_quintile_popwt")     # 5 = most deprived

con.execute("""CREATE OR REPLACE TABLE exposure_master AS
  SELECT i.fips, i.county_name, i.pop_total, i.ice_raceinc, iq.ice_quintile_popwt,
         d.dep_index, dq.dep_quintile_popwt, e.svi_overall, e.svi_ses,
         e.pct_below_poverty, e.median_hh_income, e.pct_crowding
  FROM ice i LEFT JOIN ice_q iq USING(fips) LEFT JOIN dep d USING(fips)
  LEFT JOIN dep_qpw dq USING(fips) LEFT JOIN exposures e USING(fips)""")
con.execute(f"COPY (SELECT * FROM exposure_master ORDER BY fips) TO '{PROC}/exposure_master.csv' (HEADER)")
print("exposure_master:", con.execute("SELECT count(*) FROM exposure_master").fetchone()[0])
print("Build complete ->", DB)
con.close()
