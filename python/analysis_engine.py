"""
analysis_engine.py — disparity estimands + four suppression-handling methods.
Reference (executed) implementation. Canonical published version is R/02_aims_1_2.R.

A "county frame" is a DataFrame with columns:
  fips, pop_total (weight), dep_q (1..5, where 5 = MOST deprived), rate (age-adj /100k; NaN if suppressed/absent)
  [for bounding] pop_total + years;  [for model] state_fips.

Disparity estimands (most- vs least-deprived quintile):
  RR = rate(most)/rate(least);  RD = rate(most) - rate(least);
  gradient = OLS slope of quintile mean rate on quintile rank (1..5).
Quintile rate = population-weighted mean of county rates within the quintile.
NOTE on exposure direction: dep_q must be coded so 5 = MOST deprived. For ICE
(where lowest ICE = most deprived) the pipeline flips the quintile before calling this.
"""
import numpy as np
import pandas as pd

MOST, LEAST = 5, 1

def _wmean(vals, w):
    vals = np.asarray(vals, float); w = np.asarray(w, float)
    m = ~np.isnan(vals) & (w > 0)
    return np.nan if m.sum() == 0 else np.sum(vals[m]*w[m])/np.sum(w[m])

def quintile_rates(df):
    return {int(q): _wmean(g["rate"].values, g["pop_total"].values) for q, g in df.groupby("dep_q")}

def gradient(qr):
    xs = np.array([k for k in sorted(qr) if not np.isnan(qr[k])], float)
    ys = np.array([qr[k] for k in sorted(qr) if not np.isnan(qr[k])], float)
    return np.nan if len(xs) < 2 else float(np.polyfit(xs, ys, 1)[0])

def disparity(df):
    qr = quintile_rates(df)
    least = qr.get(LEAST, np.nan)
    rr = qr.get(MOST, np.nan)/least if least else np.nan
    return {"RR": rr, "RD": qr.get(MOST, np.nan) - least, "gradient": gradient(qr),
            "rate_most": qr.get(MOST, np.nan), "rate_least": least}

def complete_case(df):
    return disparity(df[~df["rate"].isna()].copy())

def available_case(df):
    res = complete_case(df); acct = []
    for q, g in df.groupby("dep_q"):
        kept = g[~g["rate"].isna()]
        acct.append({"dep_q": int(q), "counties_total": len(g), "counties_kept": len(kept),
                     "pop_total": float(g["pop_total"].sum()), "pop_kept": float(kept["pop_total"].sum()),
                     "pop_lost_frac": 1 - kept["pop_total"].sum()/max(g["pop_total"].sum(), 1)})
    res["retention"] = pd.DataFrame(acct); return res

def bounding(df, threshold=16, years=5):
    """Manski-style worst/best-case bounds. For a ratio/difference of the most- (Q5) vs
    least-deprived (Q1) quintile, the extremal value pushes numerator and denominator in
    OPPOSITE directions: each suppressed county's true rate lies in [0, (threshold-1)/PY].
    Max RR/RD: Q5 suppressed -> max, Q1 suppressed -> 0. Min RR/RD: Q5 -> 0, Q1 -> max.
    Observed counties keep their rates; population weighting retained."""
    d = df.copy(); sup = d["rate"].isna()
    maxrate = (threshold - 1) / (d["pop_total"] * years) * 1e5
    def qmean(frame, q):
        g = frame[frame["dep_q"] == q]
        return _wmean(g["rate"].values, g["pop_total"].values)
    def scenario(q5_to, q1_to):
        f = d.copy()
        m5 = sup & (f.dep_q == MOST); m1 = sup & (f.dep_q == LEAST)
        f.loc[m5, "rate"] = maxrate[m5] if q5_to == "max" else 0.0
        f.loc[m1, "rate"] = maxrate[m1] if q1_to == "max" else 0.0
        return qmean(f, MOST), qmean(f, LEAST)
    q5hi, q1lo = scenario("max", "low")   # -> max RR/RD
    q5lo, q1hi = scenario("low", "max")   # -> min RR/RD
    rr = tuple(sorted([q5lo / q1hi if q1hi else float("nan"), q5hi / q1lo if q1lo else float("nan")]))
    rd = tuple(sorted([q5lo - q1hi, q5hi - q1lo]))
    # gradient: coarse range under all-0 vs all-max imputation
    d0 = d.copy(); d0.loc[sup, "rate"] = 0.0
    dM = d.copy(); dM.loc[sup, "rate"] = maxrate[sup]
    g = tuple(sorted([gradient(quintile_rates(d0)), gradient(quintile_rates(dM))]))
    return {"RR": rr, "RD": rd, "gradient": g,
            "low": {"RR": rr[0], "RD": rd[0], "gradient": g[0]},
            "high": {"RR": rr[1], "RD": rd[1], "gradient": g[1]}}

