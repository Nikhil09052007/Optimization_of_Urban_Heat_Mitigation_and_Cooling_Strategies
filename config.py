# config.py
# Central configuration — imported by every script in scripts/

import os

# ── Root is always the parent of this file ──────────────────────────────────
ROOT_DIR     = os.path.dirname(os.path.abspath(__file__))
DATA_DIR     = os.path.join(ROOT_DIR, 'data', 'raw')
LANDSAT_DIR  = os.path.join(DATA_DIR, 'landsat')
SENTINEL_DIR = os.path.join(DATA_DIR, 'sentinel2')
ERA5_DIR     = os.path.join(DATA_DIR, 'era5')
OSM_DIR      = os.path.join(DATA_DIR, 'osm')
GHSL_DIR     = os.path.join(DATA_DIR, 'ghsl')
LOGS_DIR     = os.path.join(DATA_DIR, 'logs')
OUTPUTS_DIR  = os.path.join(ROOT_DIR, 'outputs')

# ── GEE settings ────────────────────────────────────────────────────────────
GEE_PROJECT   = 'urban-heat-project-499314'
GDRIVE_FOLDER = 'urban_heat_delhi_landsat'

# ── Delhi NCR AOI ────────────────────────────────────────────────────────────
# Bounding box: [west, south, east, north]
DELHI_BBOX = [76.84, 28.40, 77.58, 28.88]

# ── Time range ───────────────────────────────────────────────────────────────
START_YEAR = 2019
END_YEAR   = 2023
MONTHS     = [4, 5, 6, 7, 8, 9]   # April–September (peak heat)

# ── Export settings ──────────────────────────────────────────────────────────
SCALE                 = 30           # metres — Landsat native resolution
CRS                   = 'EPSG:32643' # UTM Zone 43N — correct for Delhi NCR
MAX_PIXELS            = 1e10
CLOUD_COVER_THRESHOLD = 20           # % — relaxed to 40 automatically if needed
