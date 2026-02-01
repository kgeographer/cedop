"""
ICH Corpus Update Script
========================

This script crawls the UNESCO ICH website to:
1. Parse the main list page to discover all inscribed elements
2. Identify new elements (2024-2025) and gap-fill missing nomination docs
3. Fetch individual element pages for summaries (2024-2025)
4. Download nomination form documents (.doc files typically, not PDF)
5. Prepare data for database insertion and LLM extraction

Key distinctions:
- NEW elements (2024-2025): Get summaries AND nomination docs
- GAP-FILL (pre-2024): Just check if doc links now exist, report findings

Note: Nomination docs are typically .doc (old Word format). Text extraction
from .doc files requires additional tools (antiword, catdoc, or python-docx
for .docx). The extracted files will need manual cleaning due to format
variations across years.

The crawling is designed to be:
- Polite (rate-limited, respects server)
- Resumable (checkpoints progress)
- Transparent (logs all actions)

Usage:
    python scripts/cdop/ich_corpus_update.py --discover    # Step 1: Parse list, find targets
    python scripts/cdop/ich_corpus_update.py --fetch       # Step 2: Fetch new element pages + docs
    python scripts/cdop/ich_corpus_update.py --check-gaps  # Step 2b: Check if gap-fill elements have docs
    python scripts/cdop/ich_corpus_update.py --fetch-gaps  # Step 2c: Download docs for gap-fill elements
    python scripts/cdop/ich_corpus_update.py --extract     # Step 3: Extract text from docs
    python scripts/cdop/ich_corpus_update.py --all         # Run steps 1-2-3 for new elements

Author: Claude Code (with human oversight)
Date: January 2026
"""

import os
import sys
import json
import re
import time
import argparse
from datetime import datetime
from pathlib import Path
from urllib.parse import urljoin
import requests
from bs4 import BeautifulSoup

# Optional: Document extraction tools
# .doc files (old Word format) can be extracted with:
#   - textutil (built into macOS)
#   - antiword or catdoc (if installed)
# .docx files can use python-docx

import subprocess
import shutil
import platform

# Check available extraction tools
HAS_TEXTUTIL = platform.system() == 'Darwin' and shutil.which('textutil') is not None
HAS_ANTIWORD = shutil.which('antiword') is not None
HAS_CATDOC = shutil.which('catdoc') is not None

if HAS_TEXTUTIL:
    print("Using textutil (macOS built-in) for .doc extraction")
elif HAS_ANTIWORD:
    print("Using antiword for .doc extraction")
elif HAS_CATDOC:
    print("Using catdoc for .doc extraction")
else:
    print("Note: No .doc extraction tool found.")
    print("  On macOS, textutil should be available by default.")
    print("  Files will be downloaded but text extraction will be manual.")

# =============================================================================
# CONFIGURATION
# =============================================================================

BASE_URL = "https://ich.unesco.org"
LIST_URL = f"{BASE_URL}/en/lists"

# Output directories
PROJECT_ROOT = Path("/Users/karlg/Documents/Repos/_cedop")
OUTPUT_DIR = PROJECT_ROOT / "output" / "cdop" / "ich_update"
PDF_DIR = OUTPUT_DIR / "docs"  # Named PDF_DIR for historical reasons, but contains .doc files
TEXT_DIR = PROJECT_ROOT / "app" / "data" / "ich" / "extracted_clean_02"

# Existing corpus location (to check what we already have)
EXISTING_DOCS_DIR = PROJECT_ROOT / "app" / "data" / "ich" / "extracted_clean_02"

# Rate limiting: be polite to UNESCO servers
REQUEST_DELAY = 1.0  # seconds between requests
REQUEST_TIMEOUT = 30  # seconds

# User agent: identify ourselves
USER_AGENT = "CEDOP-Research-Crawler/1.0 (Academic research; non-commercial)"

# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def get_session():
    """Create a requests session with appropriate headers."""
    session = requests.Session()
    session.headers.update({
        "User-Agent": USER_AGENT,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
    })
    return session


