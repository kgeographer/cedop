"""
Scrape concepts and country codes from ICH landing pages for new 2024-2025 elements.

This script fetches the landing page for each new element and extracts:
- Country code(s) from the state URL (e.g., /state/uzbekistan-UZ -> UZ)
- Primary concepts (from <a class="link primary">)
- Secondary concepts (from <a class="link secondary">)

Then updates the ich_elements table with this data.
"""
import sys
import re
import time
import json
from pathlib import Path

sys.path.insert(0, '/Users/karlg/Documents/Repos/_cedop')
from dotenv import load_dotenv
load_dotenv(Path('/Users/karlg/Documents/Repos/_cedop/.env'))

import requests
from bs4 import BeautifulSoup
from scripts.shared.db_utils import db_connect

OUTPUT_DIR = Path('/Users/karlg/Documents/Repos/_cedop/output/cdop/ich_update')
CACHE_FILE = OUTPUT_DIR / 'concept_scrape_cache.json'

REQUEST_DELAY = 1.0
USER_AGENT = "CEDOP-Research-Crawler/1.0 (Academic research; non-commercial)"


def get_session():
    """Create a requests session with appropriate headers."""
    session = requests.Session()
    session.headers.update({
        "User-Agent": USER_AGENT,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
    })
    return session


def scrape_element_page(session, ich_id: str, url: str) -> dict:
    """Scrape concepts and country codes from an element's landing page."""
    time.sleep(REQUEST_DELAY)

    try:
        response = session.get(url, timeout=30)
        response.raise_for_status()
    except requests.RequestException as e:
        return {"error": str(e)}

    soup = BeautifulSoup(response.text, 'html.parser')

    result = {
        "ich_id": ich_id,
        "url": url,
        "ccodes": [],
        "primary_concepts": [],
        "secondary_concepts": []
    }

    # Extract country codes from state links
    # Pattern: /state/country-name-XX where XX is the 2-letter code
    country_links = soup.find_all('a', href=re.compile(r'/state/.*-[A-Z]{2}$'))
    for link in country_links:
        href = link.get('href', '')
        match = re.search(r'-([A-Z]{2})$', href)
        if match:
            ccode = match.group(1)
            if ccode not in result["ccodes"]:
                result["ccodes"].append(ccode)

    # Find the Concepts section - look for h3 with exact text "Concepts"
    for h3 in soup.find_all('h3'):
        if h3.get_text(strip=True) == 'Concepts':
            concepts_ol = h3.find_next('ol')
            if concepts_ol:
                for link in concepts_ol.find_all('a'):
                    cls = link.get('class', [])
                    concept_text = link.get_text(strip=True)
                    if 'link' in cls and concept_text:
                        if 'primary' in cls:
                            if concept_text not in result["primary_concepts"]:
                                result["primary_concepts"].append(concept_text)
                        elif 'secondary' in cls:
                            if concept_text not in result["secondary_concepts"]:
                                result["secondary_concepts"].append(concept_text)
            break

    return result


def main():
    # Get new elements that need concept data
    conn = db_connect(schema='cdop')
    cur = conn.cursor()

    cur.execute("""
        SELECT ich_id, link, countries
        FROM ich_elements
        WHERE year >= 2024
        AND (primary_concepts IS NULL OR ccodes IS NULL)
        ORDER BY ich_id
    """)
    elements = cur.fetchall()
    print(f"Found {len(elements)} elements needing concept data")

    if not elements:
        print("All elements already have concept data.")
        return

    # Load cache if exists
    cache = {}
    if CACHE_FILE.exists():
        with open(CACHE_FILE) as f:
            cache = json.load(f)
        print(f"Loaded cache with {len(cache)} entries")

    session = get_session()
    results = []

    for i, (ich_id, link, countries) in enumerate(elements):
        if ich_id in cache:
            print(f"[{i+1}/{len(elements)}] {ich_id}: cached")
            results.append(cache[ich_id])
            continue

        print(f"[{i+1}/{len(elements)}] {ich_id}: scraping...", end=" ", flush=True)

        result = scrape_element_page(session, ich_id, link)

        if "error" in result:
            print(f"ERROR: {result['error']}")
        else:
            print(f"OK (ccodes:{result['ccodes']}, pri:{len(result['primary_concepts'])}, sec:{len(result['secondary_concepts'])})")

        results.append(result)
        cache[ich_id] = result

        # Save cache periodically
        if (i + 1) % 10 == 0:
            with open(CACHE_FILE, 'w') as f:
                json.dump(cache, f, indent=2)
            print(f"  [Cache saved: {i+1}/{len(elements)}]")

    # Save final cache
    with open(CACHE_FILE, 'w') as f:
        json.dump(cache, f, indent=2)

    # Update database
    print("\nUpdating database...")
    updated = 0
    for result in results:
        if "error" in result:
            continue

        ich_id = result["ich_id"]
        ccodes = result["ccodes"] if result["ccodes"] else None
        primary = "; ".join(result["primary_concepts"]) if result["primary_concepts"] else None
        secondary = "; ".join(result["secondary_concepts"]) if result["secondary_concepts"] else None

        cur.execute("""
            UPDATE ich_elements
            SET ccodes = %s,
                primary_concepts = %s,
                secondary_concepts = %s
            WHERE ich_id = %s
        """, (ccodes, primary, secondary, ich_id))
        updated += 1

    conn.commit()

    # Verify
    cur.execute("""
        SELECT count(*) FROM ich_elements
        WHERE year >= 2024 AND primary_concepts IS NOT NULL
    """)
    with_concepts = cur.fetchone()[0]

    cur.execute("""
        SELECT count(*) FROM ich_elements
        WHERE year >= 2024 AND ccodes IS NOT NULL
    """)
    with_ccodes = cur.fetchone()[0]

    print(f"\nResults:")
    print(f"  Updated: {updated}")
    print(f"  With concepts: {with_concepts}/135")
    print(f"  With ccodes: {with_ccodes}/135")

    conn.close()


if __name__ == "__main__":
    main()
