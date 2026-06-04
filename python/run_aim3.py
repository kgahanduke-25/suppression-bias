"""
run_aim3.py — Aim 3 simulation (vectorized): complete-case disparity bias vs ground truth.
Executed reference; canonical port R/03_simulation.R. See OSF prereg for the DGP and grid.
"""
import numpy as np, pandas as pd, itertools, os, sys, time

N = 3143; YEARS = 5; LOGMEAN, LOGSD = 10.272, 1.50

def wq_means(rate, pop, q):
    """population-weighted mean rate per quintile 1..5 -> array index 1..5 (0 unused). NaN-safe (rate may be NaN)."""
    ok = ~np.isnan(rate)
    num = np.bincount(q[ok], weights=(rate[ok]*pop[ok]), minlength=6)
    den = np.bincount(q[ok], weights=pop[ok], minlength=6)
    with np.errstate(invalid="ignore", divide="ignore"):
        m = num/den
    return m  # m[1]..m[5]

def disparity_from_means(m):
    rr = m[5]/m[1] if m[1] > 0 else np.nan
    rd = m[5]-m[1]
    xs = np.arange(1,6.0); ys = m[1:6]
    ok = ~np.isnan(ys)
    grad = np.polyfit(xs[ok], ys[ok], 1)[0] if ok.sum() >= 2 else np.nan
    return rr, rd, grad

def quintile(depz):
    thr = np.quantile(depz, [0.2,0.4,0.6,0.8])
    return (np.digitize(depz, thr) + 1).astype(int)   # 1..5, 5 = most deprived

def run_cell(base_rate, beta, corr, threshold, reps, seed):
    rng = np.random.default_rng(seed)
    acc = np.empty((reps, 7))
    for r in range(reps):
        depz = rng.standard_normal(N)
        logpop_z = corr*depz + np.sqrt(max(1-corr**2,0))*rng.standard_normal(N)
        pop = np.clip(np.exp(LOGMEAN + LOGSD*logpop_z), 50, None)
        q = quintile(depz)
        true_rate = base_rate*np.exp(beta*depz)
        obs_count = rng.poisson(true_rate/1e5*pop*YEARS)
        obs_rate = obs_count/(pop*YEARS)*1e5
        obs_rate = np.where(obs_count < threshold, np.nan, obs_rate)
        tr = disparity_from_means(wq_means(true_rate, pop, q))
        cc = disparity_from_means(wq_means(obs_rate, pop, q))
        acc[r] = [tr[0],cc[0],tr[1],cc[1],tr[2],cc[2], np.mean(obs_count < threshold)]
    def summ(ti,ci):
        bias = acc[:,ci]-acc[:,ti]
        rel = bias/np.where(acc[:,ti]!=0, acc[:,ti], np.nan)
        return np.nanmean(acc[:,ti]), np.nanmean(acc[:,ci]), np.nanmean(bias), np.nanmean(rel)
    rr,rd,gr = summ(0,1),summ(2,3),summ(4,5)
    return {"base_rate":base_rate,"beta_logRR_perSD":round(float(beta),4),"corr_pop_dep":corr,
            "threshold":threshold,"reps":reps,"mean_suppressed":round(float(acc[:,6].mean()),4),
            "RR_true":rr[0],"RR_cc":rr[1],"RR_bias":rr[2],"RR_relbias":rr[3],
            "RD_true":rd[0],"RD_cc":rd[1],"RD_bias":rd[2],"RD_relbias":rd[3],
            "grad_true":gr[0],"grad_cc":gr[1],"grad_bias":gr[2],"grad_relbias":gr[3]}

GRID = dict(base_rate=[5,15,50,150], beta=[0.0,np.log(1.3),np.log(1.7)],
            corr=[0.0,-0.3,-0.6], threshold=[10,16,25])

if __name__ == "__main__":
    reps = int(sys.argv[1]) if len(sys.argv) > 1 else 1000
    out  = sys.argv[2] if len(sys.argv) > 2 else "../results/aim3_simulation.csv"
    cells = list(itertools.product(GRID["base_rate"],GRID["beta"],GRID["corr"],GRID["threshold"]))
    t0=time.time(); res=[]
    for i,(b,be,c,th) in enumerate(cells):
        res.append(run_cell(b,be,c,th,reps,seed=20260604+i))
    df=pd.DataFrame(res); os.makedirs(os.path.dirname(out),exist_ok=True); df.to_csv(out,index=False)
    print(f"{len(df)} cells x {reps} reps in {time.time()-t0:.1f}s -> {out}")
    cols=["base_rate","beta_logRR_perSD","corr_pop_dep","threshold","mean_suppressed","RR_true","RR_cc","RR_relbias"]
    print(df[cols].round(3).head(12).to_string(index=False))
