"""make_figures_spec.py — STROBE-spec figures: Fig1 forest, Fig3 % erased by subgroup, Fig4 simulation.
Fig2 (choropleth) is produced separately by R/fig2_choropleth.R (needs county geometry)."""
import duckdb, numpy as np, pandas as pd, matplotlib, os, sys
matplotlib.use("Agg"); import matplotlib.pyplot as plt
R="../results"; F="../figures"; os.makedirs(F, exist_ok=True)
plt.rcParams.update({"font.size":11,"axes.grid":True,"grid.color":"#ececec","figure.dpi":150})
BLUE,ORANGE,GREEN,GREY="#2c7fb8","#e6550d","#31a354","#888"
order=["Breast (Female)","Stomach","Cervix"]; lab={s:s.replace(" (Female)","") for s in order}

# ---------- FIG 1: forest of RR by method, faceted by measure ----------
a1=pd.read_csv(f"{R}/aim1_disparities.csv"); a1=a1[a1.exposure=="ice"]
fig,axes=plt.subplots(1,2,figsize=(10.5,4.8))
for ax,measure in zip(axes,["incidence","mortality"]):
    d=a1[a1.measure==measure].set_index("site").loc[order].reset_index(); y=np.arange(len(order))
    for j,row in d.iterrows():
        ax.plot([row.RR_bound_lo,row.RR_bound_hi],[y[j],y[j]],color=GREY,lw=8,alpha=.30,solid_capstyle="butt",zorder=1,label="Bounding interval" if j==0 else "")
        ax.plot([row.RR_cc_lo,row.RR_cc_hi],[y[j],y[j]],color=BLUE,lw=2.5,zorder=2,label="Complete-case 95% CI" if j==0 else "")
        ax.scatter(row.RR_cc,y[j],color=BLUE,s=46,zorder=3,label="Complete-case" if j==0 else "")
        ax.scatter(row.RR_model,y[j],color=ORANGE,marker="D",s=40,zorder=3,label="Model-based" if j==0 else "")
        ax.text(row.RR_bound_hi+0.02,y[j]+0.18,f"{row.pct_suppressed:.0f}% suppr.",fontsize=8,color="#555",va="center")
    ax.axvline(1,color="#bbb",ls="--",lw=1); ax.set_yticks(y); ax.set_yticklabels([lab[s] for s in order])
    ax.set_xlabel("Rate ratio, most- vs least-deprived ICE quintile"); ax.set_title(measure.capitalize(),fontweight="bold")
axes[0].legend(fontsize=8,loc="lower right",framealpha=.9)
fig.tight_layout(); fig.savefig(f"{F}/fig1_forest_by_method.png"); plt.close(fig)

# ---------- FIG 3: % population erased by subgroup (overall / rural / minority), by site ----------
con=duckdb.connect("scp.duckdb", read_only=True)
BASE="race='All Races (includes Hispanic)' AND stage='All Stages' AND age='All Ages' AND year='Latest 5-year average'"
con.execute("CREATE OR REPLACE TEMP VIEW wht AS SELECT area_code fips, TRY_CAST(percent AS DOUBLE) v FROM demo WHERE topic='pop' AND demo_label='White' AND race='All Races (includes Hispanic)' AND sex='Both Sexes' AND age='All Ages'")
con.execute("CREATE OR REPLACE TEMP VIEW ru AS SELECT fips, any_value(rucc_note) rucc FROM incidence GROUP BY fips")
base=con.execute("""SELECT e.fips, e.pop_total, w.v pct_white, ru.rucc FROM exposure_master e
   LEFT JOIN wht w USING(fips) LEFT JOIN ru USING(fips)
   WHERE substr(e.fips,1,2) NOT IN ('72','78','60','66','69') AND e.ice_quintile_popwt IS NOT NULL""").df()
