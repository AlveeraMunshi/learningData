"""
Econ 322 — Problem Set 3
"""

import argparse
import os
import sys
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")  # headless-safe
import matplotlib.pyplot as plt
import statsmodels.formula.api as smf

# Input file path constants
DEFAULT_GRADES_CSV = "grades_and_temps.csv"
DEFAULT_PERMITS_CSV = "middlesex_permits.csv"
DEFAULT_OUTPUT_DIR = "out"

# Output file path constants
Q1_TEMPERATURE_REGRESSION_CSV = "q1_temperature_regression.csv"
Q1_HYPOTHESIS_TESTS_CSV = "q1_hypothesis_tests.csv"
Q1_RESIDUAL_VARIANCE_BY_TEMP_BIN_CSV = "q1_residual_variance_by_temp_bin.csv"
Q1_SCATTER_PNG = "q1_scatter.png"
Q2_EQ2_SIMPLE_REGRESSION_CSV = "q2_eq2_simple_regression.csv"
Q2_EQ3_WITH_UNITS_CSV = "q2_eq3_with_units.csv"
Q2_EQ4_KITCHEN_SINK_CSV = "q2_eq4_kitchen_sink.csv"
PS3_KEY_NUMBERS_CSV = "ps3_key_numbers.csv"
PS3_ANSWERS_SHORT_TXT = "ps3_answers_short.txt"
PS3_TABLES_XLSX = "ps3_tables.xlsx"

def r3(x):
    return np.round(x, 3)

def standardize_cols(df: pd.DataFrame) -> pd.DataFrame:
    df.columns = [c.strip().lower().replace(" ", "_") for c in df.columns]
    return df

def analyze_q1(grades: pd.DataFrame, outdir: str) -> dict:
    # Prepare data
    grades = grades.copy()
    grades = standardize_cols(grades)
    if "avg_temp" not in grades or "math_score" not in grades:
        raise ValueError("grades_and_temps.csv must include columns: avg_temp, math_score")
    grades["avg_temp_f"] = grades["avg_temp"] * 9/5 + 32

    # Regression
    m = smf.ols("math_score ~ avg_temp_f", data=grades).fit()
    mr = m.get_robustcov_results(cov_type="HC1")

    # Build regression table (homoskedastic vs robust)
    q1_reg_table = pd.DataFrame({
        "coef": r3(m.params),
        "SE (homosked.)": r3(m.bse),
        "SE (robust HC1)": r3(pd.Series(mr.bse, index=m.params.index)),
        "t (robust)": r3(pd.Series(mr.tvalues, index=m.params.index)),
        "p>|t| (robust)": r3(pd.Series(mr.pvalues, index=m.params.index))
    })
    q1_reg_table.to_csv(os.path.join(outdir, Q1_TEMPERATURE_REGRESSION_CSV))

    # Heteroskedasticity quick check
    grades["resid"] = m.resid
    bins = pd.qcut(grades["avg_temp_f"], q=4, duplicates="drop")
    var_by_bin = grades.groupby(bins, observed=False)["resid"].agg(["count", "var"]).rename(columns={"var": "resid_variance"}).reset_index()
    var_by_bin.to_csv(os.path.join(outdir, Q1_RESIDUAL_VARIANCE_BY_TEMP_BIN_CSV), index=False)

    # Hypothesis tests (robust)
    beta_hat = m.params["avg_temp_f"]
    se_beta_rob = pd.Series(mr.bse, index=m.params.index)["avg_temp_f"]
    t_beta_eq0 = (beta_hat - 0) / se_beta_rob
    t_beta_eq_m185 = (beta_hat - (-1.85)) / se_beta_rob
    hypo_table = pd.DataFrame({
        "Null hypothesis": ["β = 0", "β = -1.85"],
        "t-stat (robust)": r3([t_beta_eq0, t_beta_eq_m185])
    })
    hypo_table.to_csv(os.path.join(outdir, Q1_HYPOTHESIS_TESTS_CSV), index=False)

    # Scatter plot (saved to PNG)
    plt.figure()
    plt.scatter(grades["avg_temp_f"], grades["math_score"])
    plt.xlabel("Average yearly temperature (°F)")
    plt.ylabel("Average PISA math score")
    plt.title("PISA Math vs. Average Yearly Temperature")
    plt.tight_layout()
    plt.savefig(os.path.join(outdir, Q1_SCATTER_PNG), dpi=200)
    plt.close()

    # Correlation and delta for -2.35°F
    corr_q1 = grades[["avg_temp_f", "math_score"]].corr().iloc[0,1]
    delta = beta_hat * (-2.35)

    return {
        "alpha_hat": float(m.params["Intercept"]),
        "beta_hat": float(beta_hat),
        "se_alpha_homo": float(m.bse["Intercept"]),
        "se_beta_homo": float(m.bse["avg_temp_f"]),
        "se_alpha_rob": float(pd.Series(mr.bse, index=m.params.index)["Intercept"]),
        "se_beta_rob": float(se_beta_rob),
        "t_beta_eq0": float(t_beta_eq0),
        "t_beta_eq_m185": float(t_beta_eq_m185),
        "corr_q1": float(corr_q1),
        "delta_math_for_minus2_35F": float(delta)
    }

