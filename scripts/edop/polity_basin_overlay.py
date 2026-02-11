"""
Areal interpolation demo: polity–basin overlay across time slices.

For a given polity (e.g. Northern Song), retrieves temporal geometries
from gaz.clio_polities, finds intersecting basin08 sub-basins, computes
area-weighted environmental signatures, and generates static map PNGs.

Usage:
    python scripts/edop/polity_basin_overlay.py

Output:
    output/edop/polity_overlay/northern_song_{year}.png
    output/edop/polity_overlay/northern_song_signatures.png
"""

import os
import sys
from pathlib import Path

import geopandas as gpd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
import pandas as pd
import psycopg
from shapely import wkb

# ── connection ──────────────────────────────────────────────────────
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from scripts.shared.db_utils import db_connect

# ── config ──────────────────────────────────────────────────────────
POLITY_NAME = "Northern Song"
OUTPUT_DIR = Path("output/edop/polity_overlay")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Signature fields to include in weighted composite (bands A–C)
SIG_FIELDS = {
    # Band A: Physiographic
    "ele_mt_smn": "Elev min (m)",
    "ele_mt_smx": "Elev max (m)",
    "slp_dg_sav": "Slope avg (°)",
    # Band B: Hydro-climatic
    "dis_m3_pyr": "Discharge (m³/s)",
    "run_mm_syr": "Runoff (mm/yr)",
    "gwt_cm_sav": "GW depth (cm)",
    # Band C: Bioclimatic
    "tmp_dc_syr": "Temp (°C×10)",
    "pre_mm_syr": "Precip (mm/yr)",
    "ari_ix_sav": "Aridity idx",
}

# Field to use for basin coloring on maps
COLOR_FIELD = "ari_ix_sav"
COLOR_LABEL = "Aridity Index"


def get_polity_geometries(conn, name):
    """Retrieve all temporal geometries for a named polity."""
    sql = """
        SELECT fromyear as from_year, toyear as to_year,
               ST_AsEWKB(geom) as geom
        FROM gaz.clio_polities
        WHERE name = %s
        ORDER BY fromyear
    """
    rows = conn.execute(sql, [name]).fetchall()
    records = []
    for r in rows:
        geom = wkb.loads(r[2])
        records.append({
            "from_year": r[0],
            "to_year": r[1],
            "geometry": geom,
        })
    return gpd.GeoDataFrame(records, crs="EPSG:4326")


def get_intersecting_basins(conn, polity_geom, sig_fields):
    """Find basins intersecting a polity, with intersection area weights."""
    fields_sql = ", ".join(f"b.{f}" for f in sig_fields)
    polity_wkt = polity_geom.wkt
    sql = f"""
        SELECT b.hybas_id,
               {fields_sql},
               ST_Area(ST_Intersection(b.geom, ST_GeomFromText(%(polity)s, 4326))::geography) AS intersect_area,
               ST_Area(b.geom::geography) AS basin_area,
               ST_AsEWKB(b.geom) AS geom,
               ST_AsEWKB(ST_Intersection(b.geom, ST_GeomFromText(%(polity)s, 4326))) AS clipped_geom
        FROM public.basin08 b
        WHERE ST_Intersects(b.geom, ST_GeomFromText(%(polity)s, 4326))
    """
    rows = conn.execute(sql, {"polity": polity_wkt}).fetchall()

    records = []
    for r in rows:
        rec = {"hybas_id": r[0]}
        for i, f in enumerate(sig_fields):
            rec[f] = r[1 + i]
        n = 1 + len(sig_fields)
        rec["intersect_area"] = r[n]
        rec["basin_area"] = r[n + 1]
        rec["geometry"] = wkb.loads(r[n + 2])
        rec["clipped_geometry"] = wkb.loads(r[n + 3])
        records.append(rec)

    gdf = gpd.GeoDataFrame(records, crs="EPSG:4326")
    total_intersect = gdf["intersect_area"].sum()
    gdf["weight"] = gdf["intersect_area"] / total_intersect
    return gdf


