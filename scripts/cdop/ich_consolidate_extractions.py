"""
ICH Extraction Consolidation
=============================

Merges all extraction batches into a single consolidated file.

Sources:
- tier_ab.json (72 docs)
- tier_cd.json (494 docs)
- tier_new_2026-01.json (167 docs)

Output:
- consolidated_all.json (733 docs)
"""
import json
from datetime import datetime
from pathlib import Path

OUTPUT_DIR = Path('/Users/karlg/Documents/Repos/_cedop/output/cdop/ich_extractions')
LEGACY_DIR = Path('/Users/karlg/Documents/Repos/_cedop/output/cdop')

# Source files
SOURCES = [
    ('tier_ab', LEGACY_DIR / 'ich_llm_extractions_tier_ab.json'),
    ('tier_cd', LEGACY_DIR / 'ich_llm_extractions_tier_cd.json'),
    ('tier_new', OUTPUT_DIR / 'tier_new_2026-01.json'),
]

OUTPUT_FILE = OUTPUT_DIR / 'consolidated_all.json'


def main():
    print("ICH Extraction Consolidation")
    print("=" * 60)

    all_extractions = []
    seen_ids = set()
    source_stats = {}

    for source_name, source_path in SOURCES:
        if not source_path.exists():
            print(f"\n{source_name}: NOT FOUND - {source_path}")
            source_stats[source_name] = {'found': False, 'count': 0}
            continue

        with open(source_path) as f:
            data = json.load(f)

        extractions = data.get('extractions', [])
        new_count = 0
        dup_count = 0

        for ext in extractions:
            ich_id = ext.get('ich_id')
            if ich_id and ich_id not in seen_ids:
                # Add source marker
                ext['_source'] = source_name
                all_extractions.append(ext)
                seen_ids.add(ich_id)
                new_count += 1
            else:
                dup_count += 1

        source_stats[source_name] = {
            'found': True,
            'total': len(extractions),
            'added': new_count,
            'duplicates': dup_count
        }
        print(f"\n{source_name}: {new_count} added ({dup_count} duplicates)")

    # Sort by ich_id
    all_extractions.sort(key=lambda x: x.get('ich_id', ''))

    # Count stats
    successful = sum(1 for e in all_extractions if 'error' not in e)
    failed = sum(1 for e in all_extractions if 'error' in e)
    with_coords = sum(1 for e in all_extractions
                      if e.get('coordinates', {}).get('explicit', False))

    # Build consolidated output
    consolidated = {
        "consolidation_date": datetime.now().isoformat(),
        "sources": source_stats,
        "total_documents": len(all_extractions),
        "successful": successful,
        "failed": failed,
        "with_explicit_coordinates": with_coords,
        "extractions": all_extractions
    }

    # Save
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_FILE, 'w') as f:
        json.dump(consolidated, f, indent=2, ensure_ascii=False)

    # Summary
    print(f"\n{'='*60}")
    print("CONSOLIDATION COMPLETE")
    print('='*60)
    print(f"Total unique extractions: {len(all_extractions)}")
    print(f"Successful: {successful}")
    print(f"Failed: {failed}")
    print(f"With explicit coordinates: {with_coords}")
    print(f"\nSaved to: {OUTPUT_FILE}")

    # Breakdown by source
    print(f"\nBy source:")
    for name, stats in source_stats.items():
        if stats.get('found'):
            print(f"  {name}: {stats['added']} docs")
        else:
            print(f"  {name}: NOT FOUND")


if __name__ == "__main__":
    main()
