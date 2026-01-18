#!/usr/bin/env python3
"""
SIGNATURE-BASED: Compute correlations between EDOP signature fields and D-PLACE cultural variables.

Uses the curated 47 signature fields from v_basin08_persist, organized by persistence band:
  A: Physiographic bedrock (geological timescale)
  B: Hydro-climatic baselines (centuries to millennia)
  C: Bioclimatic proxies (decades to centuries)
  D: Anthropocene markers (recent decades)

Band differentiation enables filtering for historical inquiry - e.g., correlations with
Band A fields reflect adaptations to deep-time environmental constraints.

Usage:
    python scripts/dplace_env_correlations_signature.py [--min-societies N] [--band X] [--output FILE]

Requires:
    pip install psycopg[binary] pandas scipy python-dotenv
"""

import argparse
import os
from dotenv import load_dotenv
import pandas as pd
import numpy as np
from scipy import stats

load_dotenv()

DB_PARAMS = {
    "host": os.getenv("PGHOST", "localhost"),
    "port": os.getenv("PGPORT", "5435"),
    "dbname": os.getenv("PGDATABASE", "edop"),
    "user": os.getenv("PGUSER", "postgres"),
    "password": os.getenv("PGPASSWORD", ""),
}

# EDOP Signature fields organized by persistence band
# These match the fields in v_basin08_persist used by the signature API
SIGNATURE_BANDS = {
    'A': {
        'label': 'Physiographic bedrock',
        'description': 'Geological timescale - stable over millennia',
        'fields': {
            'elev_min': 'Elevation minimum (m)',
            'elev_max': 'Elevation maximum (m)',
            'slope_avg': 'Average slope (degrees)',
            'slope_upstream': 'Upstream slope (degrees)',
            'stream_gradient': 'Stream gradient',
            # lith_class, karst, karst_upstream are categorical - handle separately
        }
    },
    'B': {
        'label': 'Hydro-climatic baselines',
        'description': 'Centuries to millennia - hydrological regime',
        'fields': {
            'discharge_yr': 'Annual discharge (m³/s)',
            'discharge_min': 'Minimum discharge (m³/s)',
            'discharge_max': 'Maximum discharge (m³/s)',
            'river_area': 'River area (km²)',
            'river_area_upstream': 'Upstream river area (km²)',
            'runoff': 'Runoff (mm/yr)',
            'gw_table_depth': 'Groundwater table depth (cm)',
            'pct_clay': 'Soil clay content (%)',
            'pct_silt': 'Soil silt content (%)',
            'pct_sand': 'Soil sand content (%)',
            # pnv_majority, pnv_shares are categorical
        }
    },
    'C': {
        'label': 'Bioclimatic proxies',
        'description': 'Decades to centuries - climate patterns',
        'fields': {
            'temp_yr': 'Mean annual temperature (°C × 10)',
            'temp_min': 'Minimum temperature (°C × 10)',
            'temp_max': 'Maximum temperature (°C × 10)',
            'precip_yr': 'Annual precipitation (mm)',
            'aridity': 'Aridity index',
            'wet_pct_grp1': 'Wetland extent type 1 (%)',
            'wet_pct_grp2': 'Wetland extent type 2 (%)',
            'permafrost_extent': 'Permafrost extent (%)',
            # biome, ecoregion, freshwater_ecoregion are categorical
        }
    },
    'D': {
        'label': 'Anthropocene markers',
        'description': 'Recent decades - human modification',
        'fields': {
            'reservoir_vol': 'Reservoir volume (ML)',
            'cropland_extent': 'Cropland extent (%)',
            'pop_density': 'Population density',
            'human_footprint_09': 'Human footprint index (2009)',
            'gdp_avg': 'GDP average',
            'human_dev_idx': 'Human development index',
        }
    }
}

# Key cultural variables to analyze
CULTURAL_VARS = [
    'EA042',  # Dominant subsistence activity
    'EA028',  # Agriculture intensity
    'EA001',  # Subsistence: gathering %
    'EA002',  # Subsistence: hunting %
    'EA003',  # Subsistence: fishing %
    'EA004',  # Subsistence: animal husbandry %
    'EA005',  # Subsistence: agriculture %
    'EA040',  # Domestic animals: type
    'EA066',  # Class stratification
    'EA031',  # Settlement pattern
]


def get_connection():
    import psycopg
    return psycopg.connect(**DB_PARAMS)


def get_all_signature_fields(bands=None):
    """Get all numeric signature fields, optionally filtered by band."""
    fields = {}
    for band_code, band_info in SIGNATURE_BANDS.items():
        if bands and band_code not in bands:
            continue
        for field, desc in band_info['fields'].items():
            fields[field] = {'description': desc, 'band': band_code}
    return fields


