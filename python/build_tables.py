"""
build_tables.py — STROBE-style Results tables 1-3 from scp.duckdb. Every cell traceable.
Outputs CSV + Markdown (booktabs-style) to ../results/. Executed reference.
ICE quintile: 1 = MOST deprived (lowest ICE), 5 = LEAST deprived  (matches spec Q1=most deprived).
"""
import duckdb, numpy as np, pandas as pd, os, sys
sys.path.insert(0, os.path.dirname(__file__))
from analysis_engine import complete_case, model_based, bounding, bootstrap

DB = sys.argv[1] if len(sys.argv) > 1 else "scp.duckdb"
OUT = sys.argv[2] if len(sys.argv) > 2 else "../results"
con = duckdb.connect(DB, read_only=True)
BASE = "race='All Races (includes Hispanic)' AND stage='All Stages' AND age='All Ages' AND year='Latest 5-year average'"

def demo_pct(label):
    return (f"SELECT area_code fips, TRY_CAST(percent AS DOUBLE) v FROM demo WHERE topic='pop' "
            f"AND demo_label='{label}' AND race='All Races (includes Hispanic)' AND sex='Both Sexes' AND age='All Ages'")

# county frame: exposures + race + rurality + incidence rates (reported only)
con.execute(f"""CREATE OR REPLACE TEMP VIEW wht AS {demo_pct('White')}""")
con.execute(f"""CREATE OR REPLACE TEMP VIEW blk AS {demo_pct('Black')}""")
con.execute(f"""CREATE OR REPLACE TEMP VIEW hsp AS {demo_pct('Hispanic')}""")
con.execute("""CREATE OR REPLACE TEMP VIEW ru AS SELECT fips, any_value(rucc_note) rucc FROM incidence GROUP BY fips""")
def site_rate(view, site, sex):
    con.execute(f"""CREATE OR REPLACE TEMP VIEW {view} AS SELECT fips, rate FROM incidence
        WHERE {BASE} AND cancer='{site}' AND sex='{sex}' AND rate IS NOT NULL""")
site_rate("br", "Breast (Female)", "Female")
site_rate("cx", "Cervix", "Female")

cf = con.execute("""
  SELECT e.fips, e.pop_total, e.ice_raceinc, e.ice_quintile_popwt AS q, e.median_hh_income,
         w.v AS pct_white, b.v AS pct_black, h.v AS pct_hisp, ru.rucc,
         br.rate AS breast_inc, cx.rate AS cervix_inc
  FROM exposure_master e
  LEFT JOIN wht w USING(fips) LEFT JOIN blk b USING(fips) LEFT JOIN hsp h USING(fips)
  LEFT JOIN ru USING(fips) LEFT JOIN br USING(fips) LEFT JOIN cx USING(fips)
  WHERE substr(e.fips,1,2) NOT IN ('72','78','60','66','69') AND e.ice_quintile_popwt IS NOT NULL
""").df()
cf["minority_pop"] = cf["pop_total"] * (100 - cf["pct_white"].fillna(0)) / 100
con.close()

def med_iqr(s):
    s = s.dropna()
    return f"{s.median():,.0f} [{s.quantile(.25):,.0f}–{s.quantile(.75):,.0f}]"
def med_iqr1(s):
    s = s.dropna()
    return f"{s.median():.1f} [{s.quantile(.25):.1f}–{s.quantile(.75):.1f}]"
def mean_sd(s):
    s = s.dropna(); return f"{s.mean():.1f} ({s.std():.1f})"
def pct_n(mask, denom):
    n = int(mask.sum()); return f"{n:,} ({100*n/denom:.1f})"
def smd_cont(a, b):
    a, b = a.dropna(), b.dropna()
    sp = np.sqrt((a.var()+b.var())/2)
    return 0.0 if sp == 0 else abs(a.mean()-b.mean())/sp
def smd_prop(pa, pb):
    p = (pa+pb)/2; d = np.sqrt(p*(1-p)); return 0.0 if d == 0 else abs(pa-pb)/d

