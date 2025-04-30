import pandas as pd
import numpy as np
import time
import joblib
from tensorflow.keras.models import load_model

# Load model and scaler
model = load_model("lstm_model.h5")
scaler = joblib.load("scaler.save")

print("🧠 Real-time LSTM predictor started...\n")

seq_len = 20
forecast_horizon = 5

while True:
    try:
        df = pd.read_csv("ev_charging_data.csv")
        df["timestamp"] = pd.to_datetime(df["timestamp"], unit='s')
        df.set_index("timestamp", inplace=True)
        ts = df["active_sessions"].resample("2T").mean().ffill()

        # Use latest seq_len values
        if len(ts) > seq_len:
            recent = ts[-seq_len:].values.reshape(-1, 1)
            scaled_recent = scaler.transform(recent)
            input_seq = np.expand_dims(scaled_recent, axis=0)

            # Predict
            prediction = model.predict(input_seq)
            predicted_scaled = prediction[0].reshape(-1, 1)
            predicted_real = scaler.inverse_transform(predicted_scaled)

            print(f"🔮 Forecast @ {pd.Timestamp.now()}: {predicted_real.flatten().round(2)}\n")

        else:
            print("⚠️ Not enough data yet for LSTM (need at least 20 rows).")

    except Exception as e:
        print("❌ Error during prediction:", e)

    time.sleep(30)
