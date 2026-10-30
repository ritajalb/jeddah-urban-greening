#!/usr/bin/env python3
import os
import sys
import numpy as np
import xarray as xr

try:
    import rioxarray
except Exception:
    print("ERROR: Missing dependency: rioxarray")
    print("Install: pip install rioxarray rasterio")
    print(" or : conda install -c conda-forge rioxarray rasterio")
    raise


def die(msg, code=1):
    print("\n[ERROR]", msg, "\n")
    sys.exit(code)


def main():
    GEOEM_BASELINE = "./geo_em.d02_baseline.nc"
    GEOEM_OUT = "./geo_em.d02_builtup_ref.nc"
    BUILTUP_TIF = os.environ.get("BUILTUP_TIF", "./builtup_00025.tif")
    URBAN_LU_CODE = 13

    if not os.path.exists(GEOEM_BASELINE):
        die("Baseline geo_em not found")
    if not os.path.exists(BUILTUP_TIF):
        die("Built-up GeoTIFF not found")

    print("Loading geo_em baseline...")
    ds = xr.open_dataset(GEOEM_BASELINE)

    if "LU_INDEX" not in ds:
        die("LU_INDEX not found")
    if "XLAT_M" not in ds or "XLONG_M" not in ds:
        die("XLAT_M / XLONG_M not found")

    lu = ds["LU_INDEX"].copy()
    lats = ds["XLAT_M"].isel(Time=0).values
    lons = ds["XLONG_M"].isel(Time=0).values

    print("Loading built-up GeoTIFF...")
    da = xr.open_dataarray(BUILTUP_TIF, engine="rasterio")
    if "band" in da.dims:
        da = da.isel(band=0)

    if da.rio.crs is None:
        die("GeoTIFF CRS missing")

    print("Reprojecting GeoTIFF...")
    da = da.rio.reproject("EPSG:4326")

    print("Sampling to WRF grid...")
    transform = da.rio.transform()
    inv = ~transform

    cols, rows = inv * (lons, lats)
    cols = np.clip(np.round(cols).astype(int), 0, da.shape[1] - 1)
    rows = np.clip(np.round(rows).astype(int), 0, da.shape[0] - 1)

    mask = da.values[rows, cols] > 0
    print("Built-up cells:", int(mask.sum()))

    lu_new = lu.values.copy()
    lu_new[0, mask] = URBAN_LU_CODE

    ds_out = ds.copy(deep=True)
    ds_out["LU_INDEX"].values = lu_new

    print("Writing output...")
    ds_out.to_netcdf(GEOEM_OUT)
    print("Done:", GEOEM_OUT)


if __name__ == "__main__":
    main()



