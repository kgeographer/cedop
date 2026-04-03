"""
lmr_extract.py
--------------
Downloads one LMRv2.1 variable from NOAA (ensemble mean) and extracts
a time series for a query point and period. Proof-of-concept for EDOP
temporal enrichment from the Last Millennium Reanalysis.

Default: pdsi (Palmer Drought Severity Index) — smallest spatial file,
closest conceptual match to EDOP's aridity index.

Run from repo root:
    ~/envs/_edop/bin/python3 scripts/edop/lmr_extract.py

Change VARIABLE, LAT, LON, YEAR_START, YEAR_END below to explore.
"""

import os
import requests
import numpy as np
import xarray as xr

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

VARIABLE   = "pdsi"           # pdsi | air | prate | pr_wtr | sst | prmsl
LAT        = 30.96            # query latitude  (Ur)
LON        = 46.10            # query longitude (Ur)
YEAR_START = 900
YEAR_END   = 1000

BASE_URL = "https://www.ncei.noaa.gov/pub/data/paleo/reconstructions/tardif2019lmr/v2_1/"
DATA_DIR = "data/lmr_v2.1"

# ---------------------------------------------------------------------------
# File naming convention for LMRv2.1
# ---------------------------------------------------------------------------

def nc_filename(variable):
    return f"{variable}_MCruns_ensemble_mean_LMRv2.1.nc"

# ---------------------------------------------------------------------------
# Download with progress
# ---------------------------------------------------------------------------

def download(variable):
    os.makedirs(DATA_DIR, exist_ok=True)
    fname = nc_filename(variable)
    dest = os.path.join(DATA_DIR, fname)
    if os.path.exists(dest):
        print(f"Already downloaded: {dest}")
        return dest
    url = BASE_URL + fname
    print(f"Downloading {url} ...")
    r = requests.get(url, stream=True, timeout=120)
    r.raise_for_status()
    total = int(r.headers.get("content-length", 0))
    received = 0
    with open(dest, "wb") as f:
        for chunk in r.iter_content(chunk_size=131072):
            f.write(chunk)
            received += len(chunk)
            if total:
                print(f"  {received/1e6:.0f} / {total/1e6:.0f} MB", end="\r")
    print(f"\n  Saved: {dest}")
    return dest

# ---------------------------------------------------------------------------
# Inspect structure first, then extract
# ---------------------------------------------------------------------------

def inspect(ds, variable):
    print(f"\n--- Dimensions ---")
    for name, size in ds.sizes.items():
        print(f"  {name}: {size}")
    print(f"\n--- Coordinates ---")
    for name, coord in ds.coords.items():
        vals = coord.values
        if vals.ndim == 1 and len(vals) > 1:
            print(f"  {name}: {vals[0]:.2f} → {vals[-1]:.2f}  (n={len(vals)})")
    print(f"\n--- Variable '{variable}' ---")
    var = ds[variable]
    print(f"  dims:  {var.dims}")
    print(f"  shape: {var.shape}")
    if hasattr(var, 'long_name'):  print(f"  long_name: {var.long_name}")
    if hasattr(var, 'units'):      print(f"  units:     {var.units}")

def extract(ds, variable):
    """Extract ensemble-mean time series nearest to LAT/LON for a year range."""
    da = ds[variable]

    # identify coordinate names (may vary)
    lat_dim = next((d for d in da.dims if "lat" in d.lower()), None)
    lon_dim = next((d for d in da.dims if "lon" in d.lower()), None)
    time_dim = next((d for d in da.dims if "time" in d.lower() or "year" in d.lower()), None)

    if not (lat_dim and lon_dim and time_dim):
        print(f"\nCannot find lat/lon/time dims in {da.dims} — this may be a global mean file.")
        return None

    # lon convention in LMRv2.1 is 0–358; convert negative longitudes
    query_lon = LON if LON >= 0 else LON + 360

    # nearest-neighbour selection; average MCrun ensemble dimension if present
    ens_dim = next((d for d in da.dims if d.lower() in ("mcrun", "ens", "ensemble")), None)
    sel_kwargs = {lat_dim: LAT, lon_dim: query_lon}
    ts        = da.sel(**sel_kwargs, method="nearest")
    ts_spread = ts.std(dim=ens_dim)  if ens_dim else xr.zeros_like(ts)
    ts        = ts.mean(dim=ens_dim) if ens_dim else ts

    # time coords are cftime objects in LMRv2.1 — extract year as integer
    time_vals = ds[time_dim].values
    try:
        years = np.array([t.year for t in time_vals])
    except AttributeError:
        years = time_vals.astype(int)
    mask = (years >= YEAR_START) & (years <= YEAR_END)

    ts_mean   = ts.values[mask]
    ts_spread = ts_spread.values[mask]

    yrs = years[mask]

    grid_lat = float(ts.coords[lat_dim])
    grid_lon = float(ts.coords[lon_dim])
    print(f"\n  Grid cell selected: {grid_lat:.1f}N, {grid_lon:.1f}E")
    print(f"\n--- Extraction: {variable} at ({LAT}N, {LON}E), {YEAR_START}–{YEAR_END} CE ---")
    print(f"  n years:      {len(yrs)}")
    print(f"  mean value:   {ts_mean.mean():.4f}")
    print(f"  min / max:    {ts_mean.min():.4f} / {ts_mean.max():.4f}")
    print(f"  mean spread:  {ts_spread.mean():.4f}  (MC ensemble std)")
    print(f"\n  Sample (first 15 years):")
    print(f"  {'year':>6}  {'value':>10}  {'±spread':>10}")
    for y, v, s in zip(yrs[:15], ts_mean[:15], ts_spread[:15]):
        print(f"  {int(y):>6}  {v:>10.4f}  {s:>10.4f}")

    return years, ts_mean, ts_spread

# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    dest = download(VARIABLE)
    print(f"\nOpening {dest} ...")
    ds = xr.open_dataset(dest)
    inspect(ds, VARIABLE)
    extract(ds, VARIABLE)
    ds.close()

if __name__ == "__main__":
    main()