def compute_weighted_signature(basins_gdf, sig_fields):
    """Compute area-weighted mean of signature fields."""
    result = {}
    for f in sig_fields:
        vals = basins_gdf[f].astype(float)
        weights = basins_gdf["weight"]
        # Drop NaN pairs
        mask = vals.notna() & weights.notna()
        if mask.sum() > 0:
            result[f] = np.average(vals[mask], weights=weights[mask])
        else:
            result[f] = np.nan
    return result


def plot_overlay(polity_geom, basins_gdf, year_label, color_field, color_label, outpath):
    """Generate a map showing polity outline over colored basins."""
    fig, ax = plt.subplots(1, 1, figsize=(10, 8))

    # Plot clipped basin fragments colored by the signature field
    clipped_gdf = basins_gdf.set_geometry("clipped_geometry")
    vmin = basins_gdf[color_field].quantile(0.05)
    vmax = basins_gdf[color_field].quantile(0.95)

    clipped_gdf.plot(
        ax=ax,
        column=color_field,
        cmap="RdYlBu",
        edgecolor="gray",
        linewidth=0.3,
        alpha=0.8,
        vmin=vmin,
        vmax=vmax,
        legend=True,
        legend_kwds={"label": color_label, "shrink": 0.6},
    )

    # Plot full basin outlines (faint)
    basins_gdf.plot(
        ax=ax,
        facecolor="none",
        edgecolor="#cccccc",
        linewidth=0.3,
        alpha=0.5,
    )

    # Plot polity outline
    polity_gdf = gpd.GeoDataFrame([{"geometry": polity_geom}], crs="EPSG:4326")
    polity_gdf.plot(
        ax=ax,
        facecolor="none",
        edgecolor="#993333",
        linewidth=2.5,
    )

    ax.set_title(f"{POLITY_NAME} — {year_label}", fontsize=14, fontweight="bold")
    ax.set_xlabel("Longitude")
    ax.set_ylabel("Latitude")

    # Add basin count annotation
    n_basins = len(basins_gdf)
    ax.annotate(
        f"{n_basins} intersecting basins",
        xy=(0.02, 0.02), xycoords="axes fraction",
        fontsize=10, color="#666666",
    )

    plt.tight_layout()
    fig.savefig(outpath, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"  Saved: {outpath}")


def plot_signature_comparison(signatures, sig_fields, sig_labels, outpath):
    """Bar chart comparing weighted signatures across time slices."""
    years = list(signatures.keys())
    fields = list(sig_fields.keys())
    labels = [sig_labels[f] for f in fields]
    n_fields = len(fields)
    n_years = len(years)

    fig, axes = plt.subplots(3, 3, figsize=(14, 10))
    axes = axes.flatten()

    colors = ["#4a7c59", "#2166ac", "#993333"]

    for i, f in enumerate(fields):
        ax = axes[i]
        vals = [signatures[y].get(f, 0) for y in years]
        # Adjust temperature display
        display_vals = vals
        label = labels[i]
        if "Temp" in label:
            display_vals = [v / 10 for v in vals]
            label = label.replace("°C×10", "°C")

        bars = ax.bar(
            [str(y) for y in years],
            display_vals,
            color=colors[:n_years],
            edgecolor="white",
            width=0.6,
        )
        ax.set_title(label, fontsize=10, fontweight="bold")
        ax.tick_params(labelsize=9)

        # Add value labels on bars
        for bar, v in zip(bars, display_vals):
            ax.text(
                bar.get_x() + bar.get_width() / 2, bar.get_height(),
                f"{v:.1f}",
                ha="center", va="bottom", fontsize=8,
            )

    fig.suptitle(
        f"{POLITY_NAME} — Weighted Environmental Signatures Over Time",
        fontsize=14, fontweight="bold",
    )
    plt.tight_layout()
    fig.savefig(outpath, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"  Saved: {outpath}")


