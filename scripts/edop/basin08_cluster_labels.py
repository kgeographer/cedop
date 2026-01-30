#!/usr/bin/env python3
"""
Analyze basin08 clusters to derive descriptive labels.

Examines cluster centroids and basin characteristics to suggest
meaningful labels for each of the 20 clusters.

Input:
- output/basin08_pca_coords.npy
- output/basin08_cluster_assignments.npy
- output/basin08_feature_names.json
- output/basin08_sparse_matrix.npz
- Database: basin08, wh_cities, basin08_pca_clusters

Output:
- Prints cluster characterization
- output/basin08_cluster_labels.json

Usage:
    python scripts/basin08_cluster_labels.py
"""

import json
import os
from pathlib import Path
from collections import Counter

import numpy as np
from scipy import sparse
import psycopg

OUTPUT_DIR = Path(__file__).parent.parent / "output"

# Key numerical features for interpretation (indices in feature vector)
# These are the first 31 features (normalized numerical)
NUMERICAL_LABELS = [
    "elev_min", "elev_max", "slope_avg", "slope_upstream", "stream_gradient",
    "karst", "karst_upstream",
    "discharge_yr", "discharge_min", "discharge_max", "river_area",
    "river_area_upstream", "runoff", "gw_table_depth",
    "pct_clay", "pct_silt", "pct_sand",
    "temp_yr", "temp_min", "temp_max", "precip_yr", "aridity",
    "wet_pct_grp1", "wet_pct_grp2", "permafrost_extent",
    "reservoir_vol", "cropland_extent", "pop_density",
    "human_footprint_09", "gdp_avg", "human_dev_idx"
]

# Key features for characterization
KEY_FEATURES = {
    "temp_yr": 17,      # Annual temperature
    "precip_yr": 20,    # Annual precipitation
    "aridity": 21,      # Aridity index
    "elev_min": 0,      # Minimum elevation
    "elev_max": 1,      # Maximum elevation
    "slope_avg": 2,     # Average slope
    "human_footprint_09": 28,  # Human footprint
    "permafrost_extent": 24,   # Permafrost
}


def get_db_connection():
    return psycopg.connect(
        host=os.environ.get("PGHOST", "localhost"),
        port=os.environ.get("PGPORT", "5435"),
        dbname=os.environ.get("PGDATABASE", "edop"),
        user=os.environ.get("PGUSER", "postgres"),
        password=os.environ.get("PGPASSWORD", ""),
    )


def get_dominant_categorical(matrix, assignments, cluster_id, feature_names, cat_prefix, top_n=3):
    """Get the most common categorical value for a cluster."""
    mask = assignments == cluster_id
    cluster_matrix = matrix[mask]

    # Find columns matching the prefix
    cat_cols = [(i, name) for i, name in enumerate(feature_names)
                if name.startswith(f"cat_{cat_prefix}_")]

    if not cat_cols:
        return []

    # Sum across cluster to find most common categories
    col_indices = [c[0] for c in cat_cols]
    col_names = [c[1] for c in cat_cols]

    # Get dense representation for these columns
    cat_data = cluster_matrix[:, col_indices].toarray()
    col_sums = cat_data.sum(axis=0)

    # Get top N
    top_indices = np.argsort(col_sums)[-top_n:][::-1]
    results = []
    for idx in top_indices:
        if col_sums[idx] > 0:
            # Extract the ID from column name (e.g., "cat_tbi_7" -> 7)
            cat_id = col_names[idx].split("_")[-1]
            pct = 100 * col_sums[idx] / mask.sum()
            results.append((cat_id, pct))

    return results


