import pandas as pd
import numpy as np
import statsmodels.formula.api as smf

# -------------------------
# Helpers
# -------------------------
def ols_hc3(formula, data):
    m = smf.ols(formula, data=data).fit()
    mr = m.get_robustcov_results(cov_type="HC3")
    return m, mr

def probit_model(formula, data):
    # R's glm(..., binomial(link="probit")) equivalent
    return smf.probit(formula, data=data).fit(disp=False)

def coef_table_hc3(mr):
    return pd.DataFrame({
        "coef": mr.params,
        "se_HC3": mr.bse,
        "t": mr.tvalues,
        "p": mr.pvalues
    })

# =========================================================
# QUESTION 1 — health_insurance.csv
# =========================================================
df_hi = pd.read_csv("health_insurance.csv")

# Part 1
model1, model1_r = ols_hc3("insured ~ health", df_hi)
print("\nQ1 Part 1: insured ~ health (HC3)")
print(coef_table_hc3(model1_r))

# Part 2
df_hi["ln_inc"] = np.log(df_hi["inc"])
model2, model2_r = ols_hc3("insured ~ health + ln_inc", df_hi)
print("\nQ1 Part 2: insured ~ health + ln_inc (HC3)")
print(coef_table_hc3(model2_r))

# Part 3
model3, model3_r = ols_hc3("insured ~ health + age + educ + empl + ln_inc", df_hi)
print("\nQ1 Part 3: full LPM (HC3)")
print(coef_table_hc3(model3_r))

pred_A = model3.predict(pd.DataFrame({
    "health": [5],
    "age": [30],
    "educ": [13],
    "empl": [1],
    "ln_inc": [np.log(45000)]
})).iloc[0]

print("\nQ1 Part 3 prediction (A):")
print(pred_A)

# Part 4
pred_B_lpm = model3.predict(pd.DataFrame({
    "health": [5],
    "age": [21],
    "educ": [10],
    "empl": [0],
    "ln_inc": [np.log(1000)]
})).iloc[0]

print("\nQ1 Part 4 prediction (B, LPM):")
print(pred_B_lpm)

# Part 5 (Probit)
probit_m = probit_model("insured ~ health + age + educ + empl + ln_inc", df_hi)

pred_B_probit = probit_m.predict(pd.DataFrame({
    "health": [5],
    "age": [21],
    "educ": [10],
    "empl": [0],
    "ln_inc": [np.log(1000)]
})).iloc[0]

print("\nQ1 Part 5 prediction (B, Probit):")
print(pred_B_probit)

# Part 6 (Average individual, empl 0→1)
avg_vals = pd.DataFrame({
    "health": [df_hi["health"].mean()],
    "age":    [df_hi["age"].mean()],
    "educ":   [df_hi["educ"].mean()],
    "ln_inc": [df_hi["ln_inc"].mean()]
})

p0 = probit_m.predict(pd.concat([avg_vals, pd.DataFrame({"empl":[0]})], axis=1)).iloc[0]
p1 = probit_m.predict(pd.concat([avg_vals, pd.DataFrame({"empl":[1]})], axis=1)).iloc[0]

print("\nQ1 Part 6: p1 - p0 (avg person, Probit):")
print(p1 - p0)

# =========================================================
# QUESTION 2 — crime_and_schools.csv
# =========================================================
df_cs = pd.read_csv("crime_and_schools.csv")

# Part 1
q2_m1, q2_m1r = ols_hc3("mathpct ~ crime_exposure", df_cs)
print("\nQ2 Part 1: mathpct ~ crime_exposure (HC3)")
print(coef_table_hc3(q2_m1r).loc[["crime_exposure"]])

# Part 2: Neighborhood FE
# R fixest: feols(mathpct ~ crime_exposure | nhoodid)
q2_m2 = smf.ols("mathpct ~ crime_exposure + C(nhoodid)", data=df_cs).fit()
q2_m2r = q2_m2.get_robustcov_results(cov_type="HC3")

print("\nQ2 Part 2: + neighborhood FE (HC3)")
print(coef_table_hc3(q2_m2r).loc[["crime_exposure"]])

# Part 3: Neighborhood + Year FE
# R fixest: feols(mathpct ~ crime_exposure | nhoodid + year)
q2_m3 = smf.ols("mathpct ~ crime_exposure + C(nhoodid) + C(year)", data=df_cs).fit()
q2_m3r = q2_m3.get_robustcov_results(cov_type="HC3")

print("\nQ2 Part 3: + neighborhood FE + year FE (HC3)")
print(coef_table_hc3(q2_m3r).loc[["crime_exposure"]])

# Part 4: high_income + interaction + both FEs
df_cs["high_income"] = (df_cs["med_inc_hh"] > 40000).astype(int)

q2_m4 = smf.ols(
    "mathpct ~ crime_exposure * high_income + C(nhoodid) + C(year)",
    data=df_cs
).fit()
q2_m4r = q2_m4.get_robustcov_results(cov_type="HC3")

print("\nQ2 Part 4: interaction + FE (HC3)")
print(coef_table_hc3(q2_m4r).loc[
    ["crime_exposure", "high_income", "crime_exposure:high_income"]
])
