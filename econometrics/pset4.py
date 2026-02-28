# ============================
# Econ 322 - Problem Set 4
# Q1 (grades_and_temps.csv) + Q2 (DDCG_dataset.csv)
# Python / statsmodels, robust SEs (HC1)
# ============================

import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy import stats
import statsmodels.api as sm
import statsmodels.formula.api as smf

# ---------- File path constants ----------
# Input files
GRADES_TEMPS_CSV = "grades_and_temps.csv"
DDCG_DATASET_CSV = "DDCG_dataset.csv"

# Output directory
OUTDIR = "ps4_outputs_py"

# Output files - Question 1
Q1_PART1_SCATTER_PNG = "Q1_part1_scatter.png"
Q1_PART2_LINEAR_CSV = "Q1_part2_linear_coef_robust.csv"
Q1_PART2_QUADRATIC_CSV = "Q1_part2_quadratic_coef_robust.csv"
Q1_PART3_DIFF_CSV = "Q1_part3_diff_10k_vs_5k.csv"
Q1_PART4_SCATTER_PNG = "Q1_part4_scatter_logx.png"
Q1_PART5_LINLOG_CSV = "Q1_part5_linearlog_coef_robust.csv"
Q1_PART5_LOGLOG_CSV = "Q1_part5_loglog_coef_robust.csv"
Q1_PART6_RSQ_CSV = "Q1_part6_rsq_compare.csv"

# Output files - Question 2
Q2_PART1_MEANS_CSV = "Q2_part1_means_ttest.csv"
Q2_PART1_REG_CSV = "Q2_part1_reg_2005_coef_robust.csv"
Q2_PART2_BASELINE_CSV = "Q2_part2_baseline_coef_robust.csv"
Q2_PART4_EDU_CSV = "Q2_part4_edu_controls_coef_robust.csv"
Q2_PART5_ECON_CSV = "Q2_part5_econ_controls_coef_robust.csv"
Q2_PART6_JOINT_CSV = "Q2_part6_joint_test_ginv_tradewb.csv"

# ---------- helpers ----------
os.makedirs(OUTDIR, exist_ok=True)

def r3(x):
    """Round numbers to 3 decimals; leave others as-is."""
    if isinstance(x, (int, float, np.floating)):
        return np.round(x, 3)
    return x

def tidy_robust(result, model_name=None):
    """
    Return tidy table from a statsmodels RegressionResults with robust cov already applied.
    """
    coefs = result.params
    se = result.bse
    tvals = result.tvalues
    pvals = result.pvalues

    # Ensure we're working with pandas Series
    if not isinstance(coefs, pd.Series):
        coefs = pd.Series(coefs)
    if not isinstance(se, pd.Series):
        se = pd.Series(se, index=coefs.index)
    if not isinstance(tvals, pd.Series):
        tvals = pd.Series(tvals, index=coefs.index)
    if not isinstance(pvals, pd.Series):
        pvals = pd.Series(pvals, index=coefs.index)

    df = pd.DataFrame({
        "term": coefs.index,
        "estimate": coefs.values,
        "robust_se": se.values,
        "t": tvals.values,
        "p": pvals.values
    })
    if model_name:
        df.insert(0, "model", model_name)
    return df.applymap(r3)

def save_print(df, fn):
    path = os.path.join(OUTDIR, fn)
    df.to_csv(path, index=False)
    print(f"Saved -> {path}")

# ======================================================
# ===================== QUESTION 1 =====================
# Uses: cname, year, read_score, math_score, sci_score, avg_temp, gdppc, income_group
# ======================================================
q1 = pd.read_csv(GRADES_TEMPS_CSV)

# sanity checks
assert {"math_score", "gdppc"}.issubset(q1.columns), "Expected columns math_score and gdppc."

# 0) gdppc in thousands
q1["gdppc1k"] = q1["gdppc"] / 1000.0

# ---------- Part 1: scatter ----------
plt.figure()
plt.scatter(q1["gdppc1k"], q1["math_score"])
plt.xlabel("GDP per capita (thousands USD)")
plt.ylabel("Math score")
plt.title("Math score vs GDP per capita (thousands)")
plt.tight_layout()
plt.savefig(os.path.join(OUTDIR, Q1_PART1_SCATTER_PNG), dpi=300)
plt.close()

