import os
import pandas as pd
import cdsapi

START_YEAR = 2015
END_YEAR = 2024

VARIABLES = [
    'mean_sea_level_pressure',
    'surface_solar_radiation_downwards',
    '10m_u_component_of_wind',
    '10m_v_component_of_wind'
]

df = pd.read_csv("era5_district_grid_bounds.csv")
c = cdsapi.Client()

os.makedirs("data", exist_ok=True)

for _, row in df.iterrows():
    district = row["district"]
    print(f"\n=== {district} ===")

    district_dir = os.path.join("data", district)
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
                district_dir, f"{district}_{year}_{month:02d}.nc"
            )

            if os.path.exists(outfile):
                continue

            print(f"  → {year}-{month:02d}")

            c.retrieve(
                "reanalysis-era5-single-levels",
                {
                    "product_type": "reanalysis",
                    "variable": VARIABLES,
                    "year": str(year),
                    "month": f"{month:02d}",
                    "day": [f"{d:02d}" for d in range(1, 32)],
                    "time": [f"{h:02d}:00" for h in range(24)],
                    "area": area,
                    "format": "netcdf"
                },
                outfile
            )
