"""
Summarize Wikipedia sections by semantic band using Claude API.

For each site, concatenates mapped sections per band, then uses Claude
to generate a consistent ~200-300 word summary per band.

Usage:
    python scripts/corpus/summarize_bands.py

Requires:
    ANTHROPIC_API_KEY in environment or .env file
    pip install anthropic
"""

import json
import os
import time
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# Check for API key before importing anthropic
api_key = os.getenv("ANTHROPIC_API_KEY")
if not api_key:
    print("ERROR: ANTHROPIC_API_KEY not found in environment or .env")
    print("Add to .env: ANTHROPIC_API_KEY=sk-ant-...")
    exit(1)

import anthropic

# Paths
OUTPUT_DIR = Path("output/corpus")
MAPPING_FILE = OUTPUT_DIR / "band_mapping_draft.json"
SECTIONS_FILE = OUTPUT_DIR / "wiki_sections_pilot.json"
OUTPUT_FILE = OUTPUT_DIR / "band_summaries_pilot.json"

# Load mapping
with open(MAPPING_FILE) as f:
    MAPPING = json.load(f)

# Claude client
client = anthropic.Anthropic(api_key=api_key)

# Band-specific prompts
BAND_PROMPTS = {
    "history": """Summarize the historical profile of {place_name} in 200-300 words.
Focus on: origins and founding, major historical periods, key events and transitions,
archaeological significance if applicable.
Write in past tense for historical events. Be factual and specific about dates and periods mentioned.""",

    "environment": """Summarize the environmental and geographic setting of {place_name} in 150-250 words.
Focus on: physical location and terrain, climate characteristics, notable natural features,
ecological context, relationship between landscape and settlement.
Write in present tense for enduring geographic features.""",

    "culture": """Summarize the cultural character of {place_name} in 200-300 words.
Focus on: architectural heritage, religious and spiritual significance, artistic traditions,
ethnic and linguistic composition, major monuments and cultural landmarks.
Emphasize what makes this place culturally distinctive.""",

    "modern": """Summarize the contemporary profile of {place_name} in 150-250 words.
Focus on: current urban/site function, economic activities, tourism significance,
infrastructure and accessibility, administrative status.
Write in present tense. Note if the place is primarily archaeological vs. living city."""
}

SYSTEM_PROMPT = """You are a cultural geographer writing concise, factual summaries of places for academic reference.
Use only the information provided in the source text. Do not add external knowledge.
If the source text lacks information on a topic, simply omit that topic rather than speculating.
Write in clear, neutral academic prose without promotional language."""


def get_band(heading: str) -> str | None:
    """Apply mapping rules to get band for a section heading."""
    h = heading.lower().strip()

    # Check exclusions first
    exc = MAPPING['exclude']
    if h in exc['exact']:
        return None
    for pattern in exc.get('contains', []):
        if pattern in h:
            return None

    # Check each band
    for band in ['history', 'environment', 'culture', 'modern']:
        rules = MAPPING[band]

        if h in rules['exact']:
            return band
        for pattern in rules.get('contains', []):
            if pattern in h:
                return band
        for pattern in rules.get('endswith', []):
            if h.endswith(pattern):
                return band

    return None  # unmapped


def aggregate_band_text(site_data: dict) -> dict[str, str]:
    """Aggregate all section text by band for a site."""
    band_texts = {'history': [], 'environment': [], 'culture': [], 'modern': []}

    for sec in site_data.get('sections', []):
        band = get_band(sec['title'])
        if band and band in band_texts:
            # Include section title as context
            band_texts[band].append(f"[{sec['title']}]\n{sec['text']}")

    # Join with double newlines
    return {band: "\n\n".join(texts) for band, texts in band_texts.items()}


def summarize_band(place_name: str, band: str, source_text: str) -> dict:
    """Call Claude to summarize a band's text."""
    if not source_text.strip():
        return {
            "band": band,
            "status": "no_content",
            "summary": None,
            "source_chars": 0
        }

    prompt = BAND_PROMPTS[band].format(place_name=place_name)

    # Truncate source text if very long (keep under ~15k chars to leave room for response)
    max_source = 15000
    if len(source_text) > max_source:
        source_text = source_text[:max_source] + "\n\n[Source text truncated...]"

    try:
        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=500,
            system=SYSTEM_PROMPT,
            messages=[
                {
                    "role": "user",
                    "content": f"{prompt}\n\n--- SOURCE TEXT ---\n\n{source_text}"
                }
            ]
        )

        summary = response.content[0].text

        return {
            "band": band,
            "status": "ok",
            "summary": summary,
            "source_chars": len(source_text),
            "summary_chars": len(summary),
            "input_tokens": response.usage.input_tokens,
            "output_tokens": response.usage.output_tokens
        }

    except Exception as e:
        return {
            "band": band,
            "status": "error",
            "error": str(e),
            "summary": None,
            "source_chars": len(source_text)
        }


def process_site(site_data: dict) -> dict:
    """Process a single site: aggregate bands and summarize each."""
    place_name = site_data['name']
    wiki_slug = site_data['wiki_slug']

    print(f"  Aggregating bands...")
    band_texts = aggregate_band_text(site_data)

    summaries = {}
    for band in ['history', 'environment', 'culture', 'modern']:
        source_text = band_texts[band]
        char_count = len(source_text)

        if char_count == 0:
            print(f"    {band}: no content")
            summaries[band] = {
                "status": "no_content",
                "summary": None,
                "source_chars": 0
            }
        else:
            print(f"    {band}: {char_count:,} chars -> summarizing...")
            result = summarize_band(place_name, band, source_text)
            summaries[band] = result

            if result['status'] == 'ok':
                print(f"      -> {result['summary_chars']} chars summary")
            else:
                print(f"      -> {result['status']}")

            # Rate limiting
            time.sleep(0.5)

    return {
        "site_id": site_data['site_id'],
        "name": place_name,
        "wiki_slug": wiki_slug,
        "place_type": site_data['place_type'],
        "summaries": summaries,
        "processed_at": datetime.utcnow().isoformat()
    }


def main():
    print(f"Loading sections from {SECTIONS_FILE}...")
    with open(SECTIONS_FILE) as f:
        sites = json.load(f)

    print(f"Processing {len(sites)} sites...\n")

    results = []
    total_tokens = {"input": 0, "output": 0}

    for i, site in enumerate(sites, 1):
        print(f"[{i:2d}/{len(sites)}] {site['name']}")

        if site.get('status') != 'ok':
            print(f"  Skipping (status: {site.get('status')})")
            continue

        result = process_site(site)
        results.append(result)

        # Tally tokens
        for band_result in result['summaries'].values():
            if band_result.get('status') == 'ok':
                total_tokens['input'] += band_result.get('input_tokens', 0)
                total_tokens['output'] += band_result.get('output_tokens', 0)

        print()

    # Write results
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    print(f"Wrote summaries to {OUTPUT_FILE}")
    print(f"\nToken usage: {total_tokens['input']:,} input, {total_tokens['output']:,} output")

    # Quick coverage stats
    bands_with_content = {'history': 0, 'environment': 0, 'culture': 0, 'modern': 0}
    for r in results:
        for band, data in r['summaries'].items():
            if data.get('status') == 'ok':
                bands_with_content[band] += 1

    print(f"\nBand coverage across {len(results)} sites:")
    for band, count in bands_with_content.items():
        print(f"  {band}: {count}/{len(results)} sites")


if __name__ == "__main__":
    main()