# ---------- Part 2: linear & quadratic ----------
# linear: math_score ~ gdppc1k
m_lin = smf.ols("math_score ~ gdppc1k", data=q1).fit()
m_lin_HC1 = m_lin.get_robustcov_results(cov_type="HC1")

# quadratic: math_score ~ gdppc1k + gdppc1k^2
q1["gdppc1k_sq"] = q1["gdppc1k"] ** 2
m_quad = smf.ols("math_score ~ gdppc1k + gdppc1k_sq", data=q1).fit()
m_quad_HC1 = m_quad.get_robustcov_results(cov_type="HC1")

tab_lin = tidy_robust(m_lin_HC1, "Q1 linear")
tab_quad = tidy_robust(m_quad_HC1, "Q1 quadratic")
save_print(tab_lin, Q1_PART2_LINEAR_CSV)
save_print(tab_quad, Q1_PART2_QUADRATIC_CSV)

# ---------- Part 3: expected difference (10k vs 5k), using Eq(2) ----------
b0, b1, b2 = m_quad.params["Intercept"], m_quad.params["gdppc1k"], m_quad.params["gdppc1k_sq"]
pred_5  = b0 + b1*5 + b2*(5**2)
pred_10 = b0 + b1*10 + b2*(10**2)
diff_10_5 = pred_10 - pred_5
print("Q1 Part 3: Predicted difference (10k - 5k) =", r3(diff_10_5))
pd.DataFrame({"diff_10k_minus_5k": [r3(diff_10_5)]}).to_csv(
    os.path.join(OUTDIR, Q1_PART3_DIFF_CSV), index=False
)

# ---------- Part 4: scatter with log x ----------
q1_pos = q1[q1["gdppc1k"] > 0].copy()
q1_pos["log_gdppc1k"] = np.log(q1_pos["gdppc1k"])

plt.figure()
plt.scatter(q1_pos["log_gdppc1k"], q1_pos["math_score"])
plt.xlabel("log(GDP per capita in thousands)")
plt.ylabel("Math score")
plt.title("Math score vs log(GDP per capita in thousands)")
plt.tight_layout()
plt.savefig(os.path.join(OUTDIR, Q1_PART4_SCATTER_PNG), dpi=300)
plt.close()

# ---------- Part 5: linear-log & log-log ----------
m_linlog = smf.ols("math_score ~ log_gdppc1k", data=q1_pos).fit()
m_linlog_HC1 = m_linlog.get_robustcov_results(cov_type="HC1")

q1_pos2 = q1_pos[q1_pos["math_score"] > 0].copy()
q1_pos2["log_math"] = np.log(q1_pos2["math_score"])
m_loglog = smf.ols("log_math ~ log_gdppc1k", data=q1_pos2).fit()
m_loglog_HC1 = m_loglog.get_robustcov_results(cov_type="HC1")

tab_linlog = tidy_robust(m_linlog_HC1, "Q1 linear-log")
tab_loglog = tidy_robust(m_loglog_HC1, "Q1 log-log")
save_print(tab_linlog, Q1_PART5_LINLOG_CSV)
save_print(tab_loglog, Q1_PART5_LOGLOG_CSV)

# ---------- Part 6: R^2 comparison ----------
rsq_df = pd.DataFrame({
    "model": ["Linear", "Quadratic", "Linear-Log", "Log-Log*"],
    "r_squared": [
        m_lin.rsquared,
        m_quad.rsquared,
        m_linlog.rsquared,
        m_loglog.rsquared
    ],
    "note": ["", "", "", "*DV transformed; R^2 not directly comparable"]
})
rsq_df["r_squared"] = rsq_df["r_squared"].map(r3)
save_print(rsq_df, Q1_PART6_RSQ_CSV)

# ======================================================
# ===================== QUESTION 2 =====================
# DDCG dataset
# ======================================================
dd = pd.read_csv(DDCG_DATASET_CSV)

# ---------- Part 1: 2005 means + t-test + 2005 regression ----------
dd05 = dd[dd["year"] == 2005].copy()
assert {"gdp_capita", "dem"}.issubset(dd05.columns), "Q2 needs gdp_capita, dem."

