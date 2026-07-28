# 06_verify_sentinel2.py
# Run after downloading all 5 S2 .tif files from Google Drive to data/raw/sentinel2/
# Expected: 5 files | 10 bands | CRS 32643 | NDVI range -0.2 to 0.8

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import rasterio
import numpy as np
from config import SENTINEL_DIR

files = sorted([f for f in os.listdir(SENTINEL_DIR) if f.endswith('.tif')])
print(f"Files found: {len(files)}\n")
print(f"{'File':<25} {'MB':>6} {'W':>6} {'H':>6} {'Bands':>5} {'CRS':>8} {'NDVI Min':>9} {'NDVI Max':>9}")
print("-" * 85)

all_ok = True
for fname in files:
    path = os.path.join(SENTINEL_DIR, fname)
    size = os.path.getsize(path) / 1e6
    with rasterio.open(path) as src:
        w, h, b = src.width, src.height, src.count
        crs     = src.crs.to_epsg()
        ndvi    = src.read(7, masked=True)   # band 7 = NDVI
        mn, mx  = float(np.nanmin(ndvi)), float(np.nanmax(ndvi))

    status = "✅" if (b == 10 and crs == 32643) else "❌"
    if status == "❌":
        all_ok = False
    print(f"{status} {fname:<23} {size:>6.1f} {w:>6} {h:>6} {b:>5} {str(crs):>8} {mn:>9.3f} {mx:>9.3f}")

print()
print("Expected: 5 files | 10 bands | CRS 32643 | NDVI -0.2 to 0.8")
print("Overall:", "✅ ALL CHECKS PASSED" if all_ok and len(files) == 5 else "❌ ISSUES FOUND — check above")
