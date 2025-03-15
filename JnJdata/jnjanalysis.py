import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import folium
from folium.plugins import HeatMap
from scipy.stats import ttest_ind

# Load datasets
# Store locations datasets
store_data = pd.read_csv("JnJdata/store_location_data.csv")
marketing_data = pd.read_csv("JnJdata/marketing_campaign_data.csv")
demographics_data = pd.read_csv("JnJdata/demographics_data.csv")
competitor_data = pd.read_csv("JnJdata/competitor_data.csv")
revenue_expense_data = pd.read_csv("JnJdata/revenue_expense_data.csv")
cac_data = pd.read_csv("JnJdata/cac_data.csv")
roi_data = pd.read_csv("JnJdata/roi_data.csv")
ab_test_data = pd.read_csv("JnJdata/ab_test_data.csv")
population_density_data = pd.read_csv("JnJdata/population_density_data.csv")
population_growth_data = pd.read_csv("JnJdata/population_growth_data.csv")
school_enrollment_growth = pd.read_csv("JnJdata/school_enrollment_data.csv")
# Marketing datasets
before_after_data = pd.read_csv("JnJdata/before_after_data.csv")

# Evaluating Store Location for a Children's Clothing Company

# 1. Store Location Comparison
plt.figure(figsize=(8, 5))
sns.barplot(x="Location", y="Projected_Revenue (monthly)", data=store_data)
plt.title("Projected Revenue Comparison")
plt.ylabel("Revenue ($)")
plt.savefig("JnJdata/images/1.1_projected_revenue.png")
plt.show()
plt.close()

# 2. Demographics Comparison
# Reshape the data from wide to long format
demographics_data_long = demographics_data.melt(id_vars=["Metric"], var_name="Location", value_name="Value")

# Filter for Median Income
income_data = demographics_data_long[demographics_data_long["Metric"] == "Median Income ($)"]

# Plot Median Income
plt.figure(figsize=(8, 5))
sns.barplot(x="Location", y="Value", data=income_data)
plt.title("Median Income by Location")
plt.ylabel("Income ($)")
plt.savefig("JnJdata/images/1.2a_demographics_income.png")
plt.show()
plt.close()

# Pivot the data to have metrics as columns for scoring
demographics_data_wide = demographics_data_long.pivot(index="Location", columns="Metric", values="Value").reset_index()

# Rename columns to remove spaces and special characters
demographics_data_wide.columns = [
    "Location",
    "Competition_Intensity",
    "Families_with_Children",
    "Median_Income",
    "Population_Size",
    "Rent_Cost"
]

# Define scoring function
def calculate_score(row):
    weights = {
        "Population_Size": 0.4,
        "Median_Income": 0.3,
        "Families_with_Children": 0.2,
        "Competition_Intensity": -0.1,  # Negative weight because higher competition is worse
        "Rent_Cost": -0.1  # Negative weight because higher rent is worse
    }
    score = (
        row["Population_Size"] * weights["Population_Size"] +
        row["Median_Income"] * weights["Median_Income"] +
        row["Families_with_Children"] * weights["Families_with_Children"] +
        row["Competition_Intensity"] * weights["Competition_Intensity"] +
        row["Rent_Cost"] * weights["Rent_Cost"]
    )
    return score

# Apply scoring model
demographics_data_wide["Location_Score"] = demographics_data_wide.apply(calculate_score, axis=1)

# Print the scored data
print(demographics_data_wide)

# Plot the location scores
plt.figure(figsize=(8, 5))
sns.barplot(x="Location", y="Location_Score", data=demographics_data_wide)

# Adjust the y-axis scale to emphasize differences
min_score = demographics_data_wide["Location_Score"].min()
max_score = demographics_data_wide["Location_Score"].max()
plt.ylim(min_score - 500, max_score + 500)  # Adjust the range to make differences more visible

# Add title and labels
plt.title("Location Scores Based on Weighted Factors")
plt.ylabel("Location Score")
plt.savefig("JnJdata/images/1.2b_location_scores.png")
plt.show()
plt.close()

# 3. Competitor Revenue vs Customer Footfall
# Create subplots
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8))

# Plot Competitor Revenue
sns.barplot(x="Location", y="Competitor_Revenue", data=competitor_data, ax=ax1, color="skyblue")
ax1.set_title("Competitor Revenue by Location")
ax1.set_ylabel("Competitor Revenue ($)")
ax1.grid(True, linestyle="--", alpha=0.7)

# Plot Customer Footfall
sns.barplot(x="Location", y="Customer_Footfall", data=competitor_data, ax=ax2, color="orange")
ax2.set_title("Customer Footfall by Location")
ax2.set_ylabel("Customer Footfall")
ax2.grid(True, linestyle="--", alpha=0.7)

# Adjust layout
plt.tight_layout()
plt.savefig("JnJdata/images/1.3_competitor_revenue_vs_footfall_subplots.png")
plt.show()
plt.close()

# 4. Revenue vs. Expenses
# Reshape the data for plotting
revenue_expense_data_melted = revenue_expense_data.melt(id_vars=["Location"], var_name="Metric", value_name="Amount")
# Plot
plt.figure(figsize=(10, 6))
sns.barplot(x="Location", y="Amount", hue="Metric", data=revenue_expense_data_melted)
plt.title("Annual Revenue vs Expenses by Location")
plt.xlabel("Location")
plt.ylabel("Amount ($)")
plt.legend(title="Metric")
plt.grid(True)
plt.savefig("JnJdata/images/1.4_revenue_expenses_by_location.png")
plt.show()
plt.close()

# 5. Customer Acquisition Cost (CAC) by Channel
plt.figure(figsize=(12, 8))
sns.barplot(x="Marketing_Channel", y="CAC ($)", hue="Location", data=cac_data, palette="Set2")
plt.title("Customer Acquisition Cost (CAC) by Marketing Channel and Location")
plt.xlabel("Marketing Channel")
plt.ylabel("CAC ($)")
plt.legend(title="Location", bbox_to_anchor=(1.05, 1), loc='upper left')  # Move legend outside the plot
plt.grid(True, axis="y", linestyle="--", alpha=0.7)
plt.tight_layout()  # Adjust layout to prevent overlap
plt.savefig("JnJdata/images/1.5_cac_by_channel_and_location.png")
plt.show()
plt.close()


# 6. ROI per Marketing Channel
plt.figure(figsize=(12, 8))
sns.barplot(x="Marketing_Channel", y="ROI (%)", hue="Location", data=roi_data, palette="Set2")
plt.title("Return on Investment (ROI) by Marketing Channel and Location")
plt.xlabel("Marketing Channel")
plt.ylabel("ROI (%)")
plt.legend(title="Location", bbox_to_anchor=(1.05, 1), loc='upper left')  # Move legend outside the plot
plt.grid(True, axis="y", linestyle="--", alpha=0.7)
plt.tight_layout()  # Adjust layout to prevent overlap
plt.savefig("JnJdata/images/1.6_roi_by_channel_and_location.png")
plt.show()
plt.close()

# 7. Population Density Heatmap
# Create a base map
m = folium.Map(location=[37.7749, -122.4194], zoom_start=5)

# Add heatmap layer
HeatMap(population_density_data[["Latitude", "Longitude", "Population_Density"]].values).add_to(m)

# Save the map
m.save("JnJdata/images/1.7_population_heatmap.html")

# 8. Population Growth Comparison
# Reshape the data from wide to long format for plotting
population_growth_data_long = population_growth_data.melt(id_vars=["Year"], var_name="Location", value_name="Population")

# Plot population growth over time
plt.figure(figsize=(10, 6))
sns.lineplot(x="Year", y="Population", hue="Location", data=population_growth_data_long, marker="o")
plt.title("Population Growth Over Time by Location")
plt.xlabel("Year")
plt.ylabel("Population")
plt.grid(True, linestyle="--", alpha=0.7)
plt.tight_layout()  # Adjust layout to prevent overlap
plt.savefig("JnJdata/images/1.8_population_growth_over_time.png")
plt.show()
plt.close()

# 8. School Enrollment Growth Over Time
#Reshape the data from wide to long format for plotting
school_enrollment_growth_long = school_enrollment_growth.melt(id_vars=["Year"], var_name="Location", value_name="Enrollment")

# Plot the data
plt.figure(figsize=(10, 6))
sns.lineplot(x="Year", y="Enrollment", hue="Location", data=school_enrollment_growth_long, marker="o")
plt.title("School Enrollment Growth Over Time by Location")
plt.xlabel("Year")
plt.ylabel("Number of Children Enrolled")
plt.grid(True, linestyle="--", alpha=0.7)
plt.tight_layout()  # Adjust layout to prevent overlap
plt.savefig("JnJdata/images/1.13_school_enrollment_growth_over_time.png")
plt.show()
plt.close()

# Measuring the Effectiveness of a Marketing Campaign

# 1. Website Visitors Over Time
plt.figure(figsize=(10, 5))
plt.plot(marketing_data["Date"], marketing_data["Website_Visitors"], marker="o", label="Website Visitors")
plt.xticks(rotation=45)
plt.title("Website Visitors Over Time")
plt.xlabel("Date")
plt.ylabel("Visitors")
plt.legend()
plt.savefig("JnJdata/images/2.1_website_visitors.png")
plt.show()
plt.close()

# 2. Ad Spend Over Time
plt.figure(figsize=(6, 6))
sns.scatterplot(x="Ad_Spend ($)", y="Revenue ($)", data=marketing_data)
plt.title("Ad Spend vs. Revenue")
plt.xlabel("Ad Spend ($)")
plt.ylabel("Revenue ($)")
plt.savefig("JnJdata/images/2.2_ad_spend_vs_revenue.png")
plt.show()
plt.close()

# 3. Conversion Rate Over Time
plt.figure(figsize=(10, 5))
sns.lineplot(x=marketing_data["Date"], y=marketing_data["Conversion_Rate (%)"])
plt.xticks(rotation=45)
plt.title("Conversion Rate Over Time")
plt.xlabel("Date")
plt.ylabel("Conversion Rate (%)")
plt.savefig("JnJdata/images/2.3_conversion_rate_trend.png")
plt.show()
plt.close()


# 4. Sales Before and After Campaign
plt.figure(figsize=(10, 5))
sns.barplot(x="Period", y="Sales", data=before_after_data, palette="Set2")
plt.title("Sales Before and After Campaign")
plt.ylabel("Sales ($)")
plt.savefig("JnJdata/images/2.4_before_after_sales.png")
plt.show()
plt.close()

# 5. A/B Test Analysis
# Perform t-test
group_a = ab_test_data[ab_test_data["Group"] == "A"]["Conversion_Rate"]
group_b = ab_test_data[ab_test_data["Group"] == "B"]["Conversion_Rate"]
t_stat, p_value = ttest_ind(group_a, group_b)

print(f"T-statistic: {t_stat}, P-value: {p_value}")

if p_value < 0.05:
    print("There is a significant difference between Group A and Group B.")
else:
    print("There is no significant difference between Group A and Group B.")
