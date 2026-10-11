import pandas as pd

# 1. Load the original dataset
df = pd.read_csv("temperature_dataset.csv", sep=None, engine="python")

# 2. Clean column names
df.columns = df.columns.str.strip()

print("Original columns:", df.columns.tolist())

# 3. Check required columns
required_columns = [
    "timestamp_sec",
    "adc_value",
    "temperature_C"
]

if not set(required_columns).issubset(df.columns):
    raise ValueError(
        "Dataset is missing required columns. "
        "Check the column names in temperature_dataset.csv."
    )

# 4. Convert columns to numeric values
for col in required_columns:
    df[col] = pd.to_numeric(df[col], errors="coerce")

# 5. Remove missing and duplicate rows
df = df.dropna(subset=required_columns)
df = df.drop_duplicates()

# 6. Remove invalid sensor readings
df = df[
    (df["adc_value"] > 0) &
    (df["adc_value"] <= 4095) &
    (df["temperature_C"] >= 0) &
    (df["temperature_C"] <= 80)
].copy()

# 7. Assign temperature classes
def classify_temperature(temp):
    if temp < 30:
        return "Normal"
    elif temp < 35:
        return "Warning"
    else:
        return "High"

df["temperature_class"] = df["temperature_C"].apply(
    classify_temperature
)

# 8. Save the processed dataset
df.to_csv("processed_temperature_dataset.csv", index=False)

# 9. Display results
print("\nPreprocessing completed!")
print("Total valid rows:", len(df))

print("\nProcessed columns:")
print(df.columns.tolist())

print("\nTemperature class distribution:")
print(
    df["temperature_class"]
    .value_counts()
    .reindex(["Normal", "Warning", "High"], fill_value=0)
)

print("\nFirst five processed rows:")
print(df.head())

print("\nSaved as processed_temperature_dataset.csv")