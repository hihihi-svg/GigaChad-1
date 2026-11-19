
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# 1. Load your team's dataset
TEAM_NO = "11"  # Replace with your team number
df = pd.read_csv(f"data/team_{11}_train.csv")

# 2. Basic dataset information
print("\n========== DATASET OVERVIEW ==========")
print("Shape:", df.shape)
print("\nColumns:", df.columns.tolist())
print("\nFirst 5 rows:")
print(df.head())

# 3. Dataset information
print("\n========== DATA TYPES ==========")
df.info()

# 4. Missing values
print("\n========== MISSING VALUES ==========")
print(df.isnull().sum())

# 5. Statistical summary
print("\n========== STATISTICAL SUMMARY ==========")
print(df.describe())

# 6. Duplicate rows
print("\nDuplicate rows:", df.duplicated().sum())

# 7. Histograms of all columns
df.hist(figsize=(14, 10), bins=30, edgecolor="black")
plt.suptitle("Distribution of Dataset Features")
plt.tight_layout()
plt.savefig("histograms.png")
plt.show()

# 8. Input features vs target
features = [
    "battery_v",
    "temp_c",
    "rings_per_day",
    "wifi_rssi_dbm",
    "age_months"
]

for feature in features:
    plt.figure(figsize=(7, 4))
    plt.scatter(df[feature], df["days_left"], alpha=0.5)
    plt.xlabel(feature)
    plt.ylabel("Days Left")
    plt.title(f"{feature} vs Days Left")
    plt.grid(alpha=0.3)
    plt.tight_layout()
    plt.savefig(f"{feature}_vs_days_left.png")
    plt.show()

# 9. Correlation matrix
print("\n========== CORRELATION WITH DAYS_LEFT ==========")
print(df.corr(numeric_only=True)["days_left"].sort_values(ascending=False))

# 10. Correlation heatmap using Matplotlib
corr = df.corr(numeric_only=True)

plt.figure(figsize=(9, 7))
plt.imshow(corr, cmap="coolwarm", aspect="auto", vmin=-1, vmax=1)
plt.colorbar(label="Correlation")
plt.xticks(range(len(corr.columns)), corr.columns, rotation=45)
plt.yticks(range(len(corr.columns)), corr.columns)
plt.title("Feature Correlation Heatmap")

for i in range(len(corr.columns)):
    for j in range(len(corr.columns)):
        plt.text(j, i, f"{corr.iloc[i, j]:.2f}",
                 ha="center", va="center", fontsize=8)

plt.tight_layout()
plt.savefig("correlation_heatmap.png")
plt.show()

print("\nEDA completed successfully!")
