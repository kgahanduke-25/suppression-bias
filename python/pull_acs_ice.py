#!/usr/bin/env python3
"""
pull_acs_ice.py — Pull county-level ACS 5-year data and compute the
Index of Concentration at the Extremes for racialized economic segregation,
ICE(race+income), following Krieger et al. (AJPH 2016).

WHY YOU RUN THIS LOCALLY: the Cowork sandbox cannot reach api.census.gov.
Run this on your machine; it writes county_ice.csv into data/raw/ where the
pipeline picks it up automatically.

Definition (household-based, fully reproducible):
  A_i = # White non-Hispanic households with income >= $100,000   (privileged extreme)
  P_i = # households of color (all races minus White NH) with income < $25,000 (deprived extreme)
  T_i = total households with income data
  ICE_i = (A_i - P_i) / T_i        in [-1, +1];  +1 = all privileged, -1 = all deprived

Tables: B19001 (household income, all) and B19001H (household income, White alone not Hispanic).
Vintage: ACS 2018-2022 5-year (year=2022) to match the State Cancer Profiles
'Latest 5-year average' incidence window. Change ACS_YEAR if needed.

Usage:
  pip install requests
  export CENSUS_API_KEY=xxxx     # optional; get a free key at https://api.census.gov/data/key_signup.html
  python pull_acs_ice.py
"""
import os, sys, csv, json, urllib.request, urllib.parse

ACS_YEAR = 2022
BASE = f"https://api.census.gov/data/{ACS_YEAR}/acs/acs5"
KEY = os.environ.get("CENSUS_API_KEY", "").strip()
OUT = os.path.join(os.path.dirname(__file__), "..", "data", "raw", "county_ice.csv")

# B19001 income brackets: _002.._017. <25k = 002,003,004,005 ; >=100k = 014,015,016,017
LOW  = ["002", "003", "004", "005"]            # <10k,10-15,15-20,20-25
HIGH = ["014", "015", "016", "017"]            # 100-125,125-150,150-200,>=200k

def fetch(table):
    cols = [f"{table}_{i:03d}E" for i in range(1, 18)]  # _001 total .. _017
    params = {"get": "NAME," + ",".join(cols), "for": "county:*"}
    if KEY:
        params["key"] = KEY
    url = BASE + "?" + urllib.parse.urlencode(params)
    with urllib.request.urlopen(url, timeout=120) as r:
        data = json.load(r)
    head, *rows = data
    idx = {h: k for k, h in enumerate(head)}
    out = {}
    for row in rows:
        fips = row[idx["state"]] + row[idx["county"]]
        out[fips] = {c: (int(row[idx[c]]) if row[idx[c]] not in (None, "", "-") else 0) for c in cols}
        out[fips]["NAME"] = row[idx["NAME"]]
    return out, table

def s(d, table, codes):
    return sum(d[f"{table}_{c}E"] for c in codes)

def fetch_pop():
    """Total county population (B01003_001E) for population-weighting."""
    params = {"get": "B01003_001E", "for": "county:*"}
    if KEY:
        params["key"] = KEY
    url = BASE + "?" + urllib.parse.urlencode(params)
    with urllib.request.urlopen(url, timeout=120) as r:
        data = json.load(r)
    head, *rows = data
    idx = {h: k for k, h in enumerate(head)}
    out = {}
    for row in rows:
        fips = row[idx["state"]] + row[idx["county"]]
        v = row[idx["B01003_001E"]]
        out[fips] = int(v) if v not in (None, "", "-") else 0
    return out

def main():
    print(f"Pulling ACS {ACS_YEAR} 5-year B19001 + B19001H (county) ...", flush=True)
    allinc, _ = fetch("B19001")
    whinc, _  = fetch("B19001H")
    pop = fetch_pop()
    rows = []
    for fips, d in allinc.items():
        total = d["B19001_001E"]
        if total == 0 or fips not in whinc:
            continue
        w = whinc[fips]
        A = s(w, "B19001H", HIGH)                       # white NH, >=100k
        low_all = s(d, "B19001", LOW)                   # all races, <25k
        low_wh  = s(w, "B19001H", LOW)                  # white NH, <25k
        P = max(low_all - low_wh, 0)                    # households of color, <25k
        ice = (A - P) / total
        rows.append({"fips": fips, "county_name": d["NAME"], "pop_total": pop.get(fips, 0),
                     "hh_total": total, "A_white_highinc": A, "P_color_lowinc": P,
                     "ice_raceinc": round(ice, 5)})
    rows.sort(key=lambda r: r["fips"])
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader(); w.writerows(rows)
    print(f"Wrote {len(rows)} counties -> {os.path.abspath(OUT)}")
    print("ICE range:", min(r['ice_raceinc'] for r in rows), "to", max(r['ice_raceinc'] for r in rows))

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print("ERROR:", e, file=sys.stderr)
        print("If this is a network/key issue, get a free key at "
              "https://api.census.gov/data/key_signup.html and set CENSUS_API_KEY.", file=sys.stderr)
        sys.exit(1)