def load_society_env_data(conn, bands=None):
    """Load societies with environmental features from v_basin08_persist."""
    fields = get_all_signature_fields(bands)
    if not fields:
        raise ValueError("No fields selected")

    field_list = ', '.join([f'v.{f}' for f in fields.keys()])
    # dplace_societies.basin_id stores hybas_id (meaningful HydroATLAS ID)
    # v_basin08_persist.id references basin08.id (serial row number)
    # So we join through basin08 to translate: hybas_id → id
    query = f"""
        SELECT
            s.id as soc_id,
            s.name as society,
            s.region,
            {field_list}
        FROM gaz.dplace_societies s
        JOIN public.basin08 b ON b.hybas_id = s.basin_id
        JOIN public.v_basin08_persist v ON v.id = b.id
        WHERE s.basin_id IS NOT NULL
    """
    return pd.read_sql(query, conn), fields


def load_cultural_data(conn, var_ids):
    """Load cultural variable values for societies."""
    var_list = "', '".join(var_ids)
    query = f"""
        SELECT
            d.soc_id,
            v.id as var_id,
            v.name as var_name,
            c.name as value
        FROM gaz.dplace_data d
        JOIN gaz.dplace_variables v ON v.id = d.var_id
        JOIN gaz.dplace_codes c ON c.id = d.code_id
        WHERE d.var_id IN ('{var_list}')
          AND c.name NOT IN ('Missing data', '')
    """
    return pd.read_sql(query, conn)


def compute_correlations(env_df, culture_df, field_info, min_societies=10):
    """
    For each cultural variable, compute ANOVA F-statistic for each env feature.
    Returns DataFrame with band attribution.
    """
    results = []

    # Merge env and culture data
    merged = culture_df.merge(env_df, on='soc_id')

    # Get unique cultural variables
    cultural_vars = merged['var_id'].unique()
    env_cols = [c for c in env_df.columns if c in field_info]

    for var_id in cultural_vars:
        var_data = merged[merged['var_id'] == var_id]
        var_name = var_data['var_name'].iloc[0]

        # Get categories with enough societies
        category_counts = var_data['value'].value_counts()
        valid_categories = category_counts[category_counts >= min_societies].index.tolist()

        if len(valid_categories) < 2:
            continue

        var_data_filtered = var_data[var_data['value'].isin(valid_categories)]

        for env_col in env_cols:
            # Skip if too many NaN values
            env_values = var_data_filtered[env_col].dropna()
            if len(env_values) < min_societies * 2:
                continue

            # Group by cultural category
            groups = [
                var_data_filtered[var_data_filtered['value'] == cat][env_col].dropna().values
                for cat in valid_categories
            ]
            groups = [g for g in groups if len(g) >= 3]

            if len(groups) < 2:
                continue

            try:
                # ANOVA
                f_stat, p_value = stats.f_oneway(*groups)

                # Effect size (eta-squared)
                all_values = np.concatenate(groups)
                grand_mean = np.mean(all_values)
                ss_between = sum(len(g) * (np.mean(g) - grand_mean)**2 for g in groups)
                ss_total = sum((v - grand_mean)**2 for v in all_values)
                eta_sq = ss_between / ss_total if ss_total > 0 else 0

                # Category means for interpretation
                cat_means = {cat: var_data_filtered[var_data_filtered['value'] == cat][env_col].mean()
                            for cat in valid_categories}

                results.append({
                    'band': field_info[env_col]['band'],
                    'band_label': SIGNATURE_BANDS[field_info[env_col]['band']]['label'],
                    'cultural_var_id': var_id,
                    'cultural_var': var_name,
                    'env_feature': env_col,
                    'env_description': field_info[env_col]['description'],
                    'n_categories': len(valid_categories),
                    'n_societies': len(var_data_filtered),
                    'f_stat': f_stat,
                    'p_value': p_value,
                    'eta_squared': eta_sq,
                    'category_means': cat_means,
                })
            except Exception as e:
                continue

    return pd.DataFrame(results)


