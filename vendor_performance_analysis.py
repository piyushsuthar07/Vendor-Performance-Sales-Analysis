import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import warnings 
import sqlite3
from scipy.stats import ttest_ind
import scipy.stats as stats
warnings.filterwarnings("ignore")

#load dataset connection
conn = sqlite3.connect("inventory.db")

#fetching vendor summary data
df = pd.read_sql_query("SELECT * FROM vendor_sales_summary1", conn)
print(df)

#EDA again

#summary statics
print(df.describe().T)

numerical_cols = df.select_dtypes(include=np.number).columns

#Distribution plot for numerical columns
numerical_cols = df.select_dtypes(include=np.number).columns

plt.figure(figsize=(15, 10))  # Optional: bigger figure size

for i, col in enumerate(numerical_cols):
    plt.subplot(4, 4, i + 1)  # i + 1 for correct subplot index
    sns.histplot(df[col], kde=True, bins=30)
    plt.title(col)

plt.tight_layout()
plt.show()

#outline detection with boxplot

plt.figure(figsize=(15,10))
for i, col in enumerate(numerical_cols):
    plt.subplot(4, 4, i+1)
    sns.boxplot(y=df[col])
    plt.title(col)
plt.tight_layout()
plt.show()

df = pd.read_sql_query("""SELECT *
                       FROM vendor_sales_summary1
                       WHERE GrossProfit > 0
                       AND ProfitMargin > 0
                       AND TotalSalesQuantity > 0""", conn)
print(df)


#count plot for categorical columns
catogorical_cols = ["VendorName", "Description"]

plt.figure(figsize=(12,5))
for i, col in enumerate(catogorical_cols):
    plt.subplot(1, 2, i+1)
    sns.countplot(y=df[col], order=df[col].value_counts().index[:10])
    plt.title(f"count plot of {col}")
plt.tight_layout()
plt.show()

#correlation Heatmap
plt.figure(figsize=(12,8))
correlation_matrix = df[numerical_cols].corr()
sns.heatmap(correlation_matrix, annot=True, fmt=".2f", cmap="coolwarm", linewidths=0.5)
plt.title("correlation headmap")
plt.show()


#DATA ANALYSIS

#1. identify brands that needs promotional or pricing adjustments which exhibit lower sales performance but higher profit margin
brand_performance = df.groupby("Description").agg({
    'TotalSalesDollars':'sum',
    'ProfitMargin': 'mean'
}).reset_index()

print(brand_performance)

low_sales_threshold = brand_performance['TotalSalesDollars'].quantile(0.15)
high_margin_threshold = brand_performance['ProfitMargin'].quantile(0.85)
print(low_sales_threshold)
print(high_margin_threshold)

#Filter brands with low sales but high profit margin
target_brands = brand_performance[
    (brand_performance['TotalSalesDollars'] <= low_sales_threshold) &
    (brand_performance['ProfitMargin'] >= high_margin_threshold)
]
print("brands with low sales and high profit margin: ", target_brands.sort_values('TotalSalesDollars'))

#create this using scatterplot

plt.figure(figsize=(10, 6))
# Scatter plot for all brands
sns.scatterplot(data=brand_performance, x='TotalSalesDollars', y='ProfitMargin', color="blue", label="All Brands", alpha=0.2)
# Scatter plot for target brands
sns.scatterplot(data=target_brands, x='TotalSalesDollars', y='ProfitMargin', color="red", label="Target Brands")
# Threshold lines
plt.axhline(high_margin_threshold, linestyle="--", color="black", label="High Margin Threshold")
plt.axhline(low_sales_threshold, linestyle="--", color="black", label="Low Sales Threshold")
# Labels and legend
plt.xlabel("Total Sales ($)")
plt.ylabel("Profit Margin (%)")
plt.title("Brands for Promotional or Pricing Adjustment")
plt.legend()
plt.grid(True)
plt.show()

#2. which vendor and brands demonstrate the highest sales performance?

top_vendor = df.groupby("VendorName")["TotalSalesDollars"].sum().nlargest(10)
top_brand = df.groupby("Description")["TotalSalesDollars"].sum().nlargest(10)

plt.figure(figsize=(15, 6))

plt.subplot(1, 2, 1)
ax1 = sns.barplot(y=top_vendor.index, x=top_vendor.values, palette="Blues_r")
plt.title("Top 10 Vendors by Sales")

