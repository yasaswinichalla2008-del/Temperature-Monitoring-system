import serial
import joblib
import pandas as pd
from pathlib import Path
from xgboost import XGBClassifier

# Use the folder containing this Python script.
PROJECT_DIR = Path(__file__).resolve().parent
MODEL_PATH = PROJECT_DIR / "xgboost_temperature_model.json"
ENCODER_PATH = PROJECT_DIR / "temperature_label_encoder.joblib"

# Change COM13 if Device Manager shows a different port.
SERIAL_PORT = "COM13"
BAUD_RATE = 115200

# Load your EXISTING trained model and encoder.
model = XGBClassifier()
model.load_model(str(MODEL_PATH))
encoder = joblib.load(ENCODER_PATH)

print("Trained XGBoost model loaded.")
print("Label encoder loaded.")

try:
    with serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=2) as ser:
        print(f"Connected to STM32 on {SERIAL_PORT}")
        print("Waiting for temperature readings...")
        print("Press Ctrl+C to stop.\n")

        # Allow the serial connection to settle.
        ser.reset_input_buffer()

        while True:
            line = ser.readline().decode(
                "utf-8", errors="ignore"
            ).strip()

            if not line:
                continue

            print("STM32:", line)

            try:
                fields = dict(
                    item.split("=", 1)
                    for item in line.split()
                    if "=" in item
                )

                adc_value = int(fields["ADC"])
                temperature = float(fields["Temp"])

                # The existing model expects the adc_value feature.
                data = pd.DataFrame({
                    "adc_value": [adc_value]
                })

                prediction = model.predict(data).astype(int)
                predicted_class = encoder.inverse_transform(
                    prediction
                )[0]

                print(f"Measured temperature: {temperature:.2f} °C")
                print(f"ML predicted class: {predicted_class}\n")

            except (ValueError, KeyError, IndexError) as exc:
                print(f"Could not parse/predict this line: {exc}\n")

except KeyboardInterrupt:
    print("\nMonitoring stopped.")

except serial.SerialException as exc:
    print(f"Serial connection error: {exc}")
    print("Check the COM port and close other serial monitors.")

except FileNotFoundError as exc:
    print(f"Model or encoder file not found: {exc}")
    print("Check that both saved files are in the project folder.")