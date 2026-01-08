"""
Harvest Wikipedia sections for EDOP corpus pilot.
Fetches sections for 20 test sites, maps to semantic bands, outputs JSON + TSV reports.

Usage:
    python scripts/corpus/harvest_sections.py
"""

import wikipediaapi
import json
import csv
import time
from datetime import datetime
from pathlib import Path

# Output paths
OUTPUT_DIR = Path("output/corpus")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Wikipedia API setup
wiki = wikipediaapi.Wikipedia(
    user_agent="EDOP-Corpus/1.0 (karl.geog@gmail.com)",
    language='en'
)

# 20 pilot sites with manually verified Wikipedia slugs
PILOT_SITES = [
    {"site_id": 21, "name": "Iguazu National Park", "wiki_slug": "Iguazu_National_Park", "place_type": "natural"},
    {"site_id": 22, "name": "Uluru-Kata Tjuta National Park", "wiki_slug": "Uluru-Kata_Tjuta_National_Park", "place_type": "natural"},
    {"site_id": 23, "name": "Historic Centre of Vienna", "wiki_slug": "Vienna", "place_type": "city"},
    {"site_id": 24, "name": "Angkor", "wiki_slug": "Angkor", "place_type": "archaeological"},
    {"site_id": 25, "name": "Head-Smashed-In Buffalo Jump", "wiki_slug": "Head-Smashed-In_Buffalo_Jump", "place_type": "archaeological"},
    {"site_id": 26, "name": "Summer Palace, Beijing", "wiki_slug": "Summer_Palace", "place_type": "cultural"},
    {"site_id": 27, "name": "Old Town of Lijiang", "wiki_slug": "Lijiang", "place_type": "city"},
    {"site_id": 28, "name": "Historic Centre of Tallinn", "wiki_slug": "Tallinn", "place_type": "city"},
    {"site_id": 29, "name": "Ellora Caves", "wiki_slug": "Ellora_Caves", "place_type": "archaeological"},
    {"site_id": 30, "name": "Venice and its Lagoon", "wiki_slug": "Venice", "place_type": "city"},
    {"site_id": 31, "name": "Historic Monuments of Ancient Kyoto", "wiki_slug": "Kyoto", "place_type": "city"},
    {"site_id": 32, "name": "Petra", "wiki_slug": "Petra", "place_type": "archaeological"},
    {"site_id": 33, "name": "Timbuktu", "wiki_slug": "Timbuktu", "place_type": "city"},
    {"site_id": 34, "name": "Historic Sanctuary of Machu Picchu", "wiki_slug": "Machu_Picchu", "place_type": "archaeological"},
    {"site_id": 35, "name": "Historic City of Toledo", "wiki_slug": "Toledo,_Spain", "place_type": "city"},
    {"site_id": 36, "name": "Göbekli Tepe", "wiki_slug": "Göbekli_Tepe", "place_type": "archaeological"},
    {"site_id": 37, "name": "Kyiv (Saint-Sophia Cathedral)", "wiki_slug": "Kyiv", "place_type": "city"},
    {"site_id": 38, "name": "Taos Pueblo", "wiki_slug": "Taos_Pueblo", "place_type": "archaeological"},
    {"site_id": 39, "name": "Cahokia Mounds", "wiki_slug": "Cahokia", "place_type": "archaeological"},
    {"site_id": 40, "name": "Samarkand", "wiki_slug": "Samarkand", "place_type": "city"},
]

# Semantic band mapping - headings normalized to lowercase for matching
BAND_MAPPING = {
    'history': [
        'history', 'etymology', 'archaeology', 'excavation', 'prehistory',
        'early history', 'medieval history', 'modern history', 'historical background',
        'name', 'names', 'toponymy', 'origin', 'origins', 'founding',
        'ancient history', 'colonial era', 'colonial history', 'post-independence',
        'name and etymology', 'etymology and names', 'names and etymology',
        'historical overview', 'timeline', 'chronology'
    ],
    'environment': [
        'geography', 'climate', 'location', 'geology', 'topography', 'environment',
        'physical geography', 'geographical setting', 'setting', 'landscape',
        'geography and climate', 'geography and environment', 'ecology',
        'natural environment', 'flora', 'fauna', 'flora and fauna', 'wildlife',
        'hydrology', 'terrain', 'natural features', 'biodiversity',
        'geography, climate and ecology', 'nature'
    ],
    'culture': [
        'culture', 'religion', 'architecture', 'arts', 'education', 'demographics',
        'demography', 'population', 'notable people', 'famous people', 'language',
        'languages', 'ethnic groups', 'religious sites', 'monuments', 'landmarks',
        'cultural heritage', 'heritage', 'traditions', 'festivals', 'cuisine',
        'arts and culture', 'culture and arts', 'society', 'society and culture',
        'music', 'literature', 'museums', 'main sights', 'sights', 'attractions',
        'cityscape', 'architecture and cityscape', 'religious significance',
        'cultural significance', 'world heritage site', 'unesco'
    ],
    'modern': [
        'economy', 'transport', 'transportation', 'infrastructure', 'government',
        'tourism', 'industry', 'administration', 'politics', 'governance',
        'government and politics', 'politics and government', 'local government',
        'municipal government', 'economy and infrastructure', 'trade', 'commerce',
        'public transport', 'healthcare', 'health', 'utilities', 'services',
        'modern development', 'urban development', 'development'
    ]
}

