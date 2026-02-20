#!/usr/bin/env python3
"""
Populate the basin_cluster_labels table from basin08_cluster_labels_manual.json.

Run this after any re-clustering to keep the DB labels in sync with the
manual label assignments. Creates the table if it does not exist.

Usage:
    python scripts/edop/populate_basin_cluster_labels.py
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))
from scripts.shared.db_utils import db_connect

MANUAL_JSON = Path(__file__).parent.parent.parent / "output" / "edop" / "basin08_cluster_labels_manual.json"


def main():
    if not MANUAL_JSON.exists():
        print(f"ERROR: {MANUAL_JSON} not found")
        sys.exit(1)

    with open(MANUAL_JSON) as f:
        data = json.load(f)

    clusters = data.get("clusters", {})
    if not clusters:
        print("ERROR: no 'clusters' key found in JSON")
        sys.exit(1)

    rows = [(int(k), v["label"]) for k, v in clusters.items()]
    print(f"Loaded {len(rows)} labels from {MANUAL_JSON.name}")

    conn = db_connect()
    try:
        with conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS basin_cluster_labels (
                    cluster_id  INTEGER PRIMARY KEY,
                    label       TEXT NOT NULL
                )
            """)
            cur.execute("DELETE FROM basin_cluster_labels")
            cur.executemany(
                "INSERT INTO basin_cluster_labels (cluster_id, label) VALUES (%s, %s)",
                rows
            )
            conn.commit()
            cur.execute("SELECT cluster_id, label FROM basin_cluster_labels ORDER BY cluster_id")
            for row in cur.fetchall():
                print(f"  {row[0]:>2}: {row[1]}")
        print(f"\nDone. {len(rows)} rows in basin_cluster_labels.")
    finally:
        conn.close()


if __name__ == "__main__":
    main()