def polite_request(session, url, delay=REQUEST_DELAY):
    """Make a request with rate limiting and error handling."""
    time.sleep(delay)
    try:
        response = session.get(url, timeout=REQUEST_TIMEOUT)
        response.raise_for_status()
        return response
    except requests.RequestException as e:
        print(f"  Error fetching {url}: {e}")
        return None


def get_existing_doc_ids():
    """
    Get set of ICH IDs for which we already have nomination documents.
    These are the 5-digit IDs extracted from filenames like '00743_extracted_cleaned.txt'
    """
    existing = set()
    if EXISTING_DOCS_DIR.exists():
        for f in EXISTING_DOCS_DIR.iterdir():
            if f.suffix == '.txt':
                # Extract ID from filename patterns like:
                # - 00743_extracted_cleaned.txt
                # - 00170_full_text_clean.txt
                match = re.match(r'^(\d{5})_', f.name)
                if match:
                    existing.add(match.group(1))
    return existing


# =============================================================================
# STEP 1: DISCOVER - Parse list page, identify targets
# =============================================================================

def parse_list_page(html_content):
    """
    Parse the ICH lists page to extract all inscribed elements.

    Returns list of dicts with:
    - ich_id: 5-digit ID (e.g., "02329")
    - name: Element name
    - url: Full URL to element page
    - list_type: RL (Representative), USL (Urgent), BSP (Best Practice)
    - country: Country name(s)
    - year: Inscription year
    """
    soup = BeautifulSoup(html_content, 'html.parser')
    elements = []
    current_year = None
    current_list_type = None

    # The page structure has year headers and list type subheaders
    # followed by table rows with elements

    # Find all table rows with element links
    for row in soup.find_all('tr'):
        # Check for year header (th with id like "2025")
        year_th = row.find('th', id=re.compile(r'^\d{4}$'))
        if year_th:
            current_year = year_th.get('id')
            continue

        # Check for list type header
        list_header = row.find('th')
        if list_header:
            header_text = list_header.get_text(strip=True)
            if 'Urgent Safeguarding' in header_text:
                current_list_type = 'USL'
            elif 'Representative' in header_text:
                current_list_type = 'RL'
            elif 'Good Safeguarding' in header_text or 'Best' in header_text:
                current_list_type = 'BSP'
            continue

        # Look for element links in table cells
        cells = row.find_all('td', class_='list-element')
        if len(cells) >= 2:
            # First cell has the element link
            link = cells[0].find('a', href=re.compile(r'/en/(RL|USL|BSP)/'))
            if link:
                href = link.get('href', '')
                name = link.get_text(strip=True)
                ich_id = link.get('title', '')

                # Extract list type from URL if not already set
                url_match = re.search(r'/en/(RL|USL|BSP)/', href)
                if url_match:
                    list_type = url_match.group(1)
                else:
                    list_type = current_list_type

                # Second cell usually has country
                country = cells[1].get_text(strip=True) if len(cells) > 1 else ''

                # Normalize URL
                full_url = urljoin(BASE_URL, href.split('#')[0])  # Remove fragment

                elements.append({
                    'ich_id': ich_id,
                    'name': name,
                    'url': full_url,
                    'list_type': list_type,
                    'country': country,
                    'year': current_year,
                })

    return elements