# ============ TABLE 1 ============
groups = [1,2,3,4,5]; labels = {1:"Q1 most deprived",2:"Q2",3:"Q3",4:"Q4",5:"Q5 least deprived"}
cols = ["Overall"] + [f"{labels[g]} (n={int((cf.q==g).sum())})" for g in groups]
def row_cont_mi(name, col, fmt=med_iqr):
    vals = [fmt(cf[col])] + [fmt(cf.loc[cf.q==g, col]) for g in groups]
    sd = smd_cont(cf.loc[cf.q==1, col], cf.loc[cf.q==5, col]); vals.append(f"{sd:.2f}")
    return [name]+vals
def row_meansd(name, col):
    vals=[mean_sd(cf[col])]+[mean_sd(cf.loc[cf.q==g,col]) for g in groups]
    sd=smd_cont(cf.loc[cf.q==1,col],cf.loc[cf.q==5,col]); vals.append(f"{sd:.2f}")
    return [name]+vals
def row_urban(name):
    def f(d): return pct_n(d.rucc.eq("Urban"), len(d))
    vals=[f(cf)]+[f(cf[cf.q==g]) for g in groups]
    pa=cf.loc[cf.q==1,"rucc"].eq("Urban").mean(); pb=cf.loc[cf.q==5,"rucc"].eq("Urban").mean()
    vals.append(f"{smd_prop(pa,pb):.2f}"); return [name]+vals

t1rows=[
 row_cont_mi("Population, median [IQR]","pop_total"),
 row_urban("Urban (SCP designation), n (%)"),
 row_meansd("% Black, mean (SD)","pct_black"),
 row_meansd("% Hispanic, mean (SD)","pct_hisp"),
 row_cont_mi("Median household income ($), median [IQR]","median_hh_income"),
 row_cont_mi("ICE Race+Income, median [IQR]","ice_raceinc", med_iqr1),
 row_cont_mi("Breast incidence /100k (reported counties), median [IQR]","breast_inc", med_iqr1),
 row_cont_mi("Cervix incidence /100k (reported counties), median [IQR]","cervix_inc", med_iqr1),
]
t1=pd.DataFrame(t1rows, columns=["Characteristic"]+cols+["Std. diff (Q1 vs Q5)"])
t1.to_csv(f"{OUT}/table1_baseline.csv", index=False)

# ============ TABLE 2 ============ (per site, methods)
def frame_for(rate_col):
    d=cf[["fips","pop_total","q",rate_col]].rename(columns={rate_col:"rate"}).copy()
    d["dep_q"]=6-d["q"]            # flip so 5 = most deprived for the engine
    d["state_fips"]=d["fips"].str[:2]
    return d
def t2_panel(rate_col, site):
    d=frame_for(rate_col); univ=len(d); mostdep_total=int((d.dep_q==5).sum())
    obs=d[~d.rate.isna()]; obs_n=len(obs); mostdep_obs=int((obs.dep_q==5).sum())
    ccw=complete_case(d); ciw=bootstrap(d, complete_case, B=1000, seed=20260604)
    du=d.copy(); du["pop_total"]=1.0; ccu=complete_case(du); ciu=bootstrap(du, complete_case, B=1000, seed=20260604)
    mb=model_based(d); cimb=bootstrap(d, model_based, B=1000, seed=20260604)
    bd=bounding(d,16,5)
    def rr(p,ci): return f"{p:.2f} ({ci[0]:.2f}–{ci[1]:.2f})"
    def rd(p): return f"{p:.1f}"
    pct_ret=lambda n,tot: f"{100*n/tot:.0f}"
    rows=[
     ["Complete-case (population-weighted)", rr(ccw['RR'],ciw['RR']), rd(ccw['RD']), f"{obs_n:,}", pct_ret(mostdep_obs,mostdep_total)],
     ["Complete-case (unweighted county-mean)", rr(ccu['RR'],ciu['RR']), rd(ccu['RD']), f"{obs_n:,}", pct_ret(mostdep_obs,mostdep_total)],
     ["Available-case (= complete-case; retention shown)", rr(ccw['RR'],ciw['RR']), rd(ccw['RD']), f"{obs_n:,} of {univ:,}", pct_ret(mostdep_obs,mostdep_total)],
     ["Bounding — lower bound", f"{bd['low']['RR']:.2f}", f"{bd['low']['RD']:.1f}", f"{univ:,}", "100"],
     ["Bounding — upper bound", f"{bd['high']['RR']:.2f}", f"{bd['high']['RD']:.1f}", f"{univ:,}", "100"],
     ["Model-based (small-area)", rr(mb['RR'],cimb['RR']), rd(mb['RD']), f"{univ:,}", "100"],
    ]
    return pd.DataFrame(rows, columns=["Handling method","Rate ratio (95% CI)","Rate difference (/100k)","Counties included","% most-deprived counties retained"])
