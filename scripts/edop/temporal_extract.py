"""
temporal_extract.py
-------------------
Extracts a temporal enrichment block for a named location and period:
  - LMR v2.1 PDSI (Palmer Drought Severity Index), with decadal means
  - eVolv2k v4 volcanic event annotation for a context window

Usage:
    ~/envs/_edop/bin/python3 scripts/edop/temporal_extract.py \\
        --name Kaifeng --lat 34.80 --lon 114.30 \\
        --year-start 950 --year-end 1000

    ~/envs/_edop/bin/python3 scripts/edop/temporal_extract.py \\
        --name Ur --lat 30.96 --lon 46.10 \\
        --year-start 900 --year-end 1000

Output is written to output/edop/temporal/{name}_{year_start}_{year_end}/
  temporal_signature.json  — structured temporal block, ready to embed in a sig
  summary.txt              — plain-text summary for quick reading / email paste
"""

import argparse
import json
import os
import re
import numpy as np
import pandas as pd
import xarray as xr


# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

LMR_DIR     = "data/lmr_v2.1"
EVOLV_PATH  = "data/volcano/evolv2k_v4.csv"
OUTPUT_BASE = "output/edop/temporal"

LMR_PDSI_FILE = os.path.join(LMR_DIR, "pdsi_MCruns_ensemble_mean_LMRv2.1.nc")


# ---------------------------------------------------------------------------
# LMR extraction
# ---------------------------------------------------------------------------

