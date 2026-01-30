#!/usr/bin/env python3
"""
Analyze optimal cluster count for basin08 PCA coordinates.

Uses:
- Elbow method (inertia vs k)
- Silhouette score (sampled for efficiency)
- Calinski-Harabasz index

Input:
- output/basin08_pca_coords.npy

Output:
- output/basin08_cluster_analysis.json (metrics for each k)
- output/basin08_cluster_analysis.png (elbow/silhouette plots)

Usage:
    python scripts/basin08_cluster_analysis.py
"""

import json
from pathlib import Path

import numpy as np
from sklearn.cluster import MiniBatchKMeans
from sklearn.metrics import silhouette_score, calinski_harabasz_score

OUTPUT_DIR = Path(__file__).parent.parent / "output"

# Range of k values to test
K_VALUES = [5, 10, 15, 20, 25, 30, 40, 50]

# Sample size for silhouette (full computation is O(n²))
SILHOUETTE_SAMPLE_SIZE = 10000


def main():
    print("Basin08 Cluster Analysis")
    print("=" * 60)

    # Load PCA coordinates
    print("\n1. Loading PCA coordinates...")
    coords_path = OUTPUT_DIR / "basin08_pca_coords.npy"
    pca_coords = np.load(coords_path)
    print(f"   Shape: {pca_coords.shape}")

    n_samples, n_components = pca_coords.shape

    # Results storage
    results = []

    print(f"\n2. Testing k values: {K_VALUES}")
    print(f"   Using silhouette sample size: {SILHOUETTE_SAMPLE_SIZE:,}")

    # Random sample indices for silhouette
    np.random.seed(42)
    sample_idx = np.random.choice(n_samples, size=SILHOUETTE_SAMPLE_SIZE, replace=False)
    pca_sample = pca_coords[sample_idx]

    for k in K_VALUES:
        print(f"\n   k={k}...")

        # Fit MiniBatch K-means
        kmeans = MiniBatchKMeans(
            n_clusters=k,
            random_state=42,
            batch_size=10000,
            n_init=3,
            max_iter=300
        )
        labels = kmeans.fit_predict(pca_coords)

        # Inertia (within-cluster sum of squares)
        inertia = kmeans.inertia_

        # Silhouette score on sample
        labels_sample = labels[sample_idx]
        silhouette = silhouette_score(pca_sample, labels_sample)

        # Calinski-Harabasz on sample (faster than full)
        calinski = calinski_harabasz_score(pca_sample, labels_sample)

        # Cluster sizes
        unique, counts = np.unique(labels, return_counts=True)
        size_stats = {
            "min": int(counts.min()),
            "max": int(counts.max()),
            "mean": float(counts.mean()),
            "std": float(counts.std())
        }

        result = {
            "k": k,
            "inertia": float(inertia),
            "silhouette": float(silhouette),
            "calinski_harabasz": float(calinski),
            "cluster_sizes": size_stats
        }
        results.append(result)

        print(f"      Inertia: {inertia:,.0f}")
        print(f"      Silhouette: {silhouette:.4f}")
        print(f"      Calinski-Harabasz: {calinski:,.0f}")
        print(f"      Cluster sizes: min={size_stats['min']:,}, max={size_stats['max']:,}")

    # Find best k by different metrics
    print("\n3. Analysis summary...")

    # Best silhouette
    best_silhouette_idx = np.argmax([r["silhouette"] for r in results])
    best_silhouette_k = results[best_silhouette_idx]["k"]

    # Best Calinski-Harabasz
    best_calinski_idx = np.argmax([r["calinski_harabasz"] for r in results])
    best_calinski_k = results[best_calinski_idx]["k"]

    # Elbow detection (find point of maximum curvature)
    inertias = np.array([r["inertia"] for r in results])
    k_array = np.array(K_VALUES)

    # Simple elbow: second derivative approximation
    if len(K_VALUES) >= 3:
        # Compute rate of change
        diffs = np.diff(inertias)
        # Compute second differences (acceleration)
        diffs2 = np.diff(diffs)
        # Elbow is where acceleration is highest (least negative second derivative)
        elbow_idx = np.argmax(diffs2) + 1  # +1 because diff reduces length
        elbow_k = K_VALUES[elbow_idx]
    else:
        elbow_k = K_VALUES[0]

    print(f"\n   Best by silhouette score: k={best_silhouette_k} ({results[best_silhouette_idx]['silhouette']:.4f})")
    print(f"   Best by Calinski-Harabasz: k={best_calinski_k} ({results[best_calinski_idx]['calinski_harabasz']:,.0f})")
    print(f"   Elbow method suggests: k={elbow_k}")

    # Save results
    print("\n4. Saving results...")

    analysis = {
        "n_samples": n_samples,
        "n_components": n_components,
        "silhouette_sample_size": SILHOUETTE_SAMPLE_SIZE,
        "k_values_tested": K_VALUES,
        "recommendations": {
            "best_silhouette_k": best_silhouette_k,
            "best_calinski_k": best_calinski_k,
            "elbow_k": elbow_k
        },
        "results": results
    }

    analysis_path = OUTPUT_DIR / "basin08_cluster_analysis.json"
    with open(analysis_path, 'w') as f:
        json.dump(analysis, f, indent=2)
    print(f"   Saved: {analysis_path}")

    # Create visualization
    try:
        import matplotlib
        matplotlib.use('Agg')
        import matplotlib.pyplot as plt

        fig, axes = plt.subplots(1, 3, figsize=(14, 4))

        # Elbow plot
        ax1 = axes[0]
        ax1.plot(K_VALUES, [r["inertia"] for r in results], 'bo-', linewidth=2, markersize=8)
        ax1.axvline(x=elbow_k, color='r', linestyle='--', label=f'Elbow: k={elbow_k}')
        ax1.set_xlabel('Number of Clusters (k)')
        ax1.set_ylabel('Inertia')
        ax1.set_title('Elbow Method')
        ax1.legend()
        ax1.grid(True, alpha=0.3)

        # Silhouette plot
        ax2 = axes[1]
        ax2.plot(K_VALUES, [r["silhouette"] for r in results], 'go-', linewidth=2, markersize=8)
        ax2.axvline(x=best_silhouette_k, color='r', linestyle='--', label=f'Best: k={best_silhouette_k}')
        ax2.set_xlabel('Number of Clusters (k)')
        ax2.set_ylabel('Silhouette Score')
        ax2.set_title('Silhouette Analysis')
        ax2.legend()
        ax2.grid(True, alpha=0.3)

        # Calinski-Harabasz plot
        ax3 = axes[2]
        ax3.plot(K_VALUES, [r["calinski_harabasz"] for r in results], 'mo-', linewidth=2, markersize=8)
        ax3.axvline(x=best_calinski_k, color='r', linestyle='--', label=f'Best: k={best_calinski_k}')
        ax3.set_xlabel('Number of Clusters (k)')
        ax3.set_ylabel('Calinski-Harabasz Index')
        ax3.set_title('Calinski-Harabasz Analysis')
        ax3.legend()
        ax3.grid(True, alpha=0.3)

        plt.tight_layout()

        plot_path = OUTPUT_DIR / "basin08_cluster_analysis.png"
        plt.savefig(plot_path, dpi=150, bbox_inches='tight')
        print(f"   Saved: {plot_path}")

    except ImportError:
        print("   (matplotlib not available, skipping plot)")

    print("\n" + "=" * 60)
    print("DONE!")
    print(f"\nRecommendation: Review metrics and choose k based on:")
    print(f"  - Silhouette suggests k={best_silhouette_k}")
    print(f"  - Calinski-Harabasz suggests k={best_calinski_k}")
    print(f"  - Elbow method suggests k={elbow_k}")


if __name__ == "__main__":
    main()
