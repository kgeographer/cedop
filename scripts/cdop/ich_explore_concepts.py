"""
ICH Data Exploration - Phase 1: Concept Taxonomy Analysis
"""
import sys
sys.path.insert(0, '/Users/karlg/Documents/Repos/_cedop')

from scripts.shared.db_utils import db_connect
from psycopg.rows import dict_row

def run_query(conn, query, description):
    """Run a query and print results."""
    print(f"\n{'='*60}")
    print(f"{description}")
    print('='*60)
    with conn.cursor(row_factory=dict_row) as cur:
        cur.execute(query)
        rows = cur.fetchall()
        for row in rows:
            print(dict(row))
        print(f"\n({len(rows)} rows)")
    return rows

def main():
    conn = db_connect(schema="cdop")

    # 1. Get all distinct concepts with counts
    print("\n" + "="*60)
    print("1. ALL DISTINCT CONCEPTS (with element counts)")
    print("="*60)

    query1 = """
    SELECT concept, count(*) as element_count
    FROM (
        SELECT ich_id, trim(unnest(string_to_array(primary_concepts, '; '))) as concept
        FROM cdop.ich_elements
        WHERE primary_concepts IS NOT NULL AND primary_concepts != ''
    ) sub
    GROUP BY concept
    ORDER BY element_count DESC;
    """

    with conn.cursor(row_factory=dict_row) as cur:
        cur.execute(query1)
        concepts = cur.fetchall()

        # Categorize concepts
        env_concepts = ['Mountains', 'Drylands', 'Forests', 'Grasslands, savannahs',
                        'Marine, coastal and island areas', 'Inland wetlands']

        print("\n--- ENVIRONMENTAL CONCEPTS ---")
        for row in concepts:
            if row['concept'] in env_concepts:
                print(f"  {row['concept']}: {row['element_count']}")

        print("\n--- OTHER CONCEPTS (top 30) ---")
        other_count = 0
        for row in concepts:
            if row['concept'] not in env_concepts:
                if other_count < 30:
                    print(f"  {row['concept']}: {row['element_count']}")
                other_count += 1
        print(f"\n  ... and {other_count - 30} more concepts" if other_count > 30 else "")

        print(f"\nTotal distinct concepts: {len(concepts)}")

    # 2. Environmental concept co-occurrence with other concepts
    print("\n" + "="*60)
    print("2. ENVIRONMENTAL CONCEPT CO-OCCURRENCE (top 25)")
    print("="*60)

    query2 = """
    SELECT e1.concept as env_concept, e2.concept as co_concept, count(*) as count
    FROM (
        SELECT ich_id, trim(unnest(string_to_array(primary_concepts, '; '))) as concept
        FROM cdop.ich_elements
    ) e1
    JOIN (
        SELECT ich_id, trim(unnest(string_to_array(primary_concepts, '; '))) as concept
        FROM cdop.ich_elements
    ) e2 ON e1.ich_id = e2.ich_id
    WHERE e1.concept IN ('Mountains','Drylands','Forests','Grasslands, savannahs',
                         'Marine, coastal and island areas','Inland wetlands')
      AND e2.concept NOT IN ('Mountains','Drylands','Forests','Grasslands, savannahs',
                             'Marine, coastal and island areas','Inland wetlands')
    GROUP BY 1,2
    ORDER BY 3 DESC
    LIMIT 25;
    """

    with conn.cursor(row_factory=dict_row) as cur:
        cur.execute(query2)
        for row in cur.fetchall():
            print(f"  {row['env_concept']} + {row['co_concept']}: {row['count']}")

    # 3. Elements per environmental concept
    print("\n" + "="*60)
    print("3. SAMPLE ELEMENTS BY ENVIRONMENTAL CONCEPT")
    print("="*60)

    for env in ['Mountains', 'Drylands', 'Marine, coastal and island areas']:
        query3 = f"""
        SELECT e.ich_id, e.label, e.countries
        FROM cdop.ich_elements e
        WHERE e.primary_concepts LIKE '%{env}%'
        LIMIT 5;
        """
        print(f"\n--- {env.upper()} (sample of 5) ---")
        with conn.cursor(row_factory=dict_row) as cur:
            cur.execute(query3)
            for row in cur.fetchall():
                countries = row['countries'][:50] + '...' if len(row['countries']) > 50 else row['countries']
                print(f"  [{row['ich_id']}] {row['label'][:60]}")
                print(f"       Countries: {countries}")

    conn.close()
    print("\n" + "="*60)
    print("Phase 1 complete.")

if __name__ == "__main__":
    main()