base["minority_pop"]=base.pop_total*(100-base.pct_white.fillna(0))/100
rows=[]
for site,sex in [("Breast (Female)","Female"),("Stomach","Both Sexes"),("Cervix","Female")]:
    obs=con.execute(f"SELECT DISTINCT fips FROM incidence WHERE {BASE} AND cancer='{site}' AND sex='{sex}' AND rate IS NOT NULL").df()
    d=base.merge(obs.assign(rep=1),on="fips",how="left"); sup=d.rep.isna()
    rural=d.rucc.eq("Rural")
    rows.append({"site":lab[site],
       "overall":100*d.loc[sup,"pop_total"].sum()/d.pop_total.sum(),
       "rural":100*d.loc[sup&rural,"pop_total"].sum()/d.loc[rural,"pop_total"].sum(),
       "minority":100*d.loc[sup,"minority_pop"].sum()/d.minority_pop.sum()})
con.close()
er=pd.DataFrame(rows).set_index("site").loc[[lab[s] for s in order]]
fig,ax=plt.subplots(figsize=(8,4.6)); x=np.arange(len(order)); w=0.26
ax.bar(x-w,er["overall"],w,label="Overall population",color=BLUE)
ax.bar(x,  er["rural"], w,label="Rural population",color=ORANGE)
ax.bar(x+w,er["minority"],w,label="Minority population",color=GREEN)
ax.set_xticks(x); ax.set_xticklabels([lab[s] for s in order]); ax.set_ylim(0,100)
ax.set_ylabel("% of subgroup population erased (complete-case)")
ax.set_title("Suppression erases rural population far more than minority population",fontweight="bold",fontsize=11.5)
ax.legend(fontsize=9)
fig.tight_layout(); fig.savefig(f"{F}/fig3_pct_erased_subgroup.png"); plt.close(fig)

# ---------- FIG 4: simulation — complete-case vs true; bias vs threshold ----------
sim=pd.read_csv(f"{R}/aim3_simulation.csv")
fig,axes=plt.subplots(1,2,figsize=(10.5,4.4))
s=sim[(abs(sim.beta_logRR_perSD-0.5306)<0.01)]  # strong gradient slice
cmap={5:"#08519c",15:"#3182bd",50:"#6baed6",150:"#bdd7e7"}
for br in [5,15,50,150]:
    d=s[s.base_rate==br]
    axes[0].scatter(d.RR_true,d.RR_cc,s=28,color=cmap[br],label=f"{br}/100k",alpha=.85)
lims=[s.RR_true.min()-0.1,s.RR_true.max()+0.1]
axes[0].plot(lims,lims,"--",color="#999"); axes[0].set_xlim(lims); axes[0].set_ylim(lims)
axes[0].set_xlabel("True disparity (rate ratio)"); axes[0].set_ylabel("Complete-case estimate")
axes[0].set_title("Complete-case vs truth (by base rate)",fontsize=10.5,fontweight="bold"); axes[0].legend(title="Base incidence",fontsize=8)
# rare cancer (base 5); bias vs threshold separated by deprivation-county-size correlation
ccol={0.0:"#bdbdbd",-0.3:"#3182bd",-0.6:"#08519c"}
clab={0.0:"corr 0 (size ⊥ deprivation)",-0.3:"corr −0.3 (observed)",-0.6:"corr −0.6 (steeper)"}
sr=sim[(abs(sim.beta_logRR_perSD-0.5306)<0.01)&(sim.base_rate==5)]
for c in [0.0,-0.3,-0.6]:
    d=sr[sr.corr_pop_dep==c].sort_values("threshold")
    axes[1].plot(d.threshold,d.RR_relbias*100,"-o",color=ccol[c],label=clab[c])
axes[1].axhline(0,color="#bbb",lw=1)
axes[1].set_xlabel("Suppression threshold (period count)"); axes[1].set_ylabel("Relative bias in rate ratio (%)")
axes[1].set_title("Bias vs threshold (rare cancer), by deprivation–size correlation",fontsize=9.5,fontweight="bold"); axes[1].set_xticks([10,16,25]); axes[1].legend(fontsize=7.5)
fig.suptitle("Simulation: population-weighted complete-case bias is small; direction depends on the deprivation–size gradient",fontsize=10.8,fontweight="bold")
fig.tight_layout(rect=[0,0,1,0.94]); fig.savefig(f"{F}/fig4_simulation.png"); plt.close(fig)
print("wrote fig1_forest_by_method.png, fig3_pct_erased_subgroup.png, fig4_simulation.png")
print(er.round(1).to_string())
