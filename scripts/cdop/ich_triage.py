"""
ICH Document Triage
Quick quality assessment of nomination documents without LLM calls
"""
import os
import re
import json

DOC_DIR = '/Users/karlg/Documents/Repos/_cedop/app/data/ich/extracted_clean_02'
OUTPUT_FILE = '/Users/karlg/Documents/Repos/_cedop/output/cdop/ich_triage.json'

# Patterns for coordinate detection
COORD_PATTERNS = [
    r'\d+°\s*\d*[\'′]?\s*[NSEW]',  # 32°03' N
    r'[NSEW]\s*\d+°',              # N 32°
    r'longitude\s+\d+',            # longitude 108
    r'latitude\s+\d+',             # latitude 25
    r'\d+°.*longitude',            # 108° east longitude
    r'\d+°.*latitude',             # 25° north latitude
]

def has_coordinates(text: str) -> bool:
    """Check if document contains explicit coordinates."""
    text_lower = text.lower()
    for pattern in COORD_PATTERNS:
        if re.search(pattern, text, re.IGNORECASE):
            return True
    return False

def has_geo_section(text: str) -> bool:
    """Check if document has a Geographic location section."""
    patterns = [
        r'geographic location',
        r'location and range',
        r'geographical scope',
    ]
    text_lower = text.lower()
    return any(p in text_lower for p in patterns)

def extract_ich_id(filename: str) -> str:
    """Extract ICH ID from filename."""
    return filename.split('_')[0]

def count_place_indicators(text: str) -> int:
    """Count indicators of specific place mentions."""
    indicators = [
        r'\b[A-Z][a-z]+ (?:Province|County|District|Prefecture|City|Town|Village|Island|Region)\b',
        r'\b(?:Province|County|District|Prefecture) of [A-Z][a-z]+\b',
        r'\bkm\s*(?:from|north|south|east|west)\b',
        r'\bsquare\s*(?:km|kilometer|kilometre)\b',
    ]
    count = 0
    for pattern in indicators:
        count += len(re.findall(pattern, text, re.IGNORECASE))
    return count

def main():
    results = {
        "triage_date": "2026-01-30",
        "total_documents": 0,
        "tiers": {
            "A": {"description": "Has explicit coordinates", "count": 0, "docs": []},
            "B": {"description": "Has 'Geographic location' section, no coords", "count": 0, "docs": []},
            "C": {"description": "Long doc (>5000 chars) with place indicators", "count": 0, "docs": []},
            "D": {"description": "Short or vague", "count": 0, "docs": []},
        },
        "stats": {
            "avg_length": 0,
            "min_length": float('inf'),
            "max_length": 0,
            "length_buckets": {
                "<3000": 0,
                "3000-5000": 0,
                "5000-10000": 0,
                "10000-15000": 0,
                ">15000": 0,
            }
        },
        "documents": []
    }

    all_lengths = []

    for filename in sorted(os.listdir(DOC_DIR)):
        if not filename.endswith('.txt'):
            continue

        filepath = os.path.join(DOC_DIR, filename)
        with open(filepath, 'r') as f:
            text = f.read()

        ich_id = extract_ich_id(filename)
        length = len(text)
        all_lengths.append(length)

        has_coords = has_coordinates(text)
        has_geo = has_geo_section(text)
        place_count = count_place_indicators(text)

        # Determine tier
        if has_coords:
            tier = "A"
        elif has_geo:
            tier = "B"
        elif length > 5000 and place_count >= 3:
            tier = "C"
        else:
            tier = "D"

        doc_info = {
            "ich_id": ich_id,
            "filename": filename,
            "length": length,
            "has_coordinates": has_coords,
            "has_geo_section": has_geo,
            "place_indicators": place_count,
            "tier": tier,
        }

        results["documents"].append(doc_info)
        results["tiers"][tier]["count"] += 1
        results["tiers"][tier]["docs"].append(ich_id)

        # Update length buckets
        if length < 3000:
            results["stats"]["length_buckets"]["<3000"] += 1
        elif length < 5000:
            results["stats"]["length_buckets"]["3000-5000"] += 1
        elif length < 10000:
            results["stats"]["length_buckets"]["5000-10000"] += 1
        elif length < 15000:
            results["stats"]["length_buckets"]["10000-15000"] += 1
        else:
            results["stats"]["length_buckets"][">15000"] += 1

        results["stats"]["min_length"] = min(results["stats"]["min_length"], length)
        results["stats"]["max_length"] = max(results["stats"]["max_length"], length)

    results["total_documents"] = len(all_lengths)
    results["stats"]["avg_length"] = int(sum(all_lengths) / len(all_lengths))

    # Print summary
    print("="*60)
    print("ICH DOCUMENT TRIAGE SUMMARY")
    print("="*60)
    print(f"\nTotal documents: {results['total_documents']}")
    print(f"\nLength stats:")
    print(f"  Min: {results['stats']['min_length']:,} chars")
    print(f"  Max: {results['stats']['max_length']:,} chars")
    print(f"  Avg: {results['stats']['avg_length']:,} chars")

    print(f"\nLength distribution:")
    for bucket, count in results["stats"]["length_buckets"].items():
        pct = 100 * count / results["total_documents"]
        print(f"  {bucket}: {count} ({pct:.1f}%)")

    print(f"\n" + "="*60)
    print("QUALITY TIERS")
    print("="*60)
    for tier, info in results["tiers"].items():
        pct = 100 * info["count"] / results["total_documents"]
        print(f"\nTier {tier}: {info['description']}")
        print(f"  Count: {info['count']} ({pct:.1f}%)")
        if info["count"] <= 10:
            print(f"  IDs: {info['docs']}")
        else:
            print(f"  Sample IDs: {info['docs'][:5]}...")

    # Save full results
    with open(OUTPUT_FILE, 'w') as f:
        json.dump(results, f, indent=2)

    print(f"\n" + "="*60)
    print(f"Full results saved to: {OUTPUT_FILE}")

    # Recommended next steps
    print(f"\n" + "="*60)
    print("RECOMMENDED NEXT STEPS")
    print("="*60)
    tier_a = results["tiers"]["A"]["count"]
    tier_b = results["tiers"]["B"]["count"]
    print(f"\n1. Run LLM extraction on Tier A+B ({tier_a + tier_b} docs)")
    print(f"   Estimated cost: ${(tier_a + tier_b) * 0.02:.2f}")
    print(f"\n2. Review Tier D samples to assess salvageability")
    print(f"\n3. Consider whether Tier C docs need full extraction or simpler regex")

if __name__ == "__main__":
    main()
