import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense
import joblib

# Load and preprocess data
df = pd.read_csv("ev_charging_data.csv")
df["timestamp"] = pd.to_datetime(df["timestamp"], unit='s')
df.set_index("timestamp", inplace=True)
ts = df["active_sessions"].resample("2min").mean().ffill()

# Normalize
scaler = MinMaxScaler()
scaled_ts = scaler.fit_transform(ts.values.reshape(-1, 1))

# Create sequences
seq_len = 20
forecast_horizon = 5
X, y = [], []

for i in range(seq_len, len(scaled_ts) - forecast_horizon):
    X.append(scaled_ts[i - seq_len:i])
    y.append(scaled_ts[i:i + forecast_horizon])
X, y = np.array(X), np.array(y)

# ✅ Add a sanity check
print(f"X shape: {X.shape}, y shape: {y.shape}")
if X.shape[0] == 0:
    raise ValueError("❌ Not enough data to train LSTM. Try reducing seq_len or collecting more data.")

# Build LSTM model
model = Sequential([
    LSTM(64, activation='relu', input_shape=(X.shape[1], 1)),
    Dense(forecast_horizon)
])
model.compile(optimizer='adam', loss='mse')

# Train the model
model.fit(X, y, epochs=30, batch_size=16, validation_split=0.1)

# Save model and scaler
model.save("lstm_model.h5")
joblib.dump(scaler, "scaler.save")
