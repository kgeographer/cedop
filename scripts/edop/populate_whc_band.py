#!/usr/bin/env python3
"""
Populate WHC band tables from corpus_258 JSON files.

Reads:
- output/corpus_258/band_summaries.json -> whc_band_summaries
- output/corpus_258/band_embeddings.json -> whc_band_clusters, whc_band_similarity, whc_band_metadata

Prerequisites:
- sql/whc_band_schema.sql run to create tables
- wh_cities table populated

Usage:
    python scripts/populate_whc_band.py
"""

import json
import os
from datetime import datetime
from pathlib import Path

import psycopg

INPUT_DIR = Path(__file__).parent.parent / "output" / "corpus_258"
SUMMARIES_FILE = INPUT_DIR / "band_summaries.json"
EMBEDDINGS_FILE = INPUT_DIR / "band_embeddings.json"


def get_db_connection():
    """Create database connection from environment variables."""
    return psycopg.connect(
        host=os.environ.get("PGHOST", "localhost"),
        port=os.environ.get("PGPORT", "5435"),
        dbname=os.environ.get("PGDATABASE", "edop"),
        user=os.environ.get("PGUSER", "postgres"),
        password=os.environ.get("PGPASSWORD", ""),
    )


def parse_whc_id(whc_id: str) -> int:
    """Convert 'whc_1' or 'whc_001' to integer 1."""
    return int(whc_id.replace("whc_", "").lstrip("0") or "0")


def load_summaries() -> list[dict]:
    """Load band summaries JSON."""
    with open(SUMMARIES_FILE) as f:
        return json.load(f)


def load_embeddings() -> dict:
    """Load band embeddings JSON."""
    with open(EMBEDDINGS_FILE) as f:
        return json.load(f)


def populate_summaries(conn, summaries: list[dict]):
    """Populate whc_band_summaries table."""
    print("\n   Populating whc_band_summaries...")

    bands = ['history', 'environment', 'culture', 'modern']
    inserted = 0

    with conn.cursor() as cur:
        cur.execute("DELETE FROM whc_band_summaries")

        for city in summaries:
            city_id = parse_whc_id(city['whc_id'])
            processed_at = city.get('processed_at')

            # Parse timestamp if present
            if processed_at:
                try:
                    processed_at = datetime.fromisoformat(processed_at.replace('Z', '+00:00'))
                except:
                    processed_at = None

            for band in bands:
                summary_data = city.get('summaries', {}).get(band, {})
                if not summary_data:
                    continue

                cur.execute("""
                    INSERT INTO whc_band_summaries
                    (city_id, band, status, summary, source_chars, summary_chars,
                     input_tokens, output_tokens, processed_at)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                """, (
                    city_id,
                    band,
                    summary_data.get('status', 'no_content'),
                    summary_data.get('summary'),
                    summary_data.get('source_chars'),
                    summary_data.get('summary_chars'),
                    summary_data.get('input_tokens'),
                    summary_data.get('output_tokens'),
                    processed_at
                ))
                inserted += 1

    print(f"   Inserted {inserted} rows into whc_band_summaries")
    return inserted


def populate_clusters(conn, embeddings: dict):
    """Populate whc_band_clusters table."""
    print("\n   Populating whc_band_clusters...")

    cities = embeddings['cities']
    bands_data = embeddings['bands']
    inserted = 0

    with conn.cursor() as cur:
        cur.execute("DELETE FROM whc_band_clusters")

        for band_name, band_data in bands_data.items():
            clusters = band_data.get('clusters', [])
            distances = band_data.get('cluster_distances', [])

            for i, (cluster_id, distance) in enumerate(zip(clusters, distances)):
                if cluster_id == -1:  # Invalid/missing
                    continue

                city_id = parse_whc_id(cities[i]['whc_id'])

                cur.execute("""
                    INSERT INTO whc_band_clusters
                    (city_id, band, cluster_id, distance_to_centroid)
                    VALUES (%s, %s, %s, %s)
                """, (city_id, band_name, cluster_id, distance))
                inserted += 1

    print(f"   Inserted {inserted} rows into whc_band_clusters")
    return inserted


