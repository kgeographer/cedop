"""
Select sample documents for LLM extraction prototype
"""
import sys
import os
sys.path.insert(0, '/Users/karlg/Documents/Repos/_cedop')

from scripts.shared.db_utils import db_connect
from psycopg.rows import dict_row

def main():
    conn = db_connect(schema="cdop")

    # Get all elements with their concepts
    query = """
    SELECT ich_id, label, countries, primary_concepts,
           CASE
             WHEN primary_concepts LIKE '%Mountains%' THEN 'Mountains'
             WHEN primary_concepts LIKE '%Drylands%' THEN 'Drylands'
             WHEN primary_concepts LIKE '%Forests%' THEN 'Forests'
             WHEN primary_concepts LIKE '%Grasslands%' THEN 'Grasslands'
             WHEN primary_concepts LIKE '%Marine%' THEN 'Marine/coastal'
             WHEN primary_concepts LIKE '%wetlands%' THEN 'Wetlands'
             ELSE NULL
           END as env_concept
    FROM cdop.ich_elements
    ORDER BY ich_id
    """

    doc_dir = '/Users/karlg/Documents/Repos/_cedop/app/data/ich/extracted_clean_02'
    available_docs = set()
    for f in os.listdir(doc_dir):
        if f.endswith('.txt'):
            # Extract ich_id from filename (format: 00202_full_text_clean.txt or 01080_extracted_cleaned.txt)
            ich_id = f.split('_')[0]
            available_docs.add(ich_id)

    print(f"Total nomination documents available: {len(available_docs)}")

    with conn.cursor(row_factory=dict_row) as cur:
        cur.execute(query)
        rows = cur.fetchall()

    # Categorize elements
    env_with_doc = []
    env_without_doc = []
    non_env_with_doc = []

    for row in rows:
        has_doc = row['ich_id'] in available_docs
        if row['env_concept']:
            if has_doc:
                env_with_doc.append(row)
            else:
                env_without_doc.append(row)
        else:
            if has_doc:
                non_env_with_doc.append(row)

    print(f"\nEnvironmental-tagged WITH nomination doc: {len(env_with_doc)}")
    print(f"Environmental-tagged WITHOUT nomination doc: {len(env_without_doc)}")
    print(f"Non-environmental WITH nomination doc: {len(non_env_with_doc)}")

    # Check for explicit coordinates in env docs
    print("\n" + "="*70)
    print("ENVIRONMENTAL DOCS WITH EXPLICIT COORDINATES")
    print("="*70)

    coord_docs = []
    for row in env_with_doc:
        doc_path = None
        for f in os.listdir(doc_dir):
            if f.startswith(row['ich_id'] + '_'):
                doc_path = os.path.join(doc_dir, f)
                break
        if doc_path:
            with open(doc_path, 'r') as f:
                content = f.read()
                if 'longitude' in content.lower() or 'latitude' in content.lower():
                    coord_docs.append((row, len(content)))
                    if len(coord_docs) <= 5:
                        print(f"\n[{row['ich_id']}] {row['label'][:50]}")
                        print(f"  Env: {row['env_concept']}, Countries: {row['countries'][:40]}")
                        print(f"  Doc length: {len(content)} chars")

    print(f"\n... {len(coord_docs)} total env docs with coordinates")

    # Suggest mixed sample
    print("\n" + "="*70)
    print("SUGGESTED MIXED SAMPLE (5 docs)")
    print("="*70)

    sample = []

    # 2 environmental with coordinates
    print("\n--- Environmental with coordinates (2) ---")
    for row, length in coord_docs[:2]:
        sample.append(row['ich_id'])
        print(f"  [{row['ich_id']}] {row['label'][:50]} ({row['env_concept']})")

    # 1 environmental without coordinates
    print("\n--- Environmental without coordinates (1) ---")
    for row in env_with_doc:
        if row['ich_id'] not in [r['ich_id'] for r, _ in coord_docs]:
            sample.append(row['ich_id'])
            print(f"  [{row['ich_id']}] {row['label'][:50]} ({row['env_concept']})")
            break

    # 2 non-environmental (one with coordinates, one without)
    print("\n--- Non-environmental (2) ---")
    added = 0
    for row in non_env_with_doc:
        doc_path = None
        for f in os.listdir(doc_dir):
            if f.startswith(row['ich_id'] + '_'):
                doc_path = os.path.join(doc_dir, f)
                break
        if doc_path:
            with open(doc_path, 'r') as f:
                content = f.read()
            has_coords = 'longitude' in content.lower() or 'latitude' in content.lower()
            # Get one with coords, one without
            if added == 0 and has_coords:
                sample.append(row['ich_id'])
                print(f"  [{row['ich_id']}] {row['label'][:50]} (with coords)")
                added += 1
            elif added == 1 and not has_coords and len(content) > 5000:
                sample.append(row['ich_id'])
                print(f"  [{row['ich_id']}] {row['label'][:50]} (no coords, {len(content)} chars)")
                added += 1
            if added >= 2:
                break

    print(f"\n\nFinal sample IDs: {sample}")

    conn.close()

if __name__ == "__main__":
    main()
