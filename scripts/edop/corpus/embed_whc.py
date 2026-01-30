"""
Generate embeddings from band summaries for 258 WHC cities.

File-only output (no database) - creates embeddings, similarity matrices,
and clustering results.

Usage:
    python scripts/corpus/embed_whc.py
"""

import json
import os
from pathlib import Path

import numpy as np
from dotenv import load_dotenv
from openai import OpenAI
from sklearn.cluster import KMeans

load_dotenv()

# Configuration
EMBEDDING_MODEL = "text-embedding-3-small"
N_CLUSTERS = 8  # More clusters for larger dataset
INPUT_DIR = Path("output/corpus_258")
SUMMARIES_FILE = INPUT_DIR / "band_summaries.json"
OUTPUT_FILE = INPUT_DIR / "band_embeddings.json"

BANDS = ['history', 'environment', 'culture', 'modern']


def load_summaries():
    """Load band summaries from JSON file."""
    with open(SUMMARIES_FILE) as f:
        return json.load(f)


def get_text_for_embedding(city: dict, band: str) -> str | None:
    """Extract summary text for a specific band."""
    summary_data = city.get('summaries', {}).get(band, {})
    if summary_data.get('status') == 'ok':
        return summary_data.get('summary')
    return None


def get_composite_text(city: dict) -> str | None:
    """Concatenate all available band summaries for composite embedding."""
    parts = []
    for band in BANDS:
        text = get_text_for_embedding(city, band)
        if text:
            parts.append(f"[{band.upper()}]\n{text}")

    if parts:
        return "\n\n".join(parts)
    return None


def generate_embeddings_batch(texts: list[str], client: OpenAI, batch_size: int = 100) -> list:
    """Generate embeddings in batches."""
    all_embeddings = []

    for i in range(0, len(texts), batch_size):
        batch = texts[i:i + batch_size]
        # Filter out None/empty
        valid_indices = [j for j, t in enumerate(batch) if t]
        valid_texts = [batch[j] for j in valid_indices]

        if valid_texts:
            response = client.embeddings.create(
                model=EMBEDDING_MODEL,
                input=valid_texts
            )

            # Map back to original positions
            batch_embeddings = [None] * len(batch)
            for idx, emb_data in zip(valid_indices, response.data):
                batch_embeddings[idx] = emb_data.embedding

            all_embeddings.extend(batch_embeddings)
        else:
            all_embeddings.extend([None] * len(batch))

    return all_embeddings


def compute_similarity(embeddings: list, valid_mask: np.ndarray) -> tuple:
    """Compute pairwise cosine similarity."""
    n = len(embeddings)
    similarity = np.zeros((n, n))

    # Convert to numpy, handling None
    emb_array = []
    for e in embeddings:
        if e is not None:
            emb_array.append(np.array(e))
        else:
            emb_array.append(np.zeros(1536))
    emb_array = np.array(emb_array)

    # Normalize for cosine similarity
    norms = np.linalg.norm(emb_array, axis=1, keepdims=True)
    norms[norms == 0] = 1  # Avoid division by zero
    normalized = emb_array / norms

    # Compute similarity matrix
    for i in range(n):
        for j in range(n):
            if valid_mask[i] and valid_mask[j]:
                similarity[i, j] = np.dot(normalized[i], normalized[j])

    return similarity


def run_clustering(embeddings: list, valid_mask: np.ndarray, n_clusters: int) -> tuple:
    """Run K-means on valid embeddings."""
    valid_indices = np.where(valid_mask)[0]

    if len(valid_indices) < n_clusters:
        return np.full(len(embeddings), -1), np.zeros(len(embeddings))

    valid_emb = np.array([embeddings[i] for i in valid_indices])

    kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
    valid_labels = kmeans.fit_predict(valid_emb)

    # Map back
    labels = np.full(len(embeddings), -1)
    distances = np.zeros(len(embeddings))

    for idx, orig_idx in enumerate(valid_indices):
        labels[orig_idx] = valid_labels[idx]
        centroid = kmeans.cluster_centers_[valid_labels[idx]]
        distances[orig_idx] = np.linalg.norm(np.array(embeddings[orig_idx]) - centroid)

    return labels, distances


