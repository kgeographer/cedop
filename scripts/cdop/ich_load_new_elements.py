"""
Load new 2024-2025 ICH elements into database.

Sources:
- output/cdop/ich_update/new_summaries.json (135 elements with summaries)
- output/cdop/ich_update/discovery.json (has URLs)

Targets:
- cdop.ich_elements
- cdop.ich_summaries
"""
import sys
import json
from pathlib import Path

sys.path.insert(0, '/Users/karlg/Documents/Repos/_cedop')
from dotenv import load_dotenv
load_dotenv(Path('/Users/karlg/Documents/Repos/_cedop/.env'))

from scripts.shared.db_utils import db_connect

OUTPUT_DIR = Path('/Users/karlg/Documents/Repos/_cedop/output/cdop/ich_update')

# Map list_type codes
LIST_MAP = {
    'RL': 'RL',
    'USL': 'USL',
    'GSP': 'GSP',
    'Representative List': 'RL',
    'Urgent Safeguarding List': 'USL',
    'Good Safeguarding Practices': 'GSP',
}


def main():
    # Load data
    with open(OUTPUT_DIR / 'new_summaries.json') as f:
        summaries = json.load(f)

    with open(OUTPUT_DIR / 'discovery.json') as f:
        discovery = json.load(f)

    # Build URL lookup from discovery
    url_lookup = {e['ich_id']: e['url'] for e in discovery['new_elements']}

    print(f"Loaded {len(summaries)} new elements")

    conn = db_connect(schema='cdop')
    cur = conn.cursor()

    # Check which elements already exist
    cur.execute("SELECT ich_id FROM ich_elements")
    existing_ids = {row[0] for row in cur.fetchall()}

    new_count = 0
    skip_count = 0

    for item in summaries:
        ich_id = item['ich_id']

        if ich_id in existing_ids:
            skip_count += 1
            continue

        # Insert into ich_elements
        cur.execute("""
            INSERT INTO ich_elements (ich_id, label, countries, year, list, link)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (
            ich_id,
            item['title'],
            item['country'],
            int(item['year']),
            LIST_MAP.get(item['list_type'], item['list_type']),
            url_lookup.get(ich_id, f"https://ich.unesco.org/en/RL/{ich_id}")
        ))

        # Insert into ich_summaries
        cur.execute("""
            INSERT INTO ich_summaries (ich_id, text)
            VALUES (%s, %s)
        """, (
            ich_id,
            item['summary']
        ))

        new_count += 1

    conn.commit()

    # Verify
    cur.execute("SELECT count(*), max(year) FROM ich_elements")
    total, max_year = cur.fetchone()

    cur.execute("SELECT count(*) FROM ich_summaries")
    summary_count = cur.fetchone()[0]

    print(f"\nResults:")
    print(f"  New elements inserted: {new_count}")
    print(f"  Skipped (already exist): {skip_count}")
    print(f"  Total elements now: {total}")
    print(f"  Max year: {max_year}")
    print(f"  Total summaries: {summary_count}")

    # Show year breakdown for new data
    cur.execute("""
        SELECT year, count(*)
        FROM ich_elements
        WHERE year >= 2024
        GROUP BY year
        ORDER BY year
    """)
    print(f"\nNew elements by year:")
    for year, count in cur.fetchall():
        print(f"  {year}: {count}")

    conn.close()


if __name__ == "__main__":
    main()
