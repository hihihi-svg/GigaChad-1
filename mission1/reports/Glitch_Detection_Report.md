
# Mission 1 – Glitch Detection and Data Quality Report

## 1. Objective

The objective of glitch detection is to identify invalid sensor readings, suspicious records, statistical outliers and inconsistencies in the Team 11 battery-life dataset before model training.

The investigation was performed without modifying or deleting any original dataset records.

## 2. Dataset Overview

| Property | Value |
|---|---:|
| Dataset | team_11_train.csv |
| Total records | 2,000 |
| Total features | 5 |
| Target variable | days_left |
| Total columns | 6 |

## 3. Data Quality Checks

### 3.1 Missing Values

All six columns were checked for missing values.

**Result:** No missing values were detected.

### 3.2 Duplicate Records

The dataset was checked for completely duplicated rows.

**Result:** Zero duplicate records were detected.

## 4. Rule-Based Glitch Detection

The following rules were applied:

| Condition | Suspicious records |
|---|---:|
| Battery voltage = 0 | 12 |
| Temperature = -127°C | 5 |
| Wi-Fi RSSI = 0 | 7 |
| Negative battery voltage | 0 |
| Negative rings per day | 0 |
| Negative device age | 0 |
| Negative remaining days | 0 |

A total of **24 unique records** were flagged by rule-based detection.

## 5. Statistical Outlier Detection

### 5.1 Interquartile Range (IQR)

The IQR method was applied to all input features and the target variable.

| Variable | IQR outliers |
|---|---:|
| battery_v | 12 |
| temp_c | 15 |
| rings_per_day | 72 |
| wifi_rssi_dbm | 7 |
| age_months | 0 |
| days_left | 14 |

### 5.2 Z-Score Analysis

A threshold of absolute Z-score greater than 3 was used.

| Variable | Potential outliers |
|---|---:|
| battery_v | 12 |
| temp_c | 5 |
| rings_per_day | 40 |
| wifi_rssi_dbm | 7 |
| age_months | 0 |
| days_left | 10 |

## 6. Detailed Investigation

### 6.1 Temperature Sensor Readings

Five records contained a temperature reading of -127°C.

This value is suspicious and may represent a sensor error or invalid sentinel reading.

Ten additional records had temperatures between 8°C and 8.2°C. These were not automatically classified as glitches because they may represent legitimate environmental conditions.

### 6.2 Battery Voltage

Twelve records contained zero battery voltage.

Among these, nine records also reported more than 30 days of remaining battery life. This inconsistency requires further investigation.

### 6.3 Wi-Fi RSSI

Seven records contained a Wi-Fi RSSI value of zero.

Since RSSI values are generally represented as negative dBm values, these readings were flagged for investigation.

### 6.4 High Usage Readings

Seventy-two records had more than 21.5 rings per day.

These readings were statistically unusual but may represent legitimate high device usage.

### 6.5 Target Variable Outliers

Fourteen records were identified as IQR outliers in `days_left`.

All fourteen had unusually high remaining battery-life values. These were kept separate from input sensor anomalies.

## 7. Combined Anomaly Analysis

The different input anomaly detection methods were combined.

| Detection method | Records flagged |
|---|---:|
| Rule-based checks | 24 |
| Input IQR checks | 105 |
| Input Z-score checks | 63 |
| Unique records flagged by at least one input check | 105 |

The 105 records represent the union of flagged input records, not 105 confirmed glitches.

## 8. Final Findings

The investigation identified:

- No missing values.
- No duplicate records.
- 24 rule-based suspicious records.
- Five highly suspicious temperature readings of -127°C.
- Twelve zero battery-voltage readings.
- Seven zero Wi-Fi RSSI readings.
- Statistical outliers in usage and target values.

## 9. Conclusion

The dataset is structurally complete, with no missing or duplicate records. However, several sensor readings require further investigation.

Rule-based and statistical techniques were used together to identify potentially invalid readings and unusual observations.

No records were removed or modified during this investigation. The original dataset was preserved for subsequent preprocessing and model development.
