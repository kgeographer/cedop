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

## Up next — Task 10 (start of next session)

**Branch**: `explore02`

**Task 10**: LMR v2.1 structure and coverage (`notebooks/edop/explore/10_lmr_structure.ipynb`)
- Characterize the LMR v2.1 reconstruction: variables (PDSI, Tmean, Pmean), spatial grid, temporal coverage (0–1998 CE), ensemble structure
- Establish what the API actually delivers vs what the NetCDF contains
- Key question: does LMR spatial resolution cause meaningful location-sensitivity for sub-basin queries, and how does the 0 CE start interact with HYDE's earlier coverage?
