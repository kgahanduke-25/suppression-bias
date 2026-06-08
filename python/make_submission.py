"""make_submission.py — assemble medRxiv submission package into ../submission/.
Builds manuscript_full.md from the manuscript/ sections + tables + figures, then pandoc -> manuscript.pdf.
Times font via newtx; wide Table 1 in landscape. Run from python/ with project as parent.
"""
import pandas as pd, os, shutil, subprocess, sys, textwrap
ROOT=os.path.abspath(os.path.join(os.path.dirname(__file__),".."))
M=os.path.join(ROOT,"manuscript"); RES=os.path.join(ROOT,"results"); FIG=os.path.join(ROOT,"figures")
SUB=os.path.join(ROOT,"submission"); os.makedirs(SUB,exist_ok=True)

def read(p):
    with open(p) as f: return f.read()
def strip_first_heading(t):
    lines=t.splitlines()
    return "\n".join(l for i,l in enumerate(lines) if not (i<3 and l.startswith("# ")))

# ---- figures (copy + rename) ----
figmap={"fig1_forest_by_method.png":"figure1.png","fig3_pct_erased_subgroup.png":"figure2.png","fig4_simulation.png":"figure3.png"}
for src,dst in figmap.items():
    shutil.copy(os.path.join(FIG,src),os.path.join(SUB,dst))

# ---- tables from CSV -> markdown ----
def tbl(csv): return pd.read_csv(os.path.join(RES,csv)).to_markdown(index=False)
t1=tbl("table1_baseline.csv"); t2a=tbl("table2_breast.csv"); t2b=tbl("table2_cervix.csv")
t3a=tbl("table3_breast.csv"); t3b=tbl("table3_cervix.csv")

tables_block = (
"# Tables\n\n"
"\\footnotesize\n\n"
"**Table 1.** Characteristics of US counties (n=3,143; analytic n=3,018) by ICE Race+Income quintile, ACS 2018–2022. "
"Unit = county; population-weighted ICE quintiles (Q1 = most deprived). Continuous: median [IQR] or mean (SD) as labelled; categorical: n (%). "
"Std. diff = standardized difference (Q1 vs Q5). Quintiles are population-weighted, so county counts differ across quintiles.\n\n"
+t1+"\n\n\\normalsize\n\n"
"\\footnotesize\n\n"
"**Table 2A.** Estimated breast-cancer incidence disparity (most- vs least-deprived ICE quintile) by suppression-handling method.\n\n"+t2a+"\n\n"
"**Table 2B.** Estimated cervix-cancer incidence disparity by suppression-handling method.\n\n"+t2b+"\n\n"
"**Table 3A.** Suppression diagnostics by ICE quintile — breast incidence.\n\n"+t3a+"\n\n"
"**Table 3B.** Suppression diagnostics by ICE quintile — cervix incidence.\n\n"+t3b+"\n\n"
"\\normalsize\n\n"
"*Abbreviations:* ICE, Index of Concentration at the Extremes; RR, rate ratio; RD, rate difference; CI, confidence interval; "
"IQR, interquartile range; SCP, State Cancer Profiles. *Source:* NCI State Cancer Profiles release 2026-06-01; ACS 2018–2022 5-year. "
"*Suppression rule:* rates with period count <16 are not reported.\n\n")

# ---- figures block (self-contained captions) ----
figs_block = (
"# Figures\n\n"
"![Estimated most- vs least-deprived ICE(race+income) quintile rate ratio (RR) for breast, stomach, and "
"cervix cancer, by suppression-handling method, for incidence (left) and mortality (right). Unit = county; blue circle = "
"population-weighted complete-case point estimate with 95% bootstrap CI; orange diamond = model-based small-area estimate; "
"grey bar = bounding interval; dashed line = no disparity (RR=1); labels = % of counties suppressed. Source: NCI State Cancer "
"Profiles release 2026-06-01; ACS 2018–2022.](figure1.png){width=95%}\n\n"
"![Percent of each subgroup's population erased under complete-case analysis (suppressed counties), by site. "
"Unit = county; subgroups are overall, rural, and minority (non-White) population. Source: NCI State Cancer Profiles release "
"2026-06-01; ACS 2018–2022.](figure2.png){width=80%}\n\n"
"![Simulation against known truth. Left: complete-case rate-ratio estimate versus the true rate ratio across "
"scenarios, by base incidence (identity line dashed). Right: relative bias in the rate ratio versus suppression threshold for a "
"rare cancer, by the deprivation–county-size correlation (observed = −0.30). Population-weighted estimand; 1,000 replicates per "
"cell (Monte Carlo SE of bias ≈0.0025).](figure3.png){width=95%}\n\n")

yaml = textwrap.dedent(r"""---
fontsize: 11pt
geometry: margin=1in
linkcolor: blue
urlcolor: blue
header-includes:
  - \usepackage{mathptmx}
  - \usepackage{booktabs}
  - \usepackage{longtable}
  - \usepackage{pdflscape}
  - \usepackage{float}
  - \usepackage{ragged2e}
  - \setlength{\emergencystretch}{3em}
---
""")

