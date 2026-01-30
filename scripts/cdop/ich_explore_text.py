"""
ICH Data Exploration - Phase 3: Text Analysis Preparation
"""
import sys
sys.path.insert(0, '/Users/karlg/Documents/Repos/_cedop')

from scripts.shared.db_utils import db_connect
from psycopg.rows import dict_row

def main():
    conn = db_connect(schema="cdop")

    # 1. Summary text length distribution
    print("\n" + "="*60)
    print("1. SUMMARY TEXT LENGTH DISTRIBUTION")
    print("="*60)

    query1 = """
    SELECT
        count(*) as total_elements,
        round(avg(length(text))) as avg_chars,
        min(length(text)) as min_chars,
        max(length(text)) as max_chars,
        percentile_cont(0.25) WITHIN GROUP (ORDER BY length(text)) as p25,
        percentile_cont(0.50) WITHIN GROUP (ORDER BY length(text)) as p50_median,
        percentile_cont(0.75) WITHIN GROUP (ORDER BY length(text)) as p75,
        percentile_cont(0.90) WITHIN GROUP (ORDER BY length(text)) as p90
    FROM cdop.ich_summaries;
    """
    with conn.cursor(row_factory=dict_row) as cur:
        cur.execute(query1)
        row = cur.fetchone()
        print(f"  Total elements: {row['total_elements']}")
        print(f"  Avg chars: {row['avg_chars']}")
        print(f"  Min chars: {row['min_chars']}")
        print(f"  Max chars: {row['max_chars']}")
        print(f"  25th percentile: {row['p25']}")
        print(f"  Median (50th): {row['p50_median']}")
        print(f"  75th percentile: {row['p75']}")
        print(f"  90th percentile: {row['p90']}")

    # 2. Text length buckets
    print("\n" + "="*60)
    print("2. TEXT LENGTH BUCKETS")
    print("="*60)

    query2 = """
    SELECT
        CASE
            WHEN length(text) < 500 THEN '< 500 chars'
            WHEN length(text) < 1000 THEN '500-999 chars'
            WHEN length(text) < 1500 THEN '1000-1499 chars'
            WHEN length(text) < 2000 THEN '1500-1999 chars'
            WHEN length(text) < 3000 THEN '2000-2999 chars'
            ELSE '3000+ chars'
        END as length_bucket,
        count(*) as count
    FROM cdop.ich_summaries
    GROUP BY 1
    ORDER BY min(length(text));
    """
    with conn.cursor(row_factory=dict_row) as cur:
        cur.execute(query2)
        for row in cur.fetchall():
            print(f"  {row['length_bucket']}: {row['count']}")

    # 3. Word count distribution
    print("\n" + "="*60)
    print("3. WORD COUNT DISTRIBUTION (approximate)")
    print("="*60)

    query3 = """
    SELECT
        round(avg(array_length(string_to_array(text, ' '), 1))) as avg_words,
        min(array_length(string_to_array(text, ' '), 1)) as min_words,
        max(array_length(string_to_array(text, ' '), 1)) as max_words,
        percentile_cont(0.50) WITHIN GROUP (ORDER BY array_length(string_to_array(text, ' '), 1)) as median_words
    FROM cdop.ich_summaries;
    """
    with conn.cursor(row_factory=dict_row) as cur:
        cur.execute(query3)
        row = cur.fetchone()
        print(f"  Avg words: {row['avg_words']}")
        print(f"  Min words: {row['min_words']}")
        print(f"  Max words: {row['max_words']}")
        print(f"  Median words: {row['median_words']}")

    # 4. Sample texts by environmental concept
    print("\n" + "="*60)
    print("4. SAMPLE TEXTS BY ENVIRONMENTAL CONCEPT")
    print("="*60)

    env_concepts = ['Mountains', 'Drylands', 'Forests', 'Grasslands, savannahs',
                    'Marine, coastal and island areas', 'Inland wetlands']

    for concept in env_concepts:
        query4 = f"""
        SELECT e.ich_id, e.label, e.countries, s.text, length(s.text) as chars
        FROM cdop.ich_elements e
        JOIN cdop.ich_summaries s ON e.ich_id = s.ich_id
        WHERE e.primary_concepts LIKE '%{concept}%'
        ORDER BY random()
        LIMIT 2;
        """
        print(f"\n--- {concept.upper()} ---")
        with conn.cursor(row_factory=dict_row) as cur:
            cur.execute(query4)
            for row in cur.fetchall():
                preview = row['text'][:400].replace('\n', ' ')
                print(f"\n  [{row['ich_id']}] {row['label'][:60]}")
                print(f"  Countries: {row['countries'][:60]}")
                print(f"  Length: {row['chars']} chars")
                print(f"  Preview: {preview}...")

    # 5. Elements with shortest/longest summaries
    print("\n" + "="*60)
    print("5. SHORTEST SUMMARIES (potential data quality issues)")
    print("="*60)

    query5 = """
    SELECT e.ich_id, e.label, length(s.text) as chars, s.text
    FROM cdop.ich_elements e
    JOIN cdop.ich_summaries s ON e.ich_id = s.ich_id
    ORDER BY length(s.text)
    LIMIT 5;
    """
    with conn.cursor(row_factory=dict_row) as cur:
        cur.execute(query5)
        for row in cur.fetchall():
            print(f"\n  [{row['ich_id']}] {row['label'][:50]} ({row['chars']} chars)")
            print(f"  Text: {row['text'][:200]}...")

    print("\n" + "="*60)
    print("6. LONGEST SUMMARIES")
    print("="*60)

    query6 = """
    SELECT e.ich_id, e.label, length(s.text) as chars
    FROM cdop.ich_elements e
    JOIN cdop.ich_summaries s ON e.ich_id = s.ich_id
    ORDER BY length(s.text) DESC
    LIMIT 5;
    """
    with conn.cursor(row_factory=dict_row) as cur:
        cur.execute(query6)
        for row in cur.fetchall():
            print(f"  [{row['ich_id']}] {row['label'][:50]} ({row['chars']} chars)")

    # 7. Check for empty or null summaries
    print("\n" + "="*60)
    print("7. DATA QUALITY: MISSING/EMPTY SUMMARIES")
    print("="*60)

    query7 = """
    SELECT
        (SELECT count(*) FROM cdop.ich_elements) as total_elements,
        (SELECT count(*) FROM cdop.ich_summaries) as total_summaries,
        (SELECT count(*) FROM cdop.ich_summaries WHERE text IS NULL OR text = '') as empty_summaries;
    """
    with conn.cursor(row_factory=dict_row) as cur:
        cur.execute(query7)
        row = cur.fetchone()
        print(f"  Total elements: {row['total_elements']}")
        print(f"  Total summaries: {row['total_summaries']}")
        print(f"  Empty/null summaries: {row['empty_summaries']}")
        missing = row['total_elements'] - row['total_summaries']
        print(f"  Missing summaries: {missing}")

    # 8. Token estimation for embeddings
    print("\n" + "="*60)
    print("8. TOKEN ESTIMATION FOR EMBEDDINGS")
    print("="*60)

    query8 = """
    SELECT
        sum(length(text)) as total_chars,
        round(sum(length(text)) / 4.0) as est_tokens_total,
        round(avg(length(text)) / 4.0) as est_tokens_avg
    FROM cdop.ich_summaries;
    """
    with conn.cursor(row_factory=dict_row) as cur:
        cur.execute(query8)
        row = cur.fetchone()
        print(f"  Total characters: {row['total_chars']:,}")
        print(f"  Est. total tokens (~4 chars/token): {int(row['est_tokens_total']):,}")
        print(f"  Est. avg tokens per element: {int(row['est_tokens_avg'])}")
        print(f"\n  OpenAI ada-002 embedding cost estimate:")
        print(f"    ~${int(row['est_tokens_total']) * 0.0001 / 1000:.2f} (at $0.0001/1K tokens)")

    # 9. Text content analysis - common terms
    print("\n" + "="*60)
    print("9. COMMON ENVIRONMENTAL TERMS IN SUMMARIES")
    print("="*60)

    env_terms = ['mountain', 'forest', 'river', 'sea', 'coast', 'desert',
                 'grassland', 'wetland', 'lake', 'island', 'valley', 'plain',
                 'climate', 'rain', 'dry', 'tropical', 'temperate', 'pastoral',
                 'agricultural', 'fishing', 'hunting', 'herding', 'farming']

    for term in env_terms:
        query9 = f"""
        SELECT count(*) as count
        FROM cdop.ich_summaries
        WHERE lower(text) LIKE '%{term}%';
        """
        with conn.cursor(row_factory=dict_row) as cur:
            cur.execute(query9)
            row = cur.fetchone()
            if row['count'] > 10:
                print(f"  '{term}': {row['count']} elements")

    conn.close()
    print("\n" + "="*60)
    print("Phase 3 complete.")

if __name__ == "__main__":
    main()
