import numpy as np
import random
import json
import time
import csv
import uuid
import os
import paho.mqtt.client as mqtt

# Kalman Filter class remains the same
class KalmanFilter:
    def __init__(self, process_variance=1e-5, estimated_measurement_variance=0.1**2):
        self.process_variance = process_variance
        self.estimated_measurement_variance = estimated_measurement_variance
        self.posteri_estimate = 0.0
        self.posteri_error_estimate = 1.0

    def update(self, measurement):
        priori_estimate = self.posteri_estimate
        priori_error_estimate = self.posteri_error_estimate + self.process_variance

        blending_factor = priori_error_estimate / (priori_error_estimate + self.estimated_measurement_variance)
        self.posteri_estimate = priori_estimate + blending_factor * (measurement - priori_estimate)
        self.posteri_error_estimate = (1 - blending_factor) * priori_error_estimate

        return self.posteri_estimate

# MQTT Setup
MQTT_BROKER = "localhost"
MQTT_PORT = 1883
MQTT_TOPIC = "ev/charging_station"

client = mqtt.Client()
client.connect(MQTT_BROKER, MQTT_PORT, 60)

# CSV Setup
CSV_FILE = "ev_charging_data.csv"
file_exists = os.path.isfile(CSV_FILE)
csv_fields = ["timestamp", "station_id", "session_id", "ev_id", "temperature", "current", "voltage", "power_kw",
              "energy_kwh", "proximity", "active_sessions", "is_charging"]

with open(CSV_FILE, mode='a', newline='') as file:
    writer = csv.DictWriter(file, fieldnames=csv_fields)
    if not file_exists:
        writer.writeheader()

# Kalman Filters
kf_temp = KalmanFilter()
kf_current = KalmanFilter()
kf_voltage = KalmanFilter()
kf_proximity = KalmanFilter()

print("✅ Publishing charger data to MQTT broker...")

active_sessions = random.randint(0, 5)

while True:
    timestamp = time.time()
    station_id = "CS001"  # Charging Station ID
    session_id = str(uuid.uuid4())
    ev_id = f"EV-{random.randint(1000, 9999)}"

    # Simulate raw sensor readings with noise
    temp = random.uniform(25, 45) + np.random.normal(0, 1)
    current = random.uniform(10, 50) + np.random.normal(0, 1)  # Amps
    voltage = random.uniform(380, 420) + np.random.normal(0, 2)  # Volts
    proximity = random.uniform(0, 200) + np.random.normal(0, 5)  # mm

    # Apply Kalman Filters
    temp_f = round(kf_temp.update(temp), 2)
    current_f = round(kf_current.update(current), 2)
    voltage_f = round(kf_voltage.update(voltage), 2)
    proximity_f = round(kf_proximity.update(proximity), 2)

    # Calculate power (P = V * I), and estimate energy if charging
    power_kw = round((voltage_f * current_f) / 1000, 2)
    energy_kwh = round(power_kw * (2 / 60), 3)  # Simulate 2-minute charging slice

    # Randomly decide if this is an active session
    is_charging = random.choice([0, 1])
    active_sessions += is_charging - random.choice([0, 1])

    # Format data
    payload = {
        "timestamp": timestamp,
        "station_id": station_id,
        "session_id": session_id,
        "ev_id": ev_id,
        "temperature": temp_f,
        "current": current_f,
        "voltage": voltage_f,
        "power_kw": power_kw,
        "energy_kwh": energy_kwh,
        "proximity": proximity_f,
        "active_sessions": max(0, active_sessions),
        "is_charging": is_charging
    }

    # Save to CSV
    with open(CSV_FILE, mode='a', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=csv_fields)
        writer.writerow(payload)

    # Publish via MQTT
    client.publish(MQTT_TOPIC, json.dumps(payload))
    print(f"📤 Published: {json.dumps(payload)}")

    time.sleep(2)