def discover_targets(session, force_refresh=False):
    """
    Step 1: Parse list page and identify elements to fetch.

    Targets are:
    - New elements (2024, 2025)
    - Any older elements missing nomination documents
    """
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    discovery_file = OUTPUT_DIR / "discovery.json"

    # Check for cached discovery
    if discovery_file.exists() and not force_refresh:
        print(f"Loading cached discovery from {discovery_file}")
        with open(discovery_file) as f:
            return json.load(f)

    print("Fetching ICH list page...")

    # For development, we can use the local copy if available
    local_list = PROJECT_ROOT / "metadata" / "ich.unesco.org_en_lists.html"
    if local_list.exists():
        print(f"  Using local copy: {local_list}")
        with open(local_list, 'r', encoding='utf-8') as f:
            html = f.read()
        # Note: local copy is in view-source format, need to clean it
        # For now, let's fetch fresh from web
        response = polite_request(session, LIST_URL)
        if not response:
            print("  Failed to fetch list page. Using local copy with view-source cleanup.")
            # Basic cleanup of view-source format (this is hacky but workable)
            html = re.sub(r'<span[^>]*class="[^"]*"[^>]*>', '', html)
            html = re.sub(r'</span>', '', html)
        else:
            html = response.text
    else:
        response = polite_request(session, LIST_URL)
        if not response:
            print("  Failed to fetch list page!")
            return None
        html = response.text

    print("Parsing list page...")
    all_elements = parse_list_page(html)
    print(f"  Found {len(all_elements)} total elements")

    # Get existing document IDs
    existing_ids = get_existing_doc_ids()
    print(f"  Existing nomination docs: {len(existing_ids)}")

    # Categorize elements
    new_elements = []      # 2024-2025
    missing_docs = []      # Older but no nomination doc
    already_have = []      # Already have nomination doc

    for elem in all_elements:
        ich_id = elem['ich_id']
        year = elem.get('year', '')

        if year in ('2024', '2025'):
            new_elements.append(elem)
        elif ich_id not in existing_ids:
            missing_docs.append(elem)
        else:
            already_have.append(elem)

    # Summary
    print(f"\nDiscovery Summary:")
    print(f"  New (2024-2025): {len(new_elements)}")
    print(f"  Missing docs (pre-2024): {len(missing_docs)}")
    print(f"  Already have: {len(already_have)}")

    # Year breakdown for new elements
    by_year = {}
    for elem in new_elements:
        y = elem.get('year', 'unknown')
        by_year[y] = by_year.get(y, 0) + 1
    print(f"  New by year: {by_year}")

    discovery = {
        'discovery_date': datetime.now().isoformat(),
        'total_elements': len(all_elements),
        'new_elements': new_elements,
        'missing_docs': missing_docs,
        'already_have_count': len(already_have),
        'existing_doc_ids': list(existing_ids),
    }

    # Save discovery
    with open(discovery_file, 'w') as f:
        json.dump(discovery, f, indent=2, ensure_ascii=False)
    print(f"\nSaved discovery to {discovery_file}")

    return discovery


# =============================================================================
# STEP 2: FETCH - Get element pages and download PDFs
# =============================================================================

def parse_element_page(html_content, ich_id):
    """
    Parse an individual element page to extract:
    - Summary text
    - Nomination form PDF URL
    - Other metadata
    """
    soup = BeautifulSoup(html_content, 'html.parser')
    result = {'ich_id': ich_id}

    # 1. Summary from meta description
    meta_desc = soup.find('meta', attrs={'name': 'DESCRIPTION'})
    if meta_desc:
        result['summary'] = meta_desc.get('content', '')

    # 2. Full summary from page content (often longer than meta)
    # Look for the main content area
    content_div = soup.find('div', class_='element-item')
    if content_div:
        # Find paragraphs that look like the description
        for p in content_div.find_all('p', class_='wiki-text'):
            text = p.get_text(strip=True)
            if len(text) > 200:  # Likely the main description
                result['summary_full'] = text
                break

    # 3. Nomination form document link (.doc typically, sometimes .pdf)
    # Look in the "Nomination file" section
    nom_section = soup.find('div', class_='nomination-file')
    if nom_section:
        # Find "Nomination form:" list item
        for li in nom_section.find_all('li'):
            li_text = li.get_text()
            if 'Nomination form' in li_text:
                # Get the English version link (first link, or one labeled "English")
                links = li.find_all('a', href=re.compile(r'download\.php'))
                for link in links:
                    link_text = link.get_text(strip=True).lower()
                    # Prefer English version
                    if 'english' in link_text or len(links) == 1:
                        result['nomination_doc_url'] = urljoin(BASE_URL, link['href'])
                        break
                # If no English found, take first link
                if 'nomination_doc_url' not in result and links:
                    result['nomination_doc_url'] = urljoin(BASE_URL, links[0]['href'])
                break

        # Also collect all document links for reference
        all_docs = []
        for li in nom_section.find_all('li'):
            doc_type = li.get_text().split(':')[0].strip() if ':' in li.get_text() else 'Unknown'
            for link in li.find_all('a', href=re.compile(r'download\.php')):
                all_docs.append({
                    'type': doc_type,
                    'label': link.get_text(strip=True),
                    'url': urljoin(BASE_URL, link['href'])
                })
        if all_docs:
            result['all_documents'] = all_docs

    # 4. Title
    title = soup.find('h1', class_='page-title')
    if title:
        result['title'] = title.get_text(strip=True)

    # 5. Country (from element-country class)
    country_p = soup.find('p', class_='element-country')
    if country_p:
        result['country'] = country_p.get_text(strip=True)

    # 6. Inscription year
    # Look for text like "Inscribed in 2025"
    inscribed = soup.find(string=re.compile(r'Inscribed in \d{4}'))
    if inscribed:
        match = re.search(r'Inscribed in (\d{4})', inscribed)
        if match:
            result['year_inscribed'] = match.group(1)

    return result


