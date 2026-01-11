#!/usr/bin/env python3
"""
Run PCA on basin08 sparse feature matrix.

Uses TruncatedSVD which works efficiently on sparse matrices.
Determines number of components needed for 90% variance.

Input:
- output/basin08_sparse_matrix.npz
- output/basin08_basin_ids.npy
- output/basin08_feature_names.json

Output:
- output/basin08_pca_coords.npy (190k × n_components)
- output/basin08_pca_variance.json (explained variance per component)
- output/basin08_pca_loadings.npy (feature loadings)

Usage:
    python scripts/basin08_pca.py
"""

import json
from pathlib import Path

import numpy as np
from scipy import sparse
from sklearn.decomposition import TruncatedSVD

OUTPUT_DIR = Path(__file__).parent.parent / "output"

# Target variance to explain
TARGET_VARIANCE = 0.90


def main():
    print("Basin08 PCA Analysis")
    print("=" * 60)

    # Load sparse matrix
    print("\n1. Loading sparse matrix...")
    matrix_path = OUTPUT_DIR / "basin08_sparse_matrix.npz"
    matrix = sparse.load_npz(matrix_path)
    print(f"   Shape: {matrix.shape}")
    print(f"   Non-zeros: {matrix.nnz:,}")

    # Load basin IDs and feature names
    basin_ids = np.load(OUTPUT_DIR / "basin08_basin_ids.npy")
    with open(OUTPUT_DIR / "basin08_feature_names.json") as f:
        feature_names = json.load(f)

    print(f"   Basin IDs: {len(basin_ids):,}")
    print(f"   Features: {len(feature_names)}")

    # For sparse PCA, we use TruncatedSVD
    # First, let's determine variance with a larger number of components
    print("\n2. Running initial TruncatedSVD (150 components) to assess variance...")

    n_initial = min(150, matrix.shape[1] - 1)
    svd_initial = TruncatedSVD(n_components=n_initial, random_state=42)
    svd_initial.fit(matrix)

    # Compute cumulative variance
    cumsum = np.cumsum(svd_initial.explained_variance_ratio_)
    print(f"\n   Variance explained by first N components:")
    for n in [10, 20, 30, 50, 75, 100, 125, 150]:
        if n <= n_initial:
            print(f"      {n:3d} components: {100*cumsum[n-1]:.1f}%")

    # Find number of components for target variance
    n_target = np.argmax(cumsum >= TARGET_VARIANCE) + 1
    if cumsum[-1] < TARGET_VARIANCE:
        n_target = n_initial
        print(f"\n   Warning: {n_initial} components only explains {100*cumsum[-1]:.1f}%")

    print(f"\n   Components for {100*TARGET_VARIANCE:.0f}% variance: {n_target}")

    # Use the target number of components
    n_components = n_target
    print(f"\n3. Using {n_components} components for {100*TARGET_VARIANCE:.0f}% variance...")

    # Extract results from initial fit
    pca_coords = svd_initial.transform(matrix)[:, :n_components]
    explained_variance = svd_initial.explained_variance_[:n_components]
    explained_ratio = svd_initial.explained_variance_ratio_[:n_components]
    components = svd_initial.components_[:n_components, :]

    print(f"   PCA coordinates shape: {pca_coords.shape}")
    print(f"   Total variance explained: {100*np.sum(explained_ratio):.1f}%")

    # Save PCA coordinates
    print("\n4. Saving outputs...")

    coords_path = OUTPUT_DIR / "basin08_pca_coords.npy"
    np.save(coords_path, pca_coords.astype(np.float32))
    print(f"   Saved: {coords_path}")
    print(f"   File size: {coords_path.stat().st_size / 1024 / 1024:.1f} MB")

    # Save variance info
    variance_info = {
        "n_components": int(n_components),
        "target_variance": TARGET_VARIANCE,
        "total_variance_explained": float(np.sum(explained_ratio)),
        "components": [
            {
                "component": i + 1,
                "explained_variance": float(explained_variance[i]),
                "explained_ratio": float(explained_ratio[i]),
                "cumulative_ratio": float(np.sum(explained_ratio[:i+1]))
            }
            for i in range(n_components)
        ]
    }

    variance_path = OUTPUT_DIR / "basin08_pca_variance.json"
    with open(variance_path, 'w') as f:
        json.dump(variance_info, f, indent=2)
    print(f"   Saved: {variance_path}")

    # Save loadings (components matrix) - useful for interpretation
    # Shape: (n_components, n_features)
    loadings_path = OUTPUT_DIR / "basin08_pca_loadings.npy"
    np.save(loadings_path, components.astype(np.float32))
    print(f"   Saved: {loadings_path}")
    print(f"   File size: {loadings_path.stat().st_size / 1024 / 1024:.1f} MB")

    # Print top features for first few components
    print("\n5. Top features by absolute loading (first 5 components):")
    for pc in range(min(5, n_components)):
        loadings = components[pc, :]
        top_idx = np.argsort(np.abs(loadings))[-5:][::-1]
        print(f"\n   PC{pc+1} ({100*explained_ratio[pc]:.2f}% variance):")
        for idx in top_idx:
            print(f"      {feature_names[idx]}: {loadings[idx]:.4f}")

    print("\n" + "=" * 60)
    print("DONE!")
    print(f"PCA: {pca_coords.shape[0]:,} basins × {pca_coords.shape[1]} components")
    print(f"Total variance explained: {100*np.sum(explained_ratio):.1f}%")


if __name__ == "__main__":
    main()
