# Jeddah Urban Greening — Where to Plant, and What Happens if We Do

Two connected pieces of work on reducing urban heat in Jeddah with trees.

## 1. Tree-planting priority from satellite data

`notebooks/tree_planting_priority.ipynb`

- Pulls **NDVI** (vegetation, Sentinel-2 L2A) and **land surface temperature** (Landsat 8/9 L2) from Sentinel Hub for Jeddah neighbourhoods, May–June 2024.
- Starts with 4 neighbourhoods, then expands to **14** (Al Hamdaniyah, Abhur, Al Basateen, Al Shati, Al Salama, Al Naeem, Al Safa, Al Rawdah, Al Aziziyah, Al Balad, Ghulail, Al Hindawiyah, Al Faisaliyah).
- Ranks them with a simple, transparent **priority score**: `0.7 × LST + 0.3 × (1 − NDVI)`. Hot neighbourhoods with little vegetation rank highest.
- Adds a small Random Forest classifier as an exploratory step, and shows the result on an interactive **Folium map** coloured High / Medium / Low.

This is a prototype: the score and the labels are rule-based, and 14 neighbourhoods is a small sample.

To run it you need a free Sentinel Hub account:

```bash
pip install sentinelhub folium seaborn scikit-learn
export SH_CLIENT_ID=your-client-id
export SH_CLIENT_SECRET=your-client-secret
```

## 2. Land-use scenarios for WRF

`wrf_landuse/`

Small Python scripts that edit a WRF `geo_em` file (the static land-use input produced by WPS) to build afforestation scenarios for the same area:

| Script | What it does |
|---|---|
| `apply_builtup_to_geoem.py` | samples a built-up GeoTIFF onto the WRF grid and marks those cells as urban (code 13), giving an up-to-date built-up reference |
| `apply_green_city.py` | greening scenario inside the city |
| `apply_green_coast.py` | greening scenario along the coast |
| `apply_green_desert.py` | greening scenario on the desert edge |

Each greening script takes the built-up reference, finds the 20 non-urban, non-water grid cells nearest to a chosen centre point, sets them to a vegetated land-use class (code 7), and writes a new `geo_em` file. The number of converted cells is fixed, so the scenarios differ only in where the greening happens.

```bash
pip install numpy xarray netCDF4 rioxarray rasterio
python wrf_landuse/apply_builtup_to_geoem.py   # needs geo_em.d02_baseline.nc and a built-up GeoTIFF
python wrf_landuse/apply_green_city.py
```

The `geo_em` files themselves are not included.

**Tech:** Python · Sentinel Hub · NumPy · pandas · scikit-learn · Folium · xarray · WRF/WPS

**Author:** Ritaj Albogami
