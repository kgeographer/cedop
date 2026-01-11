#!/usr/bin/env python3
"""
Generate sparse feature matrix for all basin08 basins.

Creates a 190k × 1561 sparse matrix using the same feature definitions
as the 20 WH sites pilot (edop_matrix), suitable for PCA and clustering.

Features:
- 27 numerical fields (normalized 0-1)
- 15 PNV fields (scaled 0-1)
- 1519 categorical one-hot columns (9 lookup tables)

Output:
- output/basin08_sparse_matrix.npz (scipy sparse matrix)
- output/basin08_feature_names.json (column names for interpretation)
- output/basin08_basin_ids.npy (basin IDs in row order)

Usage:
    python scripts/basin08_sparse_matrix.py
"""

import json
import os
import sys
from pathlib import Path

import numpy as np
from scipy import sparse
import psycopg

# ---------------------------------------------------------------------------
# Configuration (same as populate_matrix.py)
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
    ("tec_cl_smj", "tec", "eco_id", "lu_tec"),
    ("fec_cl_smj", "fec", "eco_id", "lu_fec"),
    ("cls_cl_smj", "cls", "gens_id", "lu_cls"),
    ("glc_cl_smj", "glc", "glc_id", "lu_glc"),
    ("clz_cl_smj", "clz", "genz_id", "lu_clz"),
    ("lit_cl_smj", "lit", "glim_id", "lu_lit"),
    ("tbi_cl_smj", "tbi", "biome_id", "lu_tbi"),
    ("fmh_cl_smj", "fmh", "mht_id", "lu_fmh"),
    ("wet_cl_smj", "wet", "glwd_id", "lu_wet"),
]

PNV_FIELDS = [f"pnv_pc_s{i:02d}" for i in range(1, 16)]

OUTPUT_DIR = Path(__file__).parent.parent / "output"


def get_db_connection():
    """Create database connection from environment variables."""
    return psycopg.connect(
        host=os.environ.get("PGHOST", "localhost"),
        port=os.environ.get("PGPORT", "5435"),
        dbname=os.environ.get("PGDATABASE", "edop"),
        user=os.environ.get("PGUSER", "postgres"),
        password=os.environ.get("PGPASSWORD", ""),
    )


def get_global_ranges(cur) -> dict:
    """Query global min/max for numerical fields from edop_norm_ranges or compute."""
    # Try to use existing norm_ranges first
    cur.execute("SELECT COUNT(*) FROM edop_norm_ranges")
    if cur.fetchone()[0] > 0:
        cur.execute("SELECT * FROM edop_norm_ranges WHERE id = 1")
        row = cur.fetchone()
        cols = [desc[0] for desc in cur.description]
        return dict(zip(cols, row))

    # Compute from basin08 if not available
    print("   Computing global ranges from basin08...")
    agg_parts = []
    for col, name in NUMERICAL_FIELDS:
        if col in TEMP_FIELDS:
            agg_parts.append(f"MIN({col}/10.0) AS {name}_min")
            agg_parts.append(f"MAX({col}/10.0) AS {name}_max")
        else:
            agg_parts.append(f"MIN({col}) AS {name}_min")
            agg_parts.append(f"MAX({col}) AS {name}_max")

    sql = f"SELECT {', '.join(agg_parts)} FROM basin08"
    cur.execute(sql)
    row = cur.fetchone()

    result = {}
    idx = 0
    for _, name in NUMERICAL_FIELDS:
        result[f"{name}_min"] = row[idx]
        result[f"{name}_max"] = row[idx + 1]
        idx += 2
    return result


def get_categorical_ids(cur) -> dict:
    """Get all valid IDs for each categorical lookup table, sorted."""
    result = {}
    for _, prefix, id_col, table in CATEGORICAL_FIELDS:
        cur.execute(f"SELECT DISTINCT {id_col} FROM {table} ORDER BY {id_col}")
        result[prefix] = [row[0] for row in cur.fetchall()]
    return result


def build_feature_names(cat_ids: dict) -> list[str]:
    """Build ordered list of all feature names."""
    names = []

    # Numerical fields
    for _, name in NUMERICAL_FIELDS:
        names.append(f"n_{name}")

    # PNV fields
    for i in range(1, 16):
        names.append(f"pnv_{i:02d}")

    # Categorical one-hot fields
    for _, prefix, _, _ in CATEGORICAL_FIELDS:
        for id_val in cat_ids[prefix]:
            names.append(f"cat_{prefix}_{id_val}")

    return names


def normalize_value(value, min_val, max_val) -> float:
    """Normalize a value to 0-1 range."""
    if value is None or min_val is None or max_val is None:
        return 0.0  # Default for missing values
    value = float(value)
    min_val = float(min_val)
    max_val = float(max_val)
    if max_val == min_val:
        return 0.5
    return (value - min_val) / (max_val - min_val)


