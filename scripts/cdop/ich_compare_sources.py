"""
Compare ICH data sources for a specific element
"""
import sys
import json
sys.path.insert(0, '/Users/karlg/Documents/Repos/_cedop')

from scripts.shared.db_utils import db_connect
from psycopg.rows import dict_row

def main():
    ich_id = "00202"  # Grand song of the Dong

    conn = db_connect(schema="cdop")

    # 1. Get summary from database
    print("="*70)
    print(f"DATABASE SUMMARY (ich_summaries) for {ich_id}")
    print("="*70)

    with conn.cursor(row_factory=dict_row) as cur:
        cur.execute("""
            SELECT s.text, length(s.text) as chars, e.label, e.countries, e.primary_concepts
            FROM cdop.ich_summaries s
            JOIN cdop.ich_elements e ON s.ich_id = e.ich_id
            WHERE s.ich_id = %s
        """, (ich_id,))
        row = cur.fetchone()
        if row:
            print(f"Label: {row['label']}")
            print(f"Countries: {row['countries']}")
            print(f"Concepts: {row['primary_concepts']}")
            print(f"Length: {row['chars']} chars")
            print(f"\nText:\n{row['text']}")

    # 2. Get toponyms from cleaner
    print("\n" + "="*70)
    print(f"EXTRACTED TOPONYMS (ich_toponyms_cleaner) for {ich_id}")
    print("="*70)

    with conn.cursor(row_factory=dict_row) as cur:
        cur.execute("""
            SELECT array_agg(toponym ORDER BY toponym) as toponyms
            FROM cdop.ich_toponyms_cleaner
            WHERE ich_id = %s
        """, (ich_id,))
        row = cur.fetchone()
        if row and row['toponyms']:
            print(f"Toponyms ({len(row['toponyms'])}): {row['toponyms']}")

    conn.close()

    # 3. Check graph_en.json for this element
    print("\n" + "="*70)
    print(f"GRAPH DATA (graph_en.json) for element matching '{ich_id}'")
    print("="*70)

    with open('/Users/karlg/Documents/Repos/_cedop/app/data/ich/graph_en.json', 'r') as f:
        graph = json.load(f)

    # Search for element with matching ID
    for node_id, node in graph.get('nodes', {}).items():
        if node.get('type') == 'element':
            # The graph uses different IDs, try to match by label
            label = node.get('label', '')
            if 'Dong' in label and 'song' in label.lower():
                print(f"Node ID: {node_id}")
                print(f"Label: {label}")
                desc = node.get('meta', {}).get('description', '')
                print(f"Description length: {len(desc)} chars")
                print(f"Description preview: {desc[:500]}...")
                break

if __name__ == "__main__":
    main()
