#!/usr/bin/env python3
"""
Populate WHC matrix table for 258 World Heritage Cities.

This script:
1. Reads cities from wh_cities table (where basin_id IS NOT NULL)
2. Queries basin08 for each city's basin data
3. Uses existing edop_norm_ranges for normalization
4. Populates whc_matrix with normalized environmental signatures

Prerequisites:
- wh_cities table with basin_id populated
- edop_norm_ranges table with global min/max values
- whc_matrix_schema.sql run to create tables

Usage:
    python scripts/populate_whc_matrix.py
"""

import os
from pathlib import Path

import psycopg

# ---------------------------------------------------------------------------
# Configuration (same field definitions as populate_matrix.py)
# ---------------------------------------------------------------------------

NUMERICAL_FIELDS = [
    # A: Physiographic Bedrock
    ("ele_mt_smn", "elev_min"),
    ("ele_mt_smx", "elev_max"),
    ("slp_dg_sav", "slope_avg"),
    ("slp_dg_uav", "slope_upstream"),
    ("sgr_dk_sav", "stream_gradient"),
    ("kar_pc_sse", "karst"),
    ("kar_pc_use", "karst_upstream"),
    # B: Hydro-Climatic Baselines
    ("dis_m3_pyr", "discharge_yr"),
    ("dis_m3_pmn", "discharge_min"),
    ("dis_m3_pmx", "discharge_max"),
    ("ria_ha_ssu", "river_area"),
    ("ria_ha_usu", "river_area_upstream"),
    ("run_mm_syr", "runoff"),
    ("gwt_cm_sav", "gw_table_depth"),
    ("cly_pc_sav", "pct_clay"),
    ("slt_pc_sav", "pct_silt"),
    ("snd_pc_sav", "pct_sand"),
    # C: Bioclimatic Proxies
    ("tmp_dc_syr", "temp_yr"),
    ("tmp_dc_smn", "temp_min"),
    ("tmp_dc_smx", "temp_max"),
    ("pre_mm_syr", "precip_yr"),
    ("ari_ix_sav", "aridity"),
    ("wet_pc_sg1", "wet_pct_grp1"),
    ("wet_pc_sg2", "wet_pct_grp2"),
    ("prm_pc_sse", "permafrost_extent"),
    # D: Anthropocene Markers
    ("rev_mc_usu", "reservoir_vol"),
    ("crp_pc_sse", "cropland_extent"),
    ("ppd_pk_sav", "pop_density"),
    ("hft_ix_s09", "human_footprint_09"),
    ("gdp_ud_sav", "gdp_avg"),
    ("hdi_ix_sav", "human_dev_idx"),
]

TEMP_FIELDS = {"tmp_dc_syr", "tmp_dc_smn", "tmp_dc_smx"}

CATEGORICAL_FIELDS = [
    ("tec_cl_smj", "tec", "eco_id"),
    ("fec_cl_smj", "fec", "eco_id"),
    ("cls_cl_smj", "cls", "gens_id"),
    ("glc_cl_smj", "glc", "glc_id"),
    ("clz_cl_smj", "clz", "genz_id"),
    ("lit_cl_smj", "lit", "glim_id"),
    ("tbi_cl_smj", "tbi", "biome_id"),
    ("fmh_cl_smj", "fmh", "mht_id"),
    ("wet_cl_smj", "wet", "glwd_id"),
]

PNV_FIELDS = [f"pnv_pc_s{i:02d}" for i in range(1, 16)]


def get_db_connection():
    """Create database connection from environment variables."""
    return psycopg.connect(
        host=os.environ.get("PGHOST", "localhost"),
        port=os.environ.get("PGPORT", "5435"),
        dbname=os.environ.get("PGDATABASE", "edop"),
        user=os.environ.get("PGUSER", "postgres"),
        password=os.environ.get("PGPASSWORD", ""),
    )


def get_cities_with_basins(cur) -> list[dict]:
    """Get all cities with basin_id from wh_cities."""
    cur.execute("""
        SELECT id, city, country, region, basin_id
        FROM wh_cities
        WHERE basin_id IS NOT NULL
        ORDER BY id
    """)

    return [
        {
            "id": row[0],
            "city": row[1],
            "country": row[2],
            "region": row[3],
            "basin_id": row[4],
        }
        for row in cur.fetchall()
    ]


def get_basin_data(cur, basin_id: int) -> dict | None:
    """Query basin08 for environmental data by basin_id."""
    num_cols = ", ".join(f"b.{col}" for col, _ in NUMERICAL_FIELDS)
    cat_cols = ", ".join(f"b.{col}" for col, _, _ in CATEGORICAL_FIELDS)
    pnv_cols = ", ".join(f"b.{col}" for col in PNV_FIELDS)

    sql = f"""
        SELECT {num_cols}, {cat_cols}, {pnv_cols}
        FROM basin08 b
        WHERE b.id = %s
    """

    cur.execute(sql, (basin_id,))
    row = cur.fetchone()

    if not row:
        return None

    result = {}
    idx = 0

    # Numerical fields
    for _, name in NUMERICAL_FIELDS:
        result[name] = row[idx]
        idx += 1

    # Categorical fields
    for _, prefix, _ in CATEGORICAL_FIELDS:
        result[f"cat_{prefix}"] = row[idx]
        idx += 1

    # PNV fields
    for i in range(15):
        result[f"pnv_{i+1:02d}"] = row[idx]
        idx += 1

    return result


