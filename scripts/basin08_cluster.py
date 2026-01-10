#!/usr/bin/env python3
"""
Cluster all 190k basins in basin08 based on environmental bands A-D.

Creates ~20 environmental basin types and stores cluster_id in basin08.

Usage:
    python scripts/basin08_cluster.py
"""

import os
import numpy as np
import pandas as pd
import psycopg
from sklearn.cluster import MiniBatchKMeans
from sklearn.preprocessing import StandardScaler
from dotenv import load_dotenv

load_dotenv()

# Configuration
N_CLUSTERS = 20
RANDOM_STATE = 42

# Basin08 columns mapped to bands A-D
# These are the raw column names in basin08

NUMERICAL_COLUMNS = {
    # Band A: Physiographic bedrock
    'ele_mt_smn': 'elev_min',
    'ele_mt_smx': 'elev_max',
    'slp_dg_sav': 'slope_avg',
    'slp_dg_uav': 'slope_upstream',
    'sgr_dk_sav': 'stream_gradient',
    'kar_pc_sse': 'karst',
    'kar_pc_use': 'karst_upstream',

    # Band B: Hydro-climatic baselines
    'dis_m3_pyr': 'discharge_yr',
    'dis_m3_pmn': 'discharge_min',
    'dis_m3_pmx': 'discharge_max',
    'ria_ha_ssu': 'river_area',
    'ria_ha_usu': 'river_area_upstream',
    'run_mm_syr': 'runoff',
    'gwt_cm_sav': 'gw_table_depth',
    'cly_pc_sav': 'pct_clay',
    'slt_pc_sav': 'pct_silt',
    'snd_pc_sav': 'pct_sand',

    # Band C: Bioclimatic proxies
    'tmp_dc_syr': 'temp_yr',
    'tmp_dc_smn': 'temp_min',
    'tmp_dc_smx': 'temp_max',
    'pre_mm_syr': 'precip_yr',
    'ari_ix_sav': 'aridity',
    'wet_pc_sg1': 'wet_pct_grp1',
    'wet_pc_sg2': 'wet_pct_grp2',
    'prm_pc_sse': 'permafrost_extent',

    # Band D: Anthropocene markers
    'rev_mc_usu': 'reservoir_vol',
    'crp_pc_sse': 'cropland_extent',
    'ppd_pk_sav': 'pop_density',
    'hft_ix_s09': 'human_footprint_09',
    'gdp_ud_sav': 'gdp_avg',
    'hdi_ix_sav': 'human_dev_idx',
}

# PNV share columns (15 potential natural vegetation percentages)
PNV_COLUMNS = [f'pnv_pc_s{i:02d}' for i in range(1, 16)]

# Categorical columns (will be one-hot encoded)
CATEGORICAL_COLUMNS = {
    'lit_cl_smj': 'lithology',
    'tbi_cl_smj': 'biome_id',
    'clz_cl_smj': 'zone_id',
}


def get_db_connection():
    """Create database connection."""
    return psycopg.connect(
        host=os.getenv("DB_HOST", "localhost"),
        port=os.getenv("DB_PORT", "5435"),
        dbname=os.getenv("DB_NAME", "edop"),
        user=os.getenv("DB_USER", "postgres"),
        password=os.getenv("DB_PASSWORD", ""),
    )


def load_basin_features(conn):
    """Load feature columns from basin08."""

    # Build column list
    num_cols = list(NUMERICAL_COLUMNS.keys())
    cat_cols = list(CATEGORICAL_COLUMNS.keys())
    all_cols = ['id'] + num_cols + PNV_COLUMNS + cat_cols

    col_str = ', '.join(all_cols)

    print(f"Loading {len(all_cols)} columns from basin08...")

    df = pd.read_sql(
        f"SELECT {col_str} FROM basin08 ORDER BY id",
        conn
    )

    print(f"Loaded {len(df):,} basins")
    return df


def prepare_features(df):
    """Prepare feature matrix for clustering."""

    # Numerical columns
    num_cols = list(NUMERICAL_COLUMNS.keys())
    X_num = df[num_cols].values.astype(float)

    # PNV share columns (already percentages 0-100)
    X_pnv = df[PNV_COLUMNS].values.astype(float)

    # Categorical columns - one-hot encode
    cat_cols = list(CATEGORICAL_COLUMNS.keys())
    X_cat_list = []
    for col in cat_cols:
        dummies = pd.get_dummies(df[col], prefix=col, dummy_na=True)
        X_cat_list.append(dummies.values)

    if X_cat_list:
        X_cat = np.hstack(X_cat_list)
    else:
        X_cat = np.empty((len(df), 0))

    # Combine all features
    X = np.hstack([X_num, X_pnv, X_cat])

    print(f"Feature matrix shape: {X.shape}")
    print(f"  - Numerical: {X_num.shape[1]}")
    print(f"  - PNV shares: {X_pnv.shape[1]}")
    print(f"  - Categorical (one-hot): {X_cat.shape[1]}")

    # Handle NaN - replace with 0 (safe for normalized/percentage data)
    nan_count = np.isnan(X).sum()
    if nan_count > 0:
        print(f"Replacing {nan_count:,} NaN values with 0")
        X = np.nan_to_num(X, nan=0.0)

    # Standardize
    print("Standardizing features...")
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    return X_scaled


