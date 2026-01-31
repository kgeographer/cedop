"""
ICH LLM Extraction - Batch processing for Tier C+D documents
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

TRIAGE_FILE = '/Users/karlg/Documents/Repos/_cedop/output/cdop/ich_triage.json'
DOC_DIR = '/Users/karlg/Documents/Repos/_cedop/app/data/ich/extracted_clean_02'
OUTPUT_FILE = '/Users/karlg/Documents/Repos/_cedop/output/cdop/ich_llm_extractions_tier_cd.json'

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
    """Find the document file for a given ICH ID."""
    for f in os.listdir(DOC_DIR):
        if f.startswith(ich_id + '_') and f.endswith('.txt'):
            return os.path.join(DOC_DIR, f)
    return None


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
    # Load triage results
    with open(TRIAGE_FILE, 'r') as f:
        triage = json.load(f)

    # Get Tier C and D document IDs
    tier_c_ids = triage["tiers"]["C"]["docs"]
    tier_d_ids = triage["tiers"]["D"]["docs"]
    target_ids = tier_c_ids + tier_d_ids

    print(f"Processing {len(target_ids)} documents (Tier C: {len(tier_c_ids)}, Tier D: {len(tier_d_ids)})")

    # Check for existing checkpoint
    start_idx = 0
    results = {
        "extraction_date": datetime.now().isoformat(),
        "model": "claude-sonnet-4-20250514",
        "tiers_processed": ["C", "D"],
        "total_documents": len(target_ids),
        "successful": 0,
        "failed": 0,
        "extractions": []
    }

    if os.path.exists(OUTPUT_FILE):
        with open(OUTPUT_FILE, 'r') as f:
            existing = json.load(f)
            if existing.get("extractions"):
                results = existing
                start_idx = len(existing["extractions"])
                print(f"Resuming from checkpoint: {start_idx}/{len(target_ids)} already processed")

    client = anthropic.Anthropic()

    for i, ich_id in enumerate(target_ids[start_idx:], start=start_idx):
        print(f"\n[{i+1}/{len(target_ids)}] Processing {ich_id}...", end=" ", flush=True)

        doc_path = find_doc_path(ich_id)
        if not doc_path:
            print("NOT FOUND")
            results["extractions"].append({
                "ich_id": ich_id,
                "error": "Document not found"
            })
            results["failed"] += 1
            continue

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
            print(f"  [Checkpoint saved: {i+1}/{len(target_ids)}]")

    # Final save
    with open(OUTPUT_FILE, 'w') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    # Summary
    print(f"\n{'='*60}")
    print("EXTRACTION COMPLETE")
    print('='*60)
    print(f"Total processed: {len(target_ids)}")
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
