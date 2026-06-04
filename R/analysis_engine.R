# analysis_engine.R — disparity estimands + four suppression-handling methods.
# Canonical published implementation (mirrors python/analysis_engine.py, the executed reference).
#
# A county frame is a data.frame with: fips, pop_total (weight), dep_q (1..5; 5 = MOST deprived),
# rate (age-adjusted /100k; NA if suppressed/absent), state_fips (for model-based).
# RR = rate(Q5)/rate(Q1); RD = rate(Q5)-rate(Q1); gradient = OLS slope of quintile mean on rank.
# Quintile rate = population-weighted mean of county rates. For ICE (lowest = most deprived),
# the pipeline flips dep_q before calling so that 5 = most deprived throughout.

MOST <- 5L; LEAST <- 1L

wmean <- function(vals, w) {
  ok <- !is.na(vals) & w > 0
  if (!any(ok)) return(NA_real_)
  sum(vals[ok] * w[ok]) / sum(w[ok])
}

quintile_rates <- function(df) {
  sapply(split(df, df$dep_q), function(g) wmean(g$rate, g$pop_total))
}

gradient <- function(qr) {
  x <- as.numeric(names(qr)); y <- as.numeric(qr)
  ok <- !is.na(y); if (sum(ok) < 2) return(NA_real_)
  unname(coef(lm(y[ok] ~ x[ok]))[2])
}

disparity <- function(df) {
  qr <- quintile_rates(df)
  most <- qr[[as.character(MOST)]]; least <- qr[[as.character(LEAST)]]
  list(RR = if (!is.na(least) && least != 0) most/least else NA_real_,
       RD = most - least, gradient = gradient(qr),
       rate_most = most, rate_least = least)
}

complete_case <- function(df) disparity(df[!is.na(df$rate), , drop = FALSE])

available_case <- function(df) {
  res <- complete_case(df)
  acct <- do.call(rbind, lapply(split(df, df$dep_q), function(g) {
    kept <- g[!is.na(g$rate), , drop = FALSE]
    data.frame(dep_q = g$dep_q[1], counties_total = nrow(g), counties_kept = nrow(kept),
               pop_total = sum(g$pop_total), pop_kept = sum(kept$pop_total),
               pop_lost_frac = 1 - sum(kept$pop_total)/max(sum(g$pop_total), 1))
  }))
  res$retention <- acct; res
}

bounding <- function(df, threshold = 16, years = 5) {
  fill <- function(extreme) {
    d <- df; sup <- is.na(d$rate); py <- d$pop_total * years
    if (extreme == "low") d$rate[sup] <- 0 else d$rate[sup] <- (threshold - 1) / py[sup] * 1e5
    disparity(d)
  }
  lo <- fill("low"); hi <- fill("high")
  out <- list(); for (k in c("RR","RD","gradient")) out[[k]] <- sort(c(lo[[k]], hi[[k]]))
  out$low <- lo; out$high <- hi; out
}

# Empirical-Bayes state-prior shrinkage stand-in for a hierarchical Poisson small-area model.
model_based <- function(df, years = 5) {
  d <- df; obs <- d[!is.na(d$rate), , drop = FALSE]
  natl <- wmean(obs$rate, obs$pop_total)
  sm <- sapply(split(obs, obs$state_fips), function(g) wmean(g$rate, g$pop_total))
  imp <- is.na(d$rate)
  key <- as.character(d$state_fips[imp])
  vals <- sm[key]; vals[is.na(vals)] <- natl
  d$rate[imp] <- vals
  disparity(d)
}

bootstrap_ci <- function(df, fn, B = 2000, seed = 1, ...) {
  set.seed(seed); keys <- c("RR","RD","gradient")
  acc <- matrix(NA_real_, B, length(keys), dimnames = list(NULL, keys))
  qs <- split(seq_len(nrow(df)), df$dep_q)
  for (b in seq_len(B)) {
    idx <- unlist(lapply(qs, function(ix) sample(ix, length(ix), replace = TRUE)))
    r <- fn(df[idx, , drop = FALSE], ...)
    for (k in keys) { v <- r[[k]]; acc[b, k] <- if (length(v) == 1) v else NA_real_ }
  }
  apply(acc, 2, function(col) quantile(col, c(0.025, 0.975), na.rm = TRUE))
}
