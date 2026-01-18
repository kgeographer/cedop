#!/usr/bin/env python3
"""
EXPLORATORY: Compute correlations between basin08 variables and D-PLACE cultural variables.

NOTE: This script uses a hand-picked subset of basin08 variables for exploratory analysis.
For correlations using EDOP's curated signature fields, use dplace_env_correlations_signature.py

For each cultural variable (categorical), computes mean environmental values per category
and tests for significant differences using ANOVA F-statistic.

Usage:
    python scripts/dplace_env_correlations_exploratory.py [--min-societies N] [--output FILE]

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

# EXPLORATORY: Hand-picked basin08 variables (not the EDOP signature)
# Chosen for interpretability in environment-culture analysis
ENV_FEATURES = {
    # Climate
    'tmp_dc_cyr': 'Mean annual temperature (°C × 10)',
    'pre_mm_cyr': 'Annual precipitation (mm)',
    'aet_mm_cyr': 'Actual evapotranspiration (mm)',
    'ari_ix_cav': 'Aridity index',
    'cmi_ix_cyr': 'Climate moisture index',
    # Terrain
    'ele_mt_cav': 'Elevation (m)',
    'slp_dg_cav': 'Slope (degrees)',
    # Hydrology
    'dis_m3_pyr': 'River discharge (m³/year)',
    'run_mm_cyr': 'Runoff (mm/year)',
    'gwt_cm_cav': 'Groundwater table depth (cm)',
    # Soil
    'soc_th_cav': 'Soil organic carbon (tons/ha)',
    'swc_pc_cyr': 'Soil water content (%)',
    # Land cover
    'for_pc_cse': 'Forest cover (%)',
    'crp_pc_cse': 'Cropland cover (%)',
    'pst_pc_cse': 'Pasture cover (%)',
    'urb_pc_cse': 'Urban cover (%)',
    # Population
    'pop_ct_csu': 'Population count (upstream)',
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


def load_society_env_data(conn):
    """Load societies with environmental features directly from basin08."""
    env_cols = ', '.join([f'b.{col}' for col in ENV_FEATURES.keys()])
    query = f"""
        SELECT
            s.id as soc_id,
            s.name as society,
            s.region,
            {env_cols}
        FROM gaz.dplace_societies s
        JOIN public.basin08 b ON b.hybas_id = s.basin_id
        WHERE s.basin_id IS NOT NULL
    """
    return pd.read_sql(query, conn)


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


def compute_correlations(env_df, culture_df, env_features, min_societies=10):
    """
    For each cultural variable, compute ANOVA F-statistic for each env feature.
    Returns DataFrame of (cultural_var, env_feature, F_stat, p_value, effect_size).
    """
    results = []

    # Merge env and culture data
    merged = culture_df.merge(env_df, on='soc_id')

    # Get unique cultural variables
    cultural_vars = merged['var_id'].unique()
    env_cols = [c for c in env_df.columns if c in env_features]

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
                    'cultural_var_id': var_id,
                    'cultural_var': var_name,
                    'env_feature': env_col,
                    'env_description': env_features.get(env_col, env_col),
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


def summarize_top_correlations(results_df, top_n=20):
    """Print summary of strongest environment-culture relationships."""
    # Filter significant results and sort by effect size
    sig_results = results_df[results_df['p_value'] < 0.001].copy()
    sig_results = sig_results.sort_values('eta_squared', ascending=False)

    print(f"\n{'='*80}")
    print(f"TOP {top_n} ENVIRONMENT-CULTURE CORRELATIONS (p < 0.001)")
    print(f"NOTE: Using EXPLORATORY basin08 variables, not EDOP signature fields")
    print(f"{'='*80}\n")

    for i, row in sig_results.head(top_n).iterrows():
        print(f"{row['cultural_var']}")
        print(f"  vs {row['env_description']}")
        print(f"  Effect size (η²): {row['eta_squared']:.3f}  |  F: {row['f_stat']:.1f}  |  p: {row['p_value']:.2e}")
        print(f"  Categories: {row['n_categories']}  |  Societies: {row['n_societies']}")

        # Show category means
        means = row['category_means']
        sorted_means = sorted(means.items(), key=lambda x: x[1])
        print(f"  Range: {sorted_means[0][0]} ({sorted_means[0][1]:.1f}) → {sorted_means[-1][0]} ({sorted_means[-1][1]:.1f})")
        print()

    return sig_results.head(top_n)


def main():
    parser = argparse.ArgumentParser(description="Compute environment-culture correlations (EXPLORATORY)")
    parser.add_argument("--min-societies", type=int, default=10,
                       help="Minimum societies per category (default: 10)")
    parser.add_argument("--output", type=str, default="output/dplace_correlations_exploratory.csv",
                       help="Output CSV file")
    args = parser.parse_args()

    print("="*60)
    print("EXPLORATORY ANALYSIS: Using hand-picked basin08 variables")
    print("For EDOP signature analysis, use dplace_env_correlations_signature.py")
    print("="*60)

    print("\nConnecting to database...")
    conn = get_connection()

    print("Loading environmental data for societies...")
    env_df = load_society_env_data(conn)
    print(f"  Loaded {len(env_df)} societies with basin data")

    print("Loading cultural variable data...")
    culture_df = load_cultural_data(conn, CULTURAL_VARS)
    print(f"  Loaded {len(culture_df)} cultural observations")

    conn.close()

    print(f"\nComputing correlations (min {args.min_societies} societies per category)...")
    results = compute_correlations(env_df, culture_df, ENV_FEATURES, min_societies=args.min_societies)
    print(f"  Computed {len(results)} variable pairs")

    # Summarize top results
    top_results = summarize_top_correlations(results)

    # Save full results
    os.makedirs(os.path.dirname(args.output), exist_ok=True)
    results.to_csv(args.output, index=False)
    print(f"\nFull results saved to {args.output}")


if __name__ == "__main__":
    main()
