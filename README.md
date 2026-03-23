# Gulf of Mexico Plate Kinematic Reconstruction

[![Python](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/)
[![GPlates](https://img.shields.io/badge/GPlates-2.4-purple)](https://www.gplates.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Data: EarthByte](https://img.shields.io/badge/Data-EarthByte%20Müller2019-orange)](https://www.earthbyte.org/)
[![Model: Müller2019](https://img.shields.io/badge/Plate%20Model-Müller%20et%20al.%202019-blue)](https://doi.org/10.1029/2018TC005462)

Quantitative plate kinematic reconstruction of Gulf of Mexico basin formation from 200 Ma to present using the Müller et al. (2019) community plate model. Extracts divergence rates, reconstructed paleoshorelines, and timing of tectonic events relevant to petroleum systems analysis — including the Jurassic salt deposition window and Cretaceous passive margin development.

---

## Scientific Background

The Gulf of Mexico is one of the world's most prolific hydrocarbon basins, containing ~50 billion barrels of recoverable reserves. Its basin architecture was entirely controlled by plate kinematics: Triassic–Jurassic rifting separated North America from South America/Africa, creating the accommodation space later filled by Jurassic Louann Salt and Cretaceous carbonate platforms.

Understanding this kinematic history is essential for petroleum systems analysis because:
- **Source rock timing** — anoxic basin conditions for Smackover and Tithonian source rocks required restricted basin geometry (165–145 Ma)
- **Salt geometry** — Louann Salt thickness and distribution (hence structural traps) controlled by rift geometry
- **Structural inversion** — Laramide compression (80–55 Ma) created many current trap structures
- **Heat flow evolution** — crustal stretching (β factor) governs thermal maturity of source rocks

### Key Tectonic Events

| Event | Age (Ma) | Significance |
|-------|----------|-------------|
| Triassic rifting onset | ~230 | Basin initiation, initial subsidence |
| Jurassic spreading | ~165 | Main basin opening, oceanic crust formation |
| Louann Salt deposition | ~165–160 | Restricted evaporite basin; source of allochthonous salt |
| Passive margin transition | ~145 | Thermal subsidence phase begins |
| Laramide compression | ~80–55 | Structural inversion, trap formation |
| Present | 0 | Modern passive margin |

---

## Repository Structure

```
05-plate-kinematic-reconstruction/
├── src/
│   ├── download_plate_model.py     # Fetch Müller et al. 2019 from EarthByte
│   ├── reconstruction_analysis.py  # pyGPlates reconstruction at key time slices
│   ├── velocity_calculation.py     # Divergence rates, Euler poles
│   ├── basin_analysis.py           # Subsidence modeling, petroleum systems timing
│   └── visualization.py            # pygmt maps, animation, timing charts
├── scripts/
│   ├── 01_download_model.py
│   ├── 02_reconstruct_region.py
│   ├── 03_velocity_fields.py
│   ├── 04_basin_history.py
│   └── 05_export_animation.py
├── notebooks/
│   └── 01_gulf_of_mexico_reconstruction.ipynb
├── gplates_files/
│   └── README.md
├── results/
│   ├── figures/
│   ├── animations/
│   └── data_exports/
├── docs/
│   ├── methodology.md
│   ├── gulf_of_mexico_basin_history.md
│   └── petroleum_systems_context.md
└── config/
    └── config.yaml
```

---

## Data Sources

| Dataset | Source | Access |
|---------|--------|--------|
| Müller et al. (2019) plate model | [EarthByte](https://www.earthbyte.org/muller-et-al-2019-tectonics-plate-motions-and-models/) | Open (Zenodo DOI: 10.5281/zenodo.3764447) |
| GPlates software | [gplates.org](https://www.gplates.org/download/) | Free |
| pyGPlates API | [EarthByte](https://www.gplates.org/docs/pygplates/) | Free (bundled with GPlates) |
| Gulf of Mexico stratigraphy | [BOEM](https://www.boem.gov/oil-gas-energy/geology-and-geophysics) | Public |
| Paleomagnetic data | [PALEOMAGIA](http://paleomagia.fi/) | Open |

---

## Plate Model Details

**Müller et al. (2019)** is the current community standard for global plate reconstructions, covering 0–1000 Ma with full plate topology and absolute reference frame. Key parameters for this study:

| Plate | ID | Present velocity (mm/yr) |
|-------|-----|--------------------------|
| North America | 101 | 22 (absolute) |
| South America | 201 | 12 (absolute) |
| Caribbean | 501 | 21 (relative to NA) |
| Cocos | 902 | 88 (relative to NA) |

**Gulf of Mexico opening:** The GoM opened by ~45° of rotation of the Yucatan block (plate ID 314) relative to North America between 165–145 Ma. Maximum divergence rate: ~40 mm/yr at peak spreading (155 Ma).

---

## Getting Started

### Prerequisites

1. Install [GPlates 2.4](https://www.gplates.org/download/) — pyGPlates is bundled with the installation
2. Add pyGPlates to Python path:
   ```bash
   export PYTHONPATH=/path/to/GPlates/pygplates:$PYTHONPATH
   ```

### Run the Pipeline

```bash
git clone https://github.com/kalchikee/plate-kinematic-reconstruction.git
cd plate-kinematic-reconstruction
pip install -r requirements.txt

# Download Müller et al. 2019 plate model
python scripts/01_download_model.py

# Reconstruct plate positions at key time slices
python scripts/02_reconstruct_region.py

# Compute velocity fields
python scripts/03_velocity_fields.py

# Basin subsidence analysis
python scripts/04_basin_history.py

# Export animation
python scripts/05_export_animation.py
```

---

## Key Outputs

**Plate reconstruction animation (200–0 Ma):**
MP4 showing plate positions at 2 Ma intervals with velocity vectors overlaid, Gulf of Mexico highlighted, and key tectonic events annotated.

**Time-slice maps (pygmt, publication quality):**
- 200 Ma: Pre-rift configuration, Pangea intact
- 165 Ma: Active spreading, Louann Salt basin geometry
- 100 Ma: Passive margin, Cretaceous carbonate deposition
- 55 Ma: Laramide compression onset
- 0 Ma: Modern configuration

**Divergence rate time series:**
Quantitative spreadsheet of GoM opening rate vs. time, showing acceleration during main spreading phase and deceleration at spreading cessation.

**Petroleum systems timing chart:**
Gantt-style chart correlating tectonic events (rifting, spreading, compression) with petroleum system elements (source rock deposition, reservoir sand input, trap formation, migration timing).

---

## Petroleum Systems Application

The reconstruction constrains several key petroleum systems questions for the deep-water GoM:

1. **Louann Salt thickness** — thickest salt deposited above the oldest oceanic crust where subsidence was greatest
2. **Smackover source rock deposition** — restricted anoxic conditions required basin geometry between 165–155 Ma (confirmed by reconstruction)
3. **Upper Jurassic–Lower Cretaceous carbonate plays** — platform development on rifted margins
4. **Tertiary turbidite systems** — Mississippi fan geometry controlled by progradation direction, which matches reconstructed drainage basin positions

See [docs/petroleum_systems_context.md](docs/petroleum_systems_context.md) for the full petroleum systems analysis.

---

## License

MIT License. See [LICENSE](LICENSE).

---

## References

- Müller, R.D. et al. (2019). A global plate model including lithospheric deformation along major rifts and orogens since the Triassic. *Tectonics*, 38(6), 1884–1907.
- Hudec, M.R. & Jackson, M.P.A. (2004). Regional restoration across the Sigsbee Escarpment, Gulf of Mexico. *AAPG Bulletin*, 88(3), 385–413.
- Stern, R.J. & Dickerson, P.W. (1999). Late Cenozoic magmatic evolution of the Big Bend area of the Rio Grande Rift. *AAPG Memoir*, 69.
- Salvador, A. (1991). The Gulf of Mexico Basin. *Geological Society of America*, The Geology of North America, v. J.