def summarize_top_correlations(results_df, top_n=20, by_band=False):
    """Print summary of strongest environment-culture relationships."""
    # Filter significant results and sort by effect size
    sig_results = results_df[results_df['p_value'] < 0.001].copy()
    sig_results = sig_results.sort_values('eta_squared', ascending=False)

    print(f"\n{'='*80}")
    print(f"TOP {top_n} ENVIRONMENT-CULTURE CORRELATIONS (p < 0.001)")
    print(f"Using EDOP SIGNATURE fields from v_basin08_persist")
    print(f"{'='*80}\n")

    if by_band:
        for band_code in ['A', 'B', 'C', 'D']:
            band_results = sig_results[sig_results['band'] == band_code]
            if len(band_results) == 0:
                continue
            band_info = SIGNATURE_BANDS[band_code]
            print(f"\n--- BAND {band_code}: {band_info['label']} ---")
            print(f"    ({band_info['description']})\n")

            for i, row in band_results.head(5).iterrows():
                print(f"  {row['cultural_var']}")
                print(f"    vs {row['env_description']}")
                print(f"    η² = {row['eta_squared']:.3f}  |  F = {row['f_stat']:.1f}  |  n = {row['n_societies']}")
                means = row['category_means']
                sorted_means = sorted(means.items(), key=lambda x: x[1])
                print(f"    {sorted_means[0][0]} ({sorted_means[0][1]:.1f}) → {sorted_means[-1][0]} ({sorted_means[-1][1]:.1f})")
                print()
    else:
        for i, row in sig_results.head(top_n).iterrows():
            print(f"[Band {row['band']}] {row['cultural_var']}")
            print(f"  vs {row['env_description']}")
            print(f"  Effect size (η²): {row['eta_squared']:.3f}  |  F: {row['f_stat']:.1f}  |  p: {row['p_value']:.2e}")
            print(f"  Categories: {row['n_categories']}  |  Societies: {row['n_societies']}")

            means = row['category_means']
            sorted_means = sorted(means.items(), key=lambda x: x[1])
            print(f"  Range: {sorted_means[0][0]} ({sorted_means[0][1]:.1f}) → {sorted_means[-1][0]} ({sorted_means[-1][1]:.1f})")
            print()

    return sig_results


def main():
    parser = argparse.ArgumentParser(description="Compute environment-culture correlations (EDOP SIGNATURE)")
    parser.add_argument("--min-societies", type=int, default=10,
                       help="Minimum societies per category (default: 10)")
    parser.add_argument("--band", type=str, choices=['A', 'B', 'C', 'D', 'ABC', 'all'], default='all',
                       help="Filter by signature band: A, B, C, D, ABC (excludes D), or all")
    parser.add_argument("--by-band", action="store_true",
                       help="Group output by band")
    parser.add_argument("--output", type=str, default="output/dplace_correlations_signature.csv",
                       help="Output CSV file")
    args = parser.parse_args()

    if args.band == 'all':
        bands = None
    elif args.band == 'ABC':
        bands = ['A', 'B', 'C']  # Exclude Band D (Anthropocene markers)
    else:
        bands = [args.band]

    print("="*60)
    print("EDOP SIGNATURE ANALYSIS")
    print("Using curated signature fields from v_basin08_persist")
    if args.band == 'ABC':
        print("Bands A, B, C only (excluding D: Anthropocene markers)")
    elif bands:
        print(f"Filtered to Band {args.band}: {SIGNATURE_BANDS[args.band]['label']}")
    print("="*60)

    print("\nConnecting to database...")
    conn = get_connection()

    print("Loading environmental data for societies...")
    env_df, field_info = load_society_env_data(conn, bands)
    print(f"  Loaded {len(env_df)} societies with {len(field_info)} signature fields")

    print("Loading cultural variable data...")
    culture_df = load_cultural_data(conn, CULTURAL_VARS)
    print(f"  Loaded {len(culture_df)} cultural observations")

    conn.close()

    print(f"\nComputing correlations (min {args.min_societies} societies per category)...")
    results = compute_correlations(env_df, culture_df, field_info, min_societies=args.min_societies)
    print(f"  Computed {len(results)} variable pairs")

    # Summarize top results
    top_results = summarize_top_correlations(results, by_band=args.by_band)

    # Save full results
    os.makedirs(os.path.dirname(args.output), exist_ok=True)
    # Convert category_means dict to string for CSV
    results['category_means'] = results['category_means'].apply(str)
    results.to_csv(args.output, index=False)
    print(f"\nFull results saved to {args.output}")

    # Summary by band
    print("\n--- SUMMARY BY BAND ---")
    sig_results = results[results['p_value'] < 0.001]
    for band in ['A', 'B', 'C', 'D']:
        band_count = len(sig_results[sig_results['band'] == band])
        if band_count > 0:
            avg_eta = sig_results[sig_results['band'] == band]['eta_squared'].mean()
            print(f"  Band {band} ({SIGNATURE_BANDS[band]['label']}): {band_count} significant correlations, avg η² = {avg_eta:.3f}")


if __name__ == "__main__":
    main()
