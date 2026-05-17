#!/usr/bin/env python3
"""
scripts/edop/explore/12_spatial_moran.py

Univariate spatial characterisation sweep — Bands A-D at L6 and L8.

For each (variable, scale): distributional summary, global Moran's I (raw + log),
LISA classification, summary statistics. Outputs:

  spatial/variable_characterization.csv        — one row per (variable, scale); committed
  output/edop/explore/lisa_classifications.parquet  — long format per basin; gitignored

Checkpointed: rows already in variable_characterization.csv are skipped on resume.
LISA staging files are written per (variable, scale) to output/edop/explore/lisa_staging/
and merged to the final parquet when the sweep completes.

Usage:
  python scripts/edop/explore/12_spatial_moran.py
  python scripts/edop/explore/12_spatial_moran.py --l6-only
  python scripts/edop/explore/12_spatial_moran.py --l8-only
  python scripts/edop/explore/12_spatial_moran.py --merge-only   # merge staging → parquet
"""
import argparse
import sys
import time
import warnings
from pathlib import Path

import numpy as np
import pandas as pd
import geopandas as gpd
from shapely import wkt

sys.path.insert(0, str(Path(__file__).parents[3]))
from scripts.shared.db_utils import db_connect

from libpysal.weights import Queen
from esda.moran import Moran, Moran_Local

# ── paths ──────────────────────────────────────────────────────────────────────
REPO      = Path(__file__).parents[3]
CSV_OUT   = REPO / 'spatial' / 'variable_characterization.csv'
PARQ_OUT  = REPO / 'output' / 'edop' / 'esda' / 'lisa_classifications.parquet'
STAGING   = REPO / 'output' / 'edop' / 'esda' / 'lisa_staging'

# ── constants ──────────────────────────────────────────────────────────────────
SEED              = 42
PERMUTATIONS      = 999
SIGNIFICANCE      = 0.05
LOG_SKEW_THRESHOLD = 5.0
QUAD_MAP          = {1: 'HH', 2: 'LH', 3: 'LL', 4: 'HL'}

SCALES = {
    'L6': 'basin06',
    'L8': 'basin08',
}

# ── variable registry ──────────────────────────────────────────────────────────
# scale_factor: applied on load (tmp_dc_* stored ×10 in BasinATLAS)
VARIABLES = [
    # Band A — Elevation / Terrain / Geology
    dict(col='ele_mt_sav', schema_key='elevation_mean',        friendly='Mean elevation',           band='A'),
    dict(col='ele_mt_smn', schema_key='elevation_min',         friendly='Elevation minimum',         band='A'),
    dict(col='ele_mt_smx', schema_key='elevation_max',         friendly='Elevation maximum',         band='A'),
    dict(col='slp_dg_sav', schema_key='slope_deg',             friendly='Slope',                     band='A'),
    dict(col='sgr_dk_sav', schema_key='stream_gradient',       friendly='Stream gradient',           band='A'),
    dict(col='kar_pc_sse', schema_key='karst_pct',             friendly='Karst %',                   band='A'),
    dict(col='gla_pc_sse', schema_key='glacier_pct',           friendly='Glacier %',                 band='A'),
    dict(col='ero_kh_sav', schema_key='erosion_rate',          friendly='Erosion rate',              band='A'),
    # Band B — Discharge / Hydrology / Soils
    dict(col='dis_m3_pyr', schema_key='discharge_annual',      friendly='Discharge annual',          band='B'),
    dict(col='dis_m3_pmn', schema_key='discharge_min',         friendly='Discharge monthly min',     band='B'),
    dict(col='dis_m3_pmx', schema_key='discharge_max',         friendly='Discharge monthly max',     band='B'),
    dict(col='run_mm_syr', schema_key='runoff',                friendly='Annual runoff',             band='B'),
    dict(col='gwt_cm_sav', schema_key='groundwater_depth',     friendly='Groundwater depth',         band='B'),
    dict(col='swc_pc_syr', schema_key='soil_water_content',    friendly='Soil water content',        band='B'),
    dict(col='ria_ha_ssu', schema_key='river_area',            friendly='River area (local)',        band='B'),
    dict(col='wet_pc_sg1', schema_key='wetland_pct_g1',        friendly='Wetland % group 1',         band='B'),
    dict(col='wet_pc_sg2', schema_key='wetland_pct_g2',        friendly='Wetland % group 2',         band='B'),
    dict(col='lka_pc_sse', schema_key='lake_area_pct',         friendly='Lake area %',               band='B'),
    dict(col='inu_pc_smx', schema_key='inundation_max',        friendly='Inundation max',            band='B'),
    dict(col='dor_pc_pva', schema_key='degree_of_regulation',  friendly='Degree of regulation',      band='B'),
    dict(col='cly_pc_sav', schema_key='pct_clay',              friendly='Clay %',                    band='B'),
    dict(col='slt_pc_sav', schema_key='pct_silt',              friendly='Silt %',                    band='B'),
    dict(col='snd_pc_sav', schema_key='pct_sand',              friendly='Sand %',                    band='B'),
    dict(col='soc_th_sav', schema_key='soil_organic_carbon',   friendly='Soil organic carbon',       band='B'),
    # Band C — Climate / Cryosphere / Vegetation
    dict(col='tmp_dc_syr', schema_key='temperature_annual',    friendly='Temperature annual',        band='C', scale_factor=0.1),
    dict(col='pre_mm_syr', schema_key='precipitation_annual',  friendly='Precipitation annual',      band='C'),
    dict(col='pet_mm_syr', schema_key='pet_annual',            friendly='PET annual',                band='C'),
    dict(col='aet_mm_syr', schema_key='aet_annual',            friendly='AET annual',                band='C'),
    dict(col='ari_ix_sav', schema_key='aridity_index',         friendly='Aridity index',             band='C'),
    dict(col='cmi_ix_syr', schema_key='climate_moisture_index',friendly='Climate moisture index',    band='C'),
    dict(col='prm_pc_sse', schema_key='permafrost_pct',        friendly='Permafrost %',              band='C'),
    dict(col='snw_pc_syr', schema_key='snow_cover_annual',     friendly='Snow cover annual',         band='C'),
    dict(col='for_pc_sse', schema_key='forest_cover_pct',      friendly='Forest cover %',            band='C'),
    # Band D — Land use / Human presence
    dict(col='crp_pc_sse', schema_key='cropland_pct',          friendly='Cropland %',                band='D'),
    dict(col='pst_pc_sse', schema_key='pasture_pct',           friendly='Pasture %',                 band='D'),
    dict(col='ppd_pk_sav', schema_key='pop_density',           friendly='Population density',        band='D'),
    dict(col='hft_ix_s09', schema_key='human_footprint_2009',  friendly='Human footprint 2009',      band='D'),
    dict(col='gdp_ud_sav', schema_key='gdp_mean',              friendly='GDP mean',                  band='D'),
    dict(col='hdi_ix_sav', schema_key='hdi',                   friendly='HDI',                       band='D'),
    dict(col='nli_ix_sav', schema_key='nighttime_lights',      friendly='Nighttime lights',          band='D'),
]


