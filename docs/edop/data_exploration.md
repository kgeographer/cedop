# EDOPS Data Exploration Phase

## Purpose

Before reasoning about signatures in aggregate — before PCA, clustering, correspondence testing, or rubric design — a systematic characterization of the EDOPS signature dataset itself is required. This document defines the scope, task list, conventions, and guardrails for that work.

The exploration phase produces working knowledge and documented findings, not deliverables. Its output is the `logs/exploration_log.md` file and the scripts/notebooks in `scripts/edop/explore/` and `notebooks/edop/explore/`. These accrete over time and will be critical source material for any methodology document or paper.

---

## Task List

### 1. Marginal distributions — all scalar variables, globally

For every scalar variable in the L8 signature, compute the global distribution across all 190,075 sub-basins. Produce histograms (and summary statistics: mean, median, std, min, max, skew, % zero/null). Variables include at minimum:

- **Band A**: `elev_min`, `elev_max`, `slope_avg`, `slope_upstream`, `stream_gradient`, `karst`, `karst_upstream`
- **Band B**: `discharge_yr`, `discharge_min`, `discharge_max`, `runoff`, `river_area`, `river_area_upstream`, `gw_table_depth`, `pct_clay`, `pct_silt`, `pct_sand`, `wet_pct_grp1`, `wet_pct_grp2`, `reservoir_vol`
- **Band C**: `temp_yr`, `temp_min`, `temp_max`, `temp_yr_upstream`, `precip_yr`, `precip_yr_upstream`, `aridity`, `aridity_upstream`, `permafrost_extent`
- **Band D**: `pop_density`, `human_footprint_09`, `human_footprint_09_upstream`, `cropland_extent`, `cropland_extent_upstream`, `gdp_avg`, `human_dev_idx`
- **Band E**: `dist_sink`

Goal: identify which variables are informative (heavy-tailed, multimodal) vs. effectively constant or degenerate (near-zero mass, most basins null). This determines which variables to foreground in any rubric or dimensionality reduction.

### 2. Missing-data and degenerate-value patterns

For every variable, compute: % null, % zero, % at floor/ceiling values. Cross-tabulate by basin level (L8 vs. L6) to identify where variables systematically degrade at coarser resolution. Document scale-sensitivity patterns — e.g. `slope_avg` near-zero at L6 even in topographically complex terrain is a known issue; the goal is to characterize this globally.

### 3. Local/upstream divergence distribution

For every variable with both a local (`_s`) and upstream (`_u`) value, compute the distribution of divergence globally:
- Ratio `u/s` where meaningful (aridity, precip, temp)
- Difference `u - s` where ratio is unstable (near-zero denominators)

Key questions:
- Where does the Ur case (aridity divergence ~320%) sit in the global distribution — 95th percentile? 99th?
- Is strong divergence rare (a specific environmental signal) or common (a generic feature of the dataset)?
- Which variable pairs show the strongest divergence globally? Which show the least?

This is the quantitative foundation for the claim that the s/u duality is a contribution, not a data-processing choice.

### 4. Correlation structure within and across bands

Compute a full correlation matrix across all scalar variables globally at L8. Identify:
- Redundant pairs (r > 0.9) — candidates for exclusion from dimensionality reduction
- Constrained variables (e.g. `pct_clay + pct_silt + pct_sand ≈ 1`)
- Cross-band correlations — where does environmental structure cut across band boundaries?

This gives variable-selection leverage for PCA/factor work and identifies which variables are genuinely independent signals.

### 5. Geographic-type pre-clustering

Run unsupervised clustering (k-means and/or HDBSCAN) on L8 basins using Band A+B+C scalar variables (after handling nulls and scaling). Produce:
- A global map of cluster assignments
- Summary statistics per cluster
- Comparison with the existing 20-cluster result from the workbench (which used bands A–D)

Goal: establish a working typology of environmental basin types that can situate any individual signature — "this is an arid-continental-interior basin like X thousand others" vs. "this is an unusual coastal-arid combination." This situating capability is what turns a raw signature into interpretable output.

---

## What NOT to Do During Exploration

**Do not generalize from individual cases before global distributions are in hand.** Timbuktu and Kaifeng are diagnostic, not representative. They were chosen because they are distinctive. Extending from two worked cases to "here's what signatures tend to say" is seductive and tends to be wrong. Interpret individual cases against global distributions, not against each other.

**Do not let validation pull on exploration.** D-PLACE correspondence testing is a separate phase. If variable selection starts being tuned against what produces good D-PLACE correlations, the work has quietly moved from instrument characterization into optimization-against-cultural-target. Keep the phases sequential.

**Do not conflate L8 and L6 findings.** Scale-sensitivity is itself a finding. Document distributions separately at each level; do not mix.

---

## Band F Note

The F-band returns three full annual series (`pdsi_series`, `air_series`, `prate_series`) plus summary statistics and volcanic events. For individual place-period queries this is appropriate. For batch characterization across thousands of locations, the annual arrays are heavy. A lightweight F-band mode returning only means and ranges (no annual arrays) would make exploration tractable. Consider adding `?bands=F&detail=summary` or similar to the API before the exploration batch runs begin.

---

## Directory Conventions

```
scripts/edop/explore/     # Exploration scripts (Python)
notebooks/edop/explore/   # Exploration notebooks
output/edop/explore/      # Exploration outputs (gitignored)
logs/exploration_log.md   # Accreting findings log (see below)
```

Each exploration script or notebook should be named descriptively:
- `01_marginal_distributions.py`
- `02_missing_data.py`
- `03_su_divergence.py`
- `04_correlation_matrix.py`
- `05_preclustering.py`

---

## Exploration Log

`logs/exploration_log.md` is a running record of findings, not a daily work log. Each entry records:
- **Date**
- **Task** (which item from the list above)
- **Method** (script/notebook, key parameters)
- **Finding** (what was learned — the substantive result)
- **Implication** (what this changes about how we understand or use the signature)

This log is the raw material for the methodology section of any future paper. Write to it after each meaningful finding, not at the end of a session.