titleblock = textwrap.dedent(r"""
\begin{center}
{\Large\bfseries Bias from small-count suppression in county-level cancer disparity estimates: a calibrated simulation study}\\[8pt]
{\large Kamalakanta Gahan\textsuperscript{1}}\\[4pt]
\footnotesize \textsuperscript{1}Department of Population Health Sciences, Duke University, Durham, NC, USA\\
Corresponding author: Kamalakanta Gahan (email: \texttt{kamalakanta.gahan@duke.edu}; ORCID: 0000-0002-4880-6228)\\
Pre-registration: OSF \href{https://doi.org/10.17605/OSF.IO/BJZR5}{10.17605/OSF.IO/BJZR5} \quad
Code: \href{https://github.com/kgahanduke-25/suppression-bias}{github.com/kgahanduke-25/suppression-bias}
\normalsize
\end{center}

\vspace{6pt}
""")

abstract = strip_first_heading(read(os.path.join(M,"00_abstract.md")))
intro=read(os.path.join(M,"01_introduction.md"))
methods=read(os.path.join(M,"02_methods.md"))
results=read(os.path.join(M,"03_results.md"))
discussion=read(os.path.join(M,"04_discussion.md"))
statements=read(os.path.join(M,"05_statements.md"))
refs=read(os.path.join(M,"references.md"))

full = (yaml + titleblock + "\n\n" + abstract + "\n\n\\newpage\n\n" + intro + "\n\n" + methods +
        "\n\n" + results + "\n\n" + tables_block + "\\newpage\n\n" + figs_block + "\\newpage\n\n" +
        discussion + "\n\n\\newpage\n\n" + statements + "\n\n\\newpage\n\n" + refs)
# sanitize math/space unicode for pdflatex
repl={"≈":r"$\approx$","×":r"$\times$","−":"-","≥":r"$\ge$","≤":r"$\le$",
      " ":" "," ":" ","′":"'","≈":r"$\approx$"}
full=full.replace("$",r"\$")
full=full.replace("β","beta").replace("α","alpha").replace("·",".").replace("−","-")
repl={"≈":"approx. ","×":" x ","−":"-","≥":">=","≤":"<=",
      "′":"'"," ":" "," ":" "}
for k,v in repl.items(): full=full.replace(k,v)
full_path=os.path.join(SUB,"manuscript_full.md")
with open(full_path,"w") as f: f.write(full)

cmd=["pandoc","manuscript_full.md","-o","manuscript.pdf","--pdf-engine=pdflatex"]
r=subprocess.run(cmd,cwd=SUB,capture_output=True,text=True)
print("PANDOC manuscript rc=",r.returncode)
if r.returncode!=0: print(r.stdout[-2500:]); print("STDERR:",r.stderr[-2500:])
else: print("manuscript.pdf built")

# ---------------- SUPPLEMENT ----------------
sim=pd.read_csv(os.path.join(RES,"aim3_simulation.csv"))
s1=sim[["base_rate","beta_logRR_perSD","corr_pop_dep","threshold","mean_suppressed","RR_true","RR_cc","RR_relbias"]].copy()
s1=s1.round({"beta_logRR_perSD":3,"mean_suppressed":3,"RR_true":3,"RR_cc":3,"RR_relbias":4})
s2=pd.read_csv(os.path.join(RES,"aim3_calibrated_sensitivity.csv")).round(3)

strobe=[("1 Title/abstract","Design in title; structured abstract","Title; Abstract"),
("2 Background","Scientific background, rationale","Introduction"),
("3 Objectives","Stated objective/aim","Introduction (aim)"),
("4 Study design","Key design elements","Methods 1"),
("5 Setting","Setting, locations, dates","Methods 1,4"),
("6 Participants","Units, eligibility","Methods 2"),
("7 Variables","Exposure, outcome, covariates","Methods 3-4"),
("8 Data sources/measurement","Sources, measurement","Methods 1,3,4"),
("9 Bias","Sources of bias addressed","Methods 6; Discussion"),
("10 Study size","How arrived at","Methods 2,7"),
("11 Quantitative variables","Handling, groupings","Methods 3,5"),
("12 Statistical methods","Methods, subgroups, sensitivity","Methods 5-9"),
("13 Participants (results)","Numbers at each stage","Results (sample)"),
("14 Descriptive data","Characteristics","Table 1"),
("15 Outcome data","Outcomes/events","Tables 2-3"),
("16 Main results","Estimates + CIs","Tables 2; Figs 1,3"),
("17 Other analyses","Subgroups/sensitivity/sim","Methods 7-9; Fig 3"),
("18 Key results","Summary re objectives","Discussion 1"),
("19 Limitations","Limitations, bias direction","Discussion 5"),
("20 Interpretation","Cautious overall interpretation","Discussion 2-3,7"),
("21 Generalisability","External validity","Discussion 2,6"),
("22 Funding","Funding role","Statements")]
strobe_md=pd.DataFrame(strobe,columns=["STROBE item","Recommendation","Location"]).to_markdown(index=False)

