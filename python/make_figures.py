"""make_figures.py — manuscript figures from results/ CSVs. Outputs to figures/."""
import pandas as pd, numpy as np, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.ticker import PercentFormatter
import os
R="../results"; F="../figures"; os.makedirs(F, exist_ok=True)
plt.rcParams.update({"font.size":11,"axes.spedge_color" if False else "axes.edgecolor":"#444",
                     "axes.grid":True,"grid.color":"#e6e6e6","figure.dpi":150})
BLUE,ORANGE,GREEN,GREY="#2c7fb8","#e6550d","#31a354","#888"

# ---------- Figure 1: erasure profile (the equity headline) ----------
a2=pd.read_csv(f"{R}/aim2_erasure.csv")
order=["Breast (Female)","Stomach","Cervix"]; a2=a2.set_index("site").loc[order].reset_index()
metrics=[("pct_counties_suppressed","% of counties erased"),
         ("pct_pop_suppressed","% of population erased"),
         ("pct_rural_counties_suppressed","% of rural counties erased"),
         ("pct_Q5_suppressed","% of most-deprived quintile erased")]
fig,ax=plt.subplots(figsize=(8.2,4.6))
x=np.arange(len(order)); w=0.2
for i,(col,lab) in enumerate(metrics):
    ax.bar(x+(i-1.5)*w, a2[col], w, label=lab)
ax.set_xticks(x); ax.set_xticklabels([s.replace(" (Female)","") for s in order])
ax.set_ylabel("Percent erased under complete-case"); ax.set_ylim(0,100)
ax.set_title("Suppression erases most rural and most-deprived counties for rarer cancers",fontsize=12,fontweight="bold")
ax.legend(fontsize=8.5,loc="upper left",framealpha=.9)
fig.tight_layout(); fig.savefig(f"{F}/fig1_erasure.png"); plt.close(fig)

# ---------- Figure 2: disparity RR by method, faceted by measure (fragility) ----------
a1=pd.read_csv(f"{R}/aim1_disparities.csv")
a1=a1[a1.exposure=="ice"]
fig,axes=plt.subplots(1,2,figsize=(10,4.8),sharey=False)
for ax,measure in zip(axes,["incidence","mortality"]):
    d=a1[a1.measure==measure].set_index("site").loc[order].reset_index()
    y=np.arange(len(order))
    # bounding interval (light bar), complete-case point+CI, model point
    for j,row in d.iterrows():
        ax.plot([row.RR_bound_lo,row.RR_bound_hi],[y[j],y[j]],color=GREY,lw=7,alpha=.35,
                solid_capstyle="butt",zorder=1,label="Bounding interval" if j==0 else "")
        ax.plot([row.RR_cc_lo,row.RR_cc_hi],[y[j],y[j]],color=BLUE,lw=2,zorder=2,
                label="Complete-case 95% CI" if j==0 else "")
        ax.scatter(row.RR_cc,y[j],color=BLUE,zorder=3,s=42,label="Complete-case" if j==0 else "")
        ax.scatter(row.RR_model,y[j],color=ORANGE,marker="D",zorder=3,s=38,label="Model-based" if j==0 else "")
        ax.text(row.RR_bound_hi+0.02,y[j]+0.16,f"{row.pct_suppressed:.0f}% suppr.",fontsize=8,color="#555",va="center")
    ax.axvline(1,color="#bbb",ls="--",lw=1)
    ax.set_yticks(y); ax.set_yticklabels([s.replace(" (Female)","") for s in order])
    ax.set_xlabel("Rate ratio (most- vs least-deprived ICE quintile)")
    ax.set_title(measure.capitalize(),fontsize=11,fontweight="bold")
axes[0].legend(fontsize=8,loc="lower right",framealpha=.9)
fig.suptitle("Point estimate is robust; the bounding interval — and method sensitivity — widen with suppression",
             fontsize=12,fontweight="bold")
fig.tight_layout(rect=[0,0,1,0.95]); fig.savefig(f"{F}/fig2_disparity_methods.png"); plt.close(fig)

# ---------- Figure 3: calibrated simulation bias ----------
cal=pd.read_csv(f"{R}/aim3_calibrated_sensitivity.csv")
full=pd.read_csv(f"{R}/aim3_simulation.csv")
fig,axes=plt.subplots(1,2,figsize=(10,4.4))
# panel A: calibrated relbias vs suppression (weighted vs unweighted), Poisson
c0=cal[cal.overdisp==0.0].sort_values("mean_suppressed")
axes[0].plot(c0.mean_suppressed*100,c0.relbias_wt*100,"-o",color=BLUE,label="Population-weighted")
axes[0].plot(c0.mean_suppressed*100,c0.relbias_unwt*100,"-s",color=ORANGE,label="Unweighted county-unit")
axes[0].axhline(0,color="#bbb",lw=1)
axes[0].set_xlabel("% counties suppressed"); axes[0].set_ylabel("Relative bias in rate ratio (%)")
axes[0].set_title("Calibrated bias (real dep-size corr = -0.30)",fontsize=10.5,fontweight="bold")
axes[0].legend(fontsize=8.5); axes[0].set_ylim(-8,8)
# panel B: bias vs deprivation-size correlation (rare cancer), shows conditional direction
sub=full[(abs(full.beta_logRR_perSD-0.5306)<0.01)&(full.base_rate==5)&(full.threshold==16)]
sub=sub.sort_values("corr_pop_dep")
axes[1].plot(sub.corr_pop_dep,sub.RR_relbias*100,"-o",color=GREEN)
axes[1].axhline(0,color="#bbb",lw=1); axes[1].axvline(-0.30,color=GREY,ls=":",lw=1.5)
axes[1].text(-0.30,axes[1].get_ylim()[1]*0.8," real corr",fontsize=8,color="#555")
axes[1].set_xlabel("Deprivation–county-size correlation"); axes[1].set_ylabel("Relative bias in rate ratio (%)")
axes[1].set_title("Bias direction is conditional (rare cancer)",fontsize=10.5,fontweight="bold")
fig.suptitle("Population-weighted disparity bias is small and condition-dependent once calibrated to data",
             fontsize=12,fontweight="bold")
fig.tight_layout(rect=[0,0,1,0.94]); fig.savefig(f"{F}/fig3_simulation.png"); plt.close(fig)
print("wrote fig1_erasure.png, fig2_disparity_methods.png, fig3_simulation.png")
