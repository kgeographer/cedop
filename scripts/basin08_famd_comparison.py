#!/usr/bin/env python3
"""
FAMD vs PCA Comparison for basin08 clustering.

Validates whether PCA is appropriate for this mixed data by comparing
cluster assignments from PCA (already computed) vs FAMD (mixed-data method).

FAMD (Factor Analysis of Mixed Data) properly handles:
- Continuous variables via PCA-like treatment
- Categorical variables via MCA (Multiple Correspondence Analysis)

This comparison tests whether the one-hot encoding + PCA approach
produces meaningfully different clusters than the theoretically-preferred
FAMD approach.

Usage:
    pip install prince  # if not installed
    python scripts/basin08_famd_comparison.py
"""

import json
import os
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.cluster import MiniBatchKMeans
from sklearn.metrics import adjusted_rand_score, normalized_mutual_info_score
import psycopg

OUTPUT_DIR = Path(__file__).parent.parent / "output"

# Sample size for FAMD (full 190k is slow)
SAMPLE_SIZE = 50000

# Numerical columns (same as in sparse matrix script)
NUMERICAL_COLS = [
    ("ele_mt_smn", "elev_min"),
    ("ele_mt_smx", "elev_max"),
    ("slp_dg_sav", "slope_avg"),
    ("slp_dg_uav", "slope_upstream"),
    ("sgr_dk_sav", "stream_gradient"),
    ("kar_pc_sse", "karst"),
    ("kar_pc_use", "karst_upstream"),
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
    ("tmp_dc_syr", "temp_yr"),
    ("tmp_dc_smn", "temp_min"),
    ("tmp_dc_smx", "temp_max"),
    ("pre_mm_syr", "precip_yr"),
    ("ari_ix_sav", "aridity"),
    ("wet_pc_sg1", "wet_pct_grp1"),
    ("wet_pc_sg2", "wet_pct_grp2"),
    ("prm_pc_sse", "permafrost_extent"),
    ("rev_mc_usu", "reservoir_vol"),
    ("crp_pc_sse", "cropland_extent"),
    ("ppd_pk_sav", "pop_density"),
    ("hft_ix_s09", "human_footprint_09"),
    ("gdp_ud_sav", "gdp_avg"),
    ("hdi_ix_sav", "human_dev_idx"),
]

# Categorical columns (original values, not one-hot)
CATEGORICAL_COLS = [
    ("tec_cl_smj", "ecoregion"),
    ("fec_cl_smj", "freshwater_eco"),
    ("cls_cl_smj", "climate_strata"),
    ("glc_cl_smj", "land_cover"),
    ("clz_cl_smj", "climate_zone"),
    ("lit_cl_smj", "lithology"),
    ("tbi_cl_smj", "biome"),
    ("fmh_cl_smj", "freshwater_habitat"),
    ("wet_cl_smj", "wetland_type"),
]

# PNV columns (treat as continuous)
PNV_COLS = [f"pnv_pc_s{i:02d}" for i in range(1, 16)]

TEMP_FIELDS = {"tmp_dc_syr", "tmp_dc_smn", "tmp_dc_smx"}


def get_db_connection():
    return psycopg.connect(
        host=os.environ.get("PGHOST", "localhost"),
        port=os.environ.get("PGPORT", "5435"),
        dbname=os.environ.get("PGDATABASE", "edop"),
        user=os.environ.get("PGUSER", "postgres"),
        password=os.environ.get("PGPASSWORD", ""),
    )