def fetch_elements(session, discovery, limit=None):
    """
    Step 2: Fetch individual element pages and download nomination docs.

    For NEW elements (2024-2025), we fetch:
    - Summary text (for ich_summaries table)
    - Nomination document (.doc file typically)

    Args:
        session: requests Session
        discovery: discovery dict from step 1
        limit: Optional limit on number to process (for testing)
    """
    PDF_DIR.mkdir(parents=True, exist_ok=True)

    # For regular fetch, only process new elements
    # Gap-fill elements are handled by --check-gaps
    targets = discovery['new_elements'] + discovery.get('missing_docs', [])

    if limit:
        targets = targets[:limit]

    print(f"\nFetching {len(targets)} element pages...")

    # Track progress
    progress_file = OUTPUT_DIR / "fetch_progress.json"
    if progress_file.exists():
        with open(progress_file) as f:
            progress = json.load(f)
    else:
        progress = {'fetched': [], 'failed': [], 'results': []}

    already_fetched = set(progress['fetched'])

    for i, elem in enumerate(targets):
        ich_id = elem['ich_id']

        if ich_id in already_fetched:
            print(f"[{i+1}/{len(targets)}] {ich_id} - already fetched, skipping")
            continue

        print(f"[{i+1}/{len(targets)}] Fetching {ich_id}: {elem['name'][:50]}...")

        # Fetch element page
        response = polite_request(session, elem['url'])
        if not response:
            print(f"  Failed to fetch page")
            progress['failed'].append(ich_id)
            continue

        # Parse page
        page_data = parse_element_page(response.text, ich_id)
        page_data['source_url'] = elem['url']
        page_data['list_type'] = elem.get('list_type', '')
        page_data['discovery_year'] = elem.get('year', '')

        # Download nomination doc if available
        if 'nomination_doc_url' in page_data:
            doc_url = page_data['nomination_doc_url']

            # Determine file extension from content-type or URL
            # Most are .doc (old Word format)
            doc_path = PDF_DIR / f"{ich_id}_nomination.doc"

            if not doc_path.exists():
                print(f"  Downloading nomination doc...")
                doc_response = polite_request(session, doc_url)
                if doc_response:
                    content_type = doc_response.headers.get('content-type', '')
                    # Check content type and adjust extension if needed
                    if 'pdf' in content_type:
                        doc_path = PDF_DIR / f"{ich_id}_nomination.pdf"
                    elif 'openxmlformats' in content_type:
                        doc_path = PDF_DIR / f"{ich_id}_nomination.docx"

                    with open(doc_path, 'wb') as f:
                        f.write(doc_response.content)
                    page_data['doc_downloaded'] = True
                    page_data['doc_path'] = str(doc_path)
                    page_data['doc_content_type'] = content_type
                    print(f"  Saved: {doc_path.name} ({len(doc_response.content)} bytes)")
                else:
                    print(f"  Doc download failed")
                    page_data['doc_downloaded'] = False
            else:
                print(f"  Doc already exists")
                page_data['doc_downloaded'] = True
                page_data['doc_path'] = str(doc_path)
        else:
            print(f"  No nomination doc link found")
            page_data['doc_downloaded'] = False

        # Record progress
        progress['fetched'].append(ich_id)
        progress['results'].append(page_data)

        # Save progress every 10 elements
        if (i + 1) % 10 == 0:
            with open(progress_file, 'w') as f:
                json.dump(progress, f, indent=2, ensure_ascii=False)
            print(f"  [Checkpoint saved: {len(progress['fetched'])} fetched]")

    # Final save
    with open(progress_file, 'w') as f:
        json.dump(progress, f, indent=2, ensure_ascii=False)

    # Also save summaries separately for easy database import
    summaries_file = OUTPUT_DIR / "new_summaries.json"
    summaries = []
    for r in progress['results']:
        if 'error' not in r:
            summaries.append({
                'ich_id': r.get('ich_id'),
                'title': r.get('title'),
                'summary': r.get('summary', r.get('summary_full', '')),
                'country': r.get('country'),
                'year': r.get('year_inscribed', r.get('discovery_year')),
                'list_type': r.get('list_type'),
            })
    with open(summaries_file, 'w') as f:
        json.dump(summaries, f, indent=2, ensure_ascii=False)

    print(f"\nFetch complete:")
    print(f"  Fetched: {len(progress['fetched'])}")
    print(f"  Failed: {len(progress['failed'])}")
    print(f"  With docs: {sum(1 for r in progress['results'] if r.get('doc_downloaded'))}")
    print(f"  Results saved to: {progress_file}")
    print(f"  Summaries saved to: {summaries_file}")

    return progress


