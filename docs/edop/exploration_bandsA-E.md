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

**Categorical variables**: `lith_class`, `biome`, `ecoregion`, `wetland_class`, `pnv_majority`, `freshwater_ecoregion_name`, and similar fields do not take histograms. For these, compute frequency distributions and entropy globally — how skewed is the biome distribution? are there rare lithology classes present in only a handful of basins? The entropy value indicates how evenly the global basin count is distributed across categories.

**Compositional variables**: `pnv_shares` is neither scalar nor simple categorical — it is a dictionary of shares summing to ~100. Characterize its diversity separately: how many basins have a single dominant PNV class at >95%? how many are genuine mixtures? This is a distinct analytical question from the scalar distributions and should be noted as such.

Goal: identify which variables are informative (heavy-tailed, multimodal) vs. effectively constant or degenerate (near-zero mass, most basins null). This determines which variables to foreground in any rubric or dimensionality reduction.

**Artifact**: A histogram gallery (PDF or HTML) covering all scalar variables, one histogram per variable. A summary table: variable, mean, median, std, skew, % null, % zero, and an informative/degenerate classification. A companion frequency table for all categorical variables with entropy values. A short note on `pnv_shares` diversity.

### 2. Missing-data and degenerate-value patterns

For every variable, compute: % null, % zero, % at floor/ceiling values. Cross-tabulate by basin level (L8 vs. L6) to identify where variables systematically degrade at coarser resolution. Document scale-sensitivity patterns — e.g. `slope_avg` near-zero at L6 even in topographically complex terrain is a known issue; the goal is to characterize this globally.

**L6 sample-size caveat**: L6 has roughly 1/20th the basin count of L8 (~10,000 vs. ~190,000). L6 distributions will differ from L8 even for variables that don't genuinely degrade — smaller N and coarser aggregation are confounds. When comparing levels, distinguish "statistical artifact of smaller N" from "genuine scale-degradation of the variable." A variable showing higher % null at L6 could mean either.

**Artifact**: A table of all variables × {L8, L6} showing % null, % zero, and floor/ceiling rates. A written note identifying which variables show genuine scale-degradation and which differences appear to be statistical artifacts of the L6 sample size.

### 3. Local/upstream divergence distribution

For every variable with both a local (`_s`) and upstream (`_u`) value, compute the distribution of divergence globally:
- Ratio `u/s` where meaningful (aridity, precip, temp)
- Difference `u - s` where ratio is unstable (near-zero denominators)

Key questions:
- Where does the Ur case (aridity divergence ~320%) sit in the global distribution — 95th percentile? 99th?
- Is strong divergence rare (a specific environmental signal) or common (a generic feature of the dataset)?
- Which variable pairs show the strongest divergence globally? Which show the least?

This is the quantitative foundation for the claim that the s/u duality is a contribution, not a data-processing choice.

**Artifact**: Distribution plots (histogram or ECDF) for each s/u divergence pair. A ranked summary table: variable pair, global median divergence, 95th/99th percentile values, and where the Ur case falls in each distribution. A written note on which pairs show the strongest divergence and what that implies for interpretation.

### 4. Correlation structure within and across bands

Compute a full correlation matrix across all scalar variables globally at L8. Identify:
- Redundant pairs (r > 0.9) — candidates for exclusion from dimensionality reduction
- Constrained variables (e.g. `pct_clay + pct_silt + pct_sand ≈ 1`)
- Cross-band correlations — where does environmental structure cut across band boundaries?

This gives variable-selection leverage for PCA/factor work and identifies which variables are genuinely independent signals.

**Artifact**: A correlation heatmap (full matrix, with band boundaries marked). A list of variable pairs with |r| > 0.9 — candidates for exclusion from dimensionality reduction. A written note on notable cross-band correlations and what they suggest about the environmental structure underlying the band taxonomy.

### 5. Geographic-type pre-clustering

Run unsupervised clustering (k-means and/or HDBSCAN) on L8 basins using Band A+B+C scalar variables (after handling nulls and scaling). Produce:
- A global map of cluster assignments
- Summary statistics per cluster
- Comparison with the existing 20-cluster result from the workbench (which used bands A–D)

**Normalization note**: Task 1 will almost certainly reveal heavily right-skewed distributions (discharge, population density, etc.). The clustering input needs a deliberate normalization decision — log-transform, rank normalization, or z-score — made before running. Document the choice and rationale; it materially affects the typology.

**k-means vs. HDBSCAN**: These methods produce structurally different clusters. k-means imposes spherical equal-variance clusters of fixed count; HDBSCAN finds density-based clusters of varying size and can leave noise points unassigned. Run both and compare during this task, then commit to one with written justification before using the typology downstream. A 20-cluster HDBSCAN is not the same object as a 20-cluster k-means on identical data.