def cluster_basins(X, n_clusters=N_CLUSTERS):
    """Run MiniBatch K-means clustering."""

    print(f"Running MiniBatch K-means with k={n_clusters}...")

    kmeans = MiniBatchKMeans(
        n_clusters=n_clusters,
        random_state=RANDOM_STATE,
        batch_size=10000,
        n_init=10,
        max_iter=300,
        verbose=1
    )

    labels = kmeans.fit_predict(X)

    # Report cluster sizes
    unique, counts = np.unique(labels, return_counts=True)
    print("\nCluster sizes:")
    for cluster_id, count in sorted(zip(unique, counts), key=lambda x: -x[1]):
        pct = 100 * count / len(labels)
        print(f"  Cluster {cluster_id:2d}: {count:6,} basins ({pct:5.1f}%)")

    return labels, kmeans


def save_cluster_ids(conn, basin_ids, cluster_labels):
    """Save cluster_id to basin08 table."""

    print("\nSaving cluster assignments to basin08...")

    with conn.cursor() as cur:
        # Add column if it doesn't exist
        cur.execute("""
            DO $$
            BEGIN
                IF NOT EXISTS (
                    SELECT 1 FROM information_schema.columns
                    WHERE table_name = 'basin08' AND column_name = 'cluster_id'
                ) THEN
                    ALTER TABLE basin08 ADD COLUMN cluster_id INTEGER;
                END IF;
            END $$;
        """)

        # Create index if it doesn't exist
        cur.execute("""
            CREATE INDEX IF NOT EXISTS idx_basin08_cluster_id
            ON basin08(cluster_id);
        """)

        # Update in batches
        batch_size = 10000
        total = len(basin_ids)

        for i in range(0, total, batch_size):
            batch_ids = basin_ids[i:i+batch_size]
            batch_labels = cluster_labels[i:i+batch_size]

            # Build VALUES clause
            values = [(int(bid), int(label)) for bid, label in zip(batch_ids, batch_labels)]

            # Use executemany with UPDATE
            cur.executemany(
                "UPDATE basin08 SET cluster_id = %s WHERE id = %s",
                [(label, bid) for bid, label in values]
            )

            if (i + batch_size) % 50000 == 0 or i + batch_size >= total:
                pct = min(100, 100 * (i + batch_size) / total)
                print(f"  Updated {min(i + batch_size, total):,} / {total:,} ({pct:.0f}%)")

        conn.commit()

    print("Done!")


def verify_results(conn):
    """Verify cluster assignments."""

    with conn.cursor() as cur:
        cur.execute("""
            SELECT cluster_id, COUNT(*) as cnt
            FROM basin08
            WHERE cluster_id IS NOT NULL
            GROUP BY cluster_id
            ORDER BY cluster_id
        """)
        rows = cur.fetchall()

        print("\nVerification - cluster distribution in basin08:")
        total = 0
        for cluster_id, cnt in rows:
            total += cnt
            print(f"  Cluster {cluster_id}: {cnt:,}")
        print(f"  Total clustered: {total:,}")

        # Check for nulls
        cur.execute("SELECT COUNT(*) FROM basin08 WHERE cluster_id IS NULL")
        null_count = cur.fetchone()[0]
        if null_count > 0:
            print(f"  Unclustered (NULL): {null_count:,}")


def main():
    print("=" * 60)
    print("Basin08 Environmental Clustering")
    print("=" * 60)

    conn = get_db_connection()

    try:
        # Load features
        df = load_basin_features(conn)
        basin_ids = df['id'].values

        # Prepare feature matrix
        X = prepare_features(df)

        # Free memory
        del df

        # Cluster
        labels, kmeans = cluster_basins(X, N_CLUSTERS)

        # Save results
        save_cluster_ids(conn, basin_ids, labels)

        # Verify
        verify_results(conn)

        print("\n" + "=" * 60)
        print("Clustering complete!")
        print("=" * 60)

    finally:
        conn.close()


if __name__ == "__main__":
    main()