# =============================================================================
# STEP 2b: CHECK GAPS - Check if pre-2024 elements now have doc links
# =============================================================================

def check_gap_elements(session, discovery, limit=None):
    """
    Step 2b: Check pre-2024 elements that are missing docs to see if
    they now have nomination document links available.

    This is investigative - we check and report, don't bulk download.
    """
    missing_docs = discovery.get('missing_docs', [])

    if limit:
        missing_docs = missing_docs[:limit]

    print(f"\nChecking {len(missing_docs)} gap-fill elements for doc availability...")

    gap_report_file = OUTPUT_DIR / "gap_check_report.json"

    results = {
        'check_date': datetime.now().isoformat(),
        'has_docs': [],      # Elements that now have doc links
        'no_docs': [],       # Elements still without doc links
        'errors': [],        # Failed to fetch
    }

    for i, elem in enumerate(missing_docs):
        ich_id = elem['ich_id']
        print(f"[{i+1}/{len(missing_docs)}] Checking {ich_id}: {elem['name'][:40]}...", end=" ")

        response = polite_request(session, elem['url'], delay=0.5)  # Faster for just checking
        if not response:
            print("FETCH ERROR")
            results['errors'].append(elem)
            continue

        page_data = parse_element_page(response.text, ich_id)

        if 'nomination_doc_url' in page_data:
            print(f"HAS DOC")
            results['has_docs'].append({
                **elem,
                'doc_url': page_data['nomination_doc_url'],
                'all_documents': page_data.get('all_documents', [])
            })
        else:
            print("no doc")
            results['no_docs'].append(elem)

        # Save progress periodically
        if (i + 1) % 20 == 0:
            with open(gap_report_file, 'w') as f:
                json.dump(results, f, indent=2, ensure_ascii=False)

    # Final save
    with open(gap_report_file, 'w') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    # Summary
    print(f"\n{'='*60}")
    print("GAP CHECK RESULTS")
    print('='*60)
    print(f"  Now have docs: {len(results['has_docs'])}")
    print(f"  Still no docs: {len(results['no_docs'])}")
    print(f"  Errors: {len(results['errors'])}")
    print(f"\nReport saved to: {gap_report_file}")

    # Show a few examples of newly available docs
    if results['has_docs']:
        print(f"\nExamples with newly available docs:")
        for elem in results['has_docs'][:5]:
            print(f"  {elem['ich_id']}: {elem['name'][:50]}")
            print(f"    Year: {elem.get('year', '?')}, URL: {elem['doc_url'][:60]}...")

    return results


