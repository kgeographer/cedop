"""
Generate embeddings from band summaries for EDOP corpus.

Creates embeddings per band (history, environment, culture, modern) plus
a composite embedding from all bands concatenated. Computes pairwise
similarity and clustering for each embedding type.

Usage:
    python scripts/corpus/generate_band_embeddings.py

Requires:
    OPENAI_API_KEY in environment or .env file
"""

import json
import os
from pathlib import Path

import numpy as np
import psycopg
from dotenv import load_dotenv
from openai import OpenAI
from scipy.spatial.distance import pdist, squareform
from sklearn.cluster import KMeans

load_dotenv()

# Configuration
EMBEDDING_MODEL = "text-embedding-3-small"
N_CLUSTERS = 5
SUMMARIES_FILE = Path("output/corpus/band_summaries_pilot.json")
OUTPUT_FILE = Path("output/corpus/band_embeddings_pilot.json")

BANDS = ['history', 'environment', 'culture', 'modern']


def get_db_connection():
    """Create database connection from environment variables."""
    return psycopg.connect(
        host=os.environ.get("PGHOST", "localhost"),
        port=os.environ.get("PGPORT", "5435"),
        dbname=os.environ.get("PGDATABASE", "edop"),
        user=os.environ.get("PGUSER", "postgres"),
        password=os.environ.get("PGPASSWORD", ""),
    )


def load_summaries():
    """Load band summaries from JSON file."""
    with open(SUMMARIES_FILE) as f:
        return json.load(f)


def get_text_for_embedding(site: dict, band: str) -> str | None:
    """Extract summary text for a specific band."""
    summary_data = site.get('summaries', {}).get(band, {})
    if summary_data.get('status') == 'ok':
        return summary_data.get('summary')
    return None


def get_composite_text(site: dict) -> str | None:
    """Concatenate all available band summaries for composite embedding."""
    parts = []
    for band in BANDS:
        text = get_text_for_embedding(site, band)
        if text:
            parts.append(f"[{band.upper()}]\n{text}")

    if parts:
        return "\n\n".join(parts)
    return None


def generate_embeddings(texts: list[str | None], client: OpenAI) -> np.ndarray:
    """Generate OpenAI embeddings, returning zeros for None texts."""
    embeddings = []

    for i, text in enumerate(texts):
        if text:
            response = client.embeddings.create(
                model=EMBEDDING_MODEL,
                input=text
            )
            embedding = response.data[0].embedding
        else:
            # Return zero vector for missing content
            embedding = [0.0] * 1536  # text-embedding-3-small dimension

        embeddings.append(embedding)

    return np.array(embeddings)


def compute_similarity(embeddings: np.ndarray, valid_mask: np.ndarray):
    """Compute cosine similarity, handling zero vectors."""
    n = len(embeddings)
    distances = np.zeros((n, n))
    similarity = np.zeros((n, n))

    for i in range(n):
        for j in range(n):
            if i == j:
                similarity[i, j] = 1.0
            elif valid_mask[i] and valid_mask[j]:
                # Cosine distance
                dot = np.dot(embeddings[i], embeddings[j])
                norm_i = np.linalg.norm(embeddings[i])
                norm_j = np.linalg.norm(embeddings[j])
                if norm_i > 0 and norm_j > 0:
                    cos_sim = dot / (norm_i * norm_j)
                    similarity[i, j] = cos_sim
                    distances[i, j] = 1 - cos_sim

    return distances, similarity


def run_clustering(embeddings: np.ndarray, valid_mask: np.ndarray, n_clusters: int):
    """Run K-means on valid embeddings only."""
    valid_indices = np.where(valid_mask)[0]
    valid_embeddings = embeddings[valid_indices]

    if len(valid_embeddings) < n_clusters:
        # Not enough data for clustering
        labels = np.full(len(embeddings), -1)
        distances = np.zeros(len(embeddings))
        return labels, distances

    kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
    valid_labels = kmeans.fit_predict(valid_embeddings)

    # Map back to full array
    labels = np.full(len(embeddings), -1)
    distances_to_centroid = np.zeros(len(embeddings))

    for idx, orig_idx in enumerate(valid_indices):
        labels[orig_idx] = valid_labels[idx]
        centroid = kmeans.cluster_centers_[valid_labels[idx]]
        distances_to_centroid[orig_idx] = np.linalg.norm(embeddings[orig_idx] - centroid)

    return labels, distances_to_centroid


def create_tables(conn):
    """Create tables for band embeddings."""
    with conn.cursor() as cur:
        # Band embeddings table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS edop_band_embeddings (
                site_id INTEGER REFERENCES edop_wh_sites(site_id),
                band TEXT NOT NULL,
                embedding FLOAT8[],
                model TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                PRIMARY KEY (site_id, band)
            )
        """)

        # Band similarity table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS edop_band_similarity (
                site_a INTEGER NOT NULL REFERENCES edop_wh_sites(site_id),
                site_b INTEGER NOT NULL REFERENCES edop_wh_sites(site_id),
                band TEXT NOT NULL,
                distance FLOAT8,
                similarity FLOAT8,
                PRIMARY KEY (site_a, site_b, band)
            )
        """)

        # Band clusters table
        cur.execute("""
            CREATE TABLE IF NOT EXISTS edop_band_clusters (
                site_id INTEGER REFERENCES edop_wh_sites(site_id),
                band TEXT NOT NULL,
                cluster_id INTEGER,
                distance_to_centroid FLOAT8,
                PRIMARY KEY (site_id, band)
            )
        """)


