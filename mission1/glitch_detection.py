
import pandas as pd
import numpy as np
from pathlib import Path

# --------------------------------------------------
# 1. LOAD DATASET
# --------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_PATH = BASE_DIR / "data" / "team_11_train.csv"

df = pd.read_csv(DATA_PATH)

features = [
    "battery_v",
    "temp_c",
    "rings_per_day",
    "wifi_rssi_dbm",
    "age_months"
]

target = "days_left"

print("\n" + "=" * 65)
print("       TEAM 11 - GLITCH DETECTION AND DATA QUALITY AUDIT")
print("=" * 65)

print(f"\nDataset shape: {df.shape}")
print(f"Total records: {len(df)}")


# --------------------------------------------------
# 2. MISSING VALUE DETECTION
# --------------------------------------------------

print("\n\n[1] MISSING VALUE ANALYSIS")
print("-" * 45)

print(df.isnull().sum())

print("Total missing values:", df.isnull().sum().sum())


# --------------------------------------------------
# 3. DUPLICATE DETECTION
# --------------------------------------------------

print("\n\n[2] DUPLICATE RECORD DETECTION")
print("-" * 45)

duplicates = df.duplicated()

print("Duplicate records:", duplicates.sum())


# --------------------------------------------------
# 4. RULE-BASED GLITCH DETECTION
# --------------------------------------------------

print("\n\n[3] RULE-BASED GLITCH DETECTION")
print("-" * 45)

rule_flags = pd.DataFrame(index=df.index)

rule_flags["Zero battery voltage"] = df["battery_v"] == 0
rule_flags["Invalid temperature (-127)"] = df["temp_c"] == -127
rule_flags["Zero WiFi RSSI"] = df["wifi_rssi_dbm"] == 0
rule_flags["Negative battery voltage"] = df["battery_v"] < 0
rule_flags["Negative rings per day"] = df["rings_per_day"] < 0
rule_flags["Negative device age"] = df["age_months"] < 0
rule_flags["Negative remaining days"] = df["days_left"] < 0

for column in rule_flags.columns:
    print(f"{column}: {rule_flags[column].sum()}")

rule_suspicious = rule_flags.any(axis=1)

print("\nUnique rule-based suspicious records:",
      rule_suspicious.sum())


# --------------------------------------------------
# 5. STATISTICAL SUMMARY
# --------------------------------------------------

print("\n\n[4] STATISTICAL SUMMARY")
print("-" * 45)

print(df.describe().round(3))


# --------------------------------------------------
# 6. IQR OUTLIER DETECTION
# --------------------------------------------------

print("\n\n[5] IQR OUTLIER DETECTION")
print("-" * 45)

iqr_flags = pd.DataFrame(False, index=df.index, columns=features + [target])

for column in features + [target]:

    values = df[column].copy()

    # Exclude zero sentinel candidates from statistical
    # calculations for battery and WiFi.
    if column in ["battery_v", "wifi_rssi_dbm"]:
        values = values[values != 0]

    q1 = values.quantile(0.25)
    q3 = values.quantile(0.75)

    iqr = q3 - q1

    lower = q1 - 1.5 * iqr
    upper = q3 + 1.5 * iqr

    iqr_flags[column] = (
        (df[column] < lower) |
        (df[column] > upper)
    )

    print(
        f"{column}: {iqr_flags[column].sum()} outliers "
        f"(Lower: {lower:.3f}, Upper: {upper:.3f})"
    )


# --------------------------------------------------
# 7. Z-SCORE OUTLIER DETECTION
# --------------------------------------------------

print("\n\n[6] Z-SCORE OUTLIER DETECTION")
print("-" * 45)

zscore_flags = pd.DataFrame(False, index=df.index, columns=features + [target])

for column in features + [target]:

    values = df[column].copy()

    if column in ["battery_v", "wifi_rssi_dbm"]:
        values = values[values != 0]

    mean = values.mean()
    std = values.std()

    if std == 0:
        continue

    z_scores = (df[column] - mean) / std

    zscore_flags[column] = z_scores.abs() > 3

    print(
        f"{column}: {zscore_flags[column].sum()} "
        "potential outliers (|Z| > 3)"
    )


# --------------------------------------------------
# 8. TEMPERATURE INVESTIGATION
# --------------------------------------------------

print("\n\n[7] TEMPERATURE INVESTIGATION")
print("-" * 45)