def analyze_q2(permits: pd.DataFrame, outdir: str) -> dict:
    permits = permits.copy()
    permits = standardize_cols(permits)
    for col in ["construction_cost", "fees", "units", "square_feet", "volume"]:
        if col in permits.columns:
            permits[col] = pd.to_numeric(permits[col], errors="coerce")

    # Eq (2): cost ~ fees
    m2 = smf.ols("construction_cost ~ fees", data=permits).fit()
    m2r = m2.get_robustcov_results(cov_type="HC1")
    q2_eq2 = pd.DataFrame({
        "coef": r3(m2.params),
        "SE (robust HC1)": r3(pd.Series(m2r.bse, index=m2.params.index)),
        "t (robust)": r3(pd.Series(m2r.tvalues, index=m2.params.index)),
        "p>|t| (robust)": r3(pd.Series(m2r.pvalues, index=m2.params.index))
    })
    q2_eq2.to_csv(os.path.join(outdir, Q2_EQ2_SIMPLE_REGRESSION_CSV))

    # Eq (3): cost ~ fees + units
    m3 = smf.ols("construction_cost ~ fees + units", data=permits).fit()
    m3r = m3.get_robustcov_results(cov_type="HC1")
    q2_eq3 = pd.DataFrame({
        "coef": r3(m3.params),
        "SE (robust HC1)": r3(pd.Series(m3r.bse, index=m3.params.index)),
        "t (robust)": r3(pd.Series(m3r.tvalues, index=m3.params.index)),
        "p>|t| (robust)": r3(pd.Series(m3r.pvalues, index=m3.params.index))
    })
    q2_eq3.to_csv(os.path.join(outdir, Q2_EQ3_WITH_UNITS_CSV))

    # Eq (4) + dummies for NB and Edison
    permits["new_brunswick"] = (permits["municipality_name"].str.strip().str.lower() == "new brunswick").astype(int)
    permits["edison"] = (permits["municipality_name"].str.strip().str.lower() == "edison").astype(int)
    m4 = smf.ols("construction_cost ~ fees + units + square_feet + volume + new_brunswick + edison", data=permits).fit()
    m4r = m4.get_robustcov_results(cov_type="HC1")
    q2_eq4 = pd.DataFrame({
        "coef": r3(m4.params),
        "SE (robust HC1)": r3(pd.Series(m4r.bse, index=m4.params.index)),
        "t (robust)": r3(pd.Series(m4r.tvalues, index=m4.params.index)),
        "p>|t| (robust)": r3(pd.Series(m4r.pvalues, index=m4.params.index))
    })
    q2_eq4.to_csv(os.path.join(outdir, Q2_EQ4_KITCHEN_SINK_CSV))

    # Correlations used to discuss OVB
    corr_units_fees = permits[["units", "fees"]].dropna().corr().iloc[0,1]
    corr_units_cost = permits[["units", "construction_cost"]].dropna().corr().iloc[0,1]

    return {
        "beta1": float(m2.params.get("fees", np.nan)),
        "se_beta1_rob": float(pd.Series(m2r.bse, index=m2.params.index).get("fees", np.nan)),
        "beta2": float(m3.params.get("fees", np.nan)),
        "se_beta2_rob": float(pd.Series(m3r.bse, index=m3.params.index).get("fees", np.nan)),
        "theta2": float(m3.params.get("units", np.nan)),
        "se_theta2_rob": float(pd.Series(m3r.bse, index=m3.params.index).get("units", np.nan)),
        "beta3": float(m4.params.get("fees", np.nan)),
        "se_beta3_rob": float(pd.Series(m4r.bse, index=m4.params.index).get("fees", np.nan)),
        "alpha3": float(m4.params.get("Intercept", np.nan)),
        "se_alpha3_rob": float(pd.Series(m4r.bse, index=m4.params.index).get("Intercept", np.nan)),
        "theta3": float(m4.params.get("units", np.nan)),
        "se_theta3_rob": float(pd.Series(m4r.bse, index=m4.params.index).get("units", np.nan)),
        "kappa3": float(m4.params.get("square_feet", np.nan)),
        "se_kappa3_rob": float(pd.Series(m4r.bse, index=m4.params.index).get("square_feet", np.nan)),
        "nu3": float(m4.params.get("volume", np.nan)),
        "se_nu3_rob": float(pd.Series(m4r.bse, index=m4.params.index).get("volume", np.nan)),
        "phi_nb": float(m4.params.get("new_brunswick", np.nan)),
        "se_phi_nb_rob": float(pd.Series(m4r.bse, index=m4.params.index).get("new_brunswick", np.nan)),
        "phi_edison": float(m4.params.get("edison", np.nan)),
        "se_phi_edison_rob": float(pd.Series(m4r.bse, index=m4.params.index).get("edison", np.nan)),
        "corr_units_fees": float(corr_units_fees),
        "corr_units_cost": float(corr_units_cost),
        # also return tables for Excel export
        "_tables": {"eq2": q2_eq2, "eq3": q2_eq3, "eq4": q2_eq4}
    }

