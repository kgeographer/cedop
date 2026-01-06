#!/usr/bin/env python3
"""
Transform Cliopatria polities GeoJSON to Linked Places Format (LPF).

Cliopatria contains ~15,690 features representing ~1,618 polities with
multiple temporal extents. This script consolidates them into LPF format
where each polity is a single Feature with a GeometryCollection of
temporally-scoped geometries.

Input: app/data/clio/cliopatria_polities_only.geojson
Output: app/data/clio/cliopatria_lpf.json

Usage:
    python scripts/cliopatria_to_lpf.py
"""

import json
import re
from collections import defaultdict
from pathlib import Path

# Paths
INPUT_FILE = Path(__file__).parent.parent / "app" / "data" / "clio" / "cliopatria_polities_only.geojson"
OUTPUT_FILE = Path(__file__).parent.parent / "app" / "data" / "clio" / "cliopatria_lpf.json"

# LPF JSON-LD context
LPF_CONTEXT = "https://linkedpasts.org/assets/linkedplaces-context-v1.3.jsonld"

# Coordinate precision (5 decimal places ≈ 1 meter)
COORD_PRECISION = 5


def round_coords(coords, precision=COORD_PRECISION):
    """
    Recursively round coordinates to specified precision.
    Handles all GeoJSON coordinate structures (Point, LineString, Polygon, Multi*).
    """
    if isinstance(coords[0], (int, float)):
        # Base case: [lon, lat] pair
        return [round(c, precision) for c in coords]
    else:
        # Recursive case: list of coordinate arrays
        return [round_coords(c, precision) for c in coords]


def normalize_name(name):
    """Strip wrapping parentheses for grouping: '(Ottoman Empire)' -> 'Ottoman Empire'"""
    if name.startswith('(') and name.endswith(')'):
        return name[1:-1]
    return name


def format_year(year):
    """
    Convert integer year to ISO 8601 string for LPF.
    Negative years need proper formatting: -31 -> '-0031'
    Positive years: 476 -> '0476'
    """
    if year < 0:
        return f"-{abs(year):04d}"
    else:
        return f"{year:04d}"


def make_wiki_slug(wiki_value):
    """Convert Wikipedia field value to slug: 'History of Sumer' -> 'History_of_Sumer'"""
    return wiki_value.replace(' ', '_')


def build_feature_id(seshat_ids, wiki_slugs):
    """
    Determine @id for the LPF feature.
    Priority: SeshatID (full URL) > Wikipedia (wp: prefix)
    """
    if seshat_ids:
        # Use first SeshatID as primary
        seshat_id = sorted(seshat_ids)[0]
        return f"https://seshat-db.com/core/polity/{seshat_id}"
    elif wiki_slugs:
        # Use first Wikipedia slug
        wiki_slug = make_wiki_slug(sorted(wiki_slugs)[0])
        return f"wp:{wiki_slug}"
    else:
        # Fallback (shouldn't happen based on data analysis)
        return None


def build_links(seshat_ids, wiki_slugs):
    """
    Build links array for LPF feature.
    If we have SeshatID as @id, Wikipedia goes in links.
    """
    links = []

    # If SeshatID is primary, add Wikipedia as link
    if seshat_ids and wiki_slugs:
        for wiki in sorted(wiki_slugs):
            wiki_slug = make_wiki_slug(wiki)
            links.append({
                "type": "primaryTopicOf",
                "identifier": f"wp:{wiki_slug}"
            })

    return links


