"""
simulate.py — Aim 3: bias of complete-case disparity vs known ground truth.
Reference (executed) implementation; canonical published version is R/03_simulation.R.

DGP per replicate:
  depz ~ N(0,1); log(pop) z-score correlated with depz via corr_pop_dep
    (negative => more-deprived counties are SMALLER, the realistic case that drives bias);
  pop = exp(10.27 + 1.50 * logpop_z)        [calibrated to empirical US county sizes]
  dep_q = quintiles of depz (5 = most deprived)
  true_rate = base_rate * exp(beta * depz)  [beta = log RR per SD of deprivation]
  obs_count ~ Poisson(true_rate/1e5 * pop * years); suppress county if obs_count < threshold
Compare complete-case disparity (surviving counties, observed rates) to TRUE disparity
(all counties, true rates). Bias = estimate - truth; relative bias = bias/truth.
"""
import numpy as np, pandas as pd, itertools
from analysis_engine import disparity, complete_case

def one_rep(rng, N=3143, base_rate=15.0, beta=np.log(1.5), corr=-0.3,
            threshold=16, years=5, logmean=10.272, logsd=1.50):
    depz = rng.normal(0, 1, N)
    noise = rng.normal(0, 1, N)
    logpop_z = corr*depz + np.sqrt(max(1-corr**2, 0))*noise
    pop = np.clip(np.exp(logmean + logsd*logpop_z).astype(int), 50, None)
    dep_q = pd.qcut(depz, 5, labels=[1,2,3,4,5]).astype(int)
    true_rate = base_rate*np.exp(beta*depz)
    obs_count = rng.poisson(true_rate/1e5*pop*years)
    obs_rate = np.where(pop>0, obs_count/(pop*years)*1e5, np.nan)
    base = pd.DataFrame({"pop_total": pop, "dep_q": dep_q})
    truth = disparity(base.assign(rate=true_rate))
    sup = obs_count < threshold
    obs = base.assign(rate=np.where(sup, np.nan, obs_rate))
    cc = complete_case(obs)
    return truth, cc, float(sup.mean())

def run_cell(base_rate, beta, corr, threshold, reps=1000, seed=0, N=3143, years=5):
    rng = np.random.default_rng(seed)
    rows = []
    for _ in range(reps):
        t, c, sup = one_rep(rng, N=N, base_rate=base_rate, beta=beta, corr=corr,
                            threshold=threshold, years=years)
        rows.append((t["RR"], c["RR"], t["RD"], c["RD"], t["gradient"], c["gradient"], sup))
    a = np.array(rows, float)
    def summ(ti, ci):
        bias = a[:, ci]-a[:, ti]
        rel = bias/np.where(a[:, ti]!=0, a[:, ti], np.nan)
        return np.nanmean(a[:, ti]), np.nanmean(a[:, ci]), np.nanmean(bias), np.nanmean(rel)
    rr = summ(0,1); rd = summ(2,3); gr = summ(4,5)
    return {"base_rate": base_rate, "beta_logRR_perSD": round(beta,4), "corr_pop_dep": corr,
            "threshold": threshold, "reps": reps, "mean_suppressed": round(float(a[:,6].mean()),4),
            "RR_true": rr[0], "RR_cc": rr[1], "RR_bias": rr[2], "RR_relbias": rr[3],
            "RD_true": rd[0], "RD_cc": rd[1], "RD_bias": rd[2], "RD_relbias": rd[3],
            "grad_true": gr[0], "grad_cc": gr[1], "grad_bias": gr[2], "grad_relbias": gr[3]}

DEFAULT_GRID = dict(
    base_rate=[5, 15, 50, 150],
    beta=[0.0, np.log(1.3), np.log(1.7)],
    corr=[0.0, -0.3, -0.6],
    threshold=[10, 16, 25],
)

def run_full(grid=DEFAULT_GRID, reps=1000, seed0=2024, out="../results/aim3_simulation.csv"):
    cells = list(itertools.product(grid["base_rate"], grid["beta"], grid["corr"], grid["threshold"]))
    res = [run_cell(b, be, c, th, reps=reps, seed=seed0+i) for i,(b,be,c,th) in enumerate(cells)]
    df = pd.DataFrame(res)
    import os; os.makedirs(os.path.dirname(out), exist_ok=True); df.to_csv(out, index=False)
    print(f"wrote {len(df)} scenario cells -> {out}")
    return df

if __name__ == "__main__":
    # SMOKE TEST ONLY (tiny grid/reps) — not the registered run.
    smoke = dict(base_rate=[5, 50], beta=[np.log(1.5)], corr=[0.0, -0.6], threshold=[16])
    df = run_full(grid=smoke, reps=80, seed0=1, out="/tmp/aim3_smoke.csv")
    cols = ["base_rate","corr_pop_dep","mean_suppressed","RR_true","RR_cc","RR_relbias"]
    print(df[cols].to_string(index=False))
    print("SMOKE OK")