invalid_temp = df[df["temp_c"] == -127]

print("Rows with temperature -127:")
print(invalid_temp[["temp_c", "battery_v", "days_left"]])

low_temp = df[
    (df["temp_c"] >= 8) &
    (df["temp_c"] <= 8.2)
]

print("\nRows with temperature between 8 and 8.2:")
print(low_temp[["temp_c", "battery_v", "days_left"]])


# --------------------------------------------------
# 9. HIGH USAGE INVESTIGATION
# --------------------------------------------------

print("\n\n[8] HIGH RINGS-PER-DAY INVESTIGATION")
print("-" * 45)

high_usage = df[df["rings_per_day"] > 21.5]

print("High usage records:", len(high_usage))
print("Observed usage range:",
      df["rings_per_day"].max())

print("\nHigh usage values:")
print(sorted(high_usage["rings_per_day"].unique()))


# --------------------------------------------------
# 10. CROSS-FEATURE CONSISTENCY CHECK
# --------------------------------------------------

print("\n\n[9] CROSS-FEATURE CONSISTENCY CHECK")
print("-" * 45)

zero_battery = df[df["battery_v"] == 0]

print("Total zero battery records:", len(zero_battery))

inconsistent_battery = zero_battery[
    zero_battery["days_left"] > 30
]

print("Zero battery with more than 30 days remaining:",
      len(inconsistent_battery))

print("\nSuspicious records:")
print(
    inconsistent_battery[
        ["battery_v", "temp_c", "wifi_rssi_dbm", "days_left"]
    ]
)

both_zero = df[
    (df["battery_v"] == 0) &
    (df["wifi_rssi_dbm"] == 0)
]

print("\nRecords with both battery and WiFi equal to zero:",
      len(both_zero))


# --------------------------------------------------
# 11. TARGET OUTLIER INVESTIGATION
# --------------------------------------------------

print("\n\n[10] TARGET VARIABLE INVESTIGATION")
print("-" * 45)

target_outliers = df[iqr_flags[target]]

print("Target IQR outliers:", len(target_outliers))

print("\nTarget outlier values:")
print(target_outliers[target].sort_values().to_list())


# --------------------------------------------------
# 12. COMBINED INPUT ANOMALY FLAGS
# --------------------------------------------------

print("\n\n[11] COMBINED INPUT ANOMALY ANALYSIS")
print("-" * 45)

# Statistical flags are applied only to input features.
# Target outliers are kept separate.

input_iqr = iqr_flags[features].any(axis=1)
input_zscore = zscore_flags[features].any(axis=1)

combined_input_flags = (
    rule_suspicious |
    input_iqr |
    input_zscore
)

print("Rule-based suspicious records:", rule_suspicious.sum())
print("Input IQR flagged records:", input_iqr.sum())
print("Input Z-score flagged records:", input_zscore.sum())

print("\nUnique records flagged by at least one input check:",
      combined_input_flags.sum())

print("\nSuspicious dataset row indices (0-based):")
print(df.index[combined_input_flags].to_list())


# --------------------------------------------------
# 13. FINAL SUMMARY
# --------------------------------------------------

print("\n\n" + "=" * 65)
print("                  FINAL AUDIT SUMMARY")
print("=" * 65)

print("Total records:", len(df))
print("Missing values:", df.isnull().sum().sum())
print("Duplicate records:", df.duplicated().sum())

print("\nRule-based suspicious records:",
      rule_suspicious.sum())

print("Combined input anomaly flags:",
      combined_input_flags.sum())

print("Target IQR outliers:",
      iqr_flags[target].sum())

print("\nStrong candidates for invalid readings:")
print("  Zero battery voltage:", (df["battery_v"] == 0).sum())
print("  Temperature -127:", (df["temp_c"] == -127).sum())

print("\nOther readings requiring investigation:")
print("  Zero WiFi RSSI:", (df["wifi_rssi_dbm"] == 0).sum())
print("  Low temperature (8 to 8.2):", len(low_temp))
print("  High usage (above 21.5):", len(high_usage))

print("\nIMPORTANT:")
print("Statistical outliers are not automatically glitches.")
print("No records have been deleted or modified.")
print("No output CSV files have been created.")

print("\n" + "=" * 65)
print("                 AUDIT COMPLETED")
print("=" * 65)