def get_norm_ranges(cur) -> dict:
    """Get normalization ranges from edop_norm_ranges table."""
    cur.execute("SELECT * FROM edop_norm_ranges WHERE id = 1")
    row = cur.fetchone()

    if not row:
        raise RuntimeError("edop_norm_ranges table is empty - run populate_matrix.py first")

    # Get column names
    col_names = [desc[0] for desc in cur.description]

    # Build dict (skip 'id' column)
    return {col_names[i]: row[i] for i in range(1, len(col_names))}


def get_matrix_columns(cur) -> set[str]:
    """Get list of columns in whc_matrix table."""
    cur.execute("""
        SELECT column_name FROM information_schema.columns
        WHERE table_name = 'whc_matrix'
    """)
    return {row[0] for row in cur.fetchall()}


def normalize_value(value, min_val, max_val) -> float | None:
    """Normalize a value to 0-1 range."""
    if value is None or min_val is None or max_val is None:
        return None
    value = float(value)
    min_val = float(min_val)
    max_val = float(max_val)
    if max_val == min_val:
        return 0.5
    return (value - min_val) / (max_val - min_val)


def build_matrix_row(city: dict, basin_data: dict, ranges: dict, valid_columns: set) -> dict:
    """Build a single matrix row for a city."""
    if not basin_data:
        return {"city_id": city["id"]}

    row = {"city_id": city["id"]}

    # Normalized numerical fields
    for basin_col, name in NUMERICAL_FIELDS:
        raw_value = basin_data.get(name)

        # Temperature fields need /10 conversion
        if name in ("temp_yr", "temp_min", "temp_max") and raw_value is not None:
            raw_value = raw_value / 10.0

        min_val = ranges.get(f"{name}_min")
        max_val = ranges.get(f"{name}_max")
        norm_val = normalize_value(raw_value, min_val, max_val)

        col_name = f"n_{name}"
        if col_name in valid_columns:
            row[col_name] = norm_val

    # PNV share fields (rescale from 0-100 to 0-1)
    for i in range(1, 16):
        pnv_val = basin_data.get(f"pnv_{i:02d}")
        col_name = f"pnv_{i:02d}"
        if col_name in valid_columns:
            row[col_name] = (pnv_val / 100.0) if pnv_val is not None else 0.0

    # Categorical one-hot fields (only if column exists in table)
    for _, prefix, _ in CATEGORICAL_FIELDS:
        cat_value = basin_data.get(f"cat_{prefix}")
        if cat_value is not None:
            col_name = f"cat_{prefix}_{cat_value}"
            if col_name in valid_columns:
                row[col_name] = 1

    return row


def insert_matrix_row(cur, row: dict):
    """Insert a single matrix row."""
    cols = list(row.keys())
    placeholders = ", ".join(["%s"] * len(cols))
    col_names = ", ".join(cols)

    sql = f"INSERT INTO whc_matrix ({col_names}) VALUES ({placeholders})"
    cur.execute(sql, [row[c] for c in cols])


def main():
    print("=" * 60)
    print("WHC Matrix Population Script")
    print("=" * 60)

    print("\n1. Connecting to database...")
    conn = get_db_connection()

    try:
        with conn.cursor() as cur:
            # Get cities with basin_id
            print("\n2. Loading cities with basin_id...")
            cities = get_cities_with_basins(cur)
            print(f"   Found {len(cities)} cities with basin data")

            # Get normalization ranges
            print("\n3. Loading normalization ranges...")
            ranges = get_norm_ranges(cur)
            print(f"   Loaded {len(ranges)} range values")

            # Get valid columns in whc_matrix
            print("\n4. Checking whc_matrix columns...")
            valid_columns = get_matrix_columns(cur)
            print(f"   Table has {len(valid_columns)} columns")

            # Clear existing data
            print("\n5. Clearing existing whc_matrix data...")
            cur.execute("DELETE FROM whc_matrix")

            # Process each city
            print("\n6. Building and inserting matrix rows...")
            inserted = 0
            skipped = 0

            for i, city in enumerate(cities):
                # Get basin data
                basin_data = get_basin_data(cur, city["basin_id"])

                if basin_data:
                    row = build_matrix_row(city, basin_data, ranges, valid_columns)
                    insert_matrix_row(cur, row)
                    inserted += 1
                else:
                    print(f"   Warning: No basin data for {city['city']} (basin_id={city['basin_id']})")
                    skipped += 1

                if (i + 1) % 50 == 0:
                    print(f"   Processed {i + 1}/{len(cities)} cities...")

            # Commit
            conn.commit()
            print(f"\n   Inserted: {inserted}, Skipped: {skipped}")

            # Summary
            print("\n" + "=" * 60)
            print("SUMMARY")
            print("=" * 60)

            cur.execute("SELECT COUNT(*) FROM whc_matrix")
            print(f"whc_matrix rows: {cur.fetchone()[0]}")

            # Sample some data
            print("\nSample rows (first 5):")
            cur.execute("""
                SELECT m.city_id, c.city, c.country,
                       m.n_temp_yr, m.n_precip_yr, m.n_elev_min
                FROM whc_matrix m
                JOIN wh_cities c ON m.city_id = c.id
                ORDER BY m.city_id
                LIMIT 5
            """)
            for row in cur.fetchall():
                print(f"  {row[0]}: {row[1]}, {row[2]} | temp={row[3]:.3f}, precip={row[4]:.3f}, elev={row[5]:.3f}" if row[3] else f"  {row[0]}: {row[1]}, {row[2]} | (null values)")

    except Exception as e:
        conn.rollback()
        print(f"\nERROR: {e}")
        raise
    finally:
        conn.close()

    print("\nDone!")


if __name__ == "__main__":
    main()
