#!/usr/bin/env python3
import os
import sys
import numpy as np
import xarray as xr

def die(msg, code=1):
    print("\n[ERROR]", msg, "\n")
    sys.exit(code)

def main():
    GEOEM_IN = "./geo_em.d02_builtup_ref.nc"
    GEOEM_OUT = "./geo_em.d02_green_coast.nc"

    CENTER_LAT = 22.0002
    CENTER_LON = 38.9452
    HALF_SIZE_KM = 3.0

    TARGET_CELLS = 20
    GREEN_LU_CODE = 7

    WATER_LU_CODE = 17
    URBAN_LU_CODE = 13

    if not os.path.exists(GEOEM_IN):
        die(f"Input geo_em not found: {GEOEM_IN}")

    ds = xr.open_dataset(GEOEM_IN)

    if "LU_INDEX" not in ds or "XLAT_M" not in ds or "XLONG_M" not in ds:
        die("Missing required variables in geo_em")

    lu = ds["LU_INDEX"].isel(Time=0).values.astype(int)
    lats = ds["XLAT_M"].isel(Time=0).values
    lons = ds["XLONG_M"].isel(Time=0).values

    dlat = HALF_SIZE_KM / 111.0
    dlon = HALF_SIZE_KM / (111.0 * np.cos(np.deg2rad(CENTER_LAT)))

    lat_min = CENTER_LAT - dlat
    lat_max = CENTER_LAT + dlat
    lon_min = CENTER_LON - dlon
    lon_max = CENTER_LON + dlon

    bbox = (
        (lats >= lat_min) &
        (lats <= lat_max) &
        (lons >= lon_min) &
        (lons <= lon_max)
    )

    eligible = bbox & (lu != WATER_LU_CODE) & (lu != URBAN_LU_CODE)

    n_bbox = int(bbox.sum())
    n_eligible = int(eligible.sum())

    print(f"Rectangle bounds: lat[{lat_min:.5f}, {lat_max:.5f}] lon[{lon_min:.5f}, {lon_max:.5f}]")
    print(f"Cells in rectangle (bbox): {n_bbox}")
    print(f"Eligible cells (non-water, non-urban) in rectangle: {n_eligible}")

    if n_eligible < TARGET_CELLS:
        die(f"Not enough eligible cells for TARGET_CELLS={TARGET_CELLS}. Increase HALF_SIZE_KM or move center inland.")

    iy, ix = np.where(eligible)
    dist2 = (lats[iy, ix] - CENTER_LAT) ** 2 + (lons[iy, ix] - CENTER_LON) ** 2
    order = np.argsort(dist2)

    sel_y = iy[order[:TARGET_CELLS]]
    sel_x = ix[order[:TARGET_CELLS]]

    print(f"Cells to convert (fixed): {sel_y.size}")

    lu_new = lu.copy()
    lu_new[sel_y, sel_x] = GREEN_LU_CODE

    ds_out = ds.copy(deep=True)
    ds_out["LU_INDEX"].values[0, :, :] = lu_new

    ds.close()

    if os.path.exists(GEOEM_OUT):
        os.remove(GEOEM_OUT)

    ds_out.to_netcdf(GEOEM_OUT)
    print("Done:", GEOEM_OUT)

if __name__ == "__main__":
    main()