def build_lpf_feature(polity_name, features_data):
    """
    Build a single LPF Feature from multiple Cliopatria features for one polity.

    Args:
        polity_name: Normalized polity name (title)
        features_data: List of (properties, geometry) tuples for this polity

    Returns:
        LPF Feature dict
    """
    # Collect all identifiers across variants
    all_seshat = set()
    all_wiki = set()
    all_names = set()

    for props, geom in features_data:
        all_names.add(props['Name'])
        if props.get('SeshatID', '').strip():
            all_seshat.add(props['SeshatID'].strip())
        if props.get('Wikipedia', '').strip():
            all_wiki.add(props['Wikipedia'].strip())

    # Build @id
    feature_id = build_feature_id(all_seshat, all_wiki)
    if not feature_id:
        # Generate fallback from name
        slug = re.sub(r'[^a-zA-Z0-9]+', '_', polity_name).strip('_').lower()
        feature_id = f"clio:{slug}"

    # Build temporally-scoped geometries
    geometries = []
    min_year = float('inf')
    max_year = float('-inf')

    for props, geom in features_data:
        from_year = props['FromYear']
        to_year = props['ToYear']

        min_year = min(min_year, from_year)
        max_year = max(max_year, to_year)

        # Add temporal scope to geometry (with rounded coordinates)
        geom_with_when = {
            "type": geom["type"],
            "coordinates": round_coords(geom["coordinates"]),
            "when": {
                "timespans": [{
                    "start": {"in": format_year(from_year)},
                    "end": {"in": format_year(to_year)}
                }]
            }
        }
        geometries.append(geom_with_when)

    # Sort geometries by start year
    geometries.sort(key=lambda g: g["when"]["timespans"][0]["start"]["in"])

    # Build the LPF Feature
    lpf_feature = {
        "@id": feature_id,
        "type": "Feature",
        "properties": {
            "title": polity_name,
            "fclasses": ["A"]  # Administrative/political entity
        },
        "geometry": {
            "type": "GeometryCollection",
            "geometries": geometries
        },
        "when": {
            "timespans": [{
                "start": {"in": format_year(int(min_year))},
                "end": {"in": format_year(int(max_year))}
            }]
        },
        "names": [{"toponym": polity_name}],
        "types": [{"label": "polity"}],
        "links": build_links(all_seshat, all_wiki)
    }

    # Add variant names if different from normalized
    for name in sorted(all_names):
        if name != polity_name:
            lpf_feature["names"].append({"toponym": name})

    return lpf_feature


def transform():
    """Main transformation function."""
    print("Cliopatria → LPF Transformation")
    print("=" * 50)

    # Load input
    print(f"\n1. Loading {INPUT_FILE.name}...")
    with open(INPUT_FILE, 'r', encoding='utf-8') as f:
        clio_data = json.load(f)

    features = clio_data['features']
    print(f"   Loaded {len(features)} features")

    # Group by normalized polity name
    print("\n2. Grouping by polity (normalizing parentheses variants)...")
    polity_groups = defaultdict(list)

    for feat in features:
        props = feat['properties']
        geom = feat['geometry']
        name = props['Name']
        norm_name = normalize_name(name)
        polity_groups[norm_name].append((props, geom))

    print(f"   {len(polity_groups)} unique polities after conflation")

    # Transform to LPF
    print("\n3. Building LPF features...")
    lpf_features = []

    for polity_name, feat_data in polity_groups.items():
        lpf_feat = build_lpf_feature(polity_name, feat_data)
        lpf_features.append(lpf_feat)

    # Sort by title for consistent output
    lpf_features.sort(key=lambda f: f['properties']['title'])

    # Build LPF FeatureCollection
    lpf_output = {
        "type": "FeatureCollection",
        "@context": LPF_CONTEXT,
        "features": lpf_features
    }

    # Write output
    print(f"\n4. Writing {OUTPUT_FILE.name}...")
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(lpf_output, f, indent=2, ensure_ascii=False)

    # Summary stats
    print("\n" + "=" * 50)
    print("SUMMARY")
    print("=" * 50)
    print(f"Input features:  {len(features)}")
    print(f"Output features: {len(lpf_features)}")
    print(f"Conflated:       {len(features)} → {len(lpf_features)} polities")

    # Count by @id type
    seshat_count = sum(1 for f in lpf_features if f['@id'].startswith('https://seshat'))
    wp_count = sum(1 for f in lpf_features if f['@id'].startswith('wp:'))
    other_count = len(lpf_features) - seshat_count - wp_count

    print(f"\n@id breakdown:")
    print(f"  Seshat URLs: {seshat_count}")
    print(f"  wp: prefix:  {wp_count}")
    print(f"  Other:       {other_count}")

    # Geometry stats
    geom_counts = [len(f['geometry']['geometries']) for f in lpf_features]
    print(f"\nGeometries per polity:")
    print(f"  Min: {min(geom_counts)}")
    print(f"  Max: {max(geom_counts)}")
    print(f"  Avg: {sum(geom_counts) / len(geom_counts):.1f}")

    print(f"\nOutput: {OUTPUT_FILE}")
    print("Done!")


if __name__ == "__main__":
    transform()