def plot_slide_series(slide_data, color_field, color_label, max_extent, outdir):
    """
    Generate a series of identically-framed maps for slide animation.

    Each map uses the same spatial extent (max_extent) and color scale,
    but shows only that year's polity boundary and its basins.

    slide_data: list of (year, polity_geom, basins_gdf)
    max_extent: (minx, miny, maxx, maxy) — shared bounding box
    """
    # Compute shared color scale across all basins from all years
    all_vals = pd.concat([d[2][color_field] for d in slide_data])
    vmin = all_vals.quantile(0.05)
    vmax = all_vals.quantile(0.95)

    minx, miny, maxx, maxy = max_extent
    pad_x = (maxx - minx) * 0.05
    pad_y = (maxy - miny) * 0.05

    for year, polity_geom, basins_gdf in slide_data:
        fig, ax = plt.subplots(1, 1, figsize=(10, 10))

        # Plot clipped basin fragments colored by signature field
        clipped_gdf = basins_gdf.set_geometry("clipped_geometry")
        clipped_gdf.plot(
            ax=ax,
            column=color_field,
            cmap="RdYlBu",
            edgecolor="gray",
            linewidth=0.3,
            alpha=0.8,
            vmin=vmin,
            vmax=vmax,
            legend=True,
            legend_kwds={"label": color_label, "shrink": 0.5},
        )

        # Plot polity outline
        polity_gdf = gpd.GeoDataFrame([{"geometry": polity_geom}], crs="EPSG:4326")
        polity_gdf.plot(
            ax=ax,
            facecolor="none",
            edgecolor="#993333",
            linewidth=2.5,
        )

        # Lock extent to the largest territory
        ax.set_xlim(minx - pad_x, maxx + pad_x)
        ax.set_ylim(miny - pad_y, maxy + pad_y)

        ax.set_title(
            f"{POLITY_NAME} — {year} CE",
            fontsize=16, fontweight="bold",
        )
        ax.set_xlabel("Longitude")
        ax.set_ylabel("Latitude")

        n_basins = len(basins_gdf)
        ax.annotate(
            f"{n_basins} intersecting basins",
            xy=(0.02, 0.02), xycoords="axes fraction",
            fontsize=11, color="#666666",
        )

        plt.tight_layout()
        outpath = outdir / f"slide_{year}.png"
        fig.savefig(outpath, dpi=150, bbox_inches="tight")
        plt.close(fig)
        print(f"  Saved: {outpath}")


def main():
    conn = db_connect()
    print(f"Querying polity geometries for '{POLITY_NAME}'...")
    polities = get_polity_geometries(conn, POLITY_NAME)
    print(f"  Found {len(polities)} time slices")

    # Select the 3 representative years
    slide_years = [962, 970, 980]

    signatures = {}
    slide_data = []

    for _, row in polities.iterrows():
        year = row["from_year"]
        if year not in slide_years:
            continue

        print(f"\nProcessing {POLITY_NAME} @ {year}...")

        basins = get_intersecting_basins(conn, row["geometry"], SIG_FIELDS)
        print(f"  {len(basins)} intersecting basins")

        sig = compute_weighted_signature(basins, SIG_FIELDS)
        signatures[year] = sig

        # Print signature summary
        for f, label in SIG_FIELDS.items():
            val = sig[f]
            if "Temp" in label:
                print(f"    {label}: {val/10:.1f} °C")
            else:
                print(f"    {label}: {val:.1f}")

        # Generate individual map
        year_label = f"{year} CE"
        outpath = OUTPUT_DIR / f"northern_song_{year}.png"
        plot_overlay(row["geometry"], basins, year_label, COLOR_FIELD, COLOR_LABEL, outpath)

        slide_data.append((year, row["geometry"], basins))

    # Generate slide series (fixed extent, fixed color scale)
    print("\nGenerating slide series...")
    # Use the 980 CE polity bounds as the shared extent
    max_geom = [d[1] for d in slide_data if d[0] == 980][0]
    max_extent = max_geom.bounds  # (minx, miny, maxx, maxy)
    plot_slide_series(slide_data, COLOR_FIELD, COLOR_LABEL, max_extent, OUTPUT_DIR)

    # Signature comparison chart
    print("\nGenerating signature comparison chart...")
    plot_signature_comparison(signatures, SIG_FIELDS, SIG_FIELDS, OUTPUT_DIR / "northern_song_signatures.png")

    conn.close()
    print("\nDone.")


if __name__ == "__main__":
    main()
