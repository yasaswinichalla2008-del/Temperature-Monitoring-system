
import pandas as pd
import matplotlib.pyplot as plt

# Load dataset
df = pd.read_csv("temperature_dataset.csv")

print("First 5 rows:")
print(df.head())

print("\nDataset shape:", df.shape)

print("\nColumn information:")
print(df.info())

print("\nMissing values:")
print(df.isnull().sum())

print("\nDuplicate rows:", df.duplicated().sum())

print("\nTemperature statistics:")
print(df["temperature_C"].describe())

print("\nMinimum temperature:", df["temperature_C"].min())
print("Maximum temperature:", df["temperature_C"].max())

# Demo temperature classes
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

print("\nTemperature class counts:")
print(df["temperature_class"].value_counts())

# Temperature over time
plt.figure(figsize=(10, 5))
plt.plot(df["timestamp_sec"], df["temperature_C"], marker=".")
plt.xlabel("Time (seconds)")
plt.ylabel("Temperature (°C)")
plt.title("Temperature Readings Over Time")
plt.grid(True)
plt.tight_layout()
plt.savefig("temperature_readings.png")
plt.show()

# Temperature distribution
plt.figure(figsize=(8, 5))
plt.hist(df["temperature_C"], bins=15, edgecolor="black")
plt.xlabel("Temperature (°C)")
plt.ylabel("Frequency")
plt.title("Temperature Distribution")
plt.tight_layout()
plt.savefig("temperature_distribution.png")
plt.show()
