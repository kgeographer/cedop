"""
scripts/edop/explorer/precompute_lmr_notches.py
------------------------------------------------
Pre-compute LMR v2.1 notch-period means for the Explorer page.

Queries all 16,380 LMR cells from temporal.lmr_climate and computes the
mean value of pdsi, air, and prate for each of 5 named notch periods.
Writes a single GeoJSON file to app/static/explorer/lmr_notches.geojson.

GeoJSON structure:
  FeatureCollection of Polygon features (2°×2° squares).
  Each feature properties:
    lat, lon          : cell centre (lon in -180/180)
    pdsi_0..pdsi_4    : notch mean PDSI (dimensionless anomaly)
    air_0..air_4      : notch mean temperature anomaly (K)
    prate_0..prate_4  : notch mean precip rate anomaly (kg/m²/s)

Notch index → period mapping (also written to lmr_notches_meta.json):
    0  Early reliable  700–950 CE
    1  MCA             950–1250 CE
    2  Transition      1250–1450 CE
    3  LIA             1450–1850 CE
    4  Industrial      1850–1998 CE

LMR array indexing: Year Y CE → arr[Y+1] (PostgreSQL 1-indexed).
LMR lon stored as 0–360; converted to -180/180 for output.

Usage:
    python scripts/edop/explorer/precompute_lmr_notches.py
"""

import json
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
from app.db.connection import db_connect

# ---------------------------------------------------------------------------
# Notch periods (year CE, inclusive).  Index order matches GeoJSON properties.
# ---------------------------------------------------------------------------
NOTCHES = [
    {"name": "Early reliable", "label": "700–950 CE",   "y0": 700,  "y1": 950},
    {"name": "MCA",            "label": "950–1250 CE",  "y0": 950,  "y1": 1250},
    {"name": "Transition",     "label": "1250–1450 CE", "y0": 1250, "y1": 1450},
    {"name": "LIA",            "label": "1450–1850 CE", "y0": 1450, "y1": 1850},
    {"name": "Industrial",     "label": "1850–1998 CE", "y0": 1850, "y1": 1998},
]

OUT_DIR  = Path(__file__).resolve().parents[3] / "app" / "static" / "explorer"
OUT_GEO  = OUT_DIR / "lmr_notches.geojson"
OUT_META = OUT_DIR / "lmr_notches_meta.json"


def notch_sql_fragment(varname: str, notches: list) -> str:
    """Build SQL to compute per-notch means for one LMR variable column."""
    parts = []
    for n in notches:
        # PostgreSQL arrays are 1-indexed; year Y CE is at arr[Y+1]
        pg0 = n["y0"] + 1
        pg1 = n["y1"] + 1
        parts.append(
            f"(SELECT AVG(v) FROM UNNEST({varname}[{pg0}:{pg1}]) AS v)"
        )
    return ", ".join(parts)


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    pdsi_frags  = notch_sql_fragment("pdsi",  NOTCHES)
    air_frags   = notch_sql_fragment("air",   NOTCHES)
    prate_frags = notch_sql_fragment("prate", NOTCHES)

    sql = f"""
        SELECT
            lat,
            lon,
            {pdsi_frags},
            {air_frags},
            {prate_frags}
        FROM temporal.lmr_climate
        ORDER BY lat DESC, lon
    """

    print("Querying LMR climate cells …")
    with db_connect() as conn:
        rows = conn.execute(sql).fetchall()

    print(f"  {len(rows)} cells returned.")

    # Build GeoJSON FeatureCollection
    features = []
    n_notches = len(NOTCHES)

    for row in rows:
        lat      = float(row[0])
        lon_raw  = float(row[1])
        lon      = lon_raw if lon_raw <= 180 else lon_raw - 360

        # Values: columns 2..end — ordered pdsi×5, air×5, prate×5
        vals = [float(v) if v is not None else None for v in row[2:]]
        pdsi_vals  = vals[0           : n_notches]
        air_vals   = vals[n_notches   : n_notches * 2]
        prate_vals = vals[n_notches*2 : n_notches * 3]

        # 2°×2° square polygon centred on (lat, lon)
        lat_min = lat - 1.0
        lat_max = lat + 1.0
        lon_min = lon - 1.0
        lon_max = lon + 1.0
        ring = [
            [lon_min, lat_max],
            [lon_max, lat_max],
            [lon_max, lat_min],
            [lon_min, lat_min],
            [lon_min, lat_max],
        ]

        props = {"lat": lat, "lon": lon}
        for i, v in enumerate(pdsi_vals):
            props[f"pdsi_{i}"]  = round(v, 4) if v is not None else None
        for i, v in enumerate(air_vals):
            props[f"air_{i}"]   = round(v, 4) if v is not None else None
        for i, v in enumerate(prate_vals):
            props[f"prate_{i}"] = round(v, 6) if v is not None else None

        features.append({
            "type": "Feature",
            "geometry": {"type": "Polygon", "coordinates": [ring]},
            "properties": props,
        })

    geojson = {"type": "FeatureCollection", "features": features}

    print(f"Writing {OUT_GEO} …")
    with open(OUT_GEO, "w") as f:
        json.dump(geojson, f, separators=(",", ":"))

    meta = {
        "notches": [
            {"index": i, "name": n["name"], "label": n["label"],
             "y0": n["y0"], "y1": n["y1"]}
            for i, n in enumerate(NOTCHES)
        ],
        "variables": {
            "pdsi":  {"description": "PDSI anomaly (dimensionless)",         "unit": "dimensionless"},
            "air":   {"description": "2m air temperature anomaly",           "unit": "K"},
            "prate": {"description": "Precipitation rate anomaly",           "unit": "kg/m²/s"},
        },
        "note": (
            "LMR v2.1 (Tardif et al. 2019); 2°×2° grid; 0–1998 CE. "
            "Proxy network is densest in Europe and North America; "
            "reconstructions for East Asia, South Asia, and Southern Hemisphere "
            "carry greater uncertainty."
        ),
    }
    print(f"Writing {OUT_META} …")
    with open(OUT_META, "w") as f:
        json.dump(meta, f, indent=2)

    size_kb = OUT_GEO.stat().st_size / 1024
    print(f"Done. lmr_notches.geojson is {size_kb:.0f} KB ({len(features)} features).")


if __name__ == "__main__":
    main()
