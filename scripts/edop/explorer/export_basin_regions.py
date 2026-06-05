"""Precompute basin → region lookup for the Explorer Compare tab.

For each L6 basin, assigns the region_id whose bounding box contains the basin
centroid. Basins outside all six boxes get null. Outputs a flat JSON dict:
  { "1060000010": "east_asia", "1060000020": "mediterranean", ... }

Output: app/static/explorer/basin_regions.json
Run from repo root: python scripts/edop/explorer/export_basin_regions.py
"""

import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', '..'))
from app.db.connection import db_connect

OUT = os.path.join(os.path.dirname(__file__), '..', '..', '..',
                   'app', 'static', 'explorer', 'basin_regions.json')

# Matches _REGIONS in app/api/routes.py — [west, south, east, north]
REGIONS = [
    {"id": "east_asia",        "bbox": [95,   18, 145,  55]},
    {"id": "south_asia",       "bbox": [60,    5, 100,  38]},
    {"id": "southwest_asia",   "bbox": [25,   13,  65,  45]},
    {"id": "mediterranean",    "bbox": [-10,  15,  42,  50]},
    {"id": "mesoamerica",      "bbox": [-120,  5, -65,  35]},
    {"id": "pacific_northwest","bbox": [-130, 40, -108, 56]},
]


def point_in_bbox(lon, lat, bbox):
    w, s, e, n = bbox
    return w <= lon <= e and s <= lat <= n


def main():
    conn = db_connect()
    try:
        print("Fetching basin06 centroids…", flush=True)
        with conn.cursor() as cur:
            cur.execute("""
                SELECT hybas_id,
                       ST_X(ST_Centroid(geom)) AS lon,
                       ST_Y(ST_Centroid(geom)) AS lat
                FROM public.basin06
                ORDER BY hybas_id
            """)
            rows = cur.fetchall()
    finally:
        conn.close()

    print(f"  {len(rows):,} basins fetched — assigning regions…", flush=True)

    lookup = {}
    unassigned = 0
    counts = {r["id"]: 0 for r in REGIONS}

    for hybas_id, lon, lat in rows:
        assigned = None
        for reg in REGIONS:
            if point_in_bbox(lon, lat, reg["bbox"]):
                assigned = reg["id"]
                counts[reg["id"]] += 1
                break
        if assigned:
            lookup[str(int(hybas_id))] = assigned
        else:
            unassigned += 1

    print("  Region counts:")
    for reg_id, n in counts.items():
        print(f"    {reg_id}: {n:,}")
    print(f"  Outside all regions (null): {unassigned:,}")

    out_path = os.path.abspath(OUT)
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    with open(out_path, 'w') as f:
        json.dump(lookup, f, separators=(',', ':'))

    size_kb = os.path.getsize(out_path) / 1024
    print(f"\nWritten: {out_path}  ({size_kb:.1f} KB)", flush=True)


if __name__ == '__main__':
    main()