def main():
    print("FAMD vs PCA Comparison")
    print("=" * 70)

    # Check if prince is installed
    try:
        from prince import FAMD
    except ImportError:
        print("\nERROR: 'prince' package not installed.")
        print("Run: pip install prince")
        return

    # Load PCA cluster assignments
    print("\n1. Loading PCA cluster assignments...")
    pca_labels = np.load(OUTPUT_DIR / "basin08_cluster_assignments.npy")
    basin_ids = np.load(OUTPUT_DIR / "basin08_basin_ids.npy")
    print(f"   Total basins: {len(basin_ids):,}")

    # Create ID to PCA label mapping
    id_to_pca_label = dict(zip(basin_ids, pca_labels))

    # Sample basin IDs
    print(f"\n2. Sampling {SAMPLE_SIZE:,} basins...")
    np.random.seed(42)
    sample_indices = np.random.choice(len(basin_ids), size=SAMPLE_SIZE, replace=False)
    sample_ids = basin_ids[sample_indices]
    sample_pca_labels = pca_labels[sample_indices]

    # Build column lists for query
    num_cols_sql = ", ".join(col for col, _ in NUMERICAL_COLS)
    cat_cols_sql = ", ".join(col for col, _ in CATEGORICAL_COLS)
    pnv_cols_sql = ", ".join(PNV_COLS)

    # Query mixed data from database
    print("\n3. Querying mixed data from basin08...")
    conn = get_db_connection()

    with conn.cursor() as cur:
        # Get global min/max for normalization
        print("   Computing normalization ranges...")
        ranges = {}
        for db_col, name in NUMERICAL_COLS:
            if db_col in TEMP_FIELDS:
                cur.execute(f"SELECT MIN({db_col}/10.0), MAX({db_col}/10.0) FROM basin08")
            else:
                cur.execute(f"SELECT MIN({db_col}), MAX({db_col}) FROM basin08")
            min_val, max_val = cur.fetchone()
            ranges[name] = (float(min_val) if min_val else 0, float(max_val) if max_val else 1)

        # Query sample data
        print("   Fetching sample data...")
        id_list = ",".join(str(int(x)) for x in sample_ids)
        sql = f"""
            SELECT hybas_id, {num_cols_sql}, {pnv_cols_sql}, {cat_cols_sql}
            FROM basin08
            WHERE hybas_id IN ({id_list})
        """
        cur.execute(sql)
        rows = cur.fetchall()

    conn.close()
    print(f"   Retrieved {len(rows):,} rows")

    # Build DataFrame
    print("\n4. Building mixed DataFrame...")

    # Column names
    num_names = [name for _, name in NUMERICAL_COLS]
    pnv_names = [f"pnv_{i:02d}" for i in range(1, 16)]
    cat_names = [name for _, name in CATEGORICAL_COLS]

    data = []
    row_ids = []

    for row in rows:
        hybas_id = row[0]
        row_ids.append(hybas_id)

        row_data = {}
        idx = 1

        # Numerical (normalized)
        for i, (db_col, name) in enumerate(NUMERICAL_COLS):
            val = row[idx]
            if db_col in TEMP_FIELDS and val is not None:
                val = val / 10.0
            min_v, max_v = ranges[name]
            if val is not None and max_v != min_v:
                row_data[name] = (float(val) - min_v) / (max_v - min_v)
            else:
                row_data[name] = 0.0
            idx += 1

        # PNV (scaled 0-1)
        for i, pnv_col in enumerate(PNV_COLS):
            val = row[idx]
            row_data[pnv_names[i]] = float(val) / 100.0 if val else 0.0
            idx += 1

        # Categorical (as string for FAMD)
        for i, (db_col, name) in enumerate(CATEGORICAL_COLS):
            val = row[idx]
            row_data[name] = str(val) if val is not None else "missing"
            idx += 1

        data.append(row_data)

    df = pd.DataFrame(data)

    # Set categorical dtypes
    for name in cat_names:
        df[name] = df[name].astype('category')

    print(f"   DataFrame shape: {df.shape}")
    print(f"   Numerical columns: {len(num_names) + len(pnv_names)}")
    print(f"   Categorical columns: {len(cat_names)}")

    # Run FAMD
    print("\n5. Running FAMD (this may take a few minutes)...")
    n_components = 50

    famd = FAMD(n_components=n_components, random_state=42)
    coords_famd = famd.fit_transform(df)

    print(f"   FAMD coordinates shape: {coords_famd.shape}")

    # Variance explained (prince uses percentage_of_variance_ or eigenvalues_)
    try:
        explained_var = famd.percentage_of_variance_
        cumsum = np.cumsum(explained_var) / 100  # Convert from percentage
        print(f"   Variance explained (first 10): {[f'{v:.1f}%' for v in explained_var[:10]]}")
        print(f"   Cumulative at 50 components: {cumsum[-1]:.1%}")
    except AttributeError:
        print("   (Variance info not available in this prince version)")

    # Cluster FAMD coordinates
    print("\n6. Clustering FAMD coordinates (k=20)...")
    kmeans = MiniBatchKMeans(n_clusters=20, random_state=42, n_init=10)
    famd_labels = kmeans.fit_predict(coords_famd)

    # Map row_ids to FAMD labels
    id_to_famd_label = dict(zip(row_ids, famd_labels))

    # Get matching PCA labels for comparison
    pca_labels_matched = np.array([id_to_pca_label[rid] for rid in row_ids])

    # Comparison metrics
    print("\n7. Comparing PCA vs FAMD clustering...")

    ari = adjusted_rand_score(pca_labels_matched, famd_labels)
    nmi = normalized_mutual_info_score(pca_labels_matched, famd_labels)

    # Direct agreement (same cluster ID isn't meaningful, but contingency is)
    from sklearn.metrics.cluster import contingency_matrix
    contingency = contingency_matrix(pca_labels_matched, famd_labels)

    # Best match percentage (for each PCA cluster, what % goes to its most common FAMD cluster)
    pca_to_famd_match = contingency.max(axis=1).sum() / len(famd_labels)
    famd_to_pca_match = contingency.max(axis=0).sum() / len(famd_labels)

    print(f"\n   Adjusted Rand Index (ARI): {ari:.4f}")
    print(f"   Normalized Mutual Info (NMI): {nmi:.4f}")
    print(f"   PCA→FAMD best-match agreement: {pca_to_famd_match:.1%}")
    print(f"   FAMD→PCA best-match agreement: {famd_to_pca_match:.1%}")

    # Interpretation
    print("\n" + "=" * 70)
    print("INTERPRETATION")
    print("=" * 70)

    if ari > 0.7:
        print(f"\n   ARI = {ari:.3f} > 0.7: STRONG AGREEMENT")
        print("   → PCA clustering is functionally adequate")
        print("   → One-hot encoding did not materially distort results")
    elif ari > 0.4:
        print(f"\n   ARI = {ari:.3f} (0.4-0.7): MODERATE AGREEMENT")
        print("   → Some differences exist but overall structure similar")
        print("   → PCA is acceptable for exploratory work")
        print("   → Consider FAMD for rigorous analysis")
    else:
        print(f"\n   ARI = {ari:.3f} < 0.4: WEAK AGREEMENT")
        print("   → PCA and FAMD find substantially different structure")
        print("   → One-hot encoding may be distorting results")
        print("   → Recommend switching to FAMD")

    # Save results
    print("\n8. Saving results...")

    # Get cumulative variance if available
    try:
        cumsum_val = float(cumsum[-1])
    except:
        cumsum_val = None

    results = {
        "sample_size": SAMPLE_SIZE,
        "n_components_famd": n_components,
        "variance_explained_cumulative": cumsum_val,
        "metrics": {
            "adjusted_rand_index": float(ari),
            "normalized_mutual_info": float(nmi),
            "pca_to_famd_best_match": float(pca_to_famd_match),
            "famd_to_pca_best_match": float(famd_to_pca_match)
        },
        "interpretation": "strong" if ari > 0.7 else "moderate" if ari > 0.4 else "weak"
    }

    results_path = OUTPUT_DIR / "basin08_famd_comparison.json"
    with open(results_path, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"   Saved: {results_path}")

    # Save FAMD coordinates for sample (optional further analysis)
    famd_path = OUTPUT_DIR / "basin08_famd_coords_sample.npy"
    np.save(famd_path, coords_famd.values if hasattr(coords_famd, 'values') else coords_famd)
    print(f"   Saved: {famd_path}")

    print("\n" + "=" * 70)
    print("DONE!")


if __name__ == "__main__":
    main()
