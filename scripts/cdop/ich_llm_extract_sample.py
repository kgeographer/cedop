"""
ICH LLM Extraction - Sample Tier D documents
"""
import sys
import os
import json
import time
from datetime import datetime

sys.path.insert(0, '/Users/karlg/Documents/Repos/_cedop')

import anthropic
from dotenv import load_dotenv
load_dotenv()

# Tier D sample (random seed=42)
SAMPLE_IDS = ['00907', '00535', '01294', '01263', '01197', '00998', '00885', '01974', '00870', '01682']

DOC_DIR = '/Users/karlg/Documents/Repos/_cedop/app/data/ich/extracted_clean_02'
OUTPUT_FILE = '/Users/karlg/Documents/Repos/_cedop/output/cdop/ich_llm_extractions_tier_d_sample.json'

EXTRACTION_PROMPT = """You are a geographic information extraction specialist. Your task is to extract structured location and environmental data from UNESCO Intangible Cultural Heritage nomination documents.

IMPORTANT DISTINCTIONS:
1. **Practice locations**: Where the cultural practice is actually performed/originated. These are the primary geographic footprint.
2. **Diaspora locations**: Where practitioners have migrated TO, carrying the tradition with them. These are secondary/derived locations.

EXTRACTION SCHEMA (use this exact structure):

{{
  "ich_id": "string - the 5-digit ID",
  "element_name": "string - name of the cultural element",

  "practice_locations": [
    {{
      "name": "string - place name",
      "type": "string - one of: country, province, prefecture, county, city, town, village, island, river, mountain, region",
      "parent_admin": "string or null - parent administrative unit",
      "country": "string - ISO country name",
      "country_code": "string or null - 2-letter ISO code if known"
    }}
  ],

  "coordinates": {{
    "explicit": "boolean - true if lat/lon explicitly stated in document",
    "lat_min": "number or null",
    "lat_max": "number or null",
    "lon_min": "number or null",
    "lon_max": "number or null",
    "source_text": "string or null - the exact text containing coordinates"
  }},

  "diaspora_locations": [
    {{
      "name": "string - place name",
      "country": "string - country name",
      "context": "string - brief description of why mentioned (e.g., 'emigrant community', 'spread via trade')"
    }}
  ],

  "environmental_features": [
    "string - specific environmental/geographic features mentioned (e.g., 'mountainous terrain', 'river valley', 'coastal area', 'arid plateau')"
  ],

  "environmental_summary": "string - 1-2 sentence summary of the environmental/geographic context of this practice",

  "extraction_notes": "string or null - any ambiguities or issues encountered during extraction"
}}

GUIDELINES:
- Be precise about location types (don't call a province a "region")
- Extract ALL practice locations mentioned, with hierarchy where clear
- Only mark coordinates as "explicit" if actual lat/lon values appear in text
- For diaspora, look for phrases like "emigrants", "migrants", "spread to", "also practiced in [foreign country]"
- Environmental features should focus on physical geography, not cultural features
- If uncertain about a classification, note it in extraction_notes

Now extract from this nomination document:

---
DOCUMENT ID: {ich_id}
---
{document_text}
---

Return ONLY valid JSON matching the schema above. No other text."""


def find_doc_path(ich_id: str) -> str | None:
    for f in os.listdir(DOC_DIR):
        if f.startswith(ich_id + '_') and f.endswith('.txt'):
            return os.path.join(DOC_DIR, f)
    return None


def extract_with_claude(ich_id: str, document_text: str, client: anthropic.Anthropic) -> dict:
    prompt = EXTRACTION_PROMPT.format(ich_id=ich_id, document_text=document_text)

    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=4096,
        messages=[{"role": "user", "content": prompt}]
    )

    response_text = message.content[0].text

    if response_text.startswith('```'):
        lines = response_text.split('\n')
        json_lines = []
        in_block = False
        for line in lines:
            if line.startswith('```'):
                in_block = not in_block
                continue
            if in_block or not line.startswith('```'):
                json_lines.append(line)
        response_text = '\n'.join(json_lines)

    try:
        return json.loads(response_text)
    except json.JSONDecodeError as e:
        return {"ich_id": ich_id, "error": f"JSON parse error: {e}", "raw_response": response_text[:500]}


def main():
    results = {
        "extraction_date": datetime.now().isoformat(),
        "model": "claude-sonnet-4-20250514",
        "tier": "D (sample)",
        "sample_ids": SAMPLE_IDS,
        "extractions": []
    }

    client = anthropic.Anthropic()

    for i, ich_id in enumerate(SAMPLE_IDS):
        print(f"[{i+1}/{len(SAMPLE_IDS)}] Processing {ich_id}...", end=" ", flush=True)

        doc_path = find_doc_path(ich_id)
        if not doc_path:
            print("NOT FOUND")
            results["extractions"].append({"ich_id": ich_id, "error": "Document not found"})
            continue

        with open(doc_path, 'r') as f:
            document_text = f.read()

        try:
            extraction = extract_with_claude(ich_id, document_text, client)

            if "error" in extraction:
                print(f"ERROR")
            else:
                n_practice = len(extraction.get('practice_locations', []))
                n_diaspora = len(extraction.get('diaspora_locations', []))
                has_coords = extraction.get('coordinates', {}).get('explicit', False)
                env_summary = extraction.get('environmental_summary', '')[:50]
                print(f"practice:{n_practice}, diaspora:{n_diaspora}, coords:{has_coords}")
                print(f"         env: {env_summary}...")

            results["extractions"].append(extraction)

        except Exception as e:
            print(f"EXCEPTION: {e}")
            results["extractions"].append({"ich_id": ich_id, "error": str(e)})

        time.sleep(0.5)

    with open(OUTPUT_FILE, 'w') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    print(f"\n{'='*60}")
    print("TIER D SAMPLE RESULTS")
    print('='*60)

    successful = [e for e in results['extractions'] if 'error' not in e]
    print(f"Successful: {len(successful)}/{len(SAMPLE_IDS)}")

    if successful:
        with_coords = sum(1 for e in successful if e.get('coordinates', {}).get('explicit'))
        with_locations = sum(1 for e in successful if len(e.get('practice_locations', [])) >= 3)
        with_env = sum(1 for e in successful if len(e.get('environmental_features', [])) >= 1)

        print(f"With coordinates: {with_coords}")
        print(f"With 3+ practice locations: {with_locations}")
        print(f"With environmental features: {with_env}")

        salvage_rate = with_locations / len(successful) * 100
        print(f"\nEstimated salvage rate (3+ locations): {salvage_rate:.0f}%")

    print(f"\nResults saved to: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
