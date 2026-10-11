
import serial
import csv
import time

# STM32 serial configuration
PORT = "COM13"
BAUD_RATE = 115200

# Open serial connection
ser = serial.Serial(PORT, BAUD_RATE, timeout=2)

# Allow the connection to initialize
time.sleep(2)

start_time = time.time()

try:
    with open("temperature_dataset.csv", "w", newline="") as file:
        writer = csv.writer(file)

        # CSV column names
        writer.writerow([
            "timestamp_sec",
            "adc_value",
            "temperature_C"
        ])

        print("Temperature data collection started!")
        print("Press Ctrl+C to stop.\n")

        while True:
            line = ser.readline().decode(
                "utf-8", errors="ignore"
            ).strip()

            if not line:
                continue

            try:
                # Expected format: ADC=342 Temp=27.56 C
                parts = line.replace("=", " ").split()

                adc_index = parts.index("ADC") + 1
                temp_index = parts.index("Temp") + 1

                adc_value = int(parts[adc_index])
                temperature = float(parts[temp_index])

                timestamp = round(time.time() - start_time, 2)

                # Save the reading
                writer.writerow([
                    timestamp,
                    adc_value,
                    temperature
                ])

                file.flush()

                print(
                    f"Time: {timestamp}s | "
                    f"ADC: {adc_value} | "
                    f"Temperature: {temperature:.2f} °C"
                )

            except (ValueError, IndexError):
                print("Skipping unrecognized line:", line)

except KeyboardInterrupt:
    print("\nData collection stopped by user.")

finally:
    ser.close()
    print("Serial connection closed.")
    print("Dataset saved as temperature_dataset.csv")