**Comparison with workbench clustering**: The workbench 20-cluster result used bands A–D; this task uses A+B+C. Comparing them mixes two distinct questions: (a) how does the new clustering differ? and (b) why does it differ — different variable set, or different underlying structure? Separate these before interpreting changes as substantive findings about the data.

Goal: establish a working typology of environmental basin types that can situate any individual signature — "this is an arid-continental-interior basin like X thousand others" vs. "this is an unusual coastal-arid combination." This situating capability is what turns a raw signature into interpretable output.

**Artifact**: A global map of cluster assignments. Summary statistics per cluster (centroid values, within-cluster variance). A written note resolving the k-means vs. HDBSCAN choice with justification, and a brief comparison with the workbench clustering noting what changed and why.

### 6. Geographic coverage and sampling-bias characterization

BasinATLAS covers terrestrial Earth at uniform spatial density, but the places that matter for historical scholarship are heavily clustered in specific regions: Mediterranean, East Asia, South Asia, Mesoamerica, the Nile valley, etc. The D-PLACE, Cliopatria, and Reba datasets that will eventually be used for correspondence testing are geographically concentrated in those same clusters.

Once Task 1 is complete and a signature-space representation exists, characterize the geographic distribution of scholarship against the global basin distribution:
- Which regions of environmental signature space are densely sampled by historical scholarship?
- Which are sparse or absent — and are those gaps geographic (no settlements) or documentary (no data)?
- Where does the global basin distribution diverge most from the scholarship distribution?

This is not validation; it is scope characterization. It tells you in advance where correspondence experiments will have statistical power and where they won't, and it is a finding that belongs in any methods paper.

**Artifact**: A map or signature-space scatter plot showing the D-PLACE/Cliopatria basin distribution overlaid on the global distribution (Task 5 clusters provide a natural coordinate system). A written note on which environmental types are over- or under-represented in the historical record relative to their global prevalence.

---

## What NOT to Do During Exploration

**Do not generalize from individual cases before global distributions are in hand.** Timbuktu and Kaifeng are diagnostic, not representative. They were chosen because they are distinctive. Extending from two worked cases to "here's what signatures tend to say" is seductive and tends to be wrong. Interpret individual cases against global distributions, not against each other.

**Do not let validation pull on exploration.** D-PLACE correspondence testing is a separate phase. If variable selection starts being tuned against what produces good D-PLACE correlations, the work has quietly moved from instrument characterization into optimization-against-cultural-target. Keep the phases sequential.

**Do not conflate L8 and L6 findings.** Scale-sensitivity is itself a finding. Document distributions separately at each level; do not mix.

---

## Band T Note

The F-band returns three full annual series (`pdsi_series`, `air_series`, `prate_series`) plus summary statistics and volcanic events. For individual place-period queries this is appropriate. For batch characterization across thousands of locations, the annual arrays are heavy. A lightweight F-band mode returning only means and ranges (no annual arrays) would make exploration tractable. Consider adding `?bands=T&detail=summary` or similar to the API before the exploration batch runs begin.

---

## Phase 2: Temporal Variable Characterization (Band T)

Tasks 1–6 above cover the **static basin signature** — variables stored in `basin08`/`basin06` and returned as fixed attributes of a location. Band T variables (LMR v2.1 and eVolv2k) are fundamentally different: they are **time-series pulled per query**, not static table columns, so they cannot be characterized by running distributions over a basin table.

Characterizing Band T is a separate exploratory phase, to be designed after Tasks 1–6 are complete. Likely questions:

- What does the PDSI distribution look like across a sample of locations and time periods? How much variance is geographic vs. temporal?
- How often do volcanic events (eVolv2k) fall within a typical query window (e.g., a 100-year period)? What is the distribution of VSSI magnitudes?
- How do LMR temperature and precipitation anomalies relate to the static Band C climate variables at the same locations?
- What sample design (how many locations, which periods) gives adequate coverage for characterization without prohibitive API load?

This phase will likely produce its own small notebook series (e.g., `07_band_t_pdsi.ipynb`, `08_band_t_volcanic.ipynb`) and a separate section of `exploration_log.md`.

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
- `06_coverage_sampling_bias.py`

---

## Exploration Log

`logs/exploration_log.md` is a running record of findings, not a daily work log. Each entry records:
- **Date**
- **Task** (which item from the list above)
- **Method** (script/notebook, key parameters)
- **Finding** (what was learned — the substantive result)
- **Implication** (what this changes about how we understand or use the signature)

This log is the raw material for the methodology section of any future paper. Write to it after each meaningful finding, not at the end of a session.
