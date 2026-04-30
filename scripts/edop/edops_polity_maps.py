#!/usr/bin/env python3
"""
edops_polity_maps.py — Parameterized polity-basin choropleth map generator

Generates 1–3 time-slice maps for any polity in gaz.clio_polities, colored
by a chosen EDOPS Band A–C variable or HYDE 3.4 land-use variable. With 2 or
3 years, also produces a side-by-side comparison figure and a printed summary.

Usage:
    python scripts/edop/edops_polity_maps.py \
        --polity "Northern Song" --years 962 980 --variable aridity

    python scripts/edop/edops_polity_maps.py \
        --polity "Kingdom of Denmark" --years 999 1099 1199 \
        --variable hyde_cropland

    python scripts/edop/edops_polity_maps.py \
        --polity "Roman Republic" --years 1 300 --variable temp

Available static variables (Band A–C, from basin08):
    aridity, precip, temp, elevation, slope, discharge, runoff, groundwater
    Or any raw basin08 column name.

Available HYDE variables (Band T, temporal.hyde_cells):
    hyde_cropland, hyde_grazing, hyde_pasture, hyde_rangeland
"""

import argparse
import sys
from pathlib import Path

import geopandas as gpd
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from shapely import wkb

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from scripts.shared.db_utils import db_connect

# ── Static variable registry (basin08) ────────────────────────────────────────
# key → (basin08_col, display_label, scale_factor, colormap)
STATIC_VARIABLES = {
    "aridity":     ("ari_ix_sav", "Aridity Index",         1.0, "RdYlBu"),
    "precip":      ("pre_mm_syr", "Precipitation (mm/yr)",  1.0, "YlGnBu"),
    "temp":        ("tmp_dc_syr", "Temperature (°C)",       0.1, "RdYlBu_r"),
    "elevation":   ("ele_mt_smn", "Elevation min (m)",      1.0, "terrain"),
    "slope":       ("slp_dg_sav", "Slope avg (°)",          1.0, "OrRd"),
    "discharge":   ("dis_m3_pyr", "Discharge (m³/s)",       1.0, "Blues"),
    "runoff":      ("run_mm_syr", "Runoff (mm/yr)",         1.0, "YlGnBu"),
    "groundwater": ("gwt_cm_sav", "GW Table Depth (cm)",    1.0, "BrBG_r"),
}

# ── HYDE variable registry (temporal.hyde_cells) ──────────────────────────────
# key → (array_field, display_label, colormap)
HYDE_VARIABLES = {
    "hyde_cropland":  ("cropland",  "Cropland %",  "YlOrBr"),
    "hyde_grazing":   ("grazing",   "Grazing %",   "YlGn"),
    "hyde_pasture":   ("pasture",   "Pasture %",   "Greens"),
    "hyde_rangeland": ("rangeland", "Rangeland %", "BuGn"),
}

OUTPUT_DIR = Path("output/edop/polity_overlay")


def resolve_variable(var_arg):
    """
    Returns (kind, spec) where kind is 'static' or 'hyde'.
    For static: spec = (col, label, scale, cmap)
    For hyde:   spec = (field, label, cmap)
    """
    if var_arg in STATIC_VARIABLES:
        return "static", STATIC_VARIABLES[var_arg]
    if var_arg in HYDE_VARIABLES:
        return "hyde", HYDE_VARIABLES[var_arg]
    # Fall back to raw basin08 column name
    for col, label, scale, cmap in STATIC_VARIABLES.values():
        if var_arg == col:
            return "static", (col, label, scale, cmap)
    raise ValueError(
        f"Unknown variable '{var_arg}'.\n"
        f"  Static: {list(STATIC_VARIABLES)}\n"
        f"  HYDE:   {list(HYDE_VARIABLES)}\n"
        f"  Or use a raw basin08 column name."
    )


