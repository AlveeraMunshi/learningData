############################################################
# Retail Sales: Used Car Dealers (MRTSSM44112USN)
# Monthly, NOT seasonally adjusted
# Jan 1992 -> most recent observation
############################################################

# ---- packages ----
# install.packages(c("fredr","forecast","ggplot2","seasonal"))
library(fredr)
library(forecast)
library(ggplot2)
library(seasonal)

# ---- FRED key + download ----
fredr_set_key("25e01a7269f9d0fdd83a00ee95e51aee")

data <- fredr(
  series_id = "MRTSSM44112USN",
  observation_start = as.Date("1992-01-01")
)

# Convert to monthly ts
y <- ts(data$value, start = c(1992, 1), frequency = 12)

# ==========================================================
# 1) Time plot + ACF
# ==========================================================
plot(y, main="Time plot: Used Car Dealers Retail Sales (1992:1 - latest)",
     ylab="Millions of Dollars", xlab="Year", lwd=1.5)

acf(y, main="ACF: Used Car Dealers Retail Sales (raw)")

# (Optional but useful) ACF on log scale
acf(log(y), main="ACF: log(Used Car Dealers Retail Sales)")

# ==========================================================
# 2) Classical decomposition (multiplicative via logs)
#    multiplicative on original scale <=> additive on log scale
# ==========================================================
ly <- log(y)

dc_log <- decompose(ly, type="additive")
plot(dc_log)

trend_log    <- dc_log$trend
seasonal_log <- dc_log$seasonal
rem_log      <- dc_log$random

# Seasonal indices (multiplicative factors) and fitted values on original scale
seasonal_indices_classical <- exp(dc_log$figure)           # length 12 (Jan..Dec)
seasonal_indices_classical

yhat <- exp(trend_log + seasonal_log)                      # fitted (trend * seasonal) on original scale

plot.ts(y, main="Used Car Dealers Retail Sales: actual vs fitted (classical)",
        ylab="Millions of Dollars", lwd=1.5)
points(yhat, col="red", lwd=1.5, pch=1)
legend("topleft", c("Fitted (classical)"),
       col=c("red"), pch=c(1), bty="n")

# Classical seasonally adjusted series (on original scale)
# log(SA) = log(y) - seasonal_log  => SA = exp(log(y) - seasonal_log)
y_sadj_classical <- exp(ly - seasonal_log)

par(mfrow=c(2,1))
plot.ts(y, main="Raw series (Not seasonally adjusted)", ylab="Millions of Dollars", lwd=1.5)
plot.ts(y_sadj_classical, main="Seasonally adjusted (Classical, via log-additive)",
        ylab="Millions of Dollars (SA)", lwd=1.5)
par(mfrow=c(1,1))

# ==========================================================
# 3) Interpret components helpers (trend direction, hi/low months, big shock)
# ==========================================================
trend_vals <- na.omit(trend_log)
trend_direction <- ifelse(tail(trend_vals,1) > head(trend_vals,1), "Increasing", "Decreasing")
trend_direction

names(seasonal_indices_classical) <- month.abb
seasonal_indices_classical
highest_month <- names(which.max(seasonal_indices_classical))
lowest_month  <- names(which.min(seasonal_indices_classical))
highest_month
lowest_month

rem_vals <- na.omit(rem_log)
largest_shock_time <- time(rem_vals)[which.max(abs(rem_vals))]
largest_shock_time

# ==========================================================
# 4) X-11 decomposition (seasonal package)
# ==========================================================
fit <- seas(y, x11="")
plot(fit)

# Components
sa <- final(fit)         # seasonally adjusted series (X-11 "final")
s  <- seasonal(fit)      # seasonal component (multiplicative factors)
tc <- trendcycle(fit)    # trend-cycle
r  <- remainder(fit)     # irregular

plot(sa, main="Seasonally adjusted (X-11 final)", ylab="Millions of Dollars")
plot(tc, main="Trend-cycle (X-11)", ylab="Trend-cycle")
plot(s,  main="Seasonal factors (X-11)", ylab="Seasonal factor")
plot(r,  main="Remainder/Irregular (X-11)", ylab="Irregular")

# ==========================================================
# 5) Compare seasonal estimates: Classical vs X-11
# ==========================================================
# Classical monthly seasonal factors are fixed (Jan..Dec) from dc_log$figure
s_classical_12 <- exp(dc_log$figure)
names(s_classical_12) <- month.abb

# X-11 seasonal factors vary over time; compare via average factor by month
s_x11_avg <- tapply(as.numeric(s), cycle(s), mean, na.rm=TRUE)
names(s_x11_avg) <- month.abb

seasonal_compare <- data.frame(
  Month = month.abb,
  Classical = as.numeric(s_classical_12),
  X11_Avg   = as.numeric(s_x11_avg)
)
seasonal_compare

matplot(seasonal_compare$Classical, type="l", lty=1, xaxt="n",
        xlab="Month", ylab="Seasonal factor", main="Seasonal factors: Classical vs X-11 (avg)")
axis(1, at=1:12, labels=month.abb)
lines(seasonal_compare$X11_Avg, lty=2)
legend("topleft", legend=c("Classical (fixed)", "X-11 (avg; time-varying)"),
       lty=c(1,2), bty="n")

# ==========================================================
# 6) Forecasting with ETS (12-month forecast)
#    A) Forecast raw (unadjusted) series
#    B) Forecast seasonally adjusted series (X-11), then re-seasonalize (optional)
# ==========================================================

# A) ETS on raw series
fit_raw <- ets(y)
fc_raw  <- forecast(fit_raw, h = 12)

autoplot(fc_raw) + ggtitle("ETS Forecast (12 months): Raw (Unadjusted) series")

# B) ETS on seasonally adjusted series (X-11 final)
fit_sa <- ets(sa)
fc_sa  <- forecast(fit_sa, h = 12)

autoplot(fc_sa) + ggtitle("ETS Forecast (12 months): Seasonally Adjusted series (X-11)")

# Re-seasonalize SA forecast back to original scale (multiplicative): y = sa * seasonal_factor
# Use last 12 observed seasonal factors as next-year template
s_last12 <- tail(s, 12)
s_future <- rep(s_last12, length.out = 12)

fc_y <- fc_sa$mean * s_future

# Build a ts aligned to start right after the last observation of y
end_y <- end(y)  # c(year, month)
start_fc <- c(end_y[1] + (end_y[2] == 12), ifelse(end_y[2] == 12, 1, end_y[2] + 1))
fc_y <- ts(fc_y, start = start_fc, frequency = 12)

autoplot(y) +
  autolayer(fc_raw$mean, series="Forecast (raw ETS)") +
  autolayer(fc_y, series="Forecast (SA ETS × seasonal)") +
  ggtitle("Compare forecasts on original scale (12 months)") +
  ylab("Millions of Dollars")