t2a=t2_panel("breast_inc","Breast (Female)"); t2a.to_csv(f"{OUT}/table2_breast.csv",index=False)
t2b=t2_panel("cervix_inc","Cervix"); t2b.to_csv(f"{OUT}/table2_cervix.csv",index=False)

# ============ TABLE 3 ============ (per quintile, per site)
def t3_panel(rate_col):
    d=cf.copy(); d["sup"]=d[rate_col].isna()
    rows=[]
    for g in groups:
        gd=d[d.q==g]; rural=gd.rucc.eq("Rural")
        poptot=gd.pop_total.sum(); ruraltot=gd.loc[rural,"pop_total"].sum(); mintot=gd.minority_pop.sum()
        rows.append([labels[g], f"{len(gd):,}", pct_n(gd.sup,len(gd)),
                     f"{100*gd.loc[gd.sup,'pop_total'].sum()/poptot:.1f}" if poptot else "–",
                     f"{100*gd.loc[gd.sup & rural,'pop_total'].sum()/ruraltot:.1f}" if ruraltot else "–",
                     f"{100*gd.loc[gd.sup,'minority_pop'].sum()/mintot:.1f}" if mintot else "–"])
    return pd.DataFrame(rows, columns=["ICE quintile","Counties, n","Suppressed, n (%)","% population in suppressed counties","% rural population erased","% minority population erased"])
t3a=t3_panel("breast_inc"); t3a.to_csv(f"{OUT}/table3_breast.csv",index=False)
t3b=t3_panel("cervix_inc"); t3b.to_csv(f"{OUT}/table3_cervix.csv",index=False)

# ---- markdown bundle ----
def md(df): return df.to_markdown(index=False)
with open(f"{OUT}/TABLES.md","w") as f:
    f.write("# Results tables (auto-generated; numbers from scp.duckdb)\n\n")
    f.write("## Table 1. Characteristics of US counties (n=3,143) by ICE Race+Income quintile, ACS 2018–2022.\nUnit = county. Population-weighted ICE quintiles (unequal county counts). Std. diff = standardized difference, Q1 vs Q5.\n\n"+md(t1)+"\n\n")
    f.write("## Table 2A. Estimated breast-cancer incidence disparity by suppression-handling method (most- vs least-deprived ICE quintile).\n\n"+md(t2a)+"\n\n")
    f.write("## Table 2B. Estimated cervix-cancer incidence disparity by suppression-handling method.\n\n"+md(t2b)+"\n\n")
    f.write("## Table 3A. Suppression diagnostics by ICE quintile — breast incidence.\n\n"+md(t3a)+"\n\n")
    f.write("## Table 3B. Suppression diagnostics by ICE quintile — cervix incidence.\n\n"+md(t3b)+"\n\n")
    f.write("Abbreviations: ICE, Index of Concentration at the Extremes; RR, rate ratio; RD, rate difference; CI, confidence interval; IQR, interquartile range; SCP, State Cancer Profiles. Source: NCI State Cancer Profiles release 2026-06-01; ACS 2018–2022 5-year. Suppression rule: rates with period count <16 not reported.\n")
print("Tables written to", OUT)
for t in [t1,t2a,t2b,t3a,t3b]:
    print(); print(t.to_string(index=False))