def get_polity_slice(conn, polity_name, target_year):
    """
    Fetch polity geometry for the row whose window contains target_year.
    Falls back to nearest fromyear if no exact window match.
    Returns (from_yr, to_yr, shapely_geom).
    """
    row = conn.execute("""
        SELECT fromyear, toyear, ST_AsEWKB(geom)
        FROM gaz.clio_polities
        WHERE name = %s AND fromyear <= %s AND toyear >= %s
        ORDER BY fromyear
        LIMIT 1
    """, [polity_name, target_year, target_year]).fetchone()

    if not row:
        row = conn.execute("""
            SELECT fromyear, toyear, ST_AsEWKB(geom)
            FROM gaz.clio_polities
            WHERE name = %s
            ORDER BY ABS(fromyear - %s)
            LIMIT 1
        """, [polity_name, target_year]).fetchone()
        if not row:
            raise ValueError(
                f"Polity '{polity_name}' not found in gaz.clio_polities."
            )
        print(f"  [note] No window containing {target_year}; "
              f"nearest row ({row[0]}–{row[1]}) used")

    return row[0], row[1], wkb.loads(row[2])


def get_basins_static(conn, polity_geom, col):
    """
    Intersect polity with basin08 and return a GeoDataFrame with
    clipped geometries, weights, and the target field value.
    """
    wkt = polity_geom.wkt
    rows = conn.execute(f"""
        SELECT
            b.hybas_id,
            b."{col}",
            ST_Area(ST_Intersection(b.geom,
                ST_GeomFromText(%(p)s, 4326))::geography) AS intersect_area,
            ST_AsEWKB(ST_Intersection(b.geom,
                ST_GeomFromText(%(p)s, 4326))) AS clipped_geom
        FROM public.basin08 b
        WHERE ST_Intersects(b.geom, ST_GeomFromText(%(p)s, 4326))
    """, {"p": wkt}).fetchall()

    records = [
        {
            "hybas_id":         r[0],
            "value":            r[1] if r[1] is not None else np.nan,
            "intersect_area":   float(r[2]),
            "clipped_geometry": wkb.loads(r[3]),
        }
        for r in rows
    ]
    gdf = gpd.GeoDataFrame(records, geometry="clipped_geometry", crs="EPSG:4326")
    gdf["weight"] = gdf["intersect_area"] / gdf["intersect_area"].sum()
    return gdf, None  # None = no separate hyde_year


def get_basins_hyde(conn, polity_geom, hyde_field, target_year):
    """
    For each basin intersecting polity_geom, compute area-weighted
    land-use % from HYDE 3.4 at the nearest step <= target_year.

    Uses the functional centroid index on hyde_cells for performance.
    Returns (GeoDataFrame, hyde_year_used).
    """
    wkt = polity_geom.wkt
    rows = conn.execute(f"""
        WITH target_step AS (
            SELECT step_idx, year_ce
            FROM temporal.hyde_times
            WHERE year_ce <= %(year)s
            ORDER BY year_ce DESC
            LIMIT 1
        ),
        polity_basins AS (
            SELECT
                b.hybas_id,
                b.geom AS basin_geom,
                ST_Area(ST_Intersection(b.geom,
                    ST_GeomFromText(%(p)s, 4326))::geography) AS intersect_area,
                ST_AsEWKB(ST_Intersection(b.geom,
                    ST_GeomFromText(%(p)s, 4326))) AS clipped_geom,
                ST_Area(b.geom::geography) / 1e6 AS basin_area_km2
            FROM public.basin08 b
            WHERE ST_Intersects(b.geom, ST_GeomFromText(%(p)s, 4326))
        ),
        hyde_per_basin AS (
            SELECT
                pb.hybas_id,
                SUM(hc.{hyde_field}[ts.step_idx + 1]) AS field_km2,
                SUM(hc.area_km2)                       AS cell_area_km2
            FROM polity_basins pb
            JOIN temporal.hyde_cells hc
                ON ST_Within(ST_Centroid(hc.geom), pb.basin_geom)
            CROSS JOIN target_step ts
            GROUP BY pb.hybas_id
        )
        SELECT
            pb.hybas_id,
            COALESCE(hpb.field_km2, 0) / NULLIF(hpb.cell_area_km2, 0) * 100
                AS field_pct,
            pb.intersect_area,
            pb.clipped_geom,
            ts.year_ce AS hyde_year
        FROM polity_basins pb
        LEFT JOIN hyde_per_basin hpb ON hpb.hybas_id = pb.hybas_id
        CROSS JOIN target_step ts
    """, {"p": wkt, "year": target_year}).fetchall()

    records = [
        {
            "hybas_id":         r[0],
            "value":            float(r[1]) if r[1] is not None else 0.0,
            "intersect_area":   float(r[2]),
            "clipped_geometry": wkb.loads(r[3]),
        }
        for r in rows
    ]
    hyde_year = int(rows[0][4]) if rows else target_year

    gdf = gpd.GeoDataFrame(records, geometry="clipped_geometry", crs="EPSG:4326")
    gdf["weight"] = gdf["intersect_area"] / gdf["intersect_area"].sum()
    return gdf, hyde_year


