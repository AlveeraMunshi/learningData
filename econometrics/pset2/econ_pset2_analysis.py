# Econometrics — Problem Set 2

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy import stats
from pathlib import Path

# ---------- File paths ----------
SPENDING_CSV = Path("customer_spending.csv")
ACS_CSV      = Path("acs_nj.csv")
ANS_TXT      = Path("econ_pset2_answers.txt")
FIG_Q1_S     = Path("fig_q1_hist_S.png")
FIG_Q1_N2    = Path("fig_q1_n2_means.png")
FIG_Q1_N500  = Path("fig_q1_n500_means.png")
FIG_Q2_WAGE  = Path("fig_q2_hourly_wage_hist.png")

def r3(x):
    return None if x is None else float(np.round(x, 3))

def r2(x):
    return None if x is None else float(np.round(x, 2))

def main():
    # ---------- Load data ----------
    spending = pd.read_csv(SPENDING_CSV)
    acs = pd.read_csv(ACS_CSV)

    spending.columns = [c.strip().lower().replace(" ", "_") for c in spending.columns]
    acs.columns = [c.strip().lower().replace(" ", "_") for c in acs.columns]

    # === Question 1 ===
    # Identify S
    S = spending.iloc[:, 0] if 's' not in spending.columns else spending['s']
    pop_mean_S = float(S.mean())
    pop_var_S = float(S.var(ddof=0))  # population variance

    # Plot histogram of S
    plt.figure()
    plt.hist(S.dropna(), bins=30)
    plt.title("Histogram of S (Population spending)")
    plt.xlabel("S (annual $)")
    plt.ylabel("Count")
    plt.tight_layout()
    plt.savefig(FIG_Q1_S)
    plt.close()

    # Sample means for first 10/25/100
    s10 = float(S.iloc[:10].mean())
    s25 = float(S.iloc[:25].mean())
    s100 = float(S.iloc[:100].mean())
    closest_which = min(
        [("n=10", abs(s10 - pop_mean_S)),
         ("n=25", abs(s25 - pop_mean_S)),
         ("n=100", abs(s100 - pop_mean_S))],
        key=lambda x: x[1]
    )[0]

    # CLT simulations
    rng = np.random.default_rng(123)
    s_values = S.to_numpy()
    sample_means_n2 = [rng.choice(s_values, size=2, replace=True).mean() for _ in range(500)]
    avg_sample_mean_n2 = float(np.mean(sample_means_n2))

    plt.figure()
    plt.hist(sample_means_n2, bins=30)
    plt.title("Histogram of Sample Means (n=2, 500 reps)")
    plt.xlabel("Sample mean of S")
    plt.ylabel("Count")
    plt.tight_layout()
    plt.savefig(FIG_Q1_N2)
    plt.close()

    sample_means_n500 = [rng.choice(s_values, size=500, replace=True).mean() for _ in range(500)]
    avg_sample_mean_n500 = float(np.mean(sample_means_n500))

    plt.figure()
    plt.hist(sample_means_n500, bins=30)
    plt.title("Histogram of Sample Means (n=500, 500 reps)")
    plt.xlabel("Sample mean of S")
    plt.ylabel("Count")
    plt.tight_layout()
    plt.savefig(FIG_Q1_N500)
    plt.close()

    # === Question 2 ===
    expected_cols = ['pid','female','age','us_citizen','bachelor','wage','hours_worked','income','renter','rent']
    # Attempt light remap for minor naming variants
    if 'us_citizen' not in acs.columns and 'us_citizen?' in acs.columns:
        acs['us_citizen'] = acs['us_citizen?']

    # % bachelor and income means (positive income only for the means)
    has_positive_income = (acs['income'] > 0) & (~acs['income'].isna())
    pct_bachelor = float(acs['bachelor'].mean() * 100)
    mean_income_bach = float(acs.loc[has_positive_income & (acs['bachelor']==1), 'income'].mean())
    mean_income_nobach = float(acs.loc[has_positive_income & (acs['bachelor']==0), 'income'].mean())

    # For the rest: restrict to positive, non-missing income
    df = acs.loc[has_positive_income].copy()

    # Hourly wage
    df['wage_hourly'] = df['wage'] / (df['hours_worked'] * 52.0)
    wh_valid = df['wage_hourly'].replace([np.inf, -np.inf], np.nan).dropna()
    mean_wage_hourly = float(wh_valid.mean())
    var_wage_hourly = float(wh_valid.var(ddof=1))

    plt.figure()
    plt.hist(wh_valid[wh_valid <= 300], bins=30)
    plt.title("Histogram of Hourly Wage (≤ $300/hr)")
    plt.xlabel("Hourly wage ($/hr)")
    plt.ylabel("Count")
    plt.tight_layout()
    plt.savefig(FIG_Q2_WAGE)
    plt.close()

    # H0: mu = 46, two-sided
    mu0 = 46.0
    n = wh_valid.shape[0]
    xbar = mean_wage_hourly
    s = float(wh_valid.std(ddof=1))
    t_stat_two_sided = (xbar - mu0) / (s / np.sqrt(n))
    p_two_sided = 2 * (1 - stats.t.cdf(abs(t_stat_two_sided), df=n-1))
    reject_1_two  = p_two_sided < 0.01
    reject_5_two  = p_two_sided < 0.05
    reject_10_two = p_two_sided < 0.10

    # One-sided H1: mu > 46
    t_stat_one_sided = t_stat_two_sided
    p_one_sided_gt = 1 - stats.t.cdf(t_stat_one_sided, df=n-1)
    reject_5_one  = p_one_sided_gt < 0.05
    reject_10_one = p_one_sided_gt < 0.10

    # Subsample pid < 5000, one-sided test
    sub = df.loc[df['pid'] < 5000, 'wage_hourly'].replace([np.inf, -np.inf], np.nan).dropna()
    n_sub = sub.shape[0]
    xbar_sub = float(sub.mean())
    s_sub = float(sub.std(ddof=1))
    t_stat_sub = (xbar_sub - mu0) / (s_sub / np.sqrt(n_sub))
    p_one_sided_gt_sub = 1 - stats.t.cdf(t_stat_sub, df=n_sub-1)
    reject_5_one_sub  = p_one_sided_gt_sub < 0.05
    reject_10_one_sub = p_one_sided_gt_sub < 0.10

    # Difference in means: bachelor vs no bachelor
    g1 = df.loc[df['bachelor']==1, 'wage_hourly'].replace([np.inf, -np.inf], np.nan).dropna()
    g0 = df.loc[df['bachelor']==0, 'wage_hourly'].replace([np.inf, -np.inf], np.nan).dropna()
    diff_means = float(g1.mean() - g0.mean())
    t_welch, p_welch = stats.ttest_ind(g1, g0, equal_var=False, nan_policy='omit')
    signif_5 = p_welch < 0.05

    # Renters only
    renters = df.loc[df['renter']==1].copy()
    renters['rent_to_income_ratio'] = (12.0 * renters['rent'] / renters['income']) * 100.0
    corr_rent_bach = float(renters[['rent','bachelor']].dropna().corr().iloc[0,1])
    corr_ratio_bach = float(renters[['rent_to_income_ratio','bachelor']].dropna().corr().iloc[0,1])

    rb = renters.loc[renters['bachelor']==1, 'rent_to_income_ratio'].replace([np.inf, -np.inf], np.nan).dropna()
    n_rb = rb.shape[0]
    mean_rb = float(rb.mean())
    se_rb = float(rb.std(ddof=1) / np.sqrt(n_rb))
    t_crit_95 = stats.t.ppf(0.975, df=n_rb-1)
    ci_low_rb = mean_rb - t_crit_95 * se_rb
    ci_high_rb = mean_rb + t_crit_95 * se_rb
    reject_30_two_sided_rb = not (30.0 >= ci_low_rb and 30.0 <= ci_high_rb)

    rnb = renters.loc[renters['bachelor']==0, 'rent_to_income_ratio'].replace([np.inf, -np.inf], np.nan).dropna()
    n_rnb = rnb.shape[0]
    mean_rnb = float(rnb.mean())
    t_stat_rnb = (mean_rnb - 30.0) / (rnb.std(ddof=1) / np.sqrt(n_rnb))
    p_one_sided_rnb = 1 - stats.t.cdf(t_stat_rnb, df=n_rnb-1)
    reject_rnb_30 = p_one_sided_rnb < 0.05

    # Save Answers
    answers = []
    answers.append("PROBLEM SET 2 — Questions with Answers\n")

    # Q1
    answers.append("Question 1.1) ")
    answers.append(f"mean = {r3(pop_mean_S)}, variance = {r3(pop_var_S)}")

    answers.append("Question 1.2) ")
    answers.append(f"mean_10 = {r3(s10)}, mean_25 = {r3(s25)}, mean_100 = {r3(s100)}; closest: {closest_which}")

    answers.append("Question 1.3) ")
    answers.append(f"avg(sample mean, n=2) = {r3(avg_sample_mean_n2)}; avg(sample mean, n=500) = {r3(avg_sample_mean_n500)}. The n=2 distribution is wider/less normal; n=500 is tighter and approximately normal (CLT).")

    # Q2
    answers.append("Question 2.1) ")
    answers.append(f"% bachelor = {r3(pct_bachelor)}%. Mean income (bachelor) = {r3(mean_income_bach)}; mean income (no bachelor) = {r3(mean_income_nobach)}.")

    answers.append("Question 2.2) ")
    answers.append(f"mean hourly wage = {r3(mean_wage_hourly)}; variance = {r3(var_wage_hourly)}.")

    answers.append("Question 2.3) ")
    answers.append(f"t = {r3(t_stat_two_sided)}, p = {r3(p_two_sided)}. Reject at 1%? {bool(reject_1_two)}; at 5%? {bool(reject_5_two)}; at 10%? {bool(reject_10_two)}.")

    answers.append("Question 2.4) ")
    answers.append(f"t = {r3(t_stat_one_sided)}, p = {r3(p_one_sided_gt)}. Reject at 5%? {bool(reject_5_one)}; at 10%? {bool(reject_10_one)}.")

    answers.append("Question 2.5) ")
    answers.append(f"n = {int(n_sub)}, mean = {r3(xbar_sub)}, t = {r3(t_stat_sub)}, p = {r3(p_one_sided_gt_sub)}. Reject at 5%? {bool(reject_5_one_sub)}; at 10%? {bool(reject_10_one_sub)}.")

    answers.append("Question 2.6) ")
    answers.append(f"difference = {r2(diff_means)}; t = {r3(t_welch)}, p = {r3(p_welch)}; significant at 5%? {bool(signif_5)}.")

    answers.append("Question 2.7) ")
    answers.append(f"(a) corr(rent, bachelor) = {r3(corr_rent_bach)}; corr(rent_to_income_ratio, bachelor) = {r3(corr_ratio_bach)}. "
                   f"(b) mean = {r3(mean_rb)}, 95% CI = [{r3(ci_low_rb)}, {r3(ci_high_rb)}], 30% outside CI? {bool(reject_30_two_sided_rb)}. "
                   f"(c) mean(non-bachelor) = {r3(mean_rnb)}, t = {r3(t_stat_rnb)}, p = {r3(p_one_sided_rnb)}; reject at 5%? {bool(reject_rnb_30)}.")

    # Save answers
    ANS_TXT.write_text("\n".join(answers), encoding="utf-8")

    # Print compact summary to stdout
    print("=== SUMMARY ===")
    print(f"Q1.1 mean={r3(pop_mean_S)} var={r3(pop_var_S)}")
    print(f"Q1.2 mean_10={r3(s10)} mean_25={r3(s25)} mean_100={r3(s100)} closest={closest_which}")
    print(f"Q1.3 avg_n2={r3(avg_sample_mean_n2)} avg_n500={r3(avg_sample_mean_n500)}")
    print(f"Q2.1 %bachelor={r3(pct_bachelor)} mean_inc_bach={r3(mean_income_bach)} mean_inc_nobach={r3(mean_income_nobach)}")
    print(f"Q2.2 wage_hourly_mean={r3(mean_wage_hourly)} var={r3(var_wage_hourly)}")
    print(f"Q2.3 t={r3(t_stat_two_sided)} p={r3(p_two_sided)} reject(1/5/10%)={bool(reject_1_two)}/{bool(reject_5_two)}/{bool(reject_10_two)}")
    print(f"Q2.4 t={r3(t_stat_one_sided)} p={r3(p_one_sided_gt)} reject(5/10%)={bool(reject_5_one)}/{bool(reject_10_one)}")
    print(f"Q2.5 n={int(n_sub)} mean={r3(xbar_sub)} t={r3(t_stat_sub)} p={r3(p_one_sided_gt_sub)} reject(5/10%)={bool(reject_5_one_sub)}/{bool(reject_10_one_sub)}")
    print(f"Q2.6 diff_means={r2(diff_means)} t={r3(t_welch)} p={r3(p_welch)} signif_5%={bool(signif_5)}")
    print(f"Q2.7 corr(rent,bach)={r3(corr_rent_bach)} corr(ratio,bach)={r3(corr_ratio_bach)} "
          f"mean_bach_ratio={r3(mean_rb)} CI=[{r3(ci_low_rb)},{r3(ci_high_rb)}] 30% outside? {bool(reject_30_two_sided_rb)} "
          f"mean_nonbach_ratio={r3(mean_rnb)} t={r3(t_stat_rnb)} p={r3(p_one_sided_rnb)} reject_5%? {bool(reject_rnb_30)}")

if __name__ == "__main__":
    main()
