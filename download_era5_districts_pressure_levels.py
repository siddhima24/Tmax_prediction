import os
import pandas as pd
import cdsapi

# =========================
# USER CONTROLS
# =========================
START_YEAR = 2015
END_YEAR   = 2024

# How many districts to process in THIS run
# 1  → only Beed
# 2  → Beed + next district
# None → all districts
# NUM_DISTRICTS_THIS_RUN = 1   # <-- change later

# ERA5 pressure-level settings
VARIABLE = 'relative_humidity'
PRESSURE_LEVEL = '1000'   # hPa

CSV_FILE = "era5_district_grid_bounds.csv"
DATA_DIR = "data_pressure"

# =========================
# SETUP
# =========================
df = pd.read_csv(CSV_FILE)
c = cdsapi.Client()

os.makedirs(DATA_DIR, exist_ok=True)

# =========================
# DOWNLOAD LOOP
# =========================
for idx, row in df.iterrows():

    # ---- limit districts per run
    # if NUM_DISTRICTS_THIS_RUN is not None and idx >= NUM_DISTRICTS_THIS_RUN:
    #     break

    district = row["district"]
    print(f"\n=== Processing district {idx+1}: {district} ===")

    district_dir = os.path.join(DATA_DIR, district)
    os.makedirs(district_dir, exist_ok=True)

    area = [
        row["high_lat"],
        row["low_lon"],
        row["low_lat"],
        row["high_lon"]
    ]

    for year in range(START_YEAR, END_YEAR + 1):
        for month in range(1, 13):

            outfile = os.path.join(
                district_dir,
                f"{district}_rh{PRESSURE_LEVEL}_{year}_{month:02d}.nc"
            )

            if os.path.exists(outfile):
                print(f"✔ Exists, skipping {district} {year}-{month:02d}")
                continue

            print(f"→ Downloading {district} {year}-{month:02d}")

            c.retrieve(
                "reanalysis-era5-pressure-levels",
                {
                    "product_type": "reanalysis",
                    "variable": VARIABLE,
                    "pressure_level": PRESSURE_LEVEL,
                    "year": str(year),
                    "month": f"{month:02d}",
                    "day": [f"{d:02d}" for d in range(1, 32)],
                    "time": [f"{h:02d}:00" for h in range(24)],
                    "area": area,
                    "format": "netcdf"
                },
                outfile
            )

print("\n=== PRESSURE-LEVEL DOWNLOAD RUN COMPLETE ===")