# Add labels to bars
for bar in ax1.patches:
    ax1.text(bar.get_width() + (bar.get_width() * 0.02),
             bar.get_y() + bar.get_height() / 2,
             f"${bar.get_width():,.2f}",
             ha="left", va="center", fontsize=10, color="black")

# Plot for top brands
plt.subplot(1, 2, 2)
ax2 = sns.barplot(y=top_brand.index.astype(str), x=top_brand.values, palette="Reds_r")
plt.title("Top 10 Brands by Sales")

for bar in ax2.patches:
    ax2.text(bar.get_width() + (bar.get_width() * 0.02),
             bar.get_y() + bar.get_height() / 2,
             f"${bar.get_width():,.2f}",
             ha="left", va="center", fontsize=10, color="black")

plt.tight_layout()
plt.show()

#3. which vendor contribute the most to total purchase dollars?

# Group and aggregate
vendor_performance = df.groupby("VendorName").agg({
    "TotalPurchaseDollars": "sum",
    "GrossProfit": "sum",
    "TotalSalesDollars": "sum"
})

# Calculate contribution percentage
vendor_performance["PurchaseContribution%"] = vendor_performance["TotalSalesDollars"] / vendor_performance["TotalSalesDollars"].sum() * 100

# Sort and round
vendor_performance = round(vendor_performance.sort_values("PurchaseContribution%", ascending=False), 2)

# Top 10 vendors
top_vendor = vendor_performance.head(10).copy()  # important to avoid SettingWithCopyWarning

# Print results
print(top_vendor)
print(f"Total Contribution of Top 10 Vendors: {top_vendor['PurchaseContribution%'].sum():.2f}%")

# Cumulative contribution
top_vendor["Cumulative_Contribution%"] = top_vendor["PurchaseContribution%"].cumsum()

# Reset index for plotting
top_vendor = top_vendor.reset_index()

# Plotting
fig, ax1 = plt.subplots(figsize=(10, 6))

# Bar plot
sns.barplot(x="VendorName", y="PurchaseContribution%", data=top_vendor, palette="mako", ax=ax1)
for i, value in enumerate(top_vendor["PurchaseContribution%"]):
    ax1.text(i, value - 1, f"{value:.2f}%", ha="center", fontsize=10, color="white")

# Line plot
ax2 = ax1.twinx()
ax2.plot(top_vendor["VendorName"], top_vendor["Cumulative_Contribution%"], color="red", marker="o", linestyle="dashed", label="Cumulative")

# Formatting
ax1.set_xticklabels(top_vendor["VendorName"], rotation=90)
ax1.set_ylabel("Purchase Contribution %", color="blue")
ax2.set_ylabel("Cumulative Contribution %", color="red")
ax1.set_xlabel("Vendors")
ax1.set_title("Pareto Chart: Vendor Contribution to Total Purchase")

ax2.axhline(y=100, color="gray", linestyle="dashed", alpha=0.7)
ax2.legend(loc="upper right")

plt.tight_layout()
plt.show()

#4. how much of total procurement is dependent on the top vendors ?

# Print total purchase contribution
top_vendor = vendor_performance.head(10).reset_index()
print(f"Total purchase contribution of top 10 vendors is {round(top_vendor['PurchaseContribution%'].sum(), 2)}%")

# Prepare data
vendors = list(top_vendor["VendorName"].values)
purchase_contributions = list(top_vendor["PurchaseContribution%"].values)
total_contribution = sum(purchase_contributions)
remaining_contribution = 100 - total_contribution

# Append "Other Vendors"
vendors.append("Other Vendors")
purchase_contributions.append(remaining_contribution)

# Donut chart
fig, ax = plt.subplots(figsize=(8, 8))
wedges, text, autotexts = ax.pie(
    purchase_contributions,
    labels=vendors,
    autopct="%1.1f%%",
    startangle=140,
    pctdistance=0.85,
    colors=plt.cm.Paired.colors
)

# Center circle
centre_circle = plt.Circle((0, 0), 0.70, fc="white")
fig.gca().add_artist(centre_circle)

# Add total contribution in center
plt.text(0, 0, f"Top 10 total:\n{total_contribution:.2f}%", fontsize=14, fontweight="bold", ha="center", va="center")

# Title
plt.title("Top 10 Vendors' Purchase Contribution (%)")
plt.tight_layout()
plt.show()


#5. does purchasing in bulk reduce the unit price and what is the optimal purchase volume for cost saving

df["UnitPurchasePrice"] = df["TotalPurchaseDollars"] / df["TotalPurchaseQuantity"]
df["OrderSize"] = pd.qcut(df["TotalPurchaseQuantity"], q = 3, labels=["small", "medium", "large"])

mean2 = df.groupby("OrderSize")[["UnitPurchasePrice"]].mean()
print(df[["TotalPurchaseQuantity", "OrderSize"]])
print(mean2)

plt.figure(figsize=(10, 6))
sns.boxplot(data=df, x= "OrderSize", y = "UnitPurchasePrice", palette="deep")
plt.title("Impact of bulk purchasing")
plt.xlabel("Order Size")
plt.ylabel("average Unit Purchase Price")
plt.show()

#6. which vendor have low inventory turnover, indicating excess stock and slow-moving products?

hell = df[df["StockTurnover"]<1].groupby("VendorName")[["StockTurnover"]].mean().sort_values("StockTurnover", ascending= True).head(10)
print(hell)

#7. How much capital is locked in unsold inventory per vendor contribution the most to it?

df["UnsoldInventory"] = (df["TotalPurchaseQuantity"] - df["TotalSalesQuantity"])*df["PurchasePrice"]
print("Total Unsold Capital: ", df["UnsoldInventory"].sum())

#average capital locked per vendor
inventory_value_per_vandor = df.groupby("VendorName")["UnsoldInventory"].sum().reset_index()

#sort vendors with the highest locked capital
inventory_value_per_vandor = inventory_value_per_vandor.sort_values(by="UnsoldInventory", ascending=False)
inventory_value_per_vandor["UnsoldInventory"] = inventory_value_per_vandor["UnsoldInventory"]
print(inventory_value_per_vandor.head(10))


#8. What is the 95% confidence for profit margins of top-performing and low-performing vendors
top_threshold = df["TotalSalesDollars"].quantile(0.75)
low_threshold = df["TotalSalesDollars"].quantile(0.25)

top_vendor = df[df["TotalSalesDollars"] >= top_threshold]["ProfitMargin"].dropna()
low_vendor = df[df["TotalSalesDollars"] <= low_threshold]["ProfitMargin"].dropna()

def confidence_interval(data, confidence = 0.95):
    mean_val = np.mean(data)
    std_err = np.std(data, ddof=1) / np.sqrt(len(data))
    t_critical = stats.t.ppf((1+confidence)/2, df = len(data)-1)
    margin_of_error = t_critical*std_err
    return mean_val, mean_val - margin_of_error, mean_val + margin_of_error

top_mean, top_lower,top_upper = confidence_interval(top_vendor)
low_mean, low_lower, low_upper = confidence_interval(low_vendor)

print(f"Top vendor 95% CI: ({top_lower: .2f},{top_upper: .2f},Mean: {top_mean: .2f} )")
print(f"low vendor 95% CI: ({low_lower: .2f},{low_upper: .2f},Mean: {low_mean: .2f} )")
plt.figure(figsize=(12,6))

#Top vendors plot
sns.histplot(top_vendor, kde=True, color="blue", bins=30, alpha=0.5, label = "Top Vendors")
plt.axvline(top_lower, color = "blue", linestyle = "--", label= f"Top Lower: {top_lower: .2f}")
plt.axvline(top_upper, color = "blue", linestyle = "--", label= f"Top upper: {top_upper: .2f}")
plt.axvline(top_mean, color = "blue", linestyle = "--", label= f"Top mean: {top_mean: .2f}")

#low vendors plot
sns.histplot(low_vendor, kde=True, color="red", bins=30, alpha=0.5, label = "low Vendors")
plt.axvline(low_lower, color = "red", linestyle = "--", label= f"low Lower: {low_lower: .2f}")
plt.axvline(low_upper, color = "red", linestyle = "--", label= f"low upper: {low_upper: .2f}")
plt.axvline(low_mean, color = "red", linestyle = "--", label= f"low mean: {low_mean: .2f}")

#finalize plot
plt.title("Confidence Interval Comprison: Top vs. Low vendors(Profit Margin)")
plt.xlabel("Profit Margin(%)")
plt.ylabel("Frequency")
plt.legend()
plt.grid(True)
plt.show()