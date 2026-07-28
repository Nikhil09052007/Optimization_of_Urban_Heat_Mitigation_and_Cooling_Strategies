# 04_verify_landsat.py
# Run after downloading all 5 .tif files from Google Drive to data/raw/landsat/
# Expected results:
#   5 files | 9 bands | CRS 32643 | LST range 29-62°C | 2446x1818px

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import rasterio
import numpy as np
from config import LANDSAT_DIR

files = sorted([f for f in os.listdir(LANDSAT_DIR) if f.endswith('.tif')])
print(f"Files found: {len(files)}\n")
print(f"{'File':<25} {'MB':>6} {'W':>5} {'H':>5} {'Bands':>5} {'CRS':>8} {'LST Min':>8} {'LST Max':>8}")
print("-" * 80)

all_ok = True
for fname in files:
    path = os.path.join(LANDSAT_DIR, fname)
    size = os.path.getsize(path) / 1e6
    with rasterio.open(path) as src:
        w, h, b = src.width, src.height, src.count
        crs     = src.crs.to_epsg()
        lst     = src.read(7, masked=True)   # band 7 = LST_Celsius
        mn, mx  = float(np.nanmin(lst)), float(np.nanmax(lst))

    status = "✅" if (b == 9 and crs == 32643 and 15 < mn < 80 and 15 < mx < 80) else "❌"
    if status == "❌":
        all_ok = False
    print(f"{status} {fname:<23} {size:>6.1f} {w:>5} {h:>5} {b:>5} {str(crs):>8} {mn:>8.1f} {mx:>8.1f}")

print()
print("Expected: 5 files | 9 bands | CRS 32643 | LST 20–65°C")
print("Overall:", "✅ ALL CHECKS PASSED" if all_ok and len(files) == 5 else "❌ ISSUES FOUND — check above")