def weighted_mean(gdf, scale=1.0):
    """Area-weighted mean of 'value' with optional scale factor."""
    vals = gdf["value"].astype(float) * scale
    mask = vals.notna() & gdf["weight"].notna()
    if not mask.any():
        return np.nan
    return float(np.average(vals[mask], weights=gdf["weight"][mask]))


def draw_map(ax, polity_geom, basins, title, label, scale, cmap, vmin, vmax, xlim, ylim):
    """Render one choropleth panel onto ax."""
    clipped = basins.copy()
    clipped["display"] = clipped["value"].astype(float) * scale

    clipped.plot(
        ax=ax,
        column="display",
        cmap=cmap,
        edgecolor="#cccccc",
        linewidth=0.2,
        alpha=0.85,
        vmin=vmin,
        vmax=vmax,
        legend=True,
        legend_kwds={"label": label, "shrink": 0.65},
    )
    gpd.GeoDataFrame([{"geometry": polity_geom}], crs="EPSG:4326").plot(
        ax=ax, facecolor="none", edgecolor="#993333", linewidth=2.0
    )
    ax.set_xlim(*xlim)
    ax.set_ylim(*ylim)
    ax.set_facecolor("white")
    ax.set_title(title, fontsize=12, fontweight="bold")
    ax.annotate(
        f"{len(basins):,} basins",
        xy=(0.02, 0.02), xycoords="axes fraction",
        fontsize=9, color="#555555",
    )


