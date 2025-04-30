import pandas as pd
import time
from statsmodels.tsa.arima.model import ARIMA
from sklearn.metrics import mean_absolute_error, mean_squared_error
import numpy as np
import warnings
warnings.filterwarnings("ignore")

def evaluate_forecast(true_values, predictions):
    mae = mean_absolute_error(true_values, predictions)
    mse = mean_squared_error(true_values, predictions)
    rmse = np.sqrt(mse)
    mape = np.mean(np.abs((true_values - predictions) / true_values)) * 100

    print(f"📊 Evaluation Metrics:")
    print(f" - MAE : {mae:.4f}")
    print(f" - MSE : {mse:.4f}")
    print(f" - RMSE: {rmse:.4f}")
    print(f" - MAPE: {mape:.2f}%\n")

def predict_arima():
    while True:
        try:
            df = pd.read_csv("ev_charging_data.csv")
            df["timestamp"] = pd.to_datetime(df["timestamp"], unit='s')
            df.set_index("timestamp", inplace=True)
            ts = df["active_sessions"].resample("2T").mean().ffill()

            # Split into train and test (last 3 points for testing)
            train_ts = ts[:-3]
            test_ts = ts[-3:]

            model = ARIMA(train_ts, order=(2, 1, 2))
            model_fit = model.fit()
            forecast = model_fit.forecast(steps=3)

            print(f"🔮 Next Demand Prediction: {forecast.tolist()}")

            # Evaluation
            evaluate_forecast(test_ts.values, forecast.values)

            # Optional: write to file or MQTT
            forecast_df = pd.DataFrame(forecast)
            forecast_df.columns = ["forecast"]
            forecast_df.to_csv("realtime_forecast.csv")
        except Exception as e:
            print("ARIMA Prediction Error:", e)

        time.sleep(10)

if __name__ == "__main__":
    predict_arima()
