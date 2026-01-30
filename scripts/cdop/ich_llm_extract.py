"""
ICH LLM Extraction Pipeline
Extract structured geographic and environmental data from nomination documents using Claude API
"""
import sys
import os
import json
from datetime import datetime

sys.path.insert(0, '/Users/karlg/Documents/Repos/_cedop')

import anthropic
from dotenv import load_dotenv
load_dotenv()

# Sample document IDs to process
SAMPLE_IDS = ['00204', '00207', '00172', '00200', '00203']

DOC_DIR = '/Users/karlg/Documents/Repos/_cedop/app/data/ich/extracted_clean_02'
OUTPUT_FILE = '/Users/karlg/Documents/Repos/_cedop/output/cdop/ich_llm_extractions.json'

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


def extract_with_claude(ich_id: str, document_text: str) -> dict:
    """Call Claude API to extract structured data from document."""
    client = anthropic.Anthropic()

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

    # Extract JSON from response
    response_text = message.content[0].text

    # Parse JSON (handle potential markdown code blocks)
    if response_text.startswith('```'):
        # Remove markdown code block markers
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
    results = {
        "extraction_date": datetime.now().isoformat(),
        "model": "claude-sonnet-4-20250514",
        "sample_ids": SAMPLE_IDS,
        "extractions": []
    }

    for ich_id in SAMPLE_IDS:
        print(f"\n{'='*60}")
        print(f"Processing {ich_id}...")
        print('='*60)

        doc_path = find_doc_path(ich_id)
        if not doc_path:
            print(f"  ERROR: No document found for {ich_id}")
            results["extractions"].append({
                "ich_id": ich_id,
                "error": "Document not found"
            })
            continue

        with open(doc_path, 'r') as f:
            document_text = f.read()

        print(f"  Document: {os.path.basename(doc_path)}")
        print(f"  Length: {len(document_text)} chars")

        # Call Claude API
        print(f"  Calling Claude API...")
        extraction = extract_with_claude(ich_id, document_text)

        if "error" in extraction:
            print(f"  ERROR: {extraction['error']}")
        else:
            print(f"  Practice locations: {len(extraction.get('practice_locations', []))}")
            print(f"  Diaspora locations: {len(extraction.get('diaspora_locations', []))}")
            print(f"  Coordinates explicit: {extraction.get('coordinates', {}).get('explicit', False)}")
            print(f"  Environmental features: {len(extraction.get('environmental_features', []))}")

        results["extractions"].append(extraction)

    # Save results
    with open(OUTPUT_FILE, 'w') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    print(f"\n{'='*60}")
    print(f"Results saved to: {OUTPUT_FILE}")
    print(f"Processed {len(results['extractions'])} documents")


if __name__ == "__main__":
    main()