def fetch_gap_docs(session, limit=None):
    """
    Step 2c: Download nomination docs for gap-fill elements that now have them.

    Reads from gap_check_report.json (generated by --check-gaps) and downloads
    the documents for elements in has_docs list.
    """
    gap_report_file = OUTPUT_DIR / "gap_check_report.json"

    if not gap_report_file.exists():
        print("No gap check report found. Run --check-gaps first.")
        return None

    with open(gap_report_file) as f:
        gap_report = json.load(f)

    has_docs = gap_report.get('has_docs', [])
    if not has_docs:
        print("No gap-fill elements with docs found.")
        return None

    if limit:
        has_docs = has_docs[:limit]

    print(f"\nDownloading docs for {len(has_docs)} gap-fill elements...")

    PDF_DIR.mkdir(parents=True, exist_ok=True)

    # Track results
    results = {
        'downloaded': [],
        'skipped': [],
        'failed': []
    }

    for i, elem in enumerate(has_docs):
        ich_id = elem['ich_id']
        doc_url = elem.get('doc_url')

        if not doc_url:
            print(f"[{i+1}/{len(has_docs)}] {ich_id} - no doc URL, skipping")
            results['skipped'].append(ich_id)
            continue

        # Check if already downloaded
        existing_files = list(PDF_DIR.glob(f"{ich_id}_nomination.*"))
        if existing_files:
            print(f"[{i+1}/{len(has_docs)}] {ich_id} - already downloaded, skipping")
            results['skipped'].append(ich_id)
            continue

        print(f"[{i+1}/{len(has_docs)}] Downloading {ich_id}: {elem['name'][:40]}...")

        doc_response = polite_request(session, doc_url)
        if doc_response:
            content_type = doc_response.headers.get('content-type', '')
            # Determine extension
            if 'pdf' in content_type:
                ext = '.pdf'
            elif 'openxmlformats' in content_type:
                ext = '.docx'
            else:
                ext = '.doc'

            doc_path = PDF_DIR / f"{ich_id}_nomination{ext}"
            with open(doc_path, 'wb') as f:
                f.write(doc_response.content)
            print(f"  Saved: {doc_path.name} ({len(doc_response.content)} bytes)")
            results['downloaded'].append({
                'ich_id': ich_id,
                'path': str(doc_path),
                'size': len(doc_response.content)
            })
        else:
            print(f"  Download failed")
            results['failed'].append(ich_id)

    # Save results
    results_file = OUTPUT_DIR / "gap_fetch_results.json"
    with open(results_file, 'w') as f:
        json.dump(results, f, indent=2)

    print(f"\nGap fetch complete:")
    print(f"  Downloaded: {len(results['downloaded'])}")
    print(f"  Skipped (already have): {len(results['skipped'])}")
    print(f"  Failed: {len(results['failed'])}")
    print(f"  Results saved to: {results_file}")

    return results


# =============================================================================
# STEP 3: EXTRACT - Extract text from docs
# =============================================================================