def main():
    print("Basin08 Cluster Label Analysis")
    print("=" * 70)

    # Load data
    print("\n1. Loading data...")
    matrix = sparse.load_npz(OUTPUT_DIR / "basin08_sparse_matrix.npz")
    assignments = np.load(OUTPUT_DIR / "basin08_cluster_assignments.npy")
    with open(OUTPUT_DIR / "basin08_feature_names.json") as f:
        feature_names = json.load(f)

    print(f"   Matrix: {matrix.shape}")
    print(f"   Assignments: {len(assignments)}")

    # Get cluster counts
    unique, counts = np.unique(assignments, return_counts=True)
    cluster_counts = dict(zip(unique, counts))

    # Load lookup tables for categorical interpretation
    print("\n2. Loading lookup tables...")
    conn = get_db_connection()
    lookups = {}

    with conn.cursor() as cur:
        # Biomes
        cur.execute("SELECT biome_id, biome_name FROM lu_tbi")
        lookups['tbi'] = {str(row[0]): row[1] for row in cur.fetchall()}

        # Climate zones
        cur.execute("SELECT genz_id, genz_name FROM lu_clz")
        lookups['clz'] = {str(row[0]): row[1] for row in cur.fetchall()}

        # Get WHC cities per cluster (join through basin08)
        cur.execute("""
            SELECT pc.cluster_id, c.title, c.country
            FROM basin08_pca_clusters pc
            JOIN basin08 b ON b.hybas_id = pc.hybas_id
            JOIN wh_cities c ON c.basin_id = b.id
            ORDER BY pc.cluster_id, c.title
        """)
        cities_by_cluster = {}
        for row in cur.fetchall():
            cid = row[0]
            if cid not in cities_by_cluster:
                cities_by_cluster[cid] = []
            cities_by_cluster[cid].append(f"{row[1]} ({row[2]})")

    conn.close()

    # Analyze each cluster
    print("\n3. Analyzing clusters...")
    print("=" * 70)

    cluster_info = []

    # Convert to dense for numerical features (first 31 columns only)
    numerical_data = matrix[:, :31].toarray()

    for cluster_id in sorted(unique):
        mask = assignments == cluster_id
        count = cluster_counts[cluster_id]

        # Numerical feature means for this cluster
        cluster_numerical = numerical_data[mask].mean(axis=0)

        # Key characteristics
        temp = cluster_numerical[KEY_FEATURES["temp_yr"]]
        precip = cluster_numerical[KEY_FEATURES["precip_yr"]]
        aridity = cluster_numerical[KEY_FEATURES["aridity"]]
        elev = cluster_numerical[KEY_FEATURES["elev_max"]]
        slope = cluster_numerical[KEY_FEATURES["slope_avg"]]
        human = cluster_numerical[KEY_FEATURES["human_footprint_09"]]
        permafrost = cluster_numerical[KEY_FEATURES["permafrost_extent"]]

        # Dominant biome
        top_biomes = get_dominant_categorical(matrix, assignments, cluster_id, feature_names, "tbi", 2)

        # Dominant climate zone
        top_clz = get_dominant_categorical(matrix, assignments, cluster_id, feature_names, "clz", 2)

        # Generate label based on characteristics
        label_parts = []

        # Temperature
        if permafrost > 0.3:
            label_parts.append("Arctic/Permafrost")
        elif temp < 0.3:
            label_parts.append("Cold")
        elif temp < 0.5:
            label_parts.append("Temperate")
        elif temp < 0.7:
            label_parts.append("Warm")
        else:
            label_parts.append("Hot")

        # Moisture (aridity index: low = arid, high = humid)
        if aridity < 0.05:
            label_parts.append("Hyper-arid")
        elif aridity < 0.1:
            label_parts.append("Arid")
        elif aridity < 0.2:
            label_parts.append("Semi-arid")
        elif aridity < 0.4:
            label_parts.append("Dry sub-humid")
        else:
            label_parts.append("Humid")

        # Terrain (only add if distinctive)
        if elev > 0.4:
            label_parts.append("Highland")
        elif slope > 0.5:
            label_parts.append("Mountainous")
        elif elev < 0.1 and slope < 0.2:
            label_parts.append("Lowland")

        suggested_label = " / ".join(label_parts)

        # Get biome name if available
        biome_str = ""
        if top_biomes:
            biome_id = top_biomes[0][0]
            if biome_id in lookups['tbi']:
                biome_str = lookups['tbi'][biome_id][:40]

        # Cities in this cluster
        cities = cities_by_cluster.get(cluster_id, [])

        info = {
            "cluster_id": int(cluster_id),
            "count": int(count),
            "suggested_label": suggested_label,
            "characteristics": {
                "temp_yr": float(round(temp, 3)),
                "precip_yr": float(round(precip, 3)),
                "aridity": float(round(aridity, 3)),
                "elev_max": float(round(elev, 3)),
                "slope_avg": float(round(slope, 3)),
                "human_footprint": float(round(human, 3)),
                "permafrost": float(round(permafrost, 3))
            },
            "top_biome": biome_str,
            "whc_cities": cities[:5],
            "whc_city_count": len(cities)
        }
        cluster_info.append(info)

        # Print summary
        print(f"\nCluster {cluster_id}: {count:,} basins")
        print(f"  Suggested: {suggested_label}")
        print(f"  Temp={temp:.2f} Precip={precip:.2f} Aridity={aridity:.2f} Elev={elev:.2f}")
        print(f"  Biome: {biome_str}")
        if cities:
            print(f"  WHC cities ({len(cities)}): {', '.join(cities[:3])}{'...' if len(cities) > 3 else ''}")

    # Save results
    print("\n" + "=" * 70)
    print("4. Saving results...")

    output_path = OUTPUT_DIR / "basin08_cluster_labels.json"
    with open(output_path, 'w') as f:
        json.dump(cluster_info, f, indent=2)
    print(f"   Saved: {output_path}")

    # Print summary table
    print("\n" + "=" * 70)
    print("SUMMARY TABLE")
    print("=" * 70)
    print(f"{'ID':>3} {'Count':>7} {'Label':<35} {'Cities':>6}")
    print("-" * 70)
    for info in sorted(cluster_info, key=lambda x: -x['count']):
        print(f"{info['cluster_id']:>3} {info['count']:>7,} {info['suggested_label']:<35} {info['whc_city_count']:>6}")


if __name__ == "__main__":
    main()