# ── helpers ────────────────────────────────────────────────────────────────────
def elapsed(t0, label=''):
    m, s = divmod(time.time() - t0, 60)
    print(f'  {label}  [{int(m)}m {s:.0f}s]')


def load_gdf(scale_key):
    """Load basin geometry + all variable columns for one scale."""
    table = SCALES[scale_key]
    var_cols = [v['col'] for v in VARIABLES]
    cols_sql = ', '.join(var_cols)
    sql = f"SELECT hybas_id, ST_AsText(geom) AS geom_wkt, {cols_sql} FROM public.{table} ORDER BY hybas_id"

    t0 = time.time()
    conn = db_connect()
    with conn.cursor() as cur:
        cur.execute(sql)
        rows = cur.fetchall()
    conn.close()
    elapsed(t0, f'{scale_key} fetch')

    col_names = ['hybas_id', 'geom_wkt'] + var_cols
    df = pd.DataFrame(rows, columns=col_names)
    df['geometry'] = df['geom_wkt'].apply(wkt.loads)
    df = df.drop(columns='geom_wkt')
    gdf = gpd.GeoDataFrame(df, geometry='geometry', crs='EPSG:4326').set_index('hybas_id')
    print(f'  {len(gdf):,} basins loaded')
    return gdf


def build_weights(gdf, scale_key):
    print(f'  Building queen weights {scale_key} ({len(gdf):,} basins)...')
    t0 = time.time()
    w = Queen.from_dataframe(gdf, use_index=True, silence_warnings=True)
    w.transform = 'r'
    elapsed(t0, f'{scale_key} weights')
    print(f'  n={w.n:,}  mean neighbours={w.mean_neighbors:.2f}')
    return w


NODATA = -9999  # BasinATLAS NoData sentinel


def prepare_values(gdf, var_meta):
    """
    Extract values array aligned with the full GDF index (no missing rows).
    BasinATLAS -9999 sentinels are masked as NaN before any computation.
    Missing/sentinel values are imputed with the column mean so the array
    aligns with the pre-built weights matrix. Returns (values_raw, missing_pct).
    """
    scale_factor = var_meta.get('scale_factor', 1.0)
    vals = gdf[var_meta['col']].values.astype(float)

    # Mask BasinATLAS NoData sentinel before scaling
    vals[vals == NODATA] = np.nan

    if scale_factor != 1.0:
        vals = vals * scale_factor

    nan_mask = np.isnan(vals)
    missing_pct = nan_mask.mean() * 100
    if nan_mask.any():
        vals[nan_mask] = np.nanmean(vals)

    return vals, missing_pct