def extract_doc_text(doc_path):
    """
    Extract text from a .doc file.
    Returns extracted text or None on failure.

    Tries in order:
    1. textutil (macOS built-in) - preferred
    2. antiword
    3. catdoc

    Note: .doc (old Word format) requires command-line tools.
    .docx can use python-docx but is less common in this corpus.
    """
    doc_path = Path(doc_path)

    if doc_path.suffix.lower() == '.docx':
        # Try python-docx for .docx files
        try:
            import docx
            doc = docx.Document(doc_path)
            return '\n'.join(para.text for para in doc.paragraphs)
        except ImportError:
            print("  python-docx not installed for .docx extraction")
            return None
        except Exception as e:
            print(f"  Error extracting .docx: {e}")
            return None

    elif doc_path.suffix.lower() == '.doc':
        # Try textutil first (macOS built-in)
        if HAS_TEXTUTIL:
            try:
                # textutil converts to txt, writing to stdout with -stdout
                result = subprocess.run(
                    ['textutil', '-convert', 'txt', '-stdout', str(doc_path)],
                    capture_output=True, text=True, timeout=60
                )
                if result.returncode == 0 and result.stdout:
                    return result.stdout
                else:
                    print(f"  textutil error: {result.stderr[:100] if result.stderr else 'empty output'}")
            except Exception as e:
                print(f"  textutil exception: {e}")

        # Fall back to antiword
        if HAS_ANTIWORD:
            try:
                result = subprocess.run(
                    ['antiword', str(doc_path)],
                    capture_output=True, text=True, timeout=60
                )
                if result.returncode == 0:
                    return result.stdout
                else:
                    print(f"  antiword error: {result.stderr[:100]}")
            except Exception as e:
                print(f"  antiword exception: {e}")

        # Fall back to catdoc
        if HAS_CATDOC:
            try:
                result = subprocess.run(
                    ['catdoc', str(doc_path)],
                    capture_output=True, text=True, timeout=60
                )
                if result.returncode == 0:
                    return result.stdout
            except Exception as e:
                print(f"  catdoc exception: {e}")

        print("  No .doc extractor available")
        return None

    elif doc_path.suffix.lower() == '.pdf':
        # Fallback for PDF files
        try:
            import pdfplumber
            text_parts = []
            with pdfplumber.open(doc_path) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text_parts.append(page_text)
            return '\n\n'.join(text_parts)
        except ImportError:
            print("  pdfplumber not installed for PDF extraction")
            return None
        except Exception as e:
            print(f"  PDF extraction error: {e}")
            return None

    return None


def extract_all_docs(progress):
    """
    Step 3: Extract text from all downloaded nomination documents.

    Handles .doc (antiword/catdoc), .docx (python-docx), and .pdf (pdfplumber).
    """
    TEXT_DIR.mkdir(parents=True, exist_ok=True)

    results = progress.get('results', [])
    extracted_count = 0
    failed_count = 0
    skipped_count = 0

    # Filter to only elements with downloaded docs
    with_docs = [r for r in results if r.get('doc_downloaded') and r.get('doc_path')]
    print(f"\nExtracting text from {len(with_docs)} documents...")

    for i, elem in enumerate(with_docs):
        ich_id = elem['ich_id']
        doc_path = elem.get('doc_path')

        if not doc_path or not Path(doc_path).exists():
            continue

        output_path = TEXT_DIR / f"{ich_id}_nomination_clean.txt"

        if output_path.exists():
            print(f"[{i+1}] {ich_id} - already extracted, skipping")
            skipped_count += 1
            continue

        print(f"[{i+1}] Extracting {ich_id} ({Path(doc_path).suffix})...")

        text = extract_doc_text(doc_path)
        if text and len(text) > 100:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(text)
            print(f"  Saved: {output_path.name} ({len(text)} chars)")
            extracted_count += 1
        else:
            print(f"  Extraction failed or empty")
            failed_count += 1

    print(f"\nExtraction complete:")
    print(f"  Extracted: {extracted_count}")
    print(f"  Failed: {failed_count}")
    print(f"  Skipped (already done): {skipped_count}")
    print(f"\nNote: Extracted files will likely need manual cleaning.")


# =============================================================================
# MAIN
# =============================================================================