def persist_band_results(conn, site_ids, band, embeddings, distances, similarity,
                         labels, dist_to_centroid, valid_mask):
    """Persist results for a single band."""
    with conn.cursor() as cur:
        # Clear existing data for this band
        cur.execute("DELETE FROM edop_band_embeddings WHERE band = %s", (band,))
        cur.execute("DELETE FROM edop_band_similarity WHERE band = %s", (band,))
        cur.execute("DELETE FROM edop_band_clusters WHERE band = %s", (band,))

        # Insert embeddings
        for i, site_id in enumerate(site_ids):
            if valid_mask[i]:
                cur.execute(
                    """INSERT INTO edop_band_embeddings (site_id, band, embedding, model)
                       VALUES (%s, %s, %s, %s)""",
                    (int(site_id), band, embeddings[i].tolist(), EMBEDDING_MODEL)
                )

        # Insert similarity (only for valid pairs)
        n = len(site_ids)
        for i in range(n):
            for j in range(n):
                if i != j and valid_mask[i] and valid_mask[j]:
                    cur.execute(
                        """INSERT INTO edop_band_similarity (site_a, site_b, band, distance, similarity)
                           VALUES (%s, %s, %s, %s, %s)""",
                        (int(site_ids[i]), int(site_ids[j]), band,
                         float(distances[i, j]), float(similarity[i, j]))
                    )

        # Insert clusters
        for i, site_id in enumerate(site_ids):
            if valid_mask[i] and labels[i] >= 0:
                cur.execute(
                    """INSERT INTO edop_band_clusters (site_id, band, cluster_id, distance_to_centroid)
                       VALUES (%s, %s, %s, %s)""",
                    (int(site_id), band, int(labels[i]), float(dist_to_centroid[i]))
                )


def main():
    print("EDOP Band Embedding Generation")
    print("=" * 60)

    # Load summaries
    print("\n1. Loading band summaries...")
    sites = load_summaries()
    print(f"   Loaded {len(sites)} sites")

    site_ids = [s['site_id'] for s in sites]

    # Initialize OpenAI client
    client = OpenAI()

    # Connect to database
    conn = get_db_connection()
    create_tables(conn)

    # Process each band + composite
    all_bands = BANDS + ['composite']
    results = {}

    for band in all_bands:
        print(f"\n2. Processing {band.upper()} band...")

        # Extract texts
        if band == 'composite':
            texts = [get_composite_text(s) for s in sites]
        else:
            texts = [get_text_for_embedding(s, band) for s in sites]

        valid_mask = np.array([t is not None for t in texts])
        valid_count = valid_mask.sum()
        print(f"   {valid_count}/{len(sites)} sites have content")

        if valid_count == 0:
            print(f"   Skipping {band} - no content")
            continue

        # Generate embeddings
        print(f"   Generating embeddings...")
        embeddings = generate_embeddings(texts, client)

        # Compute similarity
        print(f"   Computing similarity...")
        distances, similarity = compute_similarity(embeddings, valid_mask)

        # Clustering
        print(f"   Clustering...")
        labels, dist_to_centroid = run_clustering(embeddings, valid_mask, N_CLUSTERS)

        # Persist to database
        print(f"   Persisting to database...")
        persist_band_results(conn, site_ids, band, embeddings, distances,
                           similarity, labels, dist_to_centroid, valid_mask)

        # Store for output file
        results[band] = {
            'valid_count': int(valid_count),
            'embeddings': embeddings.tolist(),
            'similarity': similarity.tolist(),
            'clusters': labels.tolist()
        }

    conn.commit()
    conn.close()

    # Write JSON output
    with open(OUTPUT_FILE, 'w') as f:
        json.dump({
            'site_ids': site_ids,
            'site_names': [s['name'] for s in sites],
            'model': EMBEDDING_MODEL,
            'bands': results
        }, f, indent=2)

    print(f"\nWrote embeddings to {OUTPUT_FILE}")

    # Print summary
    print("\n" + "=" * 60)
    print("SIMILARITY EXAMPLES (composite)")
    print("=" * 60)

    if 'composite' in results:
        sim = np.array(results['composite']['similarity'])
        names = [s['name'] for s in sites]

        # Find top pairs
        pairs = []
        for i in range(len(names)):
            for j in range(i+1, len(names)):
                if sim[i, j] > 0:
                    pairs.append((names[i], names[j], sim[i, j]))

        pairs.sort(key=lambda x: -x[2])
        print("\nMost similar pairs:")
        for n1, n2, s in pairs[:5]:
            print(f"  {s:.3f}  {n1[:30]} <-> {n2[:30]}")

        print("\nLeast similar pairs:")
        for n1, n2, s in pairs[-5:]:
            print(f"  {s:.3f}  {n1[:30]} <-> {n2[:30]}")

    print("\nDone!")


if __name__ == "__main__":
    main()
