# 10_verify_all.py
# Master verification — run at any time to see full data status
# Run: python scripts\10_verify_all.py

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import rasterio
import numpy as np
from config import LANDSAT_DIR, SENTINEL_DIR, ERA5_DIR, OSM_DIR, GHSL_DIR

print("=" * 60)
print("  URBAN HEAT DELHI — DATA STATUS REPORT")
print("=" * 60)

# ── Landsat ──────────────────────────────────────────────────
print("\n📡 LANDSAT 8 LST  (expected: 5 files, 9 bands, CRS 32643)")
l8_files = sorted([f for f in os.listdir(LANDSAT_DIR) if f.endswith('.tif')]) if os.path.exists(LANDSAT_DIR) else []
if l8_files:
    for fname in l8_files:
        path = os.path.join(LANDSAT_DIR, fname)
        with rasterio.open(path) as src:
            b   = src.count
            crs = src.crs.to_epsg()
            lst = src.read(7, masked=True)
            mn, mx = float(np.nanmin(lst)), float(np.nanmax(lst))
        ok = "✅" if b == 9 and crs == 32643 else "❌"
        print(f"  {ok} {fname}  bands={b}  CRS={crs}  LST={mn:.1f}–{mx:.1f}°C")
    print(f"  {'✅' if len(l8_files)==5 else '❌'} Total: {len(l8_files)}/5 files")
else:
    print("  ❌ No files found — download from Google Drive folder: urban_heat_delhi_landsat")

# ── Sentinel-2 ───────────────────────────────────────────────
print("\n🛰️  SENTINEL-2 LULC  (expected: 5 files, 10 bands, CRS 32643)")
s2_files = sorted([f for f in os.listdir(SENTINEL_DIR) if f.endswith('.tif')]) if os.path.exists(SENTINEL_DIR) else []
if s2_files:
    for fname in s2_files:
        path = os.path.join(SENTINEL_DIR, fname)
        with rasterio.open(path) as src:
            b   = src.count
            crs = src.crs.to_epsg()
        ok = "✅" if b == 10 and crs == 32643 else "❌"
        print(f"  {ok} {fname}  bands={b}  CRS={crs}")
    print(f"  {'✅' if len(s2_files)==5 else '❌'} Total: {len(s2_files)}/5 files")
else:
    print("  ❌ No files found — download from Google Drive folder: urban_heat_delhi_sentinel2")

# ── ERA5 ─────────────────────────────────────────────────────
print("\n🌡️  ERA5 METEOROLOGICAL  (expected: 30 NetCDF files)")
era5_files = [f for f in os.listdir(ERA5_DIR) if f.endswith('.nc')] if os.path.exists(ERA5_DIR) else []
if era5_files:
    print(f"  {'✅' if len(era5_files)==30 else '⚠️ '} {len(era5_files)}/30 files found")
else:
    print("  ❌ No files — run 07_download_era5.py after setting up .cdsapirc")

# ── OSM ──────────────────────────────────────────────────────
print("\n🗺️  OSM URBAN MORPHOLOGY  (expected: 4 GeoPackage files)")
osm_expected = ['delhi_buildings.gpkg','delhi_roads.gpkg','delhi_green.gpkg','delhi_water.gpkg']
for fname in osm_expected:
    path = os.path.join(OSM_DIR, fname)
    ok   = "✅" if os.path.exists(path) else "❌"
    print(f"  {ok} {fname}")

# ── GHSL ─────────────────────────────────────────────────────
print("\n🏙️  GHSL  (expected: 3 folders with extracted GeoTIFFs)")
ghsl_expected = ['built_surface_2020','population_2020','settlement_model_2020']
for fname in ghsl_expected:
    path = os.path.join(GHSL_DIR, fname)
    ok   = "✅" if os.path.exists(path) else "❌"
    print(f"  {ok} {fname}/")

print("\n" + "=" * 60)
print("  PHASE TRACKER")
print("=" * 60)
phases = [
    ("Phase 1", "Landsat 8 LST",        len(l8_files) == 5),
    ("Phase 2", "Sentinel-2 LULC",      len(s2_files) == 5),
    ("Phase 3", "ERA5 Meteorological",  len(era5_files) == 30),
    ("Phase 4", "OSM Morphology",       all(os.path.exists(os.path.join(OSM_DIR, f)) for f in osm_expected)),
    ("Phase 5", "GHSL",                 all(os.path.exists(os.path.join(GHSL_DIR, f)) for f in ghsl_expected)),
    ("Phase 6", "Feature Engineering",  False),
    ("Phase 7", "Hotspot Detection",    False),
    ("Phase 8", "Driver Attribution",   False),
    ("Phase 9", "PINN Model",           False),
    ("Phase 10","Scenario Optimizer",   False),
    ("Phase 11","Dashboard",            False),
]
for phase, name, done in phases:
    icon = "✅" if done else "⬜"
    print(f"  {icon} {phase} — {name}")
print()
