"""
scripts/edop/load_hyde_cells.py
-------------------------------
Load HYDE 3.4 land-use data into temporal.hyde_cells and temporal.hyde_times.

Run after creating the tables:
    psql -d cedop -f sql/edop/create_hyde_cells.sql
    python scripts/edop/load_hyde_cells.py

Variables loaded (all in km² per cell):
    cropland     ← cropland.nc
    grazing      ← grazing_land.nc
    pasture      ← pasture.nc
    rangeland    ← rangeland.nc

Grid: 2,160 lat × 4,320 lon at 5-arcmin resolution (HYDE 3.4).
Land cells: 2,215,829 (identical NaN mask across all 4 variables).
Time steps: 128 (−10000 to 2025, irregular intervals).

cell_id is computed as row_idx * 4320 + col_idx, stable and reproducible.
Cell polygons are 5-arcmin bounding boxes in EPSG:4326.
area_km2 is computed via PostGIS ST_Area after all rows are inserted.
GIST index on geom is built last (much faster than during insert).
"""

import sys
import time
import numpy as np
import xarray as xr
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT))
from scripts.shared.db_utils import db_connect

HYDE_DIR  = ROOT / 'data' / 'hyde' / 'NetCDF'
NCOLS     = 4320
HALF_STEP = 1.0 / 24.0   # half of 5-arcmin = 1/12 degree / 2
STRIP     = 200           # lat rows processed per chunk (~900 MB peak across 4 vars)
BATCH     = 5_000         # rows per DB commit


def cell_wkt(lat: float, lon: float) -> str:
    """Return WKT for the 5-arcmin cell polygon centred on (lat, lon)."""
    w, e = lon - HALF_STEP, lon + HALF_STEP
    s, n = lat - HALF_STEP, lat + HALF_STEP
    return f'POLYGON(({w} {s},{e} {s},{e} {n},{w} {n},{w} {s}))'


def extract_years(time_coord) -> list[int]:
    """Extract integer years from a cftime time coordinate array."""
    return [int(t.year) for t in time_coord.values]


def insert_batch(cur, rows: list) -> None:
    cur.executemany(
        """
        INSERT INTO temporal.hyde_cells
            (cell_id, geom, cropland, grazing, pasture, rangeland)
        VALUES
            (%s, ST_GeomFromText(%s, 4326), %s::real[], %s::real[], %s::real[], %s::real[])
        """,
        rows,
    )


