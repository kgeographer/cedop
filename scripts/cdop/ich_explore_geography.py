"""
ICH Data Exploration - Phase 2: Geographic Analysis
Uses gaz.admin0 for UN subregion mapping
"""
import sys
sys.path.insert(0, '/Users/karlg/Documents/Repos/_cedop')

from scripts.shared.db_utils import db_connect
from psycopg.rows import dict_row

def main():
    conn = db_connect()

    # 1. First, explore the country field structure
    print("\n" + "="*60)
    print("1. COUNTRY FIELD STRUCTURE (sample)")
    print("="*60)

    query1 = """
    SELECT ich_id, label, countries
    FROM cdop.ich_elements
    ORDER BY array_length(string_to_array(countries, ', '), 1) DESC NULLS LAST
    LIMIT 10;
    """
    with conn.cursor(row_factory=dict_row) as cur:
        cur.execute(query1)
        for row in cur.fetchall():
            print(f"  [{row['ich_id']}] {row['label'][:50]}")
            print(f"       Countries: {row['countries']}")

    # 2. Check gaz.admin0 structure
    print("\n" + "="*60)
    print("2. GAZ.ADMIN0 STRUCTURE (sample)")
    print("="*60)

    query2 = """
    SELECT column_name, data_type
    FROM information_schema.columns
    WHERE table_schema = 'gaz' AND table_name = 'admin0'
    ORDER BY ordinal_position;
    """
    with conn.cursor(row_factory=dict_row) as cur:
        cur.execute(query2)
        for row in cur.fetchall():
            print(f"  {row['column_name']}: {row['data_type']}")

    # 3. Sample admin0 data to see field values
    print("\n" + "="*60)
    print("3. SAMPLE ADMIN0 DATA")
    print("="*60)

    query3 = """
    SELECT name, iso_a2, subregion
    FROM gaz.admin0
    LIMIT 15;
    """
    with conn.cursor(row_factory=dict_row) as cur:
        cur.execute(query3)
        for row in cur.fetchall():
            print(f"  {row['name']} ({row['iso_a2']}): {row['subregion']}")

    # 4. Elements by country (top 20)
    print("\n" + "="*60)
    print("4. ELEMENTS BY COUNTRY (top 20)")
    print("="*60)

    query4 = """
    SELECT trim(unnest(string_to_array(countries, ', '))) as country, count(*) as count
    FROM cdop.ich_elements
    GROUP BY 1
    ORDER BY 2 DESC
    LIMIT 20;
    """
    with conn.cursor(row_factory=dict_row) as cur:
        cur.execute(query4)
        for row in cur.fetchall():
            print(f"  {row['country']}: {row['count']}")

    # 5. Try to match countries to admin0 for subregion analysis
    print("\n" + "="*60)
    print("5. ELEMENTS BY UN SUBREGION")
    print("="*60)

    query5 = """
    WITH country_elements AS (
        SELECT ich_id, trim(unnest(string_to_array(countries, ', '))) as country
        FROM cdop.ich_elements
    )
    SELECT a.subregion, count(DISTINCT ce.ich_id) as element_count
    FROM country_elements ce
    LEFT JOIN gaz.admin0 a ON lower(ce.country) = lower(a.name)
    WHERE a.subregion IS NOT NULL
    GROUP BY a.subregion
    ORDER BY element_count DESC;
    """
    with conn.cursor(row_factory=dict_row) as cur:
        cur.execute(query5)
        for row in cur.fetchall():
            print(f"  {row['subregion']}: {row['element_count']}")

    # 6. Check unmatched countries
    print("\n" + "="*60)
    print("6. UNMATCHED COUNTRIES (need name mapping)")
    print("="*60)

    query6 = """
    WITH country_elements AS (
        SELECT DISTINCT trim(unnest(string_to_array(countries, ', '))) as country
        FROM cdop.ich_elements
    )
    SELECT ce.country
    FROM country_elements ce
    LEFT JOIN gaz.admin0 a ON lower(ce.country) = lower(a.name)
    WHERE a.name IS NULL
    ORDER BY ce.country;
    """
    with conn.cursor(row_factory=dict_row) as cur:
        cur.execute(query6)
        unmatched = cur.fetchall()
        for row in unmatched:
            print(f"  {row['country']}")
        print(f"\n  ({len(unmatched)} unmatched countries)")

    # 7. Multinational elements
    print("\n" + "="*60)
    print("7. MULTINATIONAL ELEMENTS (cultural diffusion)")
    print("="*60)

    query7 = """
    SELECT ich_id, label, countries,
           array_length(string_to_array(countries, ', '), 1) as country_count
    FROM cdop.ich_elements
    WHERE array_length(string_to_array(countries, ', '), 1) > 1
    ORDER BY country_count DESC
    LIMIT 15;
    """
    with conn.cursor(row_factory=dict_row) as cur:
        cur.execute(query7)
        for row in cur.fetchall():
            print(f"  [{row['country_count']} countries] {row['label'][:50]}")
            print(f"       {row['countries'][:80]}...")

    # 8. Toponym density per element
    print("\n" + "="*60)
    print("8. TOPONYM DENSITY DISTRIBUTION")
    print("="*60)

    query8 = """
    SELECT
        CASE
            WHEN toponym_count = 0 THEN '0 toponyms'
            WHEN toponym_count BETWEEN 1 AND 5 THEN '1-5 toponyms'
            WHEN toponym_count BETWEEN 6 AND 10 THEN '6-10 toponyms'
            WHEN toponym_count BETWEEN 11 AND 20 THEN '11-20 toponyms'
            ELSE '20+ toponyms'
        END as density_bucket,
        count(*) as element_count
    FROM (
        SELECT e.ich_id, count(t.toponym) as toponym_count
        FROM cdop.ich_elements e
        LEFT JOIN cdop.ich_toponyms_cleaner t ON e.ich_id = t.ich_id
        GROUP BY e.ich_id
    ) sub
    GROUP BY 1
    ORDER BY 1;
    """
    with conn.cursor(row_factory=dict_row) as cur:
        cur.execute(query8)
        for row in cur.fetchall():
            print(f"  {row['density_bucket']}: {row['element_count']} elements")

    # 9. Elements by UNESCO list
    print("\n" + "="*60)
    print("9. ELEMENTS BY UNESCO LIST")
    print("="*60)

    query9 = """
    SELECT list, count(*) as count
    FROM cdop.ich_elements
    GROUP BY list
    ORDER BY count DESC;
    """
    with conn.cursor(row_factory=dict_row) as cur:
        cur.execute(query9)
        for row in cur.fetchall():
            print(f"  {row['list']}: {row['count']}")

    # 10. Elements by year
    print("\n" + "="*60)
    print("10. INSCRIPTIONS BY YEAR")
    print("="*60)

    query10 = """
    SELECT year, count(*) as count
    FROM cdop.ich_elements
    GROUP BY year
    ORDER BY year;
    """
    with conn.cursor(row_factory=dict_row) as cur:
        cur.execute(query10)
        for row in cur.fetchall():
            print(f"  {row['year']}: {row['count']}")

    conn.close()
    print("\n" + "="*60)
    print("Phase 2 complete.")

if __name__ == "__main__":
    main()
