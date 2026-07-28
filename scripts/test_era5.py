# test_era5.py
# Run after saving .cdsapirc at C:\Users\Nikhil Pandey\.cdsapirc
# Run: python scripts\test_era5.py

import cdsapi
c = cdsapi.Client()
print("✅ CDS ERA5 connected OK")
