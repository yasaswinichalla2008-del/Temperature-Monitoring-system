
import serial
import csv
import os
from datetime import datetime

ser = serial.Serial("COM13", 115200, timeout=2)

file_exists = os.path.exists("live_temperature_data.csv")

with open("live_temperature_data.csv", "a", newline="") as file:
    writer = csv.writer(file)

    if not file_exists or os.path.getsize("live_temperature_data.csv") == 0:
        writer.writerow(["timestamp", "adc_value", "temperature_C"])

    print("Recording started. Press Ctrl+C to stop.")

    try:
        while True:
            line = ser.readline().decode(
                "utf-8", errors="ignore"
            ).strip()

            if "ADC=" not in line or "Temp=" not in line:
                continue

            try:
                adc = int(line.split("ADC=")[1].split()[0])
                temp = float(line.split("Temp=")[1].split()[0])

                timestamp = datetime.now().isoformat(
                    timespec="seconds"
                )

                writer.writerow([timestamp, adc, temp])
                file.flush()

                print(f"{timestamp} | ADC={adc} | Temp={temp:.2f} C")

            except (ValueError, IndexError):
                continue

    except KeyboardInterrupt:
        print("\nRecording stopped.")

    finally:
        ser.close()
        print("Saved to live_temperature_data.csv")
