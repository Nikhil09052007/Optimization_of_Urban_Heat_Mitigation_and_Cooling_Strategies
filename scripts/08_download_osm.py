# 08_download_osm.py
# STATUS: READY TO RUN — requires: pip install osmnx
# Downloads buildings, roads, green spaces, water bodies for Delhi NCR
# Run: python scripts\08_download_osm.py

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import osmnx as ox
import geopandas as gpd
from config import OSM_DIR

os.makedirs(OSM_DIR, exist_ok=True)

# Delhi NCR bounding box: (south, west, north, east)
bbox = (28.40, 76.84, 28.88, 77.58)

print("Downloading buildings...")
buildings = ox.features_from_bbox(bbox, tags={'building': True})
buildings.to_file(os.path.join(OSM_DIR, 'delhi_buildings.gpkg'), driver='GPKG')
print(f"  ✅ Buildings: {len(buildings)} features")

print("Downloading road network...")
G = ox.graph_from_bbox(bbox, network_type='drive')
nodes, edges = ox.graph_to_gdfs(G)
edges.to_file(os.path.join(OSM_DIR, 'delhi_roads.gpkg'), driver='GPKG')
print(f"  ✅ Roads: {len(edges)} segments")

print("Downloading green spaces...")
green = ox.features_from_bbox(bbox, tags={
    'leisure': ['park','garden','recreation_ground'],
    'landuse': ['grass','forest','meadow'],
    'natural': ['wood','scrub','tree_row']
})
green.to_file(os.path.join(OSM_DIR, 'delhi_green.gpkg'), driver='GPKG')
print(f"  ✅ Green areas: {len(green)} features")

print("Downloading water bodies...")
water = ox.features_from_bbox(bbox, tags={
    'natural': ['water','wetland'],
    'waterway': True,
    'landuse': 'reservoir'
})
water.to_file(os.path.join(OSM_DIR, 'delhi_water.gpkg'), driver='GPKG')
print(f"  ✅ Water bodies: {len(water)} features")

print(f"\nAll OSM data saved to: {OSM_DIR}")
