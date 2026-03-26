#!/usr/bin/env python3
"""
Prepare real geological boundary GeoJSON files for the GoM plate kinematics map.

Downloads and converts:
  - Yucatan Block polygon  →  docs/data/yucatan_block.geojson
    Source: EarthByte GPlates 2.3 Static Polygons (Müller et al. 2019)
    Plate ID 314 in the GPlates rotation model

  - Continent-Ocean Boundaries (GoM)  →  docs/data/gom_cob.geojson
    Source: EarthByte GPlates 2.3 COBs
    Defines the edge of oceanic crust (Sigsbee Deep boundary)

Manual steps required (see bottom of script output):
  - Florida Platform  →  docs/data/florida_platform.geojson
  - East Texas Salt Basin  →  docs/data/east_texas_salt_basin.geojson

Usage:
    pip install requests
    python scripts/prepare_geodata.py

Note: geopandas is only needed if the COB file is a shapefile rather than GPML.
"""

import os, sys, json, zipfile, io, re, gzip
import xml.etree.ElementTree as ET

try:
    import requests
except ImportError:
    sys.exit("Missing dependency: pip install requests")

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(PROJECT_ROOT, 'docs', 'data')
os.makedirs(DATA_DIR, exist_ok=True)

def log(msg, indent=0):
    print("  " * indent + msg)

def save_geojson(path, features, source_note=""):
    fc = {
        "type": "FeatureCollection",
        "features": features
    }
    if source_note:
        fc["source"] = source_note
    with open(path, 'w') as f:
        json.dump(fc, f, separators=(',', ':'))
    log(f"✓ Saved → {os.path.relpath(path, PROJECT_ROOT)}", 1)
    return True


def fetch_zip(url, label):
    log(f"Downloading {label}...")
    try:
        r = requests.get(url, timeout=120, stream=True)
        r.raise_for_status()
        data = b"".join(r.iter_content(65536))
        log(f"  {len(data)//1024} KB downloaded", 1)
        return zipfile.ZipFile(io.BytesIO(data))
    except Exception as e:
        log(f"✗ Failed: {e}", 1)
        return None


def parse_gpml_polygons(gpml_bytes, plate_id_filter=None, region_bbox=None):
    """
    Parse a GPlates GPML file and return polygon coordinates.

    plate_id_filter : int or None — only return polygons with this plate ID
    region_bbox     : (lon_min, lat_min, lon_max, lat_max) or None — spatial filter
    """
    # Decompress if .gpmlz
    if gpml_bytes[:2] == b'\x1f\x8b':
        gpml_bytes = gzip.decompress(gpml_bytes)

    text = gpml_bytes.decode('utf-8', errors='replace')

    # ── Namespace map from the document header ───────────────────────────────
    ns = {}
    for m in re.finditer(r'xmlns:?(\w*)=["\']([^"\']+)["\']', text[:3000]):
        prefix, uri = m.group(1), m.group(2)
        if prefix:
            ns[prefix] = uri

    try:
        root = ET.fromstring(text)
    except ET.ParseError as e:
        log(f"✗ XML parse error: {e}", 2)
        return []

    features = []

    # Walk every element looking for feature containers
    for elem in root.iter():
        local = elem.tag.split('}')[-1] if '}' in elem.tag else elem.tag
        if local not in ('StaticPolygon', 'ClosedContinentalBoundary',
                         'ClosedPlatePolygon', 'gpml:StaticPolygon'):
            continue

        # ── Plate ID ─────────────────────────────────────────────────────────
        pid = None
        for child in elem.iter():
            cl = child.tag.split('}')[-1]
            if cl == 'reconstructionPlateId' or cl == 'plateId':
                for val in child.iter():
                    vl = val.tag.split('}')[-1]
                    if vl == 'value' and val.text:
                        try:
                            pid = int(val.text.strip())
                        except ValueError:
                            pass
                        break
                if pid is not None:
                    break

        if plate_id_filter is not None and pid != plate_id_filter:
            continue

        # ── Geometry ─────────────────────────────────────────────────────────
        for geo in elem.iter():
            gl = geo.tag.split('}')[-1]
            if gl == 'posList' and geo.text:
                raw = [float(x) for x in geo.text.split()]
                # GPML stores coordinates as (lon lat) pairs
                coords = [[raw[i], raw[i + 1]] for i in range(0, len(raw) - 1, 2)]
                if len(coords) < 4:
                    continue

                # Optional spatial filter
                if region_bbox:
                    lons = [c[0] for c in coords]
                    lats = [c[1] for c in coords]
                    if (max(lons) < region_bbox[0] or min(lons) > region_bbox[2] or
                            max(lats) < region_bbox[1] or min(lats) > region_bbox[3]):
                        continue

                features.append({
                    "type": "Feature",
                    "properties": {"plate_id": pid},
                    "geometry": {"type": "Polygon", "coordinates": [coords]}
                })

    return features


# ─────────────────────────────────────────────────────────────────────────────
# 1.  Yucatan Block  (plate ID 314)
# ─────────────────────────────────────────────────────────────────────────────
def download_yucatan_block():
    print("\n── 1. Yucatan Block ─────────────────────────────────────────────")
    url = ("https://www.earthbyte.org/webdav/ftp/earthbyte/GPlates/"
           "GPlates2.3_GeoData/Individual/StaticPolygons.zip")

    z = fetch_zip(url, "EarthByte Static Polygons (Müller 2019)")
    if z is None:
        return False

    gpml_file = next((n for n in z.namelist()
                      if n.endswith('.gpml') or n.endswith('.gpmlz')), None)
    if gpml_file is None:
        log("✗ No GPML file found in zip", 1)
        return False

    log(f"Parsing {gpml_file} for plate ID 314 (Yucatan)...", 1)
    raw = z.read(gpml_file)
    polys = parse_gpml_polygons(raw, plate_id_filter=314)

    if not polys:
        log("✗ Plate ID 314 not found — check GPML structure", 1)
        log("Hint: open the file in GPlates to verify the Yucatan plate ID", 2)
        return False

    for f in polys:
        f["properties"].update({
            "name": "Yucatan Block",
            "source": "EarthByte GPlates 2.3 / Müller et al. 2019",
            "note": "Paleo-microplate; rotated ~45° CCW during GoM opening 165–145 Ma"
        })

    out = os.path.join(DATA_DIR, 'yucatan_block.geojson')
    save_geojson(out, polys,
                 source_note="EarthByte GPlates 2.3 Static Polygons, Müller et al. 2019")
    log(f"  {len(polys)} polygon feature(s) written", 1)
    return True


# ─────────────────────────────────────────────────────────────────────────────
# 2.  Continent-Ocean Boundaries — Gulf of Mexico region
#     (these outline the Sigsbee Deep oceanic crust boundary)
# ─────────────────────────────────────────────────────────────────────────────
def download_cobs():
    print("\n── 2. Continent-Ocean Boundaries (GoM) ─────────────────────────")
    url = ("https://www.earthbyte.org/webdav/ftp/earthbyte/GPlates/"
           "GPlates2.3_GeoData/Individual/COBs.zip")

    z = fetch_zip(url, "EarthByte COBs")
    if z is None:
        return False

    gpml_file = next((n for n in z.namelist()
                      if n.endswith('.gpml') or n.endswith('.gpmlz')), None)
    if gpml_file is None:
        log("✗ No GPML file in COBs zip", 1)
        return False

    log(f"Parsing {gpml_file} for Gulf of Mexico region...", 1)
    raw = z.read(gpml_file)
    # GoM bounding box — lon -100 to -78, lat 16 to 32
    features = parse_gpml_polygons(raw, region_bbox=(-100, 16, -78, 32))

    if not features:
        log("⚠ No COB features found in GoM bounding box", 1)
        return False

    for f in features:
        f["properties"].update({
            "name": "GoM Continent-Ocean Boundary",
            "source": "EarthByte GPlates 2.3 COBs",
            "note": "Marks transition from continental to oceanic crust"
        })

    out = os.path.join(DATA_DIR, 'gom_cob.geojson')
    save_geojson(out, features,
                 source_note="EarthByte GPlates 2.3 COBs")
    log(f"  {len(features)} feature(s) written", 1)
    return True


# ─────────────────────────────────────────────────────────────────────────────
# 3.  Summary and manual download instructions
# ─────────────────────────────────────────────────────────────────────────────
def print_manual_instructions():
    print("""
── 3. Florida Platform  (manual download required) ─────────────────────────

  The Florida Platform boundary comes from the USGS State Geologic Map
  Compilation (SGMC).  Downloading the full 600 MB dataset just to clip
  one polygon is impractical, so the recommended approach is:

  Option A — USGS NGMDB MapView (easiest):
    1. Go to https://ngmdb.usgs.gov/mapview/
    2. Zoom to Florida / SE Gulf of Mexico
    3. Use the export tool to download the carbonate platform polygon
    4. Convert: ogr2ogr -f GeoJSON docs/data/florida_platform.geojson <file.shp>

  Option B — USGS ScienceBase (full dataset):
    1. Go to https://www.sciencebase.gov/catalog/item/5888bf4fe4b05ccb964bab9d
    2. Download USGS_SGMC_Shapefiles.zip (~634 MB)
    3. Open in QGIS, filter features for UNIT_NAME LIKE '%carbonate%'
       in the Florida/SE region, export selection as GeoJSON
    4. Save as docs/data/florida_platform.geojson

── 4. East Texas Salt Basin  (manual download required) ─────────────────────

  The Texas Bureau of Economic Geology (BEG) is the authoritative source.

  Option A — BEG GeoData Portal:
    1. Go to https://www.beg.utexas.edu/
    2. Search "East Texas Basin" or "Louann Salt" in their data catalog
    3. Download the basin boundary shapefile
    4. Convert: ogr2ogr -f GeoJSON docs/data/east_texas_salt_basin.geojson <file.shp>

  Option B — USGS Energy Resources (basin outlines):
    1. Go to https://www.usgs.gov/energy-and-minerals/oil-and-gas/
    2. Look for "Petroleum Systems and Geologic Assessment" → Gulf Coast province
    3. Download the polygon files for the East Texas Basin (province 5047)
    4. Convert and save as docs/data/east_texas_salt_basin.geojson

Once you place the files in docs/data/, the map will load them automatically.
""")


# ─────────────────────────────────────────────────────────────────────────────
if __name__ == '__main__':
    print("=" * 60)
    print("  GoM Geological Data Preparation")
    print("  EarthByte GPlates 2.3 / Müller et al. 2019")
    print("=" * 60)

    y_ok = download_yucatan_block()
    c_ok = download_cobs()
    print_manual_instructions()

    print("=" * 60)
    print(f"  Yucatan Block  : {'✓ done' if y_ok else '✗ failed'}")
    print(f"  GoM COB        : {'✓ done' if c_ok else '✗ failed'}")
    print(f"  Florida Plat.  : ✎ manual (see instructions above)")
    print(f"  E. TX Salt     : ✎ manual (see instructions above)")
    print("=" * 60)
    print(f"\nOutput directory: {DATA_DIR}\n")