# Sections to exclude entirely
EXCLUDE_SECTIONS = {
    'references', 'external links', 'see also', 'notes', 'further reading',
    'bibliography', 'sources', 'citations', 'footnotes', 'gallery',
    'image gallery', 'photo gallery', 'media gallery', 'explanatory notes',
    'notes and references', 'footnotes and references', 'works cited',
    'cited and general sources', 'general and cited sources', 'external sources'
}


def normalize_heading(heading: str) -> str:
    """Normalize heading for matching."""
    return heading.lower().strip()


def get_band(heading: str) -> str | None:
    """Map a section heading to a semantic band, or None if excluded/unmapped."""
    norm = normalize_heading(heading)

    if norm in EXCLUDE_SECTIONS:
        return None

    for band, patterns in BAND_MAPPING.items():
        if norm in patterns:
            return band

    # Partial matching for compound headings
    for band, patterns in BAND_MAPPING.items():
        for pattern in patterns:
            if pattern in norm or norm in pattern:
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

        # Recurse into subsections
        if section.sections:
            sections.extend(extract_sections(section, level + 1, path))

    return sections


def harvest_site(site: dict) -> dict:
    """Harvest Wikipedia sections for a single site."""
    slug = site['wiki_slug']
    title = slug.replace('_', ' ')

    page = wiki.page(title)

    if not page.exists():
        print(f"  WARNING: Page not found for {slug}")
        return {
            "site_id": site['site_id'],
            "name": site['name'],
            "wiki_slug": slug,
            "place_type": site['place_type'],
            "status": "not_found",
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
        "site_id": site['site_id'],
        "name": site['name'],
        "wiki_slug": slug,
        "place_type": site['place_type'],
        "wiki_title": page.title,
        "wiki_url": page.fullurl,
        "status": "ok",
        "summary": summary,
        "summary_char_count": len(summary),
        "sections": sections_with_bands,
        "retrieved_at": datetime.utcnow().isoformat()
    }


def compute_coverage(site_data: dict) -> dict:
    """Compute band coverage statistics for a site."""
    sections = site_data.get('sections', [])

    band_chars = {'history': 0, 'environment': 0, 'culture': 0, 'modern': 0, 'unmapped': 0}
    band_sections = {'history': 0, 'environment': 0, 'culture': 0, 'modern': 0, 'unmapped': 0}

    for sec in sections:
        band = sec.get('band')
        if band and band in band_chars:
            band_chars[band] += sec['char_count']
            band_sections[band] += 1

    total_chars = sum(band_chars.values())

    return {
        "site_id": site_data['site_id'],
        "name": site_data['name'],
        "wiki_slug": site_data['wiki_slug'],
        "place_type": site_data['place_type'],
        "status": site_data['status'],
        "summary_chars": site_data.get('summary_char_count', 0),
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
    print(f"Harvesting Wikipedia sections for {len(PILOT_SITES)} pilot sites...")
    print(f"Output directory: {OUTPUT_DIR}\n")

    all_results = []
    coverage_rows = []

    for i, site in enumerate(PILOT_SITES, 1):
        print(f"[{i:2d}/{len(PILOT_SITES)}] {site['name']} ({site['wiki_slug']})...")

        result = harvest_site(site)
        all_results.append(result)

        coverage = compute_coverage(result)
        coverage_rows.append(coverage)

        section_count = len(result['sections'])
        band_info = f"bands={coverage['bands_present']}/4" if result['status'] == 'ok' else result['status']
        print(f"         -> {section_count} sections, {band_info}")

        # Rate limiting - be nice to Wikipedia
        time.sleep(1)

    # Write JSON output
    json_path = OUTPUT_DIR / "wiki_sections_pilot.json"
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(all_results, f, indent=2, ensure_ascii=False)
    print(f"\nWrote sections to {json_path}")

    # Write coverage report TSV
    tsv_path = OUTPUT_DIR / "coverage_report_pilot.tsv"
    fieldnames = list(coverage_rows[0].keys())
    with open(tsv_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter='\t')
        writer.writeheader()
        writer.writerows(coverage_rows)
    print(f"Wrote coverage report to {tsv_path}")

    # Write pilot sites TSV (for reference / DB update)
    sites_path = OUTPUT_DIR / "pilot_sites.tsv"
    with open(sites_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['site_id', 'name', 'wiki_slug', 'place_type'], delimiter='\t')
        writer.writeheader()
        writer.writerows(PILOT_SITES)
    print(f"Wrote pilot sites to {sites_path}")

    # Summary statistics
    print("\n--- SUMMARY ---")
    ok_count = sum(1 for r in all_results if r['status'] == 'ok')
    print(f"Pages found: {ok_count}/{len(PILOT_SITES)}")

    total_sections = sum(len(r['sections']) for r in all_results)
    print(f"Total sections harvested: {total_sections}")

    avg_bands = sum(c['bands_present'] for c in coverage_rows) / len(coverage_rows)
    print(f"Average bands present: {avg_bands:.1f}/4")

    # Show unmapped section titles for review
    unmapped = set()
    for r in all_results:
        for sec in r['sections']:
            if sec['band'] == 'unmapped':
                unmapped.add(sec['title'])

    if unmapped:
        print(f"\nUnmapped section titles ({len(unmapped)}):")
        for title in sorted(unmapped)[:20]:
            print(f"  - {title}")
        if len(unmapped) > 20:
            print(f"  ... and {len(unmapped) - 20} more")


if __name__ == "__main__":
    main()