def distributional_summary(vals_raw):
    s = pd.Series(vals_raw)
    return dict(
        mean=float(np.mean(vals_raw)),
        median=float(np.median(vals_raw)),
        std=float(np.std(vals_raw)),
        min=float(np.min(vals_raw)),
        max=float(np.max(vals_raw)),
        skewness=float(s.skew()),
        kurtosis=float(s.kurtosis()),
        zero_fraction=float((vals_raw == 0).mean()),
    )


def global_moran(vals, w):
    with warnings.catch_warnings():
        warnings.simplefilter('ignore')
        np.random.seed(SEED)
        mi_raw = Moran(vals, w, permutations=PERMUTATIONS)
        vals_log = np.log1p(np.clip(vals, 0, None))
        np.random.seed(SEED)
        mi_log = Moran(vals_log, w, permutations=PERMUTATIONS)
    return mi_raw, mi_log, vals_log


def local_moran(canonical_vals, w):
    with warnings.catch_warnings():
        warnings.simplefilter('ignore')
        np.random.seed(SEED)
        lisa = Moran_Local(canonical_vals, w, permutations=PERMUTATIONS)
    labels = np.where(
        lisa.p_sim < SIGNIFICANCE,
        np.array([QUAD_MAP[q] for q in lisa.q]),
        'NS'
    )
    return lisa, labels


def characterize(var_meta, gdf, w, scale_key):
    col = var_meta['col']
    vals_raw, missing_pct = prepare_values(gdf, var_meta)
    dist = distributional_summary(vals_raw)
    dist['missing_pct'] = missing_pct
    dist['n_basins'] = len(vals_raw)

    # Log transform if right-skewed and non-negative
    log_transformed = (dist['skewness'] > LOG_SKEW_THRESHOLD) and (dist['min'] >= 0)

    t0 = time.time()
    mi_raw, mi_log, vals_log = global_moran(vals_raw, w)
    elapsed(t0, 'Moran I')

    canonical = vals_log if log_transformed else vals_raw
    I_canonical = mi_log.I if log_transformed else mi_raw.I

    t0 = time.time()
    lisa, labels = local_moran(canonical, w)
    elapsed(t0, 'LISA')

    n = len(labels)
    counts = pd.Series(labels).value_counts().reindex(['HH', 'LL', 'HL', 'LH', 'NS'], fill_value=0)

    row = dict(
        variable=col,
        schema_key=var_meta['schema_key'],
        friendly_name=var_meta['friendly'],
        band=var_meta['band'],
        scale=scale_key,
        **dist,
        log_transformed=log_transformed,
        I_raw=round(mi_raw.I, 6),
        I_log=round(mi_log.I, 6),
        I_canonical=round(I_canonical, 6),
        p_value=mi_log.p_sim if log_transformed else mi_raw.p_sim,
        z_score=round(mi_log.z_sim if log_transformed else mi_raw.z_sim, 4),
        n_HH=int(counts['HH']),  pct_HH=round(counts['HH'] / n * 100, 2),
        n_LL=int(counts['LL']),  pct_LL=round(counts['LL'] / n * 100, 2),
        n_HL=int(counts['HL']),  pct_HL=round(counts['HL'] / n * 100, 2),
        n_LH=int(counts['LH']),  pct_LH=round(counts['LH'] / n * 100, 2),
        n_NS=int(counts['NS']),  pct_NS=round(counts['NS'] / n * 100, 2),
        cluster_core_pct=round((counts['HH'] + counts['LL']) / n * 100, 2),
        outlier_pct=round((counts['HL'] + counts['LH']) / n * 100, 2),
        seed=SEED,
        n_permutations=PERMUTATIONS,
    )

    lisa_df = pd.DataFrame({
        'variable':   col,
        'scale':      scale_key,
        'hybas_id':   gdf.index.values,
        'lisa_class': labels,
        'p_value':    lisa.p_sim,
        'local_I':    lisa.Is,
        'quad':       lisa.q,
    })

    return row, lisa_df


# ── checkpointing ──────────────────────────────────────────────────────────────
def load_done():
    if CSV_OUT.exists():
        df = pd.read_csv(CSV_OUT)
        return set(zip(df['variable'], df['scale']))
    return set()


def append_csv(row):
    df_row = pd.DataFrame([row])
    if CSV_OUT.exists():
        df_row.to_csv(CSV_OUT, mode='a', header=False, index=False)
    else:
        df_row.to_csv(CSV_OUT, index=False)