sup = (yaml + "\n"
 "\\begin{center}{\\Large\\bfseries Supplementary Material}\\\\[4pt]"
 "{Bias from small-count suppression in county-level cancer disparity estimates: a calibrated simulation study}\\end{center}\n\n"
 "## Supplementary Table S1. Full simulation grid (108 scenarios)\nPopulation-weighted complete-case rate ratio versus known truth. "
 "beta = log rate ratio per SD of deprivation; corr = deprivation-county-size correlation. 1,000 replicates/cell.\n\n"
 "\\footnotesize\n\n"+s1.to_markdown(index=False)+"\n\n\\normalsize\n\n"
 "## Supplementary Table S2. Calibrated sensitivity (corr = -0.30)\nPopulation-weighted vs unweighted; Poisson (overdisp 0) and overdispersed (0.5).\n\n"
 "\\footnotesize\n\n"+s2.to_markdown(index=False)+"\n\n\\normalsize\n\n"
 "## Supplementary Table S3. STROBE checklist (cross-sectional)\n\n\\footnotesize\n\n"+strobe_md+"\n\n\\normalsize\n\n"
 "Simulation reporting follows ADEMP (Morris et al., 2019): aims, data-generating mechanisms, estimands, methods, and performance measures "
 "(bias, percent bias, Monte Carlo SE) are specified in Methods section 7.\n")
sup=sup.replace("$",r"\$").replace("β","beta").replace("α","alpha").replace("·",".").replace("−","-")
for k,v in repl.items(): sup=sup.replace(k,v)
with open(os.path.join(SUB,"supplement_full.md"),"w") as f: f.write(sup)
r2=subprocess.run(["pandoc","supplement_full.md","-o","supplement.pdf","--pdf-engine=pdflatex"],cwd=SUB,capture_output=True,text=True)
print("PANDOC supplement rc=",r2.returncode)
if r2.returncode!=0: print(r2.stderr[-2000:])
else: print("supplement.pdf built")

# ---------------- METADATA ----------------
meta=f"""medRxiv submission metadata — paste-ready (fill [TO COMPLETE] before submitting)

SUBJECT AREA: Epidemiology  (alternative: Health Informatics)

TITLE: Bias from small-count suppression in county-level cancer disparity estimates: a calibrated simulation study

CORRESPONDING AUTHOR: Kamalakanta Gahan — Department of Population Health Sciences, Duke University, Durham, NC, USA
  Email: kamalakanta.gahan@duke.edu   ORCID: 0000-0002-4880-6228   (mark as corresponding author)

AUTHOR LIST: Kamalakanta Gahan (sole)  [if adding a senior co-author, add here and update CRediT in the PDF]

ABSTRACT: (see manuscript.pdf, structured Background/Methods/Results/Conclusions; paste plain text if the form requires)

AUTHOR APPROVAL: All authors have seen and approved the manuscript. (Sole author: yes.)

COMPETING INTERESTS: The author declares no competing interests.

FUNDING: [TO COMPLETE — e.g., "This research received no specific grant from any funding agency in the public, commercial, or not-for-profit sectors." or your assistantship.]

DECLARATIONS:
  - Human subjects / ethics: No. Secondary analysis of publicly available, de-identified, aggregate data; not human-subjects research / IRB-exempt.
  - Clinical trial: Not applicable.
  - Funding, competing-interest, and data statements are included in the manuscript.

DATA AVAILABILITY STATEMENT:
  All data are publicly available. County cancer statistics were obtained from the NCI State Cancer Profiles public release (seandavi/state-cancer-profile-scraper, tag 2026-06-01); population and ICE covariates from the American Community Survey (2018-2022 5-year, tables B19001/B19001H/B01003); rurality from USDA Rural-Urban Continuum Codes (2023). All analysis and simulation code and the pre-registration are openly available at https://github.com/kgahanduke-25/suppression-bias and https://doi.org/10.17605/OSF.IO/BJZR5.

DATA AVAILABILITY LINKS: https://github.com/kgahanduke-25/suppression-bias ; https://doi.org/10.17605/OSF.IO/BJZR5

CLINICAL PROTOCOLS: Not applicable.

DISTRIBUTION/REUSE LICENSE: CC-BY 4.0 (recommended).

FILES:
  - manuscript.pdf  (single complete PDF: title, abstract, full text, tables, figures)
  - supplement.pdf  (Supplementary Tables S1-S3: simulation grid, calibrated sensitivity, STROBE checklist)
  Filenames contain only letters/numbers/hyphen/underscore.

REPORTING GUIDELINES: STROBE (cross-sectional) + ADEMP (simulation).
"""
with open(os.path.join(SUB,"submission_metadata.txt"),"w") as f: f.write(meta)
print("submission_metadata.txt written")
