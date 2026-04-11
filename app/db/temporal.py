"""
app/db/temporal.py
------------------
Temporal enrichment lookups for the EDOP signature API.

Functions:
  get_temporal_context(lat, lon, year_start, year_end, vssi_min)
    Returns PDSI time series (LMR v2.1) and significant volcanic events
    (eVolv2k v4) for a given location and year range.

Array indexing note:
  PostgreSQL arrays are 1-indexed. Year Y CE is stored at pdsi[Y+1].
  Slice year_start–year_end → pdsi[year_start+1 : year_end+1].
"""

from typing import Any, Dict, List, Optional
from app.db.connection import db_connect


def get_temporal_context(
    lat: float,
    lon: float,
    year_start: int = 0,
    year_end: int = 1998,
    vssi_min: float = 5.0,
) -> Dict[str, Any]:
    """
    Return PDSI time series and volcanic events for a location and year range.

    Parameters
    ----------
    lat, lon      : query coordinates (used to find nearest 2° LMR grid cell)
    year_start    : first year CE to include (0–1998); default 0
    year_end      : last year CE to include (0–1998); default 1998
    vssi_min      : minimum volcanic stratospheric sulfur injection (Tg) to
                    include an eruption event; default 5.0 (major events only)

    Returns
    -------
    dict with keys:
      grid_cell       : {lat, lon} of the nearest LMR 2° grid cell
      year_start      : actual start year returned
      year_end        : actual end year returned
      pdsi_series     : list of {year, pdsi} dicts for the requested range
      pdsi_mean       : mean PDSI over the range
      pdsi_min        : minimum PDSI (most arid)
      pdsi_max        : maximum PDSI (most wet)
      volcanic_events : list of eruption dicts with vssi_tg >= vssi_min
    """
    # Clamp to valid range
    year_start = max(0, min(year_start, 1998))
    year_end   = max(year_start, min(year_end, 1998))

    # PostgreSQL array slice bounds (1-indexed)
    pg_start = year_start + 1
    pg_end   = year_end + 1

    # lon for PostGIS must be −180/180; LMR uses 0–358
    lon_geom = lon if lon >= 0 else lon

    with db_connect() as conn:
        with conn.cursor() as cur:

            # --- PDSI nearest-cell lookup ---
            cur.execute("""
                SELECT
                    lat,
                    lon,
                    pdsi[%(pg_start)s : %(pg_end)s] AS pdsi_slice
                FROM temporal.lmr_pdsi
                ORDER BY geom <-> ST_SetSRID(ST_MakePoint(%(lon)s, %(lat)s), 4326)
                LIMIT 1
            """, {"lat": lat, "lon": lon_geom, "pg_start": pg_start, "pg_end": pg_end})

            row = cur.fetchone()
            if row is None:
                return {"error": "No LMR grid cell found"}

            grid_lat, grid_lon, pdsi_slice = row

            # Build series and stats
            years = list(range(year_start, year_end + 1))
            series = [
                {"year": y, "pdsi": round(float(v), 4)}
                for y, v in zip(years, pdsi_slice)
                if v is not None
            ]
            values = [s["pdsi"] for s in series]
            pdsi_mean = round(sum(values) / len(values), 4) if values else None
            pdsi_min  = round(min(values), 4) if values else None
            pdsi_max  = round(max(values), 4) if values else None

            # Convert native LMR lon (0–358) to −180/180 for display
            grid_lon_display = float(grid_lon) if float(grid_lon) <= 180 else float(grid_lon) - 360

            # --- Volcanic events in year range ---
            cur.execute("""
                SELECT year_ad, month, vssi_tg, vssi_1sig, asymmetry, location, tephra
                FROM temporal.evolv2k_v4
                WHERE year_ad BETWEEN %(y0)s AND %(y1)s
                  AND vssi_tg >= %(vssi_min)s
                ORDER BY year_ad
            """, {"y0": year_start, "y1": year_end, "vssi_min": vssi_min})

            events = [
                {
                    "year_ad":   r[0],
                    "month":     r[1],
                    "vssi_tg":   round(float(r[2]), 2),
                    "vssi_1sig": round(float(r[3]), 2) if r[3] is not None else None,
                    "asymmetry": round(float(r[4]), 3) if r[4] is not None else None,
                    "location":  r[5],
                    "tephra":    r[6],
                }
                for r in cur.fetchall()
            ]

    return {
        "grid_cell":       {"lat": float(grid_lat), "lon": grid_lon_display},
        "year_start":      year_start,
        "year_end":        year_end,
        "pdsi_series":     series,
        "pdsi_mean":       pdsi_mean,
        "pdsi_min":        pdsi_min,
        "pdsi_max":        pdsi_max,
        "volcanic_events": events,
    }
