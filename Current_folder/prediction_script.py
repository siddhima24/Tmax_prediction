import numpy as np
import pickle
from tensorflow.keras.models import load_model
from fetcher_script import fetch_paper_style_inputs

district = input("Enter district: ").lower()
date = input("Enter prediction date (YYYY-MM-DD): ")

model = load_model(f"models/{district}_model.keras")

with open(f"scalers/{district}_scalers.pkl","rb") as f:
    scalers = pickle.load(f)

scaler_X = scalers["scaler_X"]
scaler_y = scalers["scaler_y"]

df = fetch_paper_style_inputs(date, district.capitalize())
df = df.sort_values("date")

features = df[[
    "msl","wind_speed","solar_radiation",
    "relative_humidity","rainfall","month"
]]

last_4_days = features.head(4)
scaled = scaler_X.transform(last_4_days)

X_input = np.expand_dims(scaled, axis=0)  # shape (1,4,6)

pred_scaled = model.predict(X_input)
pred_tmax = scaler_y.inverse_transform(pred_scaled)[0]

print("\n15-Day Tmax Forecast:")
for i, temp in enumerate(pred_tmax,1):
    print(f"Day {i}: {temp:.2f} °C")