def main():
    print("WHC Band Embedding Generation")
    print("=" * 60)

    print("\n1. Loading band summaries...")
    cities = load_summaries()
    print(f"   Loaded {len(cities)} cities")

    # Initialize OpenAI client
    client = OpenAI()

    # Process each band + composite
    all_bands = BANDS + ['composite']
    results = {}

    for band in all_bands:
        print(f"\n2. Processing {band.upper()} band...")

        # Extract texts
        if band == 'composite':
            texts = [get_composite_text(c) for c in cities]
        else:
            texts = [get_text_for_embedding(c, band) for c in cities]

        valid_mask = np.array([t is not None for t in texts])
        valid_count = valid_mask.sum()
        print(f"   {valid_count}/{len(cities)} cities have content")

        if valid_count == 0:
            print(f"   Skipping {band} - no content")
            continue

        # Generate embeddings
        print(f"   Generating embeddings...")
        embeddings = generate_embeddings_batch(texts, client)

        # Compute similarity (only store top-k for space efficiency)
        print(f"   Computing similarity...")
        similarity = compute_similarity(embeddings, valid_mask)

        # Clustering
        print(f"   Clustering (k={N_CLUSTERS})...")
        labels, dist_to_centroid = run_clustering(embeddings, valid_mask, N_CLUSTERS)

        # Store results (embeddings as lists, not numpy)
        results[band] = {
            'valid_count': int(valid_count),
            'clusters': labels.tolist(),
            'cluster_distances': dist_to_centroid.tolist()
        }

        # Store top-10 similar for each city (not full matrix - too large)
        top_similar = []
        for i in range(len(cities)):
            if valid_mask[i]:
                # Get indices sorted by similarity (excluding self)
                sims = similarity[i].copy()
                sims[i] = -1  # Exclude self
                top_indices = np.argsort(sims)[-10:][::-1]
                top_similar.append([
                    {"idx": int(idx), "sim": float(sims[idx])}
                    for idx in top_indices if valid_mask[idx]
                ])
            else:
                top_similar.append([])

        results[band]['top_similar'] = top_similar

    # Build output structure
    output = {
        'model': EMBEDDING_MODEL,
        'n_clusters': N_CLUSTERS,
        'cities': [
            {
                'whc_id': c['whc_id'],
                'city': c['city'],
                'region': c['region'],
                'country': c['country'],
                'ccode': c['ccode']
            }
            for c in cities
        ],
        'bands': results
    }

    # Write output
    with open(OUTPUT_FILE, 'w') as f:
        json.dump(output, f, indent=2)

    print(f"\nWrote embeddings to {OUTPUT_FILE}")

    # Print cluster summary for composite
    if 'composite' in results:
        print("\n" + "=" * 60)
        print("COMPOSITE CLUSTERING SUMMARY")
        print("=" * 60)

        labels = results['composite']['clusters']
        for cluster_id in range(N_CLUSTERS):
            members = [cities[i]['city'] for i, l in enumerate(labels) if l == cluster_id]
            if members:
                print(f"\nCluster {cluster_id} ({len(members)} cities):")
                # Show first 10
                for m in members[:10]:
                    print(f"  - {m}")
                if len(members) > 10:
                    print(f"  ... and {len(members) - 10} more")

    # Region breakdown
    print("\n" + "=" * 60)
    print("CLUSTER × REGION CROSS-TAB")
    print("=" * 60)

    if 'composite' in results:
        labels = results['composite']['clusters']
        regions = set(c['region'] for c in cities)

        print(f"\n{'Region':<25}", end="")
        for i in range(N_CLUSTERS):
            print(f" C{i:d}", end="")
        print()
        print("-" * (25 + N_CLUSTERS * 4))

        for region in sorted(regions):
            print(f"{region[:24]:<25}", end="")
            for cluster_id in range(N_CLUSTERS):
                count = sum(1 for i, c in enumerate(cities)
                           if c['region'] == region and labels[i] == cluster_id)
                print(f" {count:3d}" if count else "   -", end="")
            print()


if __name__ == "__main__":
    main()
