"""
Harvest Wikipedia sections for 258 World Heritage Cities.

Reads from wh_cities table, fetches sections via Wikipedia API,
maps to semantic bands, outputs JSON with region/country metadata.

Usage:
    python scripts/corpus/harvest_whc.py
"""

import wikipediaapi
import json
import os
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import unquote

import psycopg
from dotenv import load_dotenv

load_dotenv()

# Output paths
OUTPUT_DIR = Path("output/corpus_258")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Load band mapping from pilot
MAPPING_FILE = Path("output/corpus/band_mapping_draft.json")
with open(MAPPING_FILE) as f:
    BAND_MAPPING = json.load(f)

# Wikipedia API setup
wiki = wikipediaapi.Wikipedia(
    user_agent="EDOP-Corpus/1.0 (karl.geog@gmail.com)",
    language='en'
)


def get_db_connection():
    """Create database connection from environment variables."""
    return psycopg.connect(
        host=os.environ.get("PGHOST", "localhost"),
        port=os.environ.get("PGPORT", "5435"),
        dbname=os.environ.get("PGDATABASE", "edop"),
        user=os.environ.get("PGUSER", "postgres"),
        password=os.environ.get("PGPASSWORD", ""),
    )


def load_whc_cities():
    """Load all cities from wh_cities table."""
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT id, city, slug, region, country, ccode
        FROM wh_cities
        ORDER BY id
    """)
    rows = cur.fetchall()
    conn.close()

    cities = []
    for row in rows:
        # Decode URL-encoded slugs
        slug = unquote(row[2]) if row[2] else None
        cities.append({
            "whc_id": f"whc_{row[0]}",
            "id": row[0],
            "city": row[1],
            "slug": slug,
            "region": row[3],
            "country": row[4],
            "ccode": row[5]
        })
    return cities


def get_band(heading: str) -> str | None:
    """Map a section heading to a semantic band."""
    h = heading.lower().strip()

    # Check exclusions first
    exc = BAND_MAPPING['exclude']
    if h in exc['exact']:
        return None
    for pattern in exc.get('contains', []):
        if pattern in h:
            return None

    # Check each band
    for band in ['history', 'environment', 'culture', 'modern']:
        rules = BAND_MAPPING[band]

        if h in rules['exact']:
            return band
        for pattern in rules.get('contains', []):
            if pattern in h:
                return band
        for pattern in rules.get('endswith', []):
            if h.endswith(pattern):
                return band

    return 'unmapped'


def extract_sections(page, level=1, parent_path=""):
    """Recursively extract all sections from a Wikipedia page."""
    sections = []

    for section in page.sections:
        path = f"{parent_path}/{section.title}" if parent_path else section.title

        sections.append({
            "title": section.title,
            "path": path,
            "level": level,
            "text": section.text,
            "char_count": len(section.text)
        })

        if section.sections:
            sections.extend(extract_sections(section, level + 1, path))

    return sections


def harvest_city(city: dict) -> dict:
    """Harvest Wikipedia sections for a single city."""
    slug = city['slug']
    if not slug:
        return {
            **city,
            "status": "no_slug",
            "sections": []
        }

    # Convert slug to title (replace underscores with spaces)
    title = slug.replace('_', ' ')

    page = wiki.page(title)

    if not page.exists():
        return {
            **city,
            "status": "not_found",
            "wiki_title": None,
            "wiki_url": None,
            "sections": []
        }

    # Get lead/intro text
    summary = page.summary

    # Extract all sections
    raw_sections = extract_sections(page)

    # Map to bands
    sections_with_bands = []
    for sec in raw_sections:
        band = get_band(sec['title'])
        sec['band'] = band
        sections_with_bands.append(sec)

    return {
        **city,
        "wiki_title": page.title,
        "wiki_url": page.fullurl,
        "status": "ok",
        "summary": summary,
        "summary_char_count": len(summary),
        "sections": sections_with_bands,
        "retrieved_at": datetime.now(timezone.utc).isoformat()
    }


def compute_coverage(city_data: dict) -> dict:
    """Compute band coverage statistics for a city."""
    sections = city_data.get('sections', [])

    band_chars = {'history': 0, 'environment': 0, 'culture': 0, 'modern': 0, 'unmapped': 0}
    band_sections = {'history': 0, 'environment': 0, 'culture': 0, 'modern': 0, 'unmapped': 0}

    for sec in sections:
        band = sec.get('band')
        if band and band in band_chars:
            band_chars[band] += sec['char_count']
            band_sections[band] += 1

    total_chars = sum(band_chars.values())

    return {
        "whc_id": city_data['whc_id'],
        "city": city_data['city'],
        "slug": city_data['slug'],
        "region": city_data['region'],
        "country": city_data['country'],
        "ccode": city_data['ccode'],
        "status": city_data['status'],
        "summary_chars": city_data.get('summary_char_count', 0),
        "total_sections": len(sections),
        "total_chars": total_chars,
        "history_chars": band_chars['history'],
        "history_sections": band_sections['history'],
        "environment_chars": band_chars['environment'],
        "environment_sections": band_sections['environment'],
        "culture_chars": band_chars['culture'],
        "culture_sections": band_sections['culture'],
        "modern_chars": band_chars['modern'],
        "modern_sections": band_sections['modern'],
        "unmapped_chars": band_chars['unmapped'],
        "unmapped_sections": band_sections['unmapped'],
        "bands_present": sum(1 for b in ['history', 'environment', 'culture', 'modern'] if band_chars[b] > 0)
    }


def main():
    print("Loading cities from wh_cities table...")
    cities = load_whc_cities()
    print(f"Found {len(cities)} cities\n")

    print(f"Harvesting Wikipedia sections...")
    print(f"Output directory: {OUTPUT_DIR}\n")

    all_results = []
    coverage_rows = []
    errors = []

    for i, city in enumerate(cities, 1):
        print(f"[{i:3d}/{len(cities)}] {city['city'][:30]:<30} ({city['ccode']})...", end=" ", flush=True)

        try:
            result = harvest_city(city)
            all_results.append(result)

            coverage = compute_coverage(result)
            coverage_rows.append(coverage)

            if result['status'] == 'ok':
                section_count = len(result['sections'])
                bands = coverage['bands_present']
                print(f"{section_count:3d} sections, {bands}/4 bands")
            else:
                print(f"[{result['status']}]")
                errors.append((city['city'], result['status']))

        except Exception as e:
            print(f"[ERROR: {e}]")
            errors.append((city['city'], str(e)))
            all_results.append({**city, "status": "error", "error": str(e), "sections": []})
            coverage_rows.append({
                "whc_id": city['whc_id'], "city": city['city'], "slug": city['slug'],
                "region": city['region'], "country": city['country'], "ccode": city['ccode'],
                "status": "error", "summary_chars": 0, "total_sections": 0, "total_chars": 0,
                "history_chars": 0, "history_sections": 0, "environment_chars": 0, "environment_sections": 0,
                "culture_chars": 0, "culture_sections": 0, "modern_chars": 0, "modern_sections": 0,
                "unmapped_chars": 0, "unmapped_sections": 0, "bands_present": 0
            })

        # Rate limiting
        time.sleep(1)

    # Write JSON output
    json_path = OUTPUT_DIR / "wiki_sections.json"
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(all_results, f, indent=2, ensure_ascii=False)
    print(f"\nWrote sections to {json_path}")

    # Write coverage report TSV
    import csv
    tsv_path = OUTPUT_DIR / "coverage_report.tsv"
    fieldnames = list(coverage_rows[0].keys())
    with open(tsv_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter='\t')
        writer.writeheader()
        writer.writerows(coverage_rows)
    print(f"Wrote coverage report to {tsv_path}")

    # Summary statistics
    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)

    ok_count = sum(1 for r in all_results if r['status'] == 'ok')
    print(f"Pages found: {ok_count}/{len(cities)}")

    if errors:
        print(f"Errors: {len(errors)}")
        for city, err in errors[:10]:
            print(f"  - {city}: {err}")
        if len(errors) > 10:
            print(f"  ... and {len(errors) - 10} more")

    total_sections = sum(len(r['sections']) for r in all_results)
    print(f"Total sections harvested: {total_sections:,}")

    avg_bands = sum(c['bands_present'] for c in coverage_rows) / len(coverage_rows)
    print(f"Average bands present: {avg_bands:.1f}/4")

    # Region breakdown
    print("\nBy region:")
    regions = {}
    for c in coverage_rows:
        r = c['region']
        if r not in regions:
            regions[r] = {'count': 0, 'ok': 0}
        regions[r]['count'] += 1
        if c['status'] == 'ok':
            regions[r]['ok'] += 1

    for region in sorted(regions.keys()):
        data = regions[region]
        print(f"  {region}: {data['ok']}/{data['count']}")


if __name__ == "__main__":
    main()
