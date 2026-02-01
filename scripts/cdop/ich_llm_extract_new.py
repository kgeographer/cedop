"""
ICH LLM Extraction - Batch processing for new 2024-25 + gap-fill documents
Adapted from ich_llm_extract_batch_cd.py
"""
import sys
import os
import json
import time
from datetime import datetime
from pathlib import Path

sys.path.insert(0, '/Users/karlg/Documents/Repos/_cedop')

import anthropic
from dotenv import load_dotenv
load_dotenv()

# Input: LLM-cleaned text files
DOC_DIR = Path('/Users/karlg/Documents/Repos/_cedop/app/data/ich/cleaned_llm')

# Output
OUTPUT_DIR = Path('/Users/karlg/Documents/Repos/_cedop/output/cdop/ich_extractions')
OUTPUT_FILE = OUTPUT_DIR / 'tier_new_2026-01.json'

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

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


def get_files_to_process():
    """Get all cleaned files sorted by ICH ID."""
    files = list(DOC_DIR.glob('*_cleaned.txt'))
    files.sort(key=lambda p: p.stem.split('_')[0])
    return files


def extract_with_claude(ich_id: str, document_text: str, client: anthropic.Anthropic) -> dict:
    """Call Claude API to extract structured data from document."""
    prompt = EXTRACTION_PROMPT.format(
        ich_id=ich_id,
        document_text=document_text
    )

    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=4096,
        messages=[
            {"role": "user", "content": prompt}
        ]
    )

    response_text = message.content[0].text

    # Parse JSON (handle potential markdown code blocks)
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
        return {
            "ich_id": ich_id,
            "error": f"JSON parse error: {e}",
            "raw_response": response_text[:500]
        }


def main():
    files = get_files_to_process()
    print(f"Found {len(files)} cleaned documents to process")

    # Check for existing checkpoint
    start_idx = 0
    results = {
        "extraction_date": datetime.now().isoformat(),
        "model": "claude-sonnet-4-20250514",
        "source": "new_2024-25_and_gap-fill",
        "total_documents": len(files),
        "successful": 0,
        "failed": 0,
        "extractions": []
    }

    if OUTPUT_FILE.exists():
        with open(OUTPUT_FILE, 'r') as f:
            existing = json.load(f)
            if existing.get("extractions"):
                results = existing
                start_idx = len(existing["extractions"])
                print(f"Resuming from checkpoint: {start_idx}/{len(files)} already processed")

    client = anthropic.Anthropic()

    for i, doc_path in enumerate(files[start_idx:], start=start_idx):
        ich_id = doc_path.stem.split('_')[0]
        print(f"\n[{i+1}/{len(files)}] Processing {ich_id}...", end=" ", flush=True)

        with open(doc_path, 'r') as f:
            document_text = f.read()

        try:
            extraction = extract_with_claude(ich_id, document_text, client)

            if "error" in extraction:
                print(f"ERROR: {extraction['error'][:50]}")
                results["failed"] += 1
            else:
                n_practice = len(extraction.get('practice_locations', []))
                n_diaspora = len(extraction.get('diaspora_locations', []))
                has_coords = extraction.get('coordinates', {}).get('explicit', False)
                print(f"OK (practice:{n_practice}, diaspora:{n_diaspora}, coords:{has_coords})")
                results["successful"] += 1

            results["extractions"].append(extraction)

        except Exception as e:
            print(f"EXCEPTION: {e}")
            results["extractions"].append({
                "ich_id": ich_id,
                "error": str(e)
            })
            results["failed"] += 1

        # Small delay to avoid rate limits
        time.sleep(0.5)

        # Save intermediate results every 10 documents
        if (i + 1) % 10 == 0:
            with open(OUTPUT_FILE, 'w') as f:
                json.dump(results, f, indent=2, ensure_ascii=False)
            print(f"  [Checkpoint saved: {i+1}/{len(files)}]")

    # Final save
    with open(OUTPUT_FILE, 'w') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    # Summary
    print(f"\n{'='*60}")
    print("EXTRACTION COMPLETE")
    print('='*60)
    print(f"Total processed: {len(files)}")
    print(f"Successful: {results['successful']}")
    print(f"Failed: {results['failed']}")
    print(f"\nResults saved to: {OUTPUT_FILE}")

    # Quick stats on successful extractions
    if results['successful'] > 0:
        coords_count = sum(1 for e in results['extractions']
                          if e.get('coordinates', {}).get('explicit', False))
        avg_practice = sum(len(e.get('practice_locations', []))
                          for e in results['extractions'] if 'error' not in e) / results['successful']
        avg_diaspora = sum(len(e.get('diaspora_locations', []))
                          for e in results['extractions'] if 'error' not in e) / results['successful']

        print(f"\nStats:")
        print(f"  With explicit coordinates: {coords_count}")
        print(f"  Avg practice locations: {avg_practice:.1f}")
        print(f"  Avg diaspora locations: {avg_diaspora:.1f}")


if __name__ == "__main__":
    main()
