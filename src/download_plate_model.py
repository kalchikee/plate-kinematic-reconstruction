"""
download_plate_model.py
-----------------------
Downloads the Müller et al. (2019) community plate model from EarthByte/Zenodo.

The Müller2019 model is the current standard for global plate reconstructions,
covering 0–1000 Ma with full plate boundary topology.

DOI: 10.5281/zenodo.3764447
Reference: Müller et al. (2019) Tectonics, doi:10.1029/2018TC005462

Files downloaded:
  - Rotation file (.rot)         : Euler rotation poles through time
  - Topology features (.gpmlz)   : Plate boundary geometries
  - Continental polygons          : Present-day and reconstructed continents
  - Coastlines                    : Global coastline geometries
"""

import logging
import zipfile
from pathlib import Path

import requests
from tqdm import tqdm

log = logging.getLogger(__name__)

# Zenodo record for Müller et al. 2019 (v2.0.0)
ZENODO_RECORD = "https://zenodo.org/record/3764447/files"

# Alternative: EarthByte direct download
EARTHBYTE_BASE = "https://www.earthbyte.org/webdav/ftp/Data_Collections/Muller_etal_2019_Tectonics/"

# GPlates web service GitHub (for additional resources)
GPLATES_WS = "https://github.com/GPlates/gplates-web-service/raw/main/django/GWS/reconstruction"

# Expected file structure after download
PLATE_MODEL_FILES = {
    "rotation": "Muller2019-Young2019-Cao2020_CombinedRotations.rot",
    "topology": "Muller2019-Young2019-Cao2020_PlateBoundaries_0-1000Ma.gpmlz",
    "continental_polygons": "StaticGeometries/AgeCodedContinentalPolygons.gpmlz",
    "coastlines": "StaticGeometries/Global_EarthByte_GPlates_Coastlines_2019_v1.gpmlz",
    "passive_margins": "StaticGeometries/Global_EarthByte_PassiveMargins_2019_v1.gpmlz",
}

# Direct download URLs (Zenodo)
DOWNLOAD_URLS = {
    "muller2019_zip": (
        "https://zenodo.org/record/3764447/files/"
        "Muller_etal_2019_PlateMotionModel_v2.0.0.zip?download=1"
    ),
}


def download_file(url: str, dest: Path, chunk_size: int = 1024 * 1024) -> Path:
    """Download a file with progress bar."""
    resp = requests.get(url, stream=True, timeout=120)
    resp.raise_for_status()

    total = int(resp.headers.get("content-length", 0))
    desc = dest.name

    with open(dest, "wb") as f, tqdm(
        desc=desc, total=total, unit="B", unit_scale=True
    ) as pbar:
        for chunk in resp.iter_content(chunk_size=chunk_size):
            f.write(chunk)
            pbar.update(len(chunk))

    return dest


def download_plate_model(output_dir: Path = Path("data/plate_model")) -> dict[str, Path]:
    """
    Download and extract the Müller et al. (2019) plate model.

    Parameters
    ----------
    output_dir : Path  Local directory for plate model files

    Returns
    -------
    dict mapping file type → local Path
    """
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    zip_path = output_dir / "Muller2019_PlateModel.zip"

    # Download archive
    if not zip_path.exists():
        log.info(f"Downloading Müller et al. 2019 plate model from Zenodo...")
        log.info(f"  URL: {DOWNLOAD_URLS['muller2019_zip']}")
        log.info(f"  Destination: {zip_path}")
        log.info(f"  Size: ~500 MB — this may take several minutes")
        try:
            download_file(DOWNLOAD_URLS["muller2019_zip"], zip_path)
        except Exception as e:
            log.error(
                f"Download failed: {e}\n"
                f"  Manual download: https://zenodo.org/record/3764447\n"
                f"  Extract to: {output_dir}"
            )
            return {}
    else:
        log.info(f"Plate model archive already exists: {zip_path}")

    # Extract archive
    extract_dir = output_dir / "Muller2019"
    if not extract_dir.exists():
        log.info(f"Extracting plate model to {extract_dir}...")
        with zipfile.ZipFile(zip_path, "r") as zf:
            zf.extractall(output_dir)
        log.info("Extraction complete")

    # Map file types to local paths
    paths = {}
    for file_type, filename in PLATE_MODEL_FILES.items():
        candidates = list(extract_dir.rglob(Path(filename).name))
        if candidates:
            paths[file_type] = candidates[0]
            log.info(f"  {file_type}: {candidates[0]}")
        else:
            log.warning(f"  {file_type} not found: {filename}")

    log.info(f"Plate model ready: {len(paths)}/{len(PLATE_MODEL_FILES)} files located")
    return paths


def verify_pygplates() -> bool:
    """Check if pyGPlates is available."""
    try:
        import pygplates
        version = pygplates.__version__
        log.info(f"pyGPlates available: version {version}")
        return True
    except ImportError:
        log.warning(
            "pyGPlates not found.\n"
            "  Install GPlates 2.4+ from: https://www.gplates.org/download/\n"
            "  Then add pyGPlates to your Python path:\n"
            "    export PYTHONPATH=/path/to/GPlates/pygplates:$PYTHONPATH"
        )
        return False


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    verify_pygplates()
    paths = download_plate_model()
    print(f"\nPlate model files:")
    for k, v in paths.items():
        print(f"  {k}: {v}")