def main():
    parser = argparse.ArgumentParser(
        description="Update ICH corpus with new elements from UNESCO website"
    )
    parser.add_argument('--discover', action='store_true',
                        help='Step 1: Discover new elements and missing docs')
    parser.add_argument('--fetch', action='store_true',
                        help='Step 2: Fetch NEW element pages (2024-2025) and download docs')
    parser.add_argument('--check-gaps', action='store_true',
                        help='Step 2b: Check if pre-2024 elements now have doc links')
    parser.add_argument('--fetch-gaps', action='store_true',
                        help='Step 2c: Download docs for gap-fill elements (requires --check-gaps first)')
    parser.add_argument('--extract', action='store_true',
                        help='Step 3: Extract text from downloaded docs')
    parser.add_argument('--all', action='store_true',
                        help='Run steps 1-2-3 for new elements (not gap check)')
    parser.add_argument('--limit', type=int,
                        help='Limit number of elements to process (for testing)')
    parser.add_argument('--refresh', action='store_true',
                        help='Force refresh (ignore cached data)')

    args = parser.parse_args()

    # Default to --discover if no args
    if not any([args.discover, args.fetch, args.check_gaps, args.fetch_gaps, args.extract, args.all]):
        args.discover = True

    session = get_session()

    # Step 1: Discover
    if args.discover or args.all:
        print("=" * 60)
        print("STEP 1: DISCOVER")
        print("=" * 60)
        discovery = discover_targets(session, force_refresh=args.refresh)
        if not discovery:
            print("Discovery failed!")
            return
    else:
        # Load existing discovery
        discovery_file = OUTPUT_DIR / "discovery.json"
        if discovery_file.exists():
            with open(discovery_file) as f:
                discovery = json.load(f)
        else:
            print("No discovery file found. Run with --discover first.")
            return

    # Step 2: Fetch NEW elements (2024-2025 only)
    if args.fetch or args.all:
        print("\n" + "=" * 60)
        print("STEP 2: FETCH NEW ELEMENTS (2024-2025)")
        print("=" * 60)
        # Only fetch new elements, not gap-fill
        new_only_discovery = {
            **discovery,
            'missing_docs': []  # Don't include gap-fill in fetch
        }
        progress = fetch_elements(session, new_only_discovery, limit=args.limit)
    else:
        progress_file = OUTPUT_DIR / "fetch_progress.json"
        if progress_file.exists():
            with open(progress_file) as f:
                progress = json.load(f)
        else:
            progress = None

    # Step 2b: Check gap-fill elements
    if args.check_gaps:
        print("\n" + "=" * 60)
        print("STEP 2b: CHECK GAP-FILL ELEMENTS")
        print("=" * 60)
        check_gap_elements(session, discovery, limit=args.limit)

    # Step 2c: Fetch gap-fill docs
    if args.fetch_gaps:
        print("\n" + "=" * 60)
        print("STEP 2c: FETCH GAP-FILL DOCS")
        print("=" * 60)
        gap_results = fetch_gap_docs(session, limit=args.limit)
        # If we downloaded new docs, update progress for extract step
        if gap_results and gap_results['downloaded']:
            # Add to progress for extraction
            if progress is None:
                progress = {'fetched': [], 'failed': [], 'results': []}
            for dl in gap_results['downloaded']:
                if dl['ich_id'] not in progress['fetched']:
                    progress['results'].append({
                        'ich_id': dl['ich_id'],
                        'doc_downloaded': True,
                        'doc_path': dl['path']
                    })

    # Step 3: Extract
    if args.extract or args.all:
        print("\n" + "=" * 60)
        print("STEP 3: EXTRACT TEXT FROM DOCS")
        print("=" * 60)
        if progress:
            extract_all_docs(progress)
        else:
            print("No fetch progress found. Run with --fetch first.")

    print("\n" + "=" * 60)
    print("COMPLETE")
    print("=" * 60)
    print(f"\nOutput directory: {OUTPUT_DIR}")
    print(f"Docs saved to: {PDF_DIR}")
    print(f"Text extracted to: {TEXT_DIR}")
    print("\nNext steps:")
    print("  1. Review and clean extracted texts")
    print("  2. Run LLM extraction pipeline")
    print("  3. Update database tables (ich_elements, ich_summaries)")


if __name__ == "__main__":
    main()