def extract_pdsi(lat, lon, year_start, year_end):
    """Extract PDSI stats and decadal means from LMRv2.1 for a point/period."""
    if not os.path.exists(LMR_PDSI_FILE):
        raise FileNotFoundError(f"LMR PDSI file not found: {LMR_PDSI_FILE}")

    ds = xr.open_dataset(LMR_PDSI_FILE)
    da = ds["pdsi"]

    lat_dim  = next(d for d in da.dims if "lat" in d.lower())
    lon_dim  = next(d for d in da.dims if "lon" in d.lower())
    time_dim = next(d for d in da.dims if "time" in d.lower() or "year" in d.lower())
    ens_dim  = next((d for d in da.dims if d.lower() in ("mcrun", "ens", "ensemble")), None)

    # LMRv2.1 lon convention is 0–358
    query_lon = lon if lon >= 0 else lon + 360

    ts = da.sel({lat_dim: lat, lon_dim: query_lon}, method="nearest")
    ts_spread = ts.std(dim=ens_dim)  if ens_dim else xr.zeros_like(ts)
    ts        = ts.mean(dim=ens_dim) if ens_dim else ts

    grid_lat = float(ts.coords[lat_dim])
    grid_lon = float(ts.coords[lon_dim])
    # Report lon in -180/180 convention
    grid_lon_display = grid_lon if grid_lon <= 180 else grid_lon - 360

    time_vals = ds[time_dim].values
    try:
        years = np.array([t.year for t in time_vals])
    except AttributeError:
        years = time_vals.astype(int)

    mask     = (years >= year_start) & (years <= year_end)
    yrs      = years[mask]
    vals     = ts.values[mask]
    spreads  = ts_spread.values[mask]

    # Decadal means
    decade_start = (year_start // 10) * 10
    decade_end   = (year_end   // 10) * 10
    decadal = {}
    for d in range(decade_start, decade_end + 10, 10):
        d_mask = (yrs >= d) & (yrs < d + 10)
        key = f"{d}-{d+9}"
        decadal[key] = round(float(vals[d_mask].mean()), 3) if d_mask.any() else None

    ds.close()

    return {
        "grid_cell":        {"lat": round(grid_lat, 1), "lon": round(grid_lon_display, 1)},
        "n_years":          int(mask.sum()),
        "mean":             round(float(vals.mean()),    3),
        "std":              round(float(vals.std()),     3),
        "min":              round(float(vals.min()),     3),
        "max":              float(round(vals.max(),      3)),
        "ensemble_spread":  round(float(spreads.mean()), 3),
        "decadal_means":    decadal,
    }


# ---------------------------------------------------------------------------
# eVolv2k extraction
# ---------------------------------------------------------------------------

def extract_volcanic(year_start, year_end, context_years=50):
    """Return volcanic events in [year_start - context_years, year_end]."""
    if not os.path.exists(EVOLV_PATH):
        raise FileNotFoundError(f"eVolv2k file not found: {EVOLV_PATH}")

    df = pd.read_csv(EVOLV_PATH)
    window_start = year_start - context_years
    mask = (df["year_ad"] >= window_start) & (df["year_ad"] <= year_end)
    sub  = df[mask].sort_values("year_ad")

    events = []
    for _, row in sub.iterrows():
        events.append({
            "year_ad":    int(row["year_ad"]),
            "location":   row["location"] if pd.notna(row["location"]) and str(row["location"]).strip() else None,
            "lat":        float(row["lat"]) if pd.notna(row["lat"]) else None,
            "vssi_tg":    float(row["vssi_tg"]) if pd.notna(row["vssi_tg"]) else None,
            "asymmetry":  float(row["asymmetry"]) if pd.notna(row["asymmetry"]) else None,
        })

    max_vssi = round(float(sub["vssi_tg"].max()), 2) if not sub.empty else None

    return {
        "source":          "eVolv2k v4 (Sigl & Toohey 2024)",
        "period_queried":  f"{window_start}/{year_end}",
        "context_note":    f"Events in {context_years}-year context window before and through query period",
        "n_events":        len(events),
        "max_vssi_tg":     max_vssi,
        "events":          events,
    }


# ---------------------------------------------------------------------------
# Plain-text summary
# ---------------------------------------------------------------------------

def build_summary(name, lat, lon, year_start, year_end, pdsi, volcanic):
    lines = []
    lines.append(f"Temporal enrichment summary — {name} ({lat}N, {lon}E), {year_start}–{year_end} CE")
    lines.append("=" * 70)

    lines.append(f"\nLMR v2.1 PDSI  (grid cell {pdsi['grid_cell']['lat']}N, {pdsi['grid_cell']['lon']}E)")
    lines.append(f"  Period mean:      {pdsi['mean']:+.3f}  (0 = climatological mean; negative = drier)")
    lines.append(f"  Std / range:      {pdsi['std']:.3f}  [{pdsi['min']:+.3f}, {pdsi['max']:+.3f}]")
    lines.append(f"  Ensemble spread:  {pdsi['ensemble_spread']:.3f}  (MC ensemble std)")
    lines.append(f"\n  Decadal means:")
    for decade, val in pdsi["decadal_means"].items():
        bar = ""
        if val is not None:
            bar_len = int(abs(val) * 10)
            bar = ("+" if val >= 0 else "-") * min(bar_len, 20)
        val_str = f"{val:+.3f}" if val is not None else "  n/a"
        lines.append(f"    {decade}:  {val_str}  {bar}")

    lines.append(f"\neVolv2k v4 — eruptions {volcanic['period_queried'].replace('/', '–')} CE")
    lines.append(f"  {volcanic['n_events']} events in window  |  largest: {volcanic['max_vssi_tg']} Tg VSSI")
    if volcanic["events"]:
        lines.append(f"\n  {'Year':>6}  {'VSSI (Tg)':>10}  {'Asym':>6}  Location")
        lines.append(f"  {'----':>6}  {'---------':>10}  {'----':>6}  --------")
        for e in volcanic["events"]:
            loc  = e["location"] or "(unknown)"
            vssi = f"{e['vssi_tg']:.2f}" if e["vssi_tg"] is not None else "  —"
            asym = f"{e['asymmetry']:.2f}" if e["asymmetry"] is not None else "  —"
            lines.append(f"  {e['year_ad']:>6}  {vssi:>10}  {asym:>6}  {loc}")
    else:
        lines.append("  (no events in window)")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="EDOP temporal enrichment extractor")
    parser.add_argument("--name",       required=True,  help="Location name (used in output path)")
    parser.add_argument("--lat",        required=True,  type=float)
    parser.add_argument("--lon",        required=True,  type=float)
    parser.add_argument("--year-start", required=True,  type=int, dest="year_start")
    parser.add_argument("--year-end",   required=True,  type=int, dest="year_end")
    parser.add_argument("--context",    default=50,     type=int,
                        help="Years before year-start to include in volcanic context window (default 50)")
    args = parser.parse_args()

    slug = re.sub(r"[^a-z0-9]+", "_", args.name.lower()).strip("_")
    out_dir = os.path.join(OUTPUT_BASE, f"{slug}_{args.year_start}_{args.year_end}")
    os.makedirs(out_dir, exist_ok=True)

    print(f"Extracting LMR PDSI for {args.name} ({args.lat}N, {args.lon}E), {args.year_start}–{args.year_end} CE ...")
    pdsi = extract_pdsi(args.lat, args.lon, args.year_start, args.year_end)

    print(f"Querying eVolv2k for volcanic events ...")
    volcanic = extract_volcanic(args.year_start, args.year_end, context_years=args.context)

    result = {
        "location":   {"name": args.name, "lat": args.lat, "lon": args.lon},
        "period":     f"{args.year_start}/{args.year_end}",
        "temporal": {
            "_note":   "Palmer Drought Severity Index from LMR v2.1. 0 = climatological mean; negative = drier than mean; positive = wetter.",
            "source":  "Last Millennium Reanalysis v2.1 (Tardif et al. 2019)",
            "pdsi":    pdsi,
        },
        "volcanic":   volcanic,
    }

    json_path = os.path.join(out_dir, "temporal_signature.json")
    with open(json_path, "w") as f:
        json.dump(result, f, indent=2)
    print(f"  Saved: {json_path}")

    summary = build_summary(args.name, args.lat, args.lon,
                            args.year_start, args.year_end, pdsi, volcanic)
    txt_path = os.path.join(out_dir, "summary.txt")
    with open(txt_path, "w") as f:
        f.write(summary)
    print(f"  Saved: {txt_path}")

    print(f"\n{summary}")


if __name__ == "__main__":
    main()