def main() -> None:
    t0 = time.time()

    print('Opening HYDE NetCDF files...')
    ds_c = xr.open_dataset(HYDE_DIR / 'cropland.nc')
    ds_g = xr.open_dataset(HYDE_DIR / 'grazing_land.nc')
    ds_p = xr.open_dataset(HYDE_DIR / 'pasture.nc')
    ds_r = xr.open_dataset(HYDE_DIR / 'rangeland.nc')

    lats  = ds_c.lat.values          # (2160,) descending N → S
    lons  = ds_c.lon.values          # (4320,) ascending  W → E
    n_lat = len(lats)
    years = extract_years(ds_c.time)  # list of 128 ints

    print(f'Grid : {n_lat} × {len(lons)}, {len(years)} time steps')
    print(f'Years: {years[0]} → {years[-1]}')

    with db_connect() as conn:
        with conn.cursor() as cur:

            # ── hyde_times ───────────────────────────────────────────────
            print('\nPopulating temporal.hyde_times...')
            cur.execute('TRUNCATE temporal.hyde_times')
            cur.executemany(
                'INSERT INTO temporal.hyde_times (step_idx, year_ce) VALUES (%s, %s)',
                [(i, y) for i, y in enumerate(years)],
            )
            conn.commit()
            print(f'  {len(years)} time steps recorded.')

            # ── hyde_cells ───────────────────────────────────────────────
            print('\nLoading hyde_cells (lat strips of', STRIP, 'rows)...')
            cur.execute('TRUNCATE temporal.hyde_cells')
            conn.commit()

            batch    = []
            inserted = 0

            for strip_start in range(0, n_lat, STRIP):
                strip_end = min(strip_start + STRIP, n_lat)
                sl = slice(strip_start, strip_end)

                # Shape after isel: (time=128, lat=strip, lon=4320)
                c = ds_c['cropland'].isel(lat=sl).values
                g = ds_g['grazing_land'].isel(lat=sl).values
                p = ds_p['pasture'].isel(lat=sl).values
                r = ds_r['rangeland'].isel(lat=sl).values

                # Transpose → (lat, lon, time) for row-major cell access
                c = c.transpose(1, 2, 0)   # (strip, 4320, 128)
                g = g.transpose(1, 2, 0)
                p = p.transpose(1, 2, 0)
                r = r.transpose(1, 2, 0)

                # NaN to 0 for land cells (land cells should never be NaN,
                # but guard against edge cases in the NetCDF)
                np.nan_to_num(c, copy=False, nan=0.0)
                np.nan_to_num(g, copy=False, nan=0.0)
                np.nan_to_num(p, copy=False, nan=0.0)
                np.nan_to_num(r, copy=False, nan=0.0)

                # Land mask (identical across all vars; use c for speed)
                # Re-derive from original: non-NaN in first time step of cropland
                c_orig = ds_c['cropland'].isel(lat=sl, time=0).values  # (strip, 4320)
                land_i, land_j = np.where(~np.isnan(c_orig))

                for i, j in zip(land_i, land_j):
                    row_idx = strip_start + i
                    lat     = float(lats[row_idx])
                    lon     = float(lons[j])
                    cell_id = int(row_idx) * NCOLS + int(j)

                    batch.append((
                        cell_id,
                        cell_wkt(lat, lon),
                        c[i, j, :].tolist(),
                        g[i, j, :].tolist(),
                        p[i, j, :].tolist(),
                        r[i, j, :].tolist(),
                    ))

                    if len(batch) >= BATCH:
                        insert_batch(cur, batch)
                        conn.commit()
                        inserted += len(batch)
                        batch = []
                        elapsed = time.time() - t0
                        print(f'  {inserted:>9,} / 2,215,829  ({elapsed:.0f}s)', end='\r')

            # Final partial batch
            if batch:
                insert_batch(cur, batch)
                conn.commit()
                inserted += len(batch)

            print(f'\n  {inserted:,} rows inserted ({time.time() - t0:.0f}s)')

            # ── area_km2 ─────────────────────────────────────────────────
            print('\nComputing area_km2 via ST_Area...')
            cur.execute("""
                UPDATE temporal.hyde_cells
                   SET area_km2 = ST_Area(geom::geography) / 1e6
            """)
            conn.commit()
            print(f'  Done ({time.time() - t0:.0f}s)')

            # ── GIST index on geom ───────────────────────────────────────
            print('\nBuilding GIST index on geom...')
            cur.execute("""
                CREATE INDEX IF NOT EXISTS idx_hyde_cells_geom
                ON temporal.hyde_cells USING GIST (geom)
            """)
            conn.commit()
            print(f'  Done ({time.time() - t0:.0f}s)')

            # ── Functional index on ST_Centroid(geom) ────────────────────
            # Required for ST_Within(ST_Centroid(hc.geom), basin.geom) to use
            # the index. Without it, every aggregation query does a full seq scan.
            print('\nBuilding functional index on ST_Centroid(geom)...')
            cur.execute("""
                CREATE INDEX IF NOT EXISTS idx_hyde_cells_centroid
                ON temporal.hyde_cells USING GIST (ST_Centroid(geom))
            """)
            conn.commit()
            print(f'  Done ({time.time() - t0:.0f}s)')

            # ── ANALYZE ──────────────────────────────────────────────────
            print('\nRunning ANALYZE to freshen planner statistics...')
            cur.execute('ANALYZE temporal.hyde_cells')
            conn.commit()
            print(f'  Done ({time.time() - t0:.0f}s)')

    for ds in [ds_c, ds_g, ds_p, ds_r]:
        ds.close()

    print(f'\nLoad complete. Total time: {(time.time() - t0) / 60:.1f} min')


if __name__ == '__main__':
    main()
