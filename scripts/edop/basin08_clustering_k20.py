#!/usr/bin/env python3
"""
Final clustering of basin08 using PCA coordinates.

Uses k=20 clusters based on analysis. Creates database table
basin08_pca_clusters with (hybas_id, cluster_id).

Input:
- output/basin08_pca_coords.npy
- output/basin08_basin_ids.npy

Output:
- Database table: basin08_pca_clusters
- output/basin08_cluster_assignments.npy
- output/basin08_cluster_centroids.npy

Usage:
    python scripts/basin08_final_clustering.py
"""

import json
import os
from pathlib import Path

import numpy as np
from sklearn.cluster import MiniBatchKMeans
import psycopg

OUTPUT_DIR = Path(__file__).parent.parent / "output"

# Final k value based on analysis
K_CLUSTERS = 20


def get_db_connection():
    """Create database connection from environment variables."""
    return psycopg.connect(
        host=os.environ.get("PGHOST", "localhost"),
        port=os.environ.get("PGPORT", "5435"),
        dbname=os.environ.get("PGDATABASE", "edop"),
        user=os.environ.get("PGUSER", "postgres"),
        password=os.environ.get("PGPASSWORD", ""),
    )


def main():
    print("Basin08 Final Clustering (k=20)")
    print("=" * 60)

    # Load PCA coordinates and basin IDs
    print("\n1. Loading data...")
    pca_coords = np.load(OUTPUT_DIR / "basin08_pca_coords.npy")
    basin_ids = np.load(OUTPUT_DIR / "basin08_basin_ids.npy")

    print(f"   PCA coordinates: {pca_coords.shape}")
    print(f"   Basin IDs: {len(basin_ids):,}")

    # Run clustering
    print(f"\n2. Running MiniBatch K-means (k={K_CLUSTERS})...")
    kmeans = MiniBatchKMeans(
        n_clusters=K_CLUSTERS,
        random_state=42,
        batch_size=10000,
        n_init=10,  # More initializations for final clustering
        max_iter=500
    )
    labels = kmeans.fit_predict(pca_coords)
    centroids = kmeans.cluster_centers_

    print(f"   Inertia: {kmeans.inertia_:,.0f}")

    # Cluster statistics
    print(f"\n3. Cluster statistics:")
    unique, counts = np.unique(labels, return_counts=True)
    for cluster_id, count in sorted(zip(unique, counts), key=lambda x: -x[1]):
        pct = 100 * count / len(labels)
        print(f"   Cluster {cluster_id:2d}: {count:6,} basins ({pct:5.1f}%)")

    # Save to files
    print("\n4. Saving to files...")

    assignments_path = OUTPUT_DIR / "basin08_cluster_assignments.npy"
    np.save(assignments_path, labels)
    print(f"   Saved: {assignments_path}")

    centroids_path = OUTPUT_DIR / "basin08_cluster_centroids.npy"
    np.save(centroids_path, centroids)
    print(f"   Saved: {centroids_path}")

    # Save metadata
    metadata = {
        "k": K_CLUSTERS,
        "n_basins": len(basin_ids),
        "n_pca_components": pca_coords.shape[1],
        "inertia": float(kmeans.inertia_),
        "cluster_counts": {int(c): int(n) for c, n in zip(unique, counts)}
    }
    metadata_path = OUTPUT_DIR / "basin08_cluster_metadata.json"
    with open(metadata_path, 'w') as f:
        json.dump(metadata, f, indent=2)
    print(f"   Saved: {metadata_path}")

    # Create database table
    print("\n5. Creating database table basin08_pca_clusters...")
    conn = get_db_connection()

    try:
        with conn.cursor() as cur:
            # Drop if exists and create new
            cur.execute("DROP TABLE IF EXISTS basin08_pca_clusters")

            cur.execute("""
                CREATE TABLE basin08_pca_clusters (
                    hybas_id BIGINT PRIMARY KEY,
                    cluster_id INTEGER NOT NULL
                )
            """)

            # Insert in batches
            batch_size = 10000
            n_batches = (len(basin_ids) + batch_size - 1) // batch_size

            for i in range(n_batches):
                start = i * batch_size
                end = min(start + batch_size, len(basin_ids))

                batch_data = [
                    (int(basin_ids[j]), int(labels[j]))
                    for j in range(start, end)
                ]

                cur.executemany(
                    "INSERT INTO basin08_pca_clusters (hybas_id, cluster_id) VALUES (%s, %s)",
                    batch_data
                )

                if (i + 1) % 5 == 0 or i == n_batches - 1:
                    print(f"   Inserted {end:,} / {len(basin_ids):,} rows")

            # Create index
            cur.execute("CREATE INDEX idx_basin08_pca_clusters_cluster ON basin08_pca_clusters(cluster_id)")

            # Add comment
            cur.execute("""
                COMMENT ON TABLE basin08_pca_clusters IS
                'K-means cluster assignments (k=20) for basin08 based on 1565-dim environmental signatures reduced via PCA to 150 components (86.2% variance). Created 11 Jan 2026.'
            """)

            conn.commit()
            print("   Table created and populated successfully")

            # Verify
            cur.execute("SELECT COUNT(*) FROM basin08_pca_clusters")
            count = cur.fetchone()[0]
            print(f"   Verified: {count:,} rows in table")

            # Show cluster distribution from DB
            cur.execute("""
                SELECT cluster_id, COUNT(*) as cnt
                FROM basin08_pca_clusters
                GROUP BY cluster_id
                ORDER BY cnt DESC
            """)
            print("\n   Cluster distribution (from DB):")
            for row in cur.fetchall()[:5]:
                print(f"      Cluster {row[0]}: {row[1]:,} basins")
            print("      ...")

    finally:
        conn.close()

    print("\n" + "=" * 60)
    print("DONE!")
    print(f"\nCreated table: basin08_pca_clusters")
    print(f"  - {len(basin_ids):,} basins assigned to {K_CLUSTERS} clusters")
    print(f"  - Based on 1565-dim signatures → 150 PCA components")
    print(f"  - Centroids saved for assigning new points")


if __name__ == "__main__":
    main()
