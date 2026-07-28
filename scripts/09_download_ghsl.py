# 09_download_ghsl.py
# STATUS: READY TO RUN — no API key needed, direct JRC download
# Downloads Global Human Settlement Layer tiles for Delhi NCR
# Run: python scripts\09_download_ghsl.py

import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import requests
import zipfile
from tqdm import tqdm
from config import GHSL_DIR

os.makedirs(GHSL_DIR, exist_ok=True)

# JRC direct download URLs for Delhi NCR tile R6_C27
GHSL_FILES = {
    'built_surface_2020': (
        'https://jeodpp.jrc.ec.europa.eu/ftp/jrc-opendata/GHSL/'
        'GHS_BUILT_S_GLOBE_R2023A/GHS_BUILT_S_E2020_GLOBE_R2023A_54009_10/V1-0/tiles/'
        'GHS_BUILT_S_E2020_GLOBE_R2023A_54009_10_V1_0_R6_C27.zip'
    ),
    'population_2020': (
        'https://jeodpp.jrc.ec.europa.eu/ftp/jrc-opendata/GHSL/'
        'GHS_POP_GLOBE_R2023A/GHS_POP_E2020_GLOBE_R2023A_54009_100/V1-0/tiles/'
        'GHS_POP_E2020_GLOBE_R2023A_54009_100_V1_0_R6_C27.zip'
    ),
    'settlement_model_2020': (
        'https://jeodpp.jrc.ec.europa.eu/ftp/jrc-opendata/GHSL/'
        'GHS_SMOD_GLOBE_R2023A/GHS_SMOD_E2020_GLOBE_R2023A_54009_1000/V1-0/tiles/'
        'GHS_SMOD_E2020_GLOBE_R2023A_54009_1000_V1_0_R6_C27.zip'
    ),
}

def download_file(url, dest):
    if os.path.exists(dest):
        print(f"  Already exists, skipping: {os.path.basename(dest)}")
        return
    r = requests.get(url, stream=True)
    total = int(r.headers.get('content-length', 0))
    with open(dest, 'wb') as f, tqdm(total=total, unit='B', unit_scale=True,
                                      desc=os.path.basename(dest)) as bar:
        for chunk in r.iter_content(chunk_size=8192):
            f.write(chunk)
            bar.update(len(chunk))

for name, url in GHSL_FILES.items():
    print(f"\nDownloading {name}...")
    zip_path  = os.path.join(GHSL_DIR, f'{name}.zip')
    ext_path  = os.path.join(GHSL_DIR, name)

    download_file(url, zip_path)

    os.makedirs(ext_path, exist_ok=True)
    with zipfile.ZipFile(zip_path, 'r') as z:
        z.extractall(ext_path)
    print(f"  ✅ Extracted to: {ext_path}")

print(f"\nAll GHSL data saved to: {GHSL_DIR}")
