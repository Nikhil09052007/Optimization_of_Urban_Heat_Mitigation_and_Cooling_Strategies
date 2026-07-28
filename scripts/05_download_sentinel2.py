# 05_download_sentinel2.py
# STATUS: SUBMITTED TO GEE — check if files are in Google Drive already
# GDrive folder: urban_heat_delhi_sentinel2
# Files expected:
#   S2_Delhi_2019.tif → data/raw/sentinel2/
#   S2_Delhi_2020.tif → data/raw/sentinel2/
#   S2_Delhi_2021.tif → data/raw/sentinel2/
#   S2_Delhi_2022.tif → data/raw/sentinel2/
#   S2_Delhi_2023.tif → data/raw/sentinel2/
#
# Only re-run if tasks failed or files lost from Drive

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import ee
import time
import json
from config import (GEE_PROJECT, DELHI_BBOX, LOGS_DIR,
                    START_YEAR, END_YEAR, CRS, MAX_PIXELS)

ee.Initialize(project=GEE_PROJECT)

AOI           = ee.Geometry.Rectangle(DELHI_BBOX)
GDRIVE_FOLDER = 'urban_heat_delhi_sentinel2'

def mask_s2_clouds(image):
    """Cloud mask using Scene Classification Layer (SCL)."""
    scl = image.select('SCL')
    good = (scl.eq(4)            # vegetation
              .Or(scl.eq(5))     # bare soil
              .Or(scl.eq(6))     # water
              .Or(scl.eq(7))     # unclassified
              .Or(scl.eq(11)))   # snow/ice
    return image.updateMask(good)

def add_indices(image):
    """Scale bands and compute spectral indices."""
    scaled = image.select(['B2','B3','B4','B8','B11','B12']) \
                  .divide(10000).toFloat()

    ndvi  = scaled.normalizedDifference(['B8','B4']).rename('NDVI').toFloat()
    ndbi  = scaled.normalizedDifference(['B11','B8']).rename('NDBI').toFloat()
    mndwi = scaled.normalizedDifference(['B3','B11']).rename('MNDWI').toFloat()
    bsi   = scaled.expression(
        '((SWIR + RED) - (NIR + BLUE)) / ((SWIR + RED) + (NIR + BLUE))',
        {
            'SWIR': scaled.select('B11'),
            'RED':  scaled.select('B4'),
            'NIR':  scaled.select('B8'),
            'BLUE': scaled.select('B2')
        }
    ).rename('BSI').toFloat()

    return (scaled
            .addBands(ndvi)
            .addBands(ndbi)
            .addBands(mndwi)
            .addBands(bsi)
            .set('system:time_start', image.get('system:time_start')))

task_ids = {}

for year in range(START_YEAR, END_YEAR + 1):
    collection = (ee.ImageCollection('COPERNICUS/S2_SR_HARMONIZED')
        .filterBounds(AOI)
        .filter(ee.Filter.calendarRange(year, year, 'year'))
        .filter(ee.Filter.calendarRange(6, 8, 'month'))
        .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', 15))
        .map(mask_s2_clouds)
        .map(add_indices))

    count = collection.size().getInfo()
    print(f"\n{year}: {count} scenes found")

    if count == 0:
        print(f"  WARNING: Relaxing cloud filter to 30%...")
        collection = (ee.ImageCollection('COPERNICUS/S2_SR_HARMONIZED')
            .filterBounds(AOI)
            .filter(ee.Filter.calendarRange(year, year, 'year'))
            .filter(ee.Filter.calendarRange(6, 8, 'month'))
            .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', 30))
            .map(mask_s2_clouds)
            .map(add_indices))

    composite = collection.median().clip(AOI).toFloat()
    bands     = ['B2','B3','B4','B8','B11','B12','NDVI','NDBI','MNDWI','BSI']

    task = ee.batch.Export.image.toDrive(
        image          = composite.select(bands),
        description    = f'S2_Delhi_{year}',
        folder         = GDRIVE_FOLDER,
        fileNamePrefix = f'S2_Delhi_{year}',
        region         = AOI,
        scale          = 10,
        crs            = CRS,
        maxPixels      = MAX_PIXELS,
        fileFormat     = 'GeoTIFF'
    )
    task.start()
    task_ids[year] = task.id
    print(f"  Task started: {task.id}")
    time.sleep(2)

os.makedirs(LOGS_DIR, exist_ok=True)
log_file = os.path.join(LOGS_DIR, 'sentinel2_task_ids.json')
with open(log_file, 'w') as f:
    json.dump(task_ids, f, indent=2)

print(f"\nAll tasks submitted. IDs saved to: {log_file}")
print("Monitor: https://code.earthengine.google.com/tasks")