def model_based(df, years=5):
    """Empirical-Bayes state-prior shrinkage stand-in for a hierarchical Poisson small-area model.
       Suppressed counties imputed by their state's pop-weighted mean rate (national fallback)."""
    d = df.copy(); obs = d[~d["rate"].isna()]
    natl = _wmean(obs["rate"], obs["pop_total"])
    state_mean = {s: _wmean(g["rate"], g["pop_total"]) for s, g in obs.groupby("state_fips")}
    def pred(row):
        if not np.isnan(row["rate"]): return row["rate"]
        sm = state_mean.get(row["state_fips"], natl)
        return sm if not np.isnan(sm) else natl
    d["rate"] = d.apply(pred, axis=1); return disparity(d)

def bootstrap(df, fn, B=500, seed=1, **kw):
    rng = np.random.default_rng(seed); keys = ["RR","RD","gradient"]; acc = {k: [] for k in keys}
    idx_by_q = {q: g.index.values for q, g in df.groupby("dep_q")}
    for _ in range(B):
        bs = pd.concat([df.loc[rng.choice(ix, len(ix), replace=True)] for ix in idx_by_q.values()])
        r = fn(bs, **kw)
        for k in keys:
            v = r[k]; acc[k].append(v if np.isscalar(v) else np.nan)
    return {k: (float(np.nanpercentile(acc[k], 2.5)), float(np.nanpercentile(acc[k], 97.5))) for k in keys}

if __name__ == "__main__":
    rng = np.random.default_rng(42); N = 3000
    pop = np.exp(rng.normal(10.27, 1.50, N)).astype(int) + 100
    depz = rng.normal(0, 1, N)
    dep_q = pd.qcut(depz, 5, labels=[1,2,3,4,5]).astype(int)
    base, beta, years = 15.0, np.log(1.5), 5
    true_rate = base * np.exp(beta * depz)
    obs_count = rng.poisson(true_rate/1e5 * pop * years)
    obs_rate = obs_count/(pop*years)*1e5
    df = pd.DataFrame({"fips": np.arange(N), "pop_total": pop, "dep_q": dep_q,
                       "rate": obs_rate, "state_fips": rng.integers(1, 50, N)})
    truth = disparity(df.assign(rate=true_rate))
    dsup = df.copy(); dsup.loc[obs_count < 16, "rate"] = np.nan
    n_sup = int((obs_count < 16).sum())
    cc, bd, mb = complete_case(dsup), bounding(dsup, 16, years), model_based(dsup, years)
    print(f"synthetic N={N}  suppressed={n_sup} ({100*n_sup/N:.1f}%)")
    print(f"TRUE      RR={truth['RR']:.3f} RD={truth['RD']:.2f} grad={truth['gradient']:.3f}")
    print(f"complete  RR={cc['RR']:.3f} RD={cc['RD']:.2f} grad={cc['gradient']:.3f}")
    print(f"model     RR={mb['RR']:.3f} RD={mb['RD']:.2f} grad={mb['gradient']:.3f}")
    print(f"bounds    RR={tuple(round(x,3) for x in bd['RR'])}  RD={tuple(round(x,2) for x in bd['RD'])}")
    ci = bootstrap(dsup, complete_case, B=200, seed=7)
    print(f"complete-case bootstrap RR CI = {tuple(round(x,3) for x in ci['RR'])}")
    print("SELF-TEST OK")
