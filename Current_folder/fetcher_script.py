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

def fetch_paper_style_inputs(date_str, district):
    """
    Fetches lagged daily weather data (today + previous 4 days)
    using Open-Meteo API, formatted as per the research paper.

    INPUTS:
    - date_str : string in 'YYYY-MM-DD' format
    - district : district name (must exist in DISTRICT_COORDS)

    OUTPUT:
    - Pandas DataFrame with daily values
    """

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
        f"&hourly=relativehumidity_2m,"
        f"pressure_msl,windspeed_10m,"
        f"shortwave_radiation,precipitation"
        f"&start_date={start_date}&end_date={end_date}"
        f"&timezone=Asia/Kolkata"
    )
    #call API
    for _ in range(3):
     try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        break
     except:
        print("Retrying API call...")
    data = response.json()

    # Convert hourly data to DataFrame
    hourly = pd.DataFrame(data["hourly"])
    hourly["time"] = pd.to_datetime(hourly["time"])
    hourly["date"] = hourly["time"].dt.date

    # Convert hourly → daily (paper-style aggregation)
    daily = hourly.groupby("date").agg({
        "relativehumidity_2m": "mean",  # Average humidity
        "pressure_msl": "mean",         # Mean sea-level pressure
        "windspeed_10m": "mean",        # Mean wind speed
        "shortwave_radiation": "sum",   # Total solar radiation
        "precipitation": "sum"          # Total rainfall
    }).reset_index()
    # Add month index (1–12)
    daily["month_index"] = pd.to_datetime(daily["date"]).dt.month

    daily = daily.rename(columns={
    "pressure_msl": "msl",
    "windspeed_10m": "wind_speed",
    "shortwave_radiation": "solar_radiation",
    "relativehumidity_2m": "relative_humidity",
    "precipitation": "rainfall",
    "month_index": "month"
    })

    daily = daily[[
     "date",
     "msl",
     "wind_speed",
     "solar_radiation",
     "relative_humidity",
     "rainfall",
     "month"
    ]]

    # fill missing values
    daily = daily.fillna(method="ffill").fillna(method="bfill")
    daily["date"] = pd.to_datetime(daily["date"])
    daily = daily.set_index("date")

    return daily