def populate_similarity(conn, embeddings: dict):
    """Populate whc_band_similarity table."""
    print("\n   Populating whc_band_similarity...")

    cities = embeddings['cities']
    bands_data = embeddings['bands']
    inserted = 0

    with conn.cursor() as cur:
        cur.execute("DELETE FROM whc_band_similarity")

        for band_name, band_data in bands_data.items():
            top_similar = band_data.get('top_similar', [])

            for i, similar_list in enumerate(top_similar):
                if not similar_list:
                    continue

                city_a_id = parse_whc_id(cities[i]['whc_id'])

                for rank, item in enumerate(similar_list, 1):
                    city_b_idx = item['idx']
                    similarity = item['sim']
                    city_b_id = parse_whc_id(cities[city_b_idx]['whc_id'])

                    cur.execute("""
                        INSERT INTO whc_band_similarity
                        (city_a, city_b, band, similarity, rank)
                        VALUES (%s, %s, %s, %s, %s)
                    """, (city_a_id, city_b_id, band_name, similarity, rank))
                    inserted += 1

    print(f"   Inserted {inserted} rows into whc_band_similarity")
    return inserted


def populate_metadata(conn, embeddings: dict):
    """Populate whc_band_metadata table."""
    print("\n   Populating whc_band_metadata...")

    with conn.cursor() as cur:
        cur.execute("DELETE FROM whc_band_metadata")
        cur.execute("""
            INSERT INTO whc_band_metadata (embedding_model, n_clusters)
            VALUES (%s, %s)
        """, (embeddings['model'], embeddings['n_clusters']))

    print("   Inserted metadata row")


def main():
    print("=" * 60)
    print("WHC Band Data Population")
    print("=" * 60)

    print("\n1. Loading JSON files...")
    summaries = load_summaries()
    embeddings = load_embeddings()
    print(f"   Summaries: {len(summaries)} cities")
    print(f"   Embeddings: {len(embeddings['cities'])} cities, {len(embeddings['bands'])} bands")

    print("\n2. Connecting to database...")
    conn = get_db_connection()

    try:
        print("\n3. Populating tables...")

        n_summaries = populate_summaries(conn, summaries)
        n_clusters = populate_clusters(conn, embeddings)
        n_similarity = populate_similarity(conn, embeddings)
        populate_metadata(conn, embeddings)

        conn.commit()
        print("\n   Committed.")

        # Summary
        print("\n" + "=" * 60)
        print("SUMMARY")
        print("=" * 60)

        with conn.cursor() as cur:
            for table in ['whc_band_summaries', 'whc_band_clusters',
                         'whc_band_similarity', 'whc_band_metadata']:
                cur.execute(f"SELECT COUNT(*) FROM {table}")
                print(f"{table}: {cur.fetchone()[0]} rows")

        # Sample queries
        print("\n" + "=" * 60)
        print("SAMPLE DATA")
        print("=" * 60)

        with conn.cursor() as cur:
            print("\nTop cities most similar to Timbuktu (composite band):")
            cur.execute("""
                SELECT c2.city, c2.country, ROUND(s.similarity::numeric, 3)
                FROM whc_band_similarity s
                JOIN wh_cities c1 ON c1.id = s.city_a
                JOIN wh_cities c2 ON c2.id = s.city_b
                WHERE c1.city = 'Timbuktu' AND s.band = 'composite'
                ORDER BY s.rank
                LIMIT 5
            """)
            for row in cur.fetchall():
                print(f"  {row[0]}, {row[1]} (sim={row[2]})")

            print("\nCluster distribution (composite):")
            cur.execute("""
                SELECT cluster_id, COUNT(*) as n
                FROM whc_band_clusters
                WHERE band = 'composite'
                GROUP BY cluster_id
                ORDER BY cluster_id
            """)
            for row in cur.fetchall():
                print(f"  Cluster {row[0]}: {row[1]} cities")

    except Exception as e:
        conn.rollback()
        print(f"\nERROR: {e}")
        raise
    finally:
        conn.close()

    print("\nDone!")


if __name__ == "__main__":
    main()