def main():
    parser = argparse.ArgumentParser(
        description="EDOPS polity choropleth map generator"
    )
    parser.add_argument("--polity",   required=True,
                        help='Polity name as in gaz.clio_polities')
    parser.add_argument("--years",    nargs="+", type=int, required=True,
                        help="1–3 target years, e.g. --years 999 1099 1199")
    parser.add_argument("--variable", default="aridity",
                        help="Variable name (default: aridity)")
    args = parser.parse_args()

    if len(args.years) > 3:
        sys.exit("This script supports 1–3 years.")

    kind, spec = resolve_variable(args.variable)

    if kind == "static":
        col, label, scale, cmap = spec
    else:
        hyde_field, label, cmap = spec
        scale = 1.0

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    slug = args.polity.lower().replace(" ", "_")

    print(f"\nPolity:   {args.polity}")
    print(f"Years:    {args.years}")
    print(f"Variable: {label}  [{'basin08:' + col if kind == 'static' else 'hyde:' + hyde_field}]")
    print("-" * 52)

    conn = db_connect()

    # Each slice: (target_yr, from_yr, to_yr, polity_geom, basins_gdf, wmean, hyde_year)
    slices = []
    for yr in args.years:
        print(f"\n{yr} CE:")
        from_yr, to_yr, geom = get_polity_slice(conn, args.polity, yr)
        print(f"  Cliopatria window: {from_yr}–{to_yr}")

        if kind == "static":
            basins, hyde_year = get_basins_static(conn, geom, col)
        else:
            print(f"  Querying HYDE 3.4 (nearest step ≤ {yr})...")
            basins, hyde_year = get_basins_hyde(conn, geom, hyde_field, yr)
            print(f"  HYDE step used: {hyde_year} CE")

        print(f"  Intersecting basins: {len(basins):,}")
        wmean = weighted_mean(basins, scale)
        print(f"  Weighted mean {label}: {wmean:.2f}")
        slices.append((yr, from_yr, to_yr, geom, basins, wmean, hyde_year))

    conn.close()

    # Shared color scale across all slices
    all_vals = pd.concat([s[4]["value"].astype(float) * scale for s in slices])
    vmin = float(all_vals.quantile(0.05))
    vmax = float(all_vals.quantile(0.95))

    # Shared spatial extent: largest polity bounding box + 5% pad
    largest_geom = max(slices, key=lambda s: s[4]["intersect_area"].sum())[3]
    minx, miny, maxx, maxy = largest_geom.bounds
    px = (maxx - minx) * 0.05
    py = (maxy - miny) * 0.05
    xlim = (minx - px, maxx + px)
    ylim = (miny - py, maxy + py)

    # Individual maps
    print()
    for target_yr, from_yr, to_yr, geom, basins, wmean, hyde_year in slices:
        if hyde_year and hyde_year != target_yr:
            title = f"{args.polity} — {target_yr} CE  [{label}: {wmean:.1f}]\n(HYDE {hyde_year} CE)"
        else:
            title = f"{args.polity} — {target_yr} CE  ({label}: {wmean:.1f})"
        fig, ax = plt.subplots(figsize=(10, 8))
        fig.patch.set_facecolor("white")
        draw_map(ax, geom, basins, title, label, scale, cmap, vmin, vmax, xlim, ylim)
        plt.tight_layout()
        outpath = OUTPUT_DIR / f"{slug}_{target_yr}_{args.variable}.png"
        fig.savefig(outpath, dpi=150, bbox_inches="tight", facecolor="white")
        plt.close(fig)
        print(f"Saved: {outpath}")

    # Multi-panel comparison figure (2 or 3 years)
    if len(slices) >= 2:
        n = len(slices)
        fig, axes = plt.subplots(1, n, figsize=(9 * n, 8))
        fig.patch.set_facecolor("white")
        for ax, (target_yr, from_yr, to_yr, geom, basins, wmean, hyde_year) in zip(axes, slices):
            if hyde_year and hyde_year != target_yr:
                panel_title = f"{target_yr} CE  (HYDE {hyde_year})\nmean: {wmean:.1f}"
            else:
                panel_title = f"{target_yr} CE\nmean: {wmean:.1f}"
            draw_map(ax, geom, basins, panel_title, label, scale, cmap, vmin, vmax, xlim, ylim)
        fig.suptitle(f"{args.polity} — {label}", fontsize=15, fontweight="bold")
        plt.tight_layout()
        outpath = OUTPUT_DIR / f"{slug}_comparison_{args.variable}.png"
        fig.savefig(outpath, dpi=150, bbox_inches="tight", facecolor="white")
        plt.close(fig)
        print(f"Saved: {outpath}")

    # Printed summary
    print(f"\n── Signature Summary {'─' * 32}")
    hyde_col = "  HYDE step" if kind == "hyde" else ""
    print(f"{'Year':>6}  {'Basins':>8}  {label:>18}  {'Clio window':>14}{hyde_col}")
    for target_yr, from_yr, to_yr, geom, basins, wmean, hyde_year in slices:
        hyde_note = f"  {hyde_year}" if kind == "hyde" else ""
        print(f"{target_yr:>6}  {len(basins):>8,}  {wmean:>18.2f}  {from_yr}–{to_yr:<10}{hyde_note}")
    if len(slices) >= 2:
        delta = slices[-1][5] - slices[0][5]
        pct   = (delta / slices[0][5] * 100) if slices[0][5] else 0
        print(f"\n  Change {args.years[0]}→{args.years[-1]}: {delta:+.2f}  ({pct:+.1f}%)")
    print()


if __name__ == "__main__":
    main()
