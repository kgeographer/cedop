"""
Summarize Wikipedia sections by semantic band for 258 WHC cities.

Reads harvested sections, concatenates by band, uses Claude API
to generate normalized summaries.

Usage:
    python scripts/corpus/summarize_whc.py
"""

import json
import os
import time
from datetime import datetime, timezone
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# Check for API key
api_key = os.getenv("ANTHROPIC_API_KEY")
if not api_key:
    print("ERROR: ANTHROPIC_API_KEY not found in environment or .env")
    exit(1)

import anthropic

# Paths
INPUT_DIR = Path("output/corpus_258")
SECTIONS_FILE = INPUT_DIR / "wiki_sections.json"
OUTPUT_FILE = INPUT_DIR / "band_summaries.json"
MAPPING_FILE = Path("output/corpus/band_mapping_draft.json")

# Load mapping
with open(MAPPING_FILE) as f:
    MAPPING = json.load(f)

# Claude client
client = anthropic.Anthropic(api_key=api_key)

BANDS = ['history', 'environment', 'culture', 'modern']

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
Focus on: current urban function, economic activities, tourism significance,
infrastructure and accessibility, administrative status.
Write in present tense."""
}

SYSTEM_PROMPT = """You are a cultural geographer writing concise, factual summaries of places for academic reference.
Use only the information provided in the source text. Do not add external knowledge.
If the source text lacks information on a topic, simply omit that topic rather than speculating.
Write in clear, neutral academic prose without promotional language."""


def get_band(heading: str) -> str | None:
    """Apply mapping rules to get band for a section heading."""
    h = heading.lower().strip()

    exc = MAPPING['exclude']
    if h in exc['exact']:
        return None
    for pattern in exc.get('contains', []):
        if pattern in h:
            return None

    for band in BANDS:
        rules = MAPPING[band]
        if h in rules['exact']:
            return band
        for pattern in rules.get('contains', []):
            if pattern in h:
                return band
        for pattern in rules.get('endswith', []):
            if h.endswith(pattern):
                return band

    return None


def aggregate_band_text(city_data: dict) -> dict[str, str]:
    """Aggregate all section text by band for a city."""
    band_texts = {band: [] for band in BANDS}

    for sec in city_data.get('sections', []):
        band = get_band(sec['title'])
        if band and band in band_texts:
            band_texts[band].append(f"[{sec['title']}]\n{sec['text']}")

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

    # Truncate if very long
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


def process_city(city_data: dict) -> dict:
    """Process a single city: aggregate bands and summarize each."""
    place_name = city_data['city']

    band_texts = aggregate_band_text(city_data)

    summaries = {}
    for band in BANDS:
        source_text = band_texts[band]
        char_count = len(source_text)

        if char_count == 0:
            summaries[band] = {
                "status": "no_content",
                "summary": None,
                "source_chars": 0
            }
        else:
            result = summarize_band(place_name, band, source_text)
            summaries[band] = result
            # Rate limiting
            time.sleep(0.3)

    return {
        "whc_id": city_data['whc_id'],
        "city": city_data['city'],
        "slug": city_data['slug'],
        "region": city_data['region'],
        "country": city_data['country'],
        "ccode": city_data['ccode'],
        "summaries": summaries,
        "processed_at": datetime.now(timezone.utc).isoformat()
    }


def main():
    print(f"Loading sections from {SECTIONS_FILE}...")
    with open(SECTIONS_FILE) as f:
        cities = json.load(f)

    # Filter to only OK status
    cities_ok = [c for c in cities if c.get('status') == 'ok']
    print(f"Processing {len(cities_ok)} cities (of {len(cities)} total)...\n")

    results = []
    total_tokens = {"input": 0, "output": 0}
    errors = []

    for i, city in enumerate(cities_ok, 1):
        bands_with_content = sum(
            1 for sec in city.get('sections', [])
            if get_band(sec['title']) in BANDS
        )

        print(f"[{i:3d}/{len(cities_ok)}] {city['city'][:30]:<30} ({city['ccode']})...", end=" ", flush=True)

        try:
            result = process_city(city)
            results.append(result)

            # Tally tokens and count successful bands
            ok_bands = 0
            for band_result in result['summaries'].values():
                if band_result.get('status') == 'ok':
                    total_tokens['input'] += band_result.get('input_tokens', 0)
                    total_tokens['output'] += band_result.get('output_tokens', 0)
                    ok_bands += 1

            print(f"{ok_bands}/4 bands summarized")

        except Exception as e:
            print(f"[ERROR: {e}]")
            errors.append((city['city'], str(e)))

        # Checkpoint every 50 cities
        if i % 50 == 0:
            checkpoint_path = INPUT_DIR / f"band_summaries_checkpoint_{i}.json"
            with open(checkpoint_path, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, ensure_ascii=False)
            print(f"  [Checkpoint saved: {checkpoint_path}]")

    # Write final results
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    print(f"\nWrote summaries to {OUTPUT_FILE}")
    print(f"\nToken usage: {total_tokens['input']:,} input, {total_tokens['output']:,} output")

    # Estimate cost (Claude Sonnet pricing ~$3/M input, $15/M output)
    cost_est = (total_tokens['input'] * 3 + total_tokens['output'] * 15) / 1_000_000
    print(f"Estimated cost: ${cost_est:.2f}")

    if errors:
        print(f"\nErrors ({len(errors)}):")
        for city, err in errors[:10]:
            print(f"  - {city}: {err}")

    # Coverage summary
    print("\n" + "=" * 60)
    print("BAND COVERAGE SUMMARY")
    print("=" * 60)

    band_counts = {band: 0 for band in BANDS}
    for r in results:
        for band, data in r['summaries'].items():
            if data.get('status') == 'ok':
                band_counts[band] += 1

    for band in BANDS:
        print(f"  {band}: {band_counts[band]}/{len(results)} cities")


if __name__ == "__main__":
    main()
