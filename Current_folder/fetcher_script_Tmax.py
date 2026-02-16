import requests
import pandas as pd
from datetime import datetime, timedelta, date

DISTRICT_COORDS = {
    "Beed": {"lat": 18.9901, "lon": 75.7531},
    "Chhatrapati Sambhajinagar": {"lat": 19.8762, "lon": 75.3433},
    "Dhule": {"lat": 20.9042, "lon": 74.7749},
    "Jalgaon": {"lat": 21.0077, "lon": 75.5626},
    "Jalna": {"lat": 19.8410, "lon": 75.8864},
    "Wardha": {"lat": 20.7453, "lon": 78.6022},
    "Yavatmal": {"lat": 20.3899, "lon": 78.1307}
}

# -----------------------------
# MAIN FUNCTION
# -----------------------------
def fetch_tmax(date_str, district):

    # Check if district exists
    if district not in DISTRICT_COORDS:
        raise ValueError(
            f"District '{district}' not found.\n"
            f"Available districts: {list(DISTRICT_COORDS.keys())}"
        )

    # Get latitude and longitude
    lat = DISTRICT_COORDS[district]["lat"]
    lon = DISTRICT_COORDS[district]["lon"]

    # Convert date string to date object
    target_date = datetime.strptime(date_str, "%Y-%m-%d").date()

    # We need previous 4 days + today
    start_date = target_date - timedelta(days=4)
    end_date = target_date

    # Get today's actual date
    today_real = date.today()

    # Decide which Open-Meteo API to use
    # Historical data → Archive API
    # Recent / future data → Forecast API
    if end_date < today_real - timedelta(days=2):
        base_url = "https://archive-api.open-meteo.com/v1/archive"
    else:
        base_url = "https://api.open-meteo.com/v1/forecast"

    # Build API URL
    url = (
        f"{base_url}?"
        f"latitude={lat}&longitude={lon}"
        f"&hourly=temperature_2m,"
        f"&start_date={start_date}&end_date={end_date}"
        f"&timezone=Asia/Kolkata"
    )

    # Call API
    response = requests.get(url)
    response.raise_for_status()
    data = response.json()

    # Convert hourly data to DataFrame
    hourly = pd.DataFrame(data["hourly"])
    hourly["time"] = pd.to_datetime(hourly["time"])
    hourly["date"] = hourly["time"].dt.date

    # Convert hourly → daily (paper-style aggregation)
    daily = hourly.groupby("date").agg({
        "temperature_2m": "max",        # Daily maximum temperature
    }).reset_index()

    # Add month index (1–12)
    daily["month_index"] = pd.to_datetime(daily["date"]).dt.month

    daily = daily.rename(columns={
    "temperature_2m": "tmax",
    "month_index": "month"
    })

    daily = daily[[
     "date",
     "tmax",
     "month"
    ]]

    # fill missing values
    daily["date"] = pd.to_datetime(daily["date"])
    daily = daily.set_index("date")

    daily = daily.ffill().bfill()

    # extract scalar Tmax value
    try:
     value = daily["tmax"].iloc[-1]
     return float(value)
    except:
     return None


    