def main():
    print("Basin08 Sparse Matrix Generation")
    print("=" * 60)

    # Ensure output directory exists
    OUTPUT_DIR.mkdir(exist_ok=True)

    conn = get_db_connection()

    try:
        with conn.cursor() as cur:
            # Get global ranges
            print("\n1. Loading global normalization ranges...")
            ranges = get_global_ranges(cur)
            print(f"   Loaded {len(ranges)} range values")

            # Get categorical IDs
            print("\n2. Loading categorical lookup IDs...")
            cat_ids = get_categorical_ids(cur)
            total_cats = sum(len(ids) for ids in cat_ids.values())
            print(f"   Loaded {total_cats} categorical IDs across {len(cat_ids)} tables")
            for prefix, ids in cat_ids.items():
                print(f"      {prefix}: {len(ids)} categories")

            # Build feature names
            feature_names = build_feature_names(cat_ids)
            n_features = len(feature_names)
            n_numerical = len(NUMERICAL_FIELDS)
            n_pnv = len(PNV_FIELDS)
            n_categorical = total_cats
            print(f"\n   Total features: {n_features}")
            print(f"      Numerical: {n_numerical}")
            print(f"      PNV: {n_pnv}")
            print(f"      Categorical: {n_categorical}")

            # Build categorical ID to column index mapping
            cat_col_offset = n_numerical + n_pnv
            cat_id_to_col = {}
            col_idx = cat_col_offset
            for _, prefix, _, _ in CATEGORICAL_FIELDS:
                cat_id_to_col[prefix] = {}
                for id_val in cat_ids[prefix]:
                    cat_id_to_col[prefix][id_val] = col_idx
                    col_idx += 1

            # Count basins
            print("\n3. Counting basins...")
            cur.execute("SELECT COUNT(*) FROM basin08")
            n_basins = cur.fetchone()[0]
            print(f"   Found {n_basins:,} basins")

            # Build column list for query
            num_cols = ", ".join(col for col, _ in NUMERICAL_FIELDS)
            pnv_cols = ", ".join(PNV_FIELDS)
            cat_cols = ", ".join(col for col, _, _, _ in CATEGORICAL_FIELDS)

            # Query all basins
            print("\n4. Querying basin data...")
            sql = f"""
                SELECT hybas_id, {num_cols}, {pnv_cols}, {cat_cols}
                FROM basin08
                ORDER BY hybas_id
            """
            cur.execute(sql)

            # Prepare arrays
            print("\n5. Building sparse matrix...")
            basin_ids = []

            # Dense arrays for numerical + PNV
            dense_data = np.zeros((n_basins, n_numerical + n_pnv), dtype=np.float32)

            # Sparse data for categorical (COO format)
            sparse_rows = []
            sparse_cols = []
            sparse_vals = []

            # Process in batches to show progress
            batch_size = 10000
            row_idx = 0

            while True:
                rows = cur.fetchmany(batch_size)
                if not rows:
                    break

                for row in rows:
                    basin_id = row[0]
                    basin_ids.append(basin_id)

                    col = 1  # Skip basin_id

                    # Numerical fields
                    for i, (db_col, name) in enumerate(NUMERICAL_FIELDS):
                        raw_val = row[col]
                        # Temperature conversion
                        if db_col in TEMP_FIELDS and raw_val is not None:
                            raw_val = raw_val / 10.0

                        min_val = ranges.get(f"{name}_min")
                        max_val = ranges.get(f"{name}_max")
                        dense_data[row_idx, i] = normalize_value(raw_val, min_val, max_val)
                        col += 1

                    # PNV fields (scale 0-100 to 0-1)
                    for i in range(n_pnv):
                        pnv_val = row[col]
                        if pnv_val is not None:
                            dense_data[row_idx, n_numerical + i] = pnv_val / 100.0
                        col += 1

                    # Categorical fields (sparse one-hot)
                    for _, prefix, _, _ in CATEGORICAL_FIELDS:
                        cat_val = row[col]
                        if cat_val is not None and cat_val in cat_id_to_col[prefix]:
                            sparse_rows.append(row_idx)
                            sparse_cols.append(cat_id_to_col[prefix][cat_val])
                            sparse_vals.append(1)
                        col += 1

                    row_idx += 1

                print(f"   Processed {row_idx:,} / {n_basins:,} basins ({100*row_idx/n_basins:.1f}%)")

            print(f"\n   Dense block shape: {dense_data.shape}")
            print(f"   Sparse entries: {len(sparse_vals):,}")

            # Build sparse categorical matrix
            print("\n6. Assembling final sparse matrix...")
            sparse_cat = sparse.coo_matrix(
                (sparse_vals, (sparse_rows, sparse_cols)),
                shape=(n_basins, n_features),
                dtype=np.float32
            )

            # Convert dense to sparse and combine
            sparse_dense = sparse.csr_matrix(dense_data)

            # Combine: put dense values in first columns of sparse matrix
            # The sparse_cat already has zeros in the first n_numerical+n_pnv columns
            # We need to add the dense values there
            final_matrix = sparse_cat.tocsr()
            final_matrix[:, :n_numerical + n_pnv] = sparse_dense

            print(f"   Final matrix shape: {final_matrix.shape}")
            print(f"   Non-zero entries: {final_matrix.nnz:,}")
            print(f"   Sparsity: {100 * (1 - final_matrix.nnz / (n_basins * n_features)):.2f}%")

            # Save outputs
            print("\n7. Saving outputs...")

            # Sparse matrix
            matrix_path = OUTPUT_DIR / "basin08_sparse_matrix.npz"
            sparse.save_npz(matrix_path, final_matrix.tocsr())
            print(f"   Saved: {matrix_path}")
            print(f"   File size: {matrix_path.stat().st_size / 1024 / 1024:.1f} MB")

            # Feature names
            names_path = OUTPUT_DIR / "basin08_feature_names.json"
            with open(names_path, 'w') as f:
                json.dump(feature_names, f, indent=2)
            print(f"   Saved: {names_path}")

            # Basin IDs
            ids_path = OUTPUT_DIR / "basin08_basin_ids.npy"
            np.save(ids_path, np.array(basin_ids, dtype=np.int64))
            print(f"   Saved: {ids_path}")

            print("\n" + "=" * 60)
            print("DONE!")
            print(f"Matrix: {n_basins:,} basins × {n_features:,} features")

    finally:
        conn.close()


if __name__ == "__main__":
    main()