mean_dem = dd05.loc[dd05["dem"] == 1, "gdp_capita"].mean()
mean_nondem = dd05.loc[dd05["dem"] == 0, "gdp_capita"].mean()
diff_means = mean_dem - mean_nondem

# unequal-variance t-test
t_stat, p_val = stats.ttest_ind(
    dd05.loc[dd05["dem"] == 1, "gdp_capita"].dropna(),
    dd05.loc[dd05["dem"] == 0, "gdp_capita"].dropna(),
    equal_var=False
)

out1 = pd.DataFrame({
    "mean_dem_2005": [r3(mean_dem)],
    "mean_nondem_2005": [r3(mean_nondem)],
    "diff_dem_minus_nondem_2005": [r3(diff_means)],
    "t_stat": [r3(t_stat)],
    "p_value": [r3(p_val)]
})
save_print(out1, Q2_PART1_MEANS_CSV)

# Regression (2005): gdp_capita ~ dem  (robust HC1)
reg2005 = smf.ols("gdp_capita ~ dem", data=dd05).fit()
reg2005_HC1 = reg2005.get_robustcov_results(cov_type="HC1")
save_print(tidy_robust(reg2005_HC1, "Q2 2005 reg"), Q2_PART1_REG_CSV)

# ---------- Part 2: log(gdp_capita) ~ dem (all years) ----------
dd2 = dd[dd["gdp_capita"] > 0].copy()
dd2["log_gdp_capita"] = np.log(dd2["gdp_capita"])
reg2 = smf.ols("log_gdp_capita ~ dem", data=dd2).fit()
reg2_HC1 = reg2.get_robustcov_results(cov_type="HC1")
save_print(tidy_robust(reg2_HC1, "Q2 baseline"), Q2_PART2_BASELINE_CSV)

# ---------- Part 4: add lp_bl, lh_bl ----------
for col in ["lp_bl", "lh_bl"]:
    assert col in dd2.columns, f"Missing column: {col}"
reg3 = smf.ols("log_gdp_capita ~ dem + lp_bl + lh_bl", data=dd2).fit()
reg3_HC1 = reg3.get_robustcov_results(cov_type="HC1")
save_print(tidy_robust(reg3_HC1, "Q2 + edu controls"), Q2_PART4_EDU_CSV)

# ---------- Part 5: add ginv, tradewb ----------
for col in ["ginv", "tradewb"]:
    assert col in dd2.columns, f"Missing column: {col}"
reg4 = smf.ols("log_gdp_capita ~ dem + lp_bl + lh_bl + ginv + tradewb", data=dd2).fit()
reg4_HC1 = reg4.get_robustcov_results(cov_type="HC1")
save_print(tidy_robust(reg4_HC1, "Q2 + econ controls"), Q2_PART5_ECON_CSV)

# ---------- Part 6: joint test that ginv = tradewb = 0 ----------
# Use robust covariance via the robust results object
wald = reg4_HC1.wald_test("ginv = 0, tradewb = 0")
wald_df = pd.DataFrame({
    "statistic": [r3(wald.statistic.item())],
    "df":        [int(wald.df_denom)],     # denominator df
    "p_value":   [r3(wald.pvalue.item())]
})
save_print(wald_df, Q2_PART6_JOINT_CSV)

# ---------- Console summary (quick glance) ----------
print("\n=== QUICK GLANCE (rounded) ===")
print("Q1 R^2:", rsq_df.to_string(index=False))
print("\nQ1 Part 3 (10k-5k):", r3(diff_10_5))
print("\nQ2 Part 2 (beta on dem):",
      r3(reg2_HC1.params.get("dem", np.nan)),
      "SE:", r3(reg2_HC1.bse.get("dem", np.nan)))
print("Q2 Part 4 (beta on dem):",
      r3(reg3_HC1.params.get("dem", np.nan)),
      "SE:", r3(reg3_HC1.bse.get("dem", np.nan)))
print("Q2 Part 5 (beta on dem):",
      r3(reg4_HC1.params.get("dem", np.nan)),
      "SE:", r3(reg4_HC1.bse.get("dem", np.nan)))
print("Q2 Part 6 joint test (ginv, tradewb):", wald_df.to_dict(orient="records")[0])