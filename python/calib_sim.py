"""
calib_sim.py — calibrated Aim 3 sensitivity. Fixes the deprivation-county-size correlation
to the empirical value (~ -0.30) and reports complete-case disparity bias vs truth for
(a) population-weighted and (b) unweighted county-unit aggregation, under Poisson and
overdispersed (gamma-Poisson) count models. Answers "how big is the bias, calibrated?"
"""
import numpy as np, pandas as pd, sys, os
N=3143; YEARS=5; LOGMEAN, LOGSD=10.272,1.50

def quintile(z):
    thr=np.quantile(z,[0.2,0.4,0.6,0.8]); return (np.digitize(z,thr)+1).astype(int)

def wmeans(rate,w,q):
    ok=~np.isnan(rate)
    num=np.bincount(q[ok],weights=rate[ok]*w[ok],minlength=6)
    den=np.bincount(q[ok],weights=w[ok],minlength=6)
    with np.errstate(invalid='ignore',divide='ignore'): return num/den
def rr(m): return m[5]/m[1] if m[1]>0 else np.nan

def cell(base, beta, corr, threshold, od, reps, seed):
    rng=np.random.default_rng(seed)
    out=np.empty((reps,4))  # rr_true, rr_cc_w, rr_cc_unw, supp
    for r in range(reps):
        depz=rng.standard_normal(N)
        lpz=corr*depz+np.sqrt(max(1-corr**2,0))*rng.standard_normal(N)
        pop=np.clip(np.exp(LOGMEAN+LOGSD*lpz),50,None)
        q=quintile(depz)
        true_rate=base*np.exp(beta*depz)
        mu=true_rate/1e5*pop*YEARS
        if od>0:  # gamma-Poisson overdispersion: var = mu + od*mu^2
            shape=1.0/od; mu=mu*rng.gamma(shape,1.0/shape,N)
        cnt=rng.poisson(mu)
        obs=np.where(cnt<threshold, np.nan, cnt/(pop*YEARS)*1e5)
        tr=rr(wmeans(true_rate,pop,q))
        ccw=rr(wmeans(obs,pop,q))
        ccu=rr(wmeans(obs,np.ones(N),q))
        out[r]=[tr,ccw,ccu,np.mean(cnt<threshold)]
    tr=np.nanmean(out[:,0])
    return {"base_rate":base,"corr_pop_dep":corr,"threshold":threshold,"overdisp":od,
            "mean_suppressed":round(float(out[:,3].mean()),3),"RR_true":round(tr,3),
            "RR_cc_wt":round(np.nanmean(out[:,1]),3),"RR_cc_unwt":round(np.nanmean(out[:,2]),3),
            "relbias_wt":round((np.nanmean(out[:,1])-tr)/tr,3),
            "relbias_unwt":round((np.nanmean(out[:,2])-tr)/tr,3)}

if __name__=="__main__":
    CORR=-0.30; BETA=np.log(1.7)  # strong gradient; calibrated corr
    rows=[]
    for base in [5,15,50,150]:
        for od in [0.0, 0.5]:   # Poisson, and moderate overdispersion
            rows.append(cell(base,BETA,CORR,16,od,reps=800,seed=2026+int(base)+int(od*10)))
    df=pd.DataFrame(rows)
    out="../results/aim3_calibrated_sensitivity.csv"; os.makedirs(os.path.dirname(out),exist_ok=True)
    df.to_csv(out,index=False)
    print(df.to_string(index=False))
    print("-> ",out)