def write_answers(outdir: str, q1: dict, q2: dict):
    lines = []
    lines.append(f"Q1.1: Visual correlation appears {'negative' if q1['corr_q1'] < 0 else 'positive' if q1['corr_q1'] > 0 else 'near zero'} (Pearson r = {r3(q1['corr_q1'])}).")
    lines.append(f"Q1.2: α̂ = {r3(q1['alpha_hat'])}, β̂ = {r3(q1['beta_hat'])}. α̂ is at 0°F (off-support); β̂ is points per 1°F.")
    lines.append("Q1.3: Residual variance differs across temperature bins ⇒ use robust SEs alongside classical SEs.")
    lines.append(f"Q1.4(a): t (β=0) = {r3(q1['t_beta_eq0'])}.")
    lines.append(f"Q1.4(b): t (β=-1.85) = {r3(q1['t_beta_eq_m185'])}.")
    lines.append(f"Q1.5: ΔTemp = −2.35°F ⇒ Δ(math) = β̂ × (−2.35) = {r3(q1['delta_math_for_minus2_35F'])} points.")
    lines.append("Q1.6: β̂ unlikely causal due to omitted variables and aggregation issues.")
    lines.append(f"Q2.1: β̂₁ (fees) = {r3(q2['beta1'])}, robust SE = {r3(q2['se_beta1_rob'])}.")
    lines.append(f"Q2.2: corr(units, fees) = {r3(q2['corr_units_fees'])}, corr(units, construction_cost) = {r3(q2['corr_units_cost'])}.")
    lines.append(f"Q2.3: β̂₂ (fees) = {r3(q2['beta2'])}, θ̂₂ (units) = {r3(q2['theta2'])}.")
    lines.append(f"Q2.4: β̂₃ (fees) = {r3(q2['beta3'])}.")
    lines.append(f"Q2.5: α̂₃ = {r3(q2['alpha3'])} (off-support). new_brunswick coef = {r3(q2['phi_nb'])}.")
    with open(os.path.join(outdir, PS3_ANSWERS_SHORT_TXT), "w") as f:
        f.write("\n".join(lines))

