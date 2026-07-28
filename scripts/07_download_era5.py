# 07_download_era5.py
# STATUS: READY TO RUN — requires .cdsapirc at C:\Users\Nikhil Pandey\.cdsapirc
#
# .cdsapirc format (save at C:\Users\Nikhil Pandey\.cdsapirc):
#   url: https://cds.climate.copernicus.eu/api
#   key: YOUR-KEY-FROM-copernicus.eu/how-to-api
#
# Run: python scripts\07_download_era5.py

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import cdsapi
from config import ERA5_DIR, START_YEAR, END_YEAR

os.makedirs(ERA5_DIR, exist_ok=True)

c = cdsapi.Client()

for year in range(START_YEAR, END_YEAR + 1):
    for month in ['04','05','06','07','08','09']:   # April–September
        out_file = os.path.join(ERA5_DIR, f'ERA5_{year}_{month}.nc')

        if os.path.exists(out_file):
            print(f"Already exists, skipping: ERA5_{year}_{month}.nc")
            continue

        print(f"Downloading ERA5_{year}_{month}.nc ...")
        c.retrieve(
            'reanalysis-era5-land',
            {
                'variable': [
                    '2m_temperature',
                    '2m_dewpoint_temperature',
                    '10m_u_component_of_wind',
                    '10m_v_component_of_wind',
                    'surface_net_solar_radiation',
                    'total_precipitation',
                    'soil_temperature_level_1',
                ],
                'year':  str(year),
                'month': month,
                'day':   [str(d).zfill(2) for d in range(1, 32)],
                'time':  ['00:00','03:00','06:00','09:00',
                          '12:00','15:00','18:00','21:00'],
                'area':  [28.88, 76.84, 28.40, 77.58],  # N, W, S, E — Delhi NCR
                'format': 'netcdf',
            },
            out_file
        )
        print(f"  Saved: {out_file}")

print("\nERA5 download complete.")
print(f"Files in: {ERA5_DIR}")
