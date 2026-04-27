# Session Log — 26 April 2026

## Overview

Continued Band T characterization on branch `explore02`. Completed Task 5b (L6 k-means clustering) as prerequisite for Task 9 stratified sampling, then completed Task 9 (HYDE basin aggregation and s/u characterization). Findings F9.1–F9.7 logged.

## Task 5b — L6 k-means clustering

Notebook: `notebooks/edop/explore/05_preclustering.ipynb` (cells 12–17 added)
Output: `output/edop/explore/05_cluster_assignments_L6.csv` (16,397 rows), `05_kmeans_cluster_summary_L6.csv`, `05b_kmeans_global_map_L6.png`

- Applied same 20-variable Band A+B+C k-means as L8 (Task 5), reusing the L8-fitted scaler on L6 data
- L6 clusters are geographically dispersed vs L8's spatially coherent clusters — logged as F5.7
- Implication for CDOP: L6 is better suited for cross-regional correspondence work; L8 captures local environmental coherence

## Task 9 — HYDE basin aggregation and s/u characterization

Notebook: `notebooks/edop/explore/09_hyde_basin_aggregation.ipynb`
Detailed findings: `logs/exploration_log.md` F9.1–F9.7
Outputs: `output/edop/explore/09_hyde_su_L8.csv`, `09_hyde_su_L6.csv`, `09_aggregation_comparison_L8.csv`, `09_aggregation_comparison.png`, `09_su_divergence_summary.csv`, `09_su_divergence_distributions.png`, `09_cropland_crosscheck.png`, `09_ref_site_static_vs_hyde.csv`

High-level results:

- **Aggregation**: polygon-interior confirmed over centroid; diverge meaningfully above ~100 km² sub_area. 8% of L8 basins too small for interior cells, centroid fallback acceptable (F9.1)
- **s values**: heavy zeros for cropland through 1000 CE; grazing more extensive than cropland at all epochs, 32× growth 1000 BCE → 2000 CE vs cropland 18×. Grazing expansion driven by colonial-era pastoral transformation, not industrialization (F9.2)
- **L6 vs L8**: L6 medians substantially higher — larger polygons capture more agricultural fringe. The two levels answer different questions (F9.3, consistent with F5.7)
- **s/u divergence**: dramatically wider than climate divergence (p95 reaches +5.52 log₂ vs climate p95 +0.39); effective N only 8–21% of sample due to headwaters + zero land use. Negative cropland median = local IS the agricultural concentration; positive tail = downstream receiver of upstream surplus. Both historically meaningful configurations (F9.4)
- **Divergence collapse**: by 2000 CE distributions converge toward zero — land use too uniform to discriminate. Most analytically productive window: 0–1000 CE (F9.5)
- **EarthStat vs HYDE cross-check**: globally agree (~15M km² each) but spatially diverge at sub-basin scale. Not a HYDE calibration failure — spatial allocation uncertainty in agricultural hotspots. Ur 3× gap (60% EarthStat vs 18% HYDE at 2000 CE) is the clearest case. Flagged for October expert meeting (F9.6)
- **Reference site trajectories**: historically legible — Kaifeng Han dynasty peak at 1 CE (175 km²), Ur consistent ancient signal, Timbuktu near-zero throughout. HYDE signal is real and discriminating (F9.7)

## Key design decisions confirmed

- HYDE variables for Band T: cropland and grazing_land only (urban_area, total_rice, population_density excluded per F8.3/F8.6)
- Baseline epoch: 1000 BCE (per F8.7)
- s/u divergence field most useful for pre-industrial queries; caveat needed for 2000 CE baseline
- Band D (EarthStat static) and Band T (HYDE temporal) are non-redundant and not interchangeable

## Open questions flagged for October 2026 expert meeting

- F8.5: Band C climate fields are silently wrong for BCE queries (WorldClim is contemporary)
- F8.6: population density may not belong in an environmental signature
- F9.6: EarthStat/HYDE spatial divergence at agricultural hotspot sub-basins

## Task 10 — LMR v2.1 temporal/spatial structure and grid behaviour

Notebook: `notebooks/edop/explore/10_lmr_structure.ipynb`
Detailed findings: `logs/exploration_log.md` F10.1–F10.5
Outputs: `output/edop/explore/10_*.csv` + `10_*.png` (7 files)

Downloaded spread files + nhmt/gmt before starting. Key structural discoveries:

- **File structure**: `(time=2001, MCrun=20, lat=91, lon=180)` — mean files retain full MCrun dimension; "ensemble mean" requires averaging over axis=1. Values are anomalies from model prior, not absolute values. Coverage 0–1998 CE.
- **Grid**: 16,380 cells at 2°×2°, values at all cells including ocean. Lon runs 0–358 (not −180/180) — convert for DB queries.
- **Funnel effect**: all variables show compressed variance in early centuries (0–500 CE), expanding through the record — regression to prior when proxies are sparse. Not a climate signal; a data-quality signature. Reconstruction most reliable ~700–1900 CE (F10.1)
- **Variance decomposition**: temporal variance dominates geographic for all three variables — PDSI 76% temporal, temperature 68%, precipitation 93%. LMR is genuinely time-dependent; Band C and Band T are non-redundant (F10.2)
- **Uncertainty**: within-run spread dominates across-run std by ~4.6×. Spread only 1.13× higher in early vs late period — spread alone won't flag sparse-proxy epochs; explicit caveat needed (F10.3)
- **Band C coherence**: Spearman r ≈ 0 for both temperature and precipitation — the two datasets are orthogonal, as expected. 1850–1900 window is slightly LIA-cool relative to 2000-yr mean (median −0.05 K) (F10.4)
- **L8→LMR mapping**: 190,675 basins → 4,999 cells; median 39 basins per cell, p95 74, max 109. Spatial precision ceiling ~200 km — LMR is a regional signal, not local (F10.5)

## Key design decisions from Task 10

- LMR API fields: grand mean (mean over 20 MCruns) + within-run spread as uncertainty
- All LMR variables are anomalies — label clearly in API, never imply absolute values
- Epoch caveat threshold: flag pre-~700 CE as "reduced reconstruction fidelity"
- 2°×2° resolution note required in API docs

## Up next — Task 11 (start of next session)

**Branch**: `explore02`

**Task 11**: LMR period and event fingerprints (`notebooks/edop/explore/11_lmr_periods_volcanics.ipynb`)
- Test whether MCA (~950–1250 CE) and LIA (~1300–1850 CE) appear as detectable anomalies at appropriate NH locations
- Volcanic response: extract LMR temperature at lag 0–3 years post-eruption for largest eVolv2k events
- Establish baseline-window convention for Band T anomaly reporting
- nhmt/gmt full-ensemble files available for hemisphere-level response curves
