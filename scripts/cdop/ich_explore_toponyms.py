"""
ICH Data Exploration - Phase 4: Toponym Quality Assessment
Assess NER extraction quality and gazetteer reconciliation readiness
"""
import sys
sys.path.insert(0, '/Users/karlg/Documents/Repos/_cedop')

from scripts.shared.db_utils import db_connect
from psycopg.rows import dict_row

def main():
    conn = db_connect(schema="cdop")

    # 1. Table structure comparison
    print("\n" + "="*60)
    print("1. TOPONYM TABLE STRUCTURES")
    print("="*60)

    for table in ['ich_toponyms_ner', 'ich_toponyms_cleaner', 'ich_lptsv_raw']:
        query = f"""
        SELECT column_name, data_type
        FROM information_schema.columns
        WHERE table_schema = 'cdop' AND table_name = '{table}'
        ORDER BY ordinal_position;
        """
        print(f"\n--- {table} ---")
        with conn.cursor(row_factory=dict_row) as cur:
            cur.execute(query)
            for row in cur.fetchall():
                print(f"  {row['column_name']}: {row['data_type']}")

    # 2. Row counts and coverage
    print("\n" + "="*60)
    print("2. ROW COUNTS AND ELEMENT COVERAGE")
    print("="*60)

    query2 = """
    SELECT
        (SELECT count(*) FROM cdop.ich_toponyms_ner) as ner_rows,
        (SELECT count(DISTINCT ich_id) FROM cdop.ich_toponyms_ner) as ner_elements,
        (SELECT count(*) FROM cdop.ich_toponyms_cleaner) as cleaner_rows,
        (SELECT count(DISTINCT ich_id) FROM cdop.ich_toponyms_cleaner) as cleaner_elements,
        (SELECT count(*) FROM cdop.ich_lptsv_raw) as lptsv_rows,
        (SELECT count(DISTINCT ich_id) FROM cdop.ich_lptsv_raw) as lptsv_elements,
        (SELECT count(*) FROM cdop.ich_elements) as total_elements;
    """
    with conn.cursor(row_factory=dict_row) as cur:
        cur.execute(query2)
        row = cur.fetchone()
        print(f"  ich_toponyms_ner:     {row['ner_rows']:,} rows, {row['ner_elements']} elements ({100*row['ner_elements']/row['total_elements']:.0f}%)")
        print(f"  ich_toponyms_cleaner: {row['cleaner_rows']:,} rows, {row['cleaner_elements']} elements")
        print(f"  ich_lptsv_raw:        {row['lptsv_rows']:,} rows, {row['lptsv_elements']} elements")
        print(f"  Rows removed by cleaning: {row['ner_rows'] - row['cleaner_rows']}")

    # 3. Sample NER vs Cleaner comparison
    print("\n" + "="*60)
    print("3. SAMPLE: NER vs CLEANER COMPARISON")
    print("="*60)

    query3 = """
    WITH ner AS (
        SELECT ich_id, array_agg(DISTINCT toponym ORDER BY toponym) as toponyms
        FROM cdop.ich_toponyms_ner
        GROUP BY ich_id
    ),
    cleaner AS (
        SELECT ich_id, array_agg(DISTINCT toponym ORDER BY toponym) as toponyms
        FROM cdop.ich_toponyms_cleaner
        GROUP BY ich_id
    )
    SELECT n.ich_id, e.label,
           array_length(n.toponyms, 1) as ner_count,
           array_length(c.toponyms, 1) as cleaner_count,
           n.toponyms as ner_toponyms,
           c.toponyms as cleaner_toponyms
    FROM ner n
    JOIN cleaner c ON n.ich_id = c.ich_id
    JOIN cdop.ich_elements e ON n.ich_id = e.ich_id
    WHERE array_length(n.toponyms, 1) > array_length(c.toponyms, 1)
    ORDER BY (array_length(n.toponyms, 1) - array_length(c.toponyms, 1)) DESC
    LIMIT 5;
    """
    with conn.cursor(row_factory=dict_row) as cur:
        cur.execute(query3)
        for row in cur.fetchall():
            print(f"\n  [{row['ich_id']}] {row['label'][:50]}")
            print(f"  NER count: {row['ner_count']}, Cleaner count: {row['cleaner_count']}")
            # Find what was removed
            ner_set = set(row['ner_toponyms']) if row['ner_toponyms'] else set()
            cleaner_set = set(row['cleaner_toponyms']) if row['cleaner_toponyms'] else set()
            removed = ner_set - cleaner_set
            print(f"  REMOVED: {list(removed)[:10]}")

    # 4. Identify NER false positive patterns
    print("\n" + "="*60)
    print("4. LIKELY FALSE POSITIVES (removed by cleaning)")
    print("="*60)

    query4 = """
    SELECT n.toponym, count(*) as occurrences
    FROM cdop.ich_toponyms_ner n
    LEFT JOIN cdop.ich_toponyms_cleaner c
        ON n.ich_id = c.ich_id AND n.toponym = c.toponym
    WHERE c.toponym IS NULL
    GROUP BY n.toponym
    ORDER BY occurrences DESC
    LIMIT 30;
    """
    with conn.cursor(row_factory=dict_row) as cur:
        cur.execute(query4)
        print("\n  Toponyms in NER but removed from cleaner (top 30):")
        for row in cur.fetchall():
            print(f"    '{row['toponym']}': {row['occurrences']} occurrences")

    # 5. Explore lptsv_raw structure
    print("\n" + "="*60)
    print("5. LPTSV_RAW SAMPLE DATA")
    print("="*60)

    query5 = """
    SELECT * FROM cdop.ich_lptsv_raw LIMIT 10;
    """
    with conn.cursor(row_factory=dict_row) as cur:
        cur.execute(query5)
        for row in cur.fetchall():
            print(f"  {dict(row)}")

    # 6. Feature class distribution in lptsv
    print("\n" + "="*60)
    print("6. FEATURE CLASS DISTRIBUTION (lptsv_raw)")
    print("="*60)

    query6 = """
    SELECT fclasses, count(*) as count
    FROM cdop.ich_lptsv_raw
    WHERE fclasses IS NOT NULL AND fclasses != ''
    GROUP BY fclasses
    ORDER BY count DESC
    LIMIT 15;
    """
    with conn.cursor(row_factory=dict_row) as cur:
        cur.execute(query6)
        rows = cur.fetchall()
        if rows:
            for row in rows:
                print(f"  '{row['fclasses']}': {row['count']}")
        else:
            print("  No feature classes found")

    # 7. Toponym complexity analysis
    print("\n" + "="*60)
    print("7. TOPONYM COMPLEXITY (sub-country challenges)")
    print("="*60)

    # Multi-word toponyms
    query7a = """
    SELECT
        CASE
            WHEN array_length(string_to_array(toponym, ' '), 1) = 1 THEN '1 word'
            WHEN array_length(string_to_array(toponym, ' '), 1) = 2 THEN '2 words'
            WHEN array_length(string_to_array(toponym, ' '), 1) = 3 THEN '3 words'
            ELSE '4+ words'
        END as word_count,
        count(*) as count
    FROM cdop.ich_toponyms_cleaner
    GROUP BY 1
    ORDER BY 1;
    """
    print("\n  Word count distribution (cleaner):")
    with conn.cursor(row_factory=dict_row) as cur:
        cur.execute(query7a)
        for row in cur.fetchall():
            print(f"    {row['word_count']}: {row['count']}")

    # 8. Ambiguous/common toponyms
    print("\n" + "="*60)
    print("8. MOST FREQUENT TOPONYMS (potential ambiguity)")
    print("="*60)

    query8 = """
    SELECT toponym, count(DISTINCT ich_id) as element_count
    FROM cdop.ich_toponyms_cleaner
    GROUP BY toponym
    HAVING count(DISTINCT ich_id) > 3
    ORDER BY element_count DESC
    LIMIT 25;
    """
    with conn.cursor(row_factory=dict_row) as cur:
        cur.execute(query8)
        for row in cur.fetchall():
            print(f"  '{row['toponym']}': {row['element_count']} elements")

    # 9. Country-level vs sub-country toponyms
    print("\n" + "="*60)
    print("9. COUNTRY-LEVEL vs SUB-COUNTRY TOPONYMS")
    print("="*60)

    query9 = """
    WITH country_names AS (
        SELECT DISTINCT lower(trim(unnest(string_to_array(countries, ', ')))) as country
        FROM cdop.ich_elements
    )
    SELECT
        count(*) as total_toponyms,
        count(*) FILTER (WHERE lower(t.toponym) IN (SELECT country FROM country_names)) as country_level,
        count(*) FILTER (WHERE lower(t.toponym) NOT IN (SELECT country FROM country_names)) as sub_country
    FROM cdop.ich_toponyms_cleaner t;
    """
    with conn.cursor(row_factory=dict_row) as cur:
        cur.execute(query9)
        row = cur.fetchone()
        print(f"  Total toponyms: {row['total_toponyms']}")
        print(f"  Country-level matches: {row['country_level']} ({100*row['country_level']/row['total_toponyms']:.1f}%)")
        print(f"  Sub-country (need geocoding): {row['sub_country']} ({100*row['sub_country']/row['total_toponyms']:.1f}%)")

    # 10. Sample sub-country toponyms by element
    print("\n" + "="*60)
    print("10. SAMPLE SUB-COUNTRY TOPONYMS (the gnarly part)")
    print("="*60)

    query10 = """
    WITH country_names AS (
        SELECT DISTINCT lower(trim(unnest(string_to_array(countries, ', ')))) as country
        FROM cdop.ich_elements
    )
    SELECT e.ich_id, e.label, e.countries,
           array_agg(t.toponym ORDER BY t.toponym) as sub_country_toponyms
    FROM cdop.ich_elements e
    JOIN cdop.ich_toponyms_cleaner t ON e.ich_id = t.ich_id
    WHERE lower(t.toponym) NOT IN (SELECT country FROM country_names)
    GROUP BY e.ich_id, e.label, e.countries
    HAVING count(*) BETWEEN 3 AND 8
    ORDER BY random()
    LIMIT 8;
    """
    with conn.cursor(row_factory=dict_row) as cur:
        cur.execute(query10)
        for row in cur.fetchall():
            print(f"\n  [{row['ich_id']}] {row['label'][:45]}")
            print(f"  Countries: {row['countries'][:50]}")
            print(f"  Sub-country toponyms: {row['sub_country_toponyms']}")

    # 11. Toponyms with special characters/diacritics
    print("\n" + "="*60)
    print("11. TOPONYMS WITH DIACRITICS/SPECIAL CHARS")
    print("="*60)

    query11 = """
    SELECT toponym
    FROM cdop.ich_toponyms_cleaner
    WHERE toponym ~ '[àáâãäåæçèéêëìíîïñòóôõöøùúûüýÿ]'
       OR toponym ~ '[ğışüöçĞİŞÜÖÇ]'
       OR toponym ~ '[αβγδεζηθικλμνξοπρστυφχψω]'
    ORDER BY random()
    LIMIT 20;
    """
    with conn.cursor(row_factory=dict_row) as cur:
        cur.execute(query11)
        toponyms = [row['toponym'] for row in cur.fetchall()]
        print(f"  Sample: {toponyms}")

    conn.close()
    print("\n" + "="*60)
    print("Phase 4 complete.")

if __name__ == "__main__":
    main()
