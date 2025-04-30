import json
import time
import paho.mqtt.client as mqtt
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
from collections import deque

# Create buffers to hold the last 50 data points
max_points = 50
temperature_data = deque(maxlen=max_points)
current_data = deque(maxlen=max_points)
voltage_data = deque(maxlen=max_points)
proximity_data = deque(maxlen=max_points)
timestamps = deque(maxlen=max_points)

# MQTT callback
def on_message(client, userdata, msg):
    try:
        data = json.loads(msg.payload.decode())
        print("Received:", data)

        timestamps.append(time.strftime('%H:%M:%S', time.localtime(data['timestamp'])))
        temperature_data.append(data['temperature'])
        current_data.append(data['current'])
        voltage_data.append(data['voltage'])
        proximity_data.append(data['proximity'])

    except Exception as e:
        print("Error parsing data:", e)

# MQTT setup
client = mqtt.Client()
client.connect("localhost", 1883, 60)
client.subscribe("ev/sensors")
client.on_message = on_message
client.loop_start()

# Matplotlib setup
fig, axs = plt.subplots(4, 1, figsize=(10, 8))
plt.tight_layout(pad=3)

def animate(i):
    for ax in axs:
        ax.clear()

    axs[0].plot(timestamps, temperature_data, color='red')
    axs[0].set_title("Temperature (°C)")

    axs[1].plot(timestamps, current_data, color='blue')
    axs[1].set_title("Current (A)")

    axs[2].plot(timestamps, voltage_data, color='green')
    axs[2].set_title("Voltage (V)")

    axs[3].plot(timestamps, proximity_data, color='purple')
    axs[3].set_title("Proximity (mm)")

    for ax in axs:
        ax.tick_params(axis='x', rotation=45)
        ax.grid(True)

# Animate the plot every 1000 ms
ani = FuncAnimation(fig, animate, interval=1000)

print("📊 Live plotting started...")
plt.show()