def save_staging(lisa_df, col, scale_key):
    STAGING.mkdir(parents=True, exist_ok=True)
    lisa_df.to_parquet(STAGING / f'{col}_{scale_key}.parquet', index=False)


def merge_staging():
    files = sorted(STAGING.glob('*.parquet'))
    if not files:
        print('No staging files to merge.')
        return
    merged = pd.concat([pd.read_parquet(f) for f in files], ignore_index=True)
    PARQ_OUT.parent.mkdir(parents=True, exist_ok=True)
    merged.to_parquet(PARQ_OUT, index=False)
    print(f'\nLISA parquet → {PARQ_OUT}  ({len(merged):,} rows)')
    for f in files:
        f.unlink()
    STAGING.rmdir()


# ── summary table ──────────────────────────────────────────────────────────────
def print_summary():
    if not CSV_OUT.exists():
        return
    df = pd.read_csv(CSV_OUT)
    pivot = df.pivot_table(
        index=['band', 'variable', 'friendly_name'],
        columns='scale',
        values=['I_canonical', 'cluster_core_pct', 'outlier_pct']
    )
    pivot.columns = [f'{v}_{s}' for v, s in pivot.columns]
    pivot = pivot.reset_index()
    if 'I_canonical_L8' in pivot.columns and 'I_canonical_L6' in pivot.columns:
        pivot['scale_dir'] = np.sign(pivot['I_canonical_L8'] - pivot['I_canonical_L6']).map(
            {1.0: '↑', -1.0: '↓', 0.0: '='}
        )
    print('\n\n' + '='*90)
    print('Phase 1 summary — I_canonical by variable and scale')
    print('='*90)
    cols = ['band', 'variable', 'friendly_name']
    for c in ['I_canonical_L6', 'I_canonical_L8', 'scale_dir',
              'cluster_core_pct_L6', 'outlier_pct_L6']:
        if c in pivot.columns:
            cols.append(c)
    print(pivot[cols].sort_values(['band', 'I_canonical_L6'], ascending=[True, False]).to_string(index=False))


# ── main ───────────────────────────────────────────────────────────────────────
def check_dependencies():
    """Fail fast if required packages are missing before any work starts."""
    missing = []
    try:
        import pyarrow  # noqa: F401
    except ImportError:
        missing.append('pyarrow  →  pip install pyarrow')
    if missing:
        print('ERROR: missing required dependencies:\n  ' + '\n  '.join(missing))
        sys.exit(1)


def main():
    check_dependencies()

    parser = argparse.ArgumentParser()
    parser.add_argument('--l6-only',    action='store_true')
    parser.add_argument('--l8-only',    action='store_true')
    parser.add_argument('--merge-only', action='store_true',
                        help='Skip sweep; just merge existing staging files to parquet')
    args = parser.parse_args()

    if args.merge_only:
        merge_staging()
        return

    scales = ['L6', 'L8']
    if args.l6_only:
        scales = ['L6']
    elif args.l8_only:
        scales = ['L8']

    done = load_done()
    print(f'Checkpoint: {len(done)} (variable, scale) pairs already complete.')
    print(f'Variables: {len(VARIABLES)}  ·  Scales: {scales}  ·  Total target: {len(VARIABLES)*len(scales)}')

    for scale_key in scales:
        pending = [v for v in VARIABLES if (v['col'], scale_key) not in done]
        if not pending:
            print(f'\n{scale_key}: all {len(VARIABLES)} variables already done, skipping.')
            continue

        print(f'\n{"="*70}')
        print(f'Scale: {scale_key}  —  {len(pending)} variables to run')
        print('='*70)

        gdf = load_gdf(scale_key)
        w   = build_weights(gdf, scale_key)

        for i, var_meta in enumerate(pending, 1):
            col = var_meta['col']
            print(f'\n[{i}/{len(pending)}] {col}  ({var_meta["friendly"]}, Band {var_meta["band"]})')
            t0 = time.time()
            try:
                row, lisa_df = characterize(var_meta, gdf, w, scale_key)
                save_staging(lisa_df, col, scale_key)  # staging first — CSV is the checkpoint
                append_csv(row)
                elapsed(t0, 'variable total')
                print(f'  I_canonical={row["I_canonical"]:.4f}  log={row["log_transformed"]}'
                      f'  HH={row["pct_HH"]:.1f}%  LL={row["pct_LL"]:.1f}%'
                      f'  HL={row["pct_HL"]:.1f}%  LH={row["pct_LH"]:.1f}%'
                      f'  NS={row["pct_NS"]:.1f}%')
            except Exception as exc:
                print(f'  ERROR: {exc}')

    merge_staging()
    print_summary()


if __name__ == '__main__':
    main()
