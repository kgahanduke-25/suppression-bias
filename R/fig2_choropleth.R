#!/usr/bin/env Rscript
# fig2_choropleth.R — county choropleth of suppressed cells (Fig 2).
# Run LOCALLY (needs county geometry via tigris; the Cowork sandbox cannot fetch it).
# Joins TIGER county geometry to results/suppression_map_data.csv (produced by the pipeline)
# and maps suppressed counties for cervix (rarest) and breast (common) side by side.
#
# Setup: install.packages(c("tigris","sf","dplyr","ggplot2","readr","patchwork"))
# Then:  Rscript R/fig2_choropleth.R   (or source() with wd at project root)

suppressPackageStartupMessages({
  library(tigris); library(sf); library(dplyr); library(ggplot2); library(readr); library(patchwork)
})
options(tigris_use_cache = TRUE)

find_csv <- function() {
  for (p in c("results/suppression_map_data.csv", "../results/suppression_map_data.csv"))
    if (file.exists(p)) return(p)
  stop("results/suppression_map_data.csv not found — run the pipeline first.")
}
sup <- read_csv(find_csv(), col_types = cols(fips = col_character())) |>
  mutate(fips = sprintf("%05s", fips))

# County + state geometry, shifted so AK/HI sit under CONUS
cty <- counties(cb = TRUE, resolution = "20m", year = 2022, progress_bar = FALSE) |>
  shift_geometry() |>
  filter(!STATEFP %in% c("72","78","60","66","69")) |>
  mutate(fips = GEOID)
st  <- states(cb = TRUE, resolution = "20m", year = 2022, progress_bar = FALSE) |>
  shift_geometry() |> filter(!STATEFP %in% c("72","78","60","66","69"))

dat <- cty |> left_join(sup, by = "fips")

panel <- function(col, title) {
  ggplot(dat) +
    geom_sf(aes(fill = factor(ifelse(is.na(.data[[col]]), 1L, .data[[col]]))),
            color = NA) +
    geom_sf(data = st, fill = NA, color = "white", linewidth = 0.2) +
    scale_fill_manual(values = c("0" = "#d9d9d9", "1" = "#08519c"),
                      labels = c("Rate reported", "Suppressed"), name = NULL,
                      na.value = "#08519c") +
    labs(title = title) +
    theme_void(base_size = 12) +
    theme(legend.position = "bottom", plot.title = element_text(face = "bold", hjust = 0.5))
}

p <- panel("breast_suppressed", "Breast (common)") + panel("cervix_suppressed", "Cervix (rare)") +
  plot_annotation(title = "Counties suppressed under complete-case analysis",
                  subtitle = "NCI State Cancer Profiles, release 2026-06-01; incidence, all races/ages",
                  theme = theme(plot.title = element_text(face = "bold")))

dir.create("figures", showWarnings = FALSE)
out <- if (dir.exists("figures")) "figures/fig2_choropleth.png" else "../figures/fig2_choropleth.png"
ggsave(out, p, width = 12, height = 5.2, dpi = 200, bg = "white")
message("Wrote ", normalizePath(out, mustWork = FALSE))
