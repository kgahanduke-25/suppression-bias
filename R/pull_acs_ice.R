#!/usr/bin/env Rscript
# pull_acs_ice.R — county ICE(race+income) + total population from ACS 5-year,
# using tidycensus. Run this LOCALLY (the Cowork sandbox cannot reach the Census API).
# Writes ../data/raw/county_ice.csv for the pipeline to pick up.
#
# ICE(race+income), Krieger et al. (AJPH 2016), household-based:
#   A = White non-Hispanic households with income >= $100,000      (B19001H 014:017)
#   P = households of color (all - White NH) with income < $25,000  (B19001 002:005 - B19001H 002:005)
#   T = total households (B19001_001);  ICE = (A - P) / T  in [-1, 1]; lower = more deprived
#
# Setup (once):
#   install.packages(c("tidycensus","dplyr","tidyr","readr"))
#   tidycensus::census_api_key("YOUR_KEY", install = TRUE)   # free: https://api.census.gov/data/key_signup.html
# Then:
#   Rscript pull_acs_ice.R

suppressPackageStartupMessages({
  library(tidycensus); library(dplyr); library(tidyr); library(readr)
})

ACS_YEAR <- 2022   # ACS 2018-2022 5-year, matches 'Latest 5-year average' cancer window
# Robust to working directory: works whether wd is the project root or the R/ folder.
find_out <- function() {
  for (d in c("data/raw", "../data/raw", file.path(getwd(), "data/raw"))) {
    if (dir.exists(d)) return(file.path(d, "county_ice.csv"))
  }
  dir.create("data/raw", recursive = TRUE, showWarnings = FALSE)
  "data/raw/county_ice.csv"
}
out_path <- find_out()

low_codes  <- sprintf("%03d", 2:5)    # <10k,10-15,15-20,20-25  -> <25k
high_codes <- sprintf("%03d", 14:17)  # 100-125,125-150,150-200,>=200k -> >=100k

get_tbl <- function(tbl) {
  get_acs(geography = "county", table = tbl, year = ACS_YEAR,
          survey = "acs5", output = "wide", cache_table = TRUE) %>%
    select(GEOID, NAME, ends_with("E"))
}

message("Pulling ACS ", ACS_YEAR, " 5-year: B19001, B19001H, B01003 (county) ...")
all_inc <- get_tbl("B19001")
wh_inc  <- get_tbl("B19001H")
pop     <- get_acs(geography = "county", variables = "B01003_001",
                   year = ACS_YEAR, survey = "acs5", output = "wide") %>%
  transmute(GEOID, pop_total = B01003_001E)

sum_codes <- function(df, tbl, codes) rowSums(df[, paste0(tbl, "_", codes, "E"), drop = FALSE], na.rm = TRUE)

res <- all_inc %>%
  transmute(fips = GEOID, county_name = NAME,
            hh_total = B19001_001E,
            low_all  = sum_codes(all_inc, "B19001", low_codes)) %>%
  left_join(wh_inc %>% transmute(fips = GEOID,
              A_white_highinc = sum_codes(wh_inc, "B19001H", high_codes),
              low_wh          = sum_codes(wh_inc, "B19001H", low_codes)), by = "fips") %>%
  left_join(pop, by = c("fips" = "GEOID")) %>%
  mutate(P_color_lowinc = pmax(low_all - low_wh, 0),
         ice_raceinc    = round((A_white_highinc - P_color_lowinc) / hh_total, 5)) %>%
  filter(hh_total > 0) %>%
  select(fips, county_name, pop_total, hh_total, A_white_highinc, P_color_lowinc, ice_raceinc) %>%
  arrange(fips)

setwd("~/Library/CloudStorage/GoogleDrive-kgahan.srf.aiims@gmail.com/My Drive/suppression-bias")
tidycensus::census_api_key("a6c65f8a5107f9105f56ca8f674de3866d64441e", install = TRUE, overwrite = TRUE)
readRenviron("~/.Renviron")
source("R/pull_acs_ice.R")

dir.create(dirname(out_path), showWarnings = FALSE, recursive = TRUE)
write_csv(res, out_path)
message("Wrote ", nrow(res), " counties -> ", normalizePath(out_path, mustWork = FALSE))
message("ICE range: ", min(res$ice_raceinc), " to ", max(res$ice_raceinc))
