import pandas as pd
import joblib
from xgboost import XGBClassifier

# Load trained model and label encoder
model = XGBClassifier()
model.load_model("xgboost_temperature_model.json")

encoder = joblib.load("temperature_label_encoder.joblib")

# Enter a new ADC reading
adc_value = float(input("Enter ADC value: "))

# Predict temperature class
data = pd.DataFrame({"adc_value": [adc_value]})
prediction = model.predict(data).astype(int)

temperature_class = encoder.inverse_transform(prediction)[0]

print("\nPredicted temperature class:", temperature_class)

# Display result
if temperature_class == "Normal":
    print("Status: Temperature is normal.")
elif temperature_class == "Warning":
    print("Status: Temperature is rising. Check the cabinet.")
else:
    print("Status: High temperature detected!")