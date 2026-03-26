# Geological Boundary Data

Place GeoJSON files here to replace approximate map overlays with real geometries.
The interactive map (`docs/index.html`) checks for these files on load and uses
them if present, otherwise falls back to approximate outlines.

## Files expected

| File | Source | How to get it |
|------|--------|---------------|
| `yucatan_block.geojson` | EarthByte GPlates 2.3 Static Polygons | Run `python scripts/prepare_geodata.py` |
| `gom_cob.geojson` | EarthByte GPlates 2.3 COBs | Run `python scripts/prepare_geodata.py` |
| `florida_platform.geojson` | USGS SGMC | See manual steps below |
| `east_texas_salt_basin.geojson` | Texas Bureau of Economic Geology | See manual steps below |

## Automated download

```bash
pip install requests
python scripts/prepare_geodata.py
```

This downloads from EarthByte and extracts:
- Yucatan block polygon (plate ID 314, Müller et al. 2019)
- Gulf of Mexico continent-ocean boundaries

## Manual downloads

### Florida Platform
1. Go to https://ngmdb.usgs.gov/mapview/
2. Zoom to Florida / SE Gulf of Mexico
3. Export the carbonate platform polygon
4. Convert: `ogr2ogr -f GeoJSON docs/data/florida_platform.geojson <file.shp>`

### East Texas Salt Basin
1. Go to https://www.beg.utexas.edu/ and search "East Texas Basin"
2. Download the basin boundary shapefile
3. Convert: `ogr2ogr -f GeoJSON docs/data/east_texas_salt_basin.geojson <file.shp>`

## Sources

- EarthByte GPlates 2.3 data: https://www.earthbyte.org/gplates-2-3-software-and-data-sets/
  (Creative Commons Attribution 3.0)
- Müller et al. (2019): https://doi.org/10.1029/2018TC005462
- USGS SGMC: https://www.sciencebase.gov/catalog/item/5888bf4fe4b05ccb964bab9d
- Texas BEG: https://www.beg.utexas.edu/
