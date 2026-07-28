# 03_download_landsat.py
# STATUS: COMPLETED — files already in Google Drive
# Task IDs (completed):
#   2019: FEJFENSJK6YU7X3O62PS5XFR
#   2020: W5TVSK6AYKVKYHL6RP73MAFQ
#   2021: GPIQVKQZXDNJJHLNDTQQW3FU
#   2022: 2IH77ATAAXRFUWR5K5MBU7QC
#   2023: ALTJR7BGOIWCUQ7KX5YKEJZE
#
# Files to download from Google Drive folder: urban_heat_delhi_landsat
#   L8_Delhi_2019.tif → data/raw/landsat/
#   L8_Delhi_2020.tif → data/raw/landsat/
#   L8_Delhi_2021.tif → data/raw/landsat/
#   L8_Delhi_2022.tif → data/raw/landsat/
#   L8_Delhi_2023.tif → data/raw/landsat/
#
# Only re-run this script if files are lost from Drive

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import ee
import time
import json
from config import (GEE_PROJECT, DELHI_BBOX, GDRIVE_FOLDER,
                    START_YEAR, END_YEAR, LOGS_DIR,
                    SCALE, CRS, MAX_PIXELS, CLOUD_COVER_THRESHOLD)

ee.Initialize(project=GEE_PROJECT)

AOI = ee.Geometry.Rectangle(DELHI_BBOX)

def mask_clouds(image):
    qa     = image.select('QA_PIXEL')
    cloud  = qa.bitwiseAnd(1 << 3).eq(0)
    shadow = qa.bitwiseAnd(1 << 4).eq(0)
    return image.updateMask(cloud).updateMask(shadow)

def compute_lst(image):
    # Scale optical bands to Float32 (Landsat Collection 2 scale factors)
    scaled = (image.select(['SR_B2','SR_B3','SR_B4','SR_B5','SR_B6','SR_B7'])
                   .multiply(0.0000275).add(-0.2)
                   .toFloat())

    # Brightness temperature from Band 10
    bt = image.select('ST_B10').multiply(0.00341802).add(149.0).toFloat()

    # NDVI
    ndvi = scaled.normalizedDifference(['SR_B5','SR_B4']).rename('NDVI').toFloat()

    # Fractional vegetation cover
    fv = ndvi.subtract(0.2).divide(0.3).clamp(0, 1).pow(2).toFloat()

    # Emissivity (Sobrino et al. 2008)
    em = fv.multiply(0.004).add(0.986).rename('Emissivity').toFloat()

    # LST in Celsius — mono-window algorithm
    lst = bt.expression(
        'BT / (1 + (0.00115 * BT / 1.4388) * log(Em)) - 273.15',
        {'BT': bt, 'Em': em}
    ).rename('LST_Celsius').toFloat()

    return (scaled.addBands(lst).addBands(ndvi).addBands(em)
            .set('system:time_start', image.get('system:time_start')))

task_ids = {}

for year in range(START_YEAR, END_YEAR + 1):
    collection = (ee.ImageCollection('LANDSAT/LC08/C02/T1_L2')
        .filterBounds(AOI)
        .filter(ee.Filter.calendarRange(year, year, 'year'))
        .filter(ee.Filter.calendarRange(4, 9, 'month'))
        .filter(ee.Filter.lt('CLOUD_COVER', CLOUD_COVER_THRESHOLD))
        .map(mask_clouds)
        .map(compute_lst))

    count = collection.size().getInfo()
    print(f"\n{year}: {count} scenes")

    if count == 0:
        print(f"  WARNING: Relaxing cloud filter to 40%...")
        collection = (ee.ImageCollection('LANDSAT/LC08/C02/T1_L2')
            .filterBounds(AOI)
            .filter(ee.Filter.calendarRange(year, year, 'year'))
            .filter(ee.Filter.calendarRange(4, 9, 'month'))
            .filter(ee.Filter.lt('CLOUD_COVER', 40))
            .map(mask_clouds)
            .map(compute_lst))

    composite = collection.mean().clip(AOI).toFloat()

    task = ee.batch.Export.image.toDrive(
        image          = composite,
        description    = f'L8_Delhi_{year}',
        folder         = GDRIVE_FOLDER,
        fileNamePrefix = f'L8_Delhi_{year}',
        region         = AOI,
        scale          = SCALE,
        crs            = CRS,
        maxPixels      = MAX_PIXELS,
        fileFormat     = 'GeoTIFF'
    )
    task.start()
    task_ids[year] = task.id
    print(f"  Task started: {task.id}")
    time.sleep(2)

os.makedirs(LOGS_DIR, exist_ok=True)
log_file = os.path.join(LOGS_DIR, 'landsat_task_ids.json')
with open(log_file, 'w') as f:
    json.dump(task_ids, f, indent=2)

print(f"\nAll tasks submitted. IDs saved to: {log_file}")
print("Monitor: https://code.earthengine.google.com/tasks")