def write_key_numbers(outdir: str, q1: dict, q2: dict):
    rows = [
        ("Q1: corr(avg_temp_f, math_score)", q1["corr_q1"]),
        ("Q1: alpha_hat", q1["alpha_hat"]),
        ("Q1: beta_hat", q1["beta_hat"]),
        ("Q1: SE_alpha_homosked", q1["se_alpha_homo"]),
        ("Q1: SE_beta_homosked", q1["se_beta_homo"]),
        ("Q1: SE_alpha_robust", q1["se_alpha_rob"]),
        ("Q1: SE_beta_robust", q1["se_beta_rob"]),
        ("Q1: t for H0: beta=0 (robust)", q1["t_beta_eq0"]),
        ("Q1: t for H0: beta=-1.85 (robust)", q1["t_beta_eq_m185"]),
        ("Q1: delta math for -2.35°F", q1["delta_math_for_minus2_35F"]),
        ("Q2 Eq2: beta1 (fees)", q2["beta1"]),
        ("Q2 Eq2: SE_beta1_robust", q2["se_beta1_rob"]),
        ("Q2: corr(units, fees)", q2["corr_units_fees"]),
        ("Q2: corr(units, construction_cost)", q2["corr_units_cost"]),
        ("Q2 Eq3: beta2 (fees)", q2["beta2"]),
        ("Q2 Eq3: SE_beta2_robust", q2["se_beta2_rob"]),
        ("Q2 Eq3: theta2 (units)", q2["theta2"]),
        ("Q2 Eq3: SE_theta2_robust", q2["se_theta2_rob"]),
        ("Q2 Eq4: alpha3 (intercept)", q2["alpha3"]),
        ("Q2 Eq4: SE_alpha3_robust", q2["se_alpha3_rob"]),
        ("Q2 Eq4: beta3 (fees)", q2["beta3"]),
        ("Q2 Eq4: SE_beta3_robust", q2["se_beta3_rob"]),
        ("Q2 Eq4: theta3 (units)", q2["theta3"]),
        ("Q2 Eq4: SE_theta3_robust", q2["se_theta3_rob"]),
        ("Q2 Eq4: kappa3 (square_feet)", q2["kappa3"]),
        ("Q2 Eq4: SE_kappa3_robust", q2["se_kappa3_rob"]),
        ("Q2 Eq4: nu3 (volume)", q2["nu3"]),
        ("Q2 Eq4: SE_nu3_robust", q2["se_nu3_rob"]),
        ("Q2 Eq4: phi_nb (new_brunswick)", q2["phi_nb"]),
        ("Q2 Eq4: SE_phi_nb_robust", q2["se_phi_nb_rob"]),
        ("Q2 Eq4: phi_edison (edison)", q2["phi_edison"]),
        ("Q2 Eq4: SE_phi_edison_robust", q2["se_phi_edison_rob"]),
    ]
    df = pd.DataFrame(rows, columns=["item", "value"])
    df["value"] = r3(df["value"].astype(float))
    df.to_csv(os.path.join(outdir, PS3_KEY_NUMBERS_CSV), index=False)

def write_excel_pack(outdir: str, q1_table_path: str, q2_tables: dict):
    # Bundle core tables into one Excel workbook for convenience.
    with pd.ExcelWriter(os.path.join(outdir, PS3_TABLES_XLSX), engine="xlsxwriter") as xw:
        pd.read_csv(q1_table_path, index_col=0).to_excel(xw, sheet_name="Q1 Regression")
        q2_tables["eq2"].to_excel(xw, sheet_name="Q2 Eq2")
        q2_tables["eq3"].to_excel(xw, sheet_name="Q2 Eq3")
        q2_tables["eq4"].to_excel(xw, sheet_name="Q2 Eq4")

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--grades", default=DEFAULT_GRADES_CSV, help="Path to grades_and_temps.csv")
    ap.add_argument("--permits", default=DEFAULT_PERMITS_CSV, help="Path to middlesex_permits.csv")
    ap.add_argument("--out", default=DEFAULT_OUTPUT_DIR, help="Output directory")
    args = ap.parse_args()

    os.makedirs(args.out, exist_ok=True)

    # Load data
    grades = pd.read_csv(args.grades)
    permits = pd.read_csv(args.permits)

    # Analyses
    q1 = analyze_q1(grades, args.out)
    q2 = analyze_q2(permits, args.out)

    # Write summary artifacts
    write_answers(args.out, q1, q2)
    write_key_numbers(args.out, q1, q2)
    write_excel_pack(args.out, os.path.join(args.out, Q1_TEMPERATURE_REGRESSION_CSV), q2["_tables"])

    # Final console print for quick verification
    print("Done. Key numbers:")
    print(pd.read_csv(os.path.join(args.out, PS3_KEY_NUMBERS_CSV)).to_string(index=False))
    print(f"\nArtifacts saved in: {os.path.abspath(args.out)}")
    print("Files created:")
    for fn in [
        Q1_TEMPERATURE_REGRESSION_CSV,
        Q1_HYPOTHESIS_TESTS_CSV,
        Q1_RESIDUAL_VARIANCE_BY_TEMP_BIN_CSV,
        Q1_SCATTER_PNG,
        Q2_EQ2_SIMPLE_REGRESSION_CSV,
        Q2_EQ3_WITH_UNITS_CSV,
        Q2_EQ4_KITCHEN_SINK_CSV,
        PS3_KEY_NUMBERS_CSV,
        PS3_ANSWERS_SHORT_TXT,
        PS3_TABLES_XLSX,
    ]:
        print(" -", fn)

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print("ERROR:", e, file=sys.stderr)
        sys.exit(1)
