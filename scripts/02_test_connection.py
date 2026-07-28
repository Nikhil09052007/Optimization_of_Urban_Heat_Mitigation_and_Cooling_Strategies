# 02_test_connection.py
# Run after authentication to confirm GEE is working

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import ee
from config import GEE_PROJECT, DELHI_BBOX, CLOUD_COVER_THRESHOLD

ee.Initialize(project=GEE_PROJECT)

# Test 1: Basic connection
print(ee.String('Connection OK').getInfo())

# Test 2: Scene count for Delhi
aoi = ee.Geometry.Rectangle(DELHI_BBOX)
collection = (ee.ImageCollection('LANDSAT/LC08/C02/T1_L2')
    .filterBounds(aoi)
    .filterDate('2019-01-01', '2023-12-31')
    .filter(ee.Filter.lt('CLOUD_COVER', CLOUD_COVER_THRESHOLD)))

count = collection.size().getInfo()
print(f"Landsat 8 scenes available for Delhi (2019-2023): {count}")
print("Expected: 150-200 scenes")
