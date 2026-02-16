import numpy as np
import pandas as pd
import pickle
from tensorflow.keras.models import load_model
from sklearn.metrics import mean_squared_error

from fetcher_script import fetch_paper_style_inputs
from fetcher_script_Tmax import fetch_tmax


# =============================
# LOAD MODEL + SCALERS
# =============================
district = input("Enter district: ").lower()

model = load_model(f"models/{district}_model.keras")

with open(f"scalers/{district}_scalers.pkl","rb") as f:
    scalers = pickle.load(f)

scaler_X = scalers["scaler_X"]
scaler_y = scalers["scaler_y"]

print("\nModel and scalers loaded successfully\n")


# =============================
# DATE RANGE
# Forecast start dates → Jan 1–31
# Actual Tmax needed → till Feb 15
# =============================
dates = pd.date_range("2026-01-01","2026-01-31")

# storage for 15 forecast horizons
pred_horizon = [[] for _ in range(15)]
actual_horizon = [[] for _ in range(15)]


# =============================
# MAIN LOOP
# =============================
for date in dates:
    date_str = date.strftime("%Y-%m-%d")
    print("Running forecast for:", date_str)

    try:
        # fetch ERA5 + rainfall inputs
        df = fetch_paper_style_inputs(date_str, district.capitalize())
        df = df.sort_values("date")

        features = df[[
            "msl","wind_speed","solar_radiation",
            "relative_humidity","rainfall","month"
        ]]

        last_4_days = features.head(4)
        scaled = scaler_X.transform(last_4_days)
        X_input = np.expand_dims(scaled, axis=0)

        # 15-day forecast from model
        pred_scaled = model.predict(X_input, verbose=0)
        pred_15days = scaler_y.inverse_transform(pred_scaled)[0]

    except Exception as e:
        print("Input fetch failed:", e)
        continue


    # =============================
    # FETCH ACTUAL Tmax FOR NEXT 15 DAYS
    # =============================
    for i in range(15):
     target_date = date + pd.Timedelta(days=i+1)
     target_str = target_date.strftime("%Y-%m-%d")

     try:
        # fetch ACTUAL Tmax from IMD fetcher
        actual = fetch_tmax(target_str, district.capitalize())

        if actual is None:
            continue

        actual = float(actual)   # ensure scalar

     except Exception as e:
        print("Tmax fetch failed:", e)
        continue

     pred_val = float(np.squeeze(pred_15days[i]))

     pred_horizon[i].append(pred_val)
     actual_horizon[i].append(actual)


# =============================
# CALCULATE RMSE FOR EACH HORIZON
# =============================
print("\n===================================")
print(" HORIZON-WISE RMSE FOR JAN 2026 ")
print("===================================\n")

for i in range(15):
    if len(actual_horizon[i]) == 0:
        print(f"Day {i+1:02d}: No data")
        continue

    rmse = np.sqrt(mean_squared_error(actual_horizon[i], pred_horizon[i]))

    print(f"Day {i+1:02d} RMSE: {rmse:.2f} °C   (samples={len(actual_horizon[i])})")
