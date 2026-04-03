"""
pages2k_inspect_nc.py
---------------------
Downloads pages2k_ngeo19_recons.nc from NOAA (if not already present)
and reports its structure: dimensions, variables, coordinate ranges.
Tells us whether the product is spatially gridded or just a global mean.

Run from repo root:
    ~/envs/_edop/bin/python3 scripts/edop/pages2k_inspect_nc.py
"""

import os
import requests
import xarray as xr

NC_URL = "https://www.ncei.noaa.gov/pub/data/paleo/pages2k/neukom2019temp/pages2k_ngeo19_recons.nc"
NC_PATH = "data/pages2k2017/pages2k_ngeo19_recons.nc"

def download_nc():
    os.makedirs(os.path.dirname(NC_PATH), exist_ok=True)
    if os.path.exists(NC_PATH):
        print(f"Already downloaded: {NC_PATH}")
        return
    print(f"Downloading {NC_URL} ...")
    r = requests.get(NC_URL, stream=True, timeout=60)
    r.raise_for_status()
    total = int(r.headers.get("content-length", 0))
    received = 0
    with open(NC_PATH, "wb") as f:
        for chunk in r.iter_content(chunk_size=65536):
            f.write(chunk)
            received += len(chunk)
            if total:
                print(f"  {received/1e6:.1f} / {total/1e6:.1f} MB", end="\r")
    print(f"\n  Saved to {NC_PATH}")

def inspect_nc():
    print(f"\nOpening {NC_PATH} with xarray ...")
    ds = xr.open_dataset(NC_PATH)

    print("\n--- Dimensions ---")
    for name, size in ds.dims.items():
        print(f"  {name}: {size}")

    print("\n--- Coordinates ---")
    for name, coord in ds.coords.items():
        vals = coord.values
        if vals.ndim == 1 and len(vals) > 1:
            print(f"  {name}: {vals[0]} → {vals[-1]}  (n={len(vals)})")
        else:
            print(f"  {name}: {vals}")

    print("\n--- Variables ---")
    for name, var in ds.data_vars.items():
        print(f"  {name}: dims={var.dims}, shape={var.shape}")
        if hasattr(var, 'long_name'):
            print(f"    long_name: {var.long_name}")
        if hasattr(var, 'units'):
            print(f"    units: {var.units}")

    print("\n--- Global attributes ---")
    for k, v in ds.attrs.items():
        print(f"  {k}: {v}")

    ds.close()

if __name__ == "__main__":
    download_nc()
    inspect_nc()
