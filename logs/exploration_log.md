# EDOPS Exploration Log

Running record of findings from the data exploration phase. See `docs/edop/data_exploration.md` for task list, conventions, and guardrails.

Each entry: **Date · Task · Method · Finding · Implication**

---

<!-- entries added below as findings accumulate -->

---

## 2026-04-18 · Task 1 · Marginal distributions, L8 globally

**Method**: `notebooks/edop/explore/01_marginal_distributions.ipynb` · 190,675 L8 sub-basins · all implemented scalar, categorical, and compositional variables

---

### F1.1 — Sentinel values (-9999) in six scalar columns

**Finding**: Six columns in `basin08` use -9999 as a NoData sentinel rather than NULL: `slp_dg_sav` (6,390 rows, 3.4%), `slp_dg_uav` (6,390, 3.4%), `sgr_dk_sav` (7,803, 4.1%), `cly_pc_sav` / `slt_pc_sav` / `snd_pc_sav` (17,374 each, 9.1%). No other scalar columns are affected.

**Implication**: These columns must be treated with `NULLIF(col, -9999)` in any SQL query, or replaced with NaN after loading (as done in the notebook via `df_raw.replace(-9999, np.nan)`). Statistics computed before this fix are invalid for these six variables. All downstream scripts must apply the same treatment.

---

### F1.2 — Slope is valid and right-skewed; apparent flatness is real

**Finding**: After sentinel removal, `slope_avg` has mean 41.7°, median 20°, skew 2.09. The distribution has a large spike near zero (flat basins) and a long right tail (mountain terrain). This is consistent with the BasinATLAS source map: plains, lowlands, and interior basins dominate by basin count; steep terrain (Andes, Himalayas) is numerically a small minority.

**Implication**: Slope is informative but right-skewed. A log-transform will be needed before using it in PCA or clustering. The averaging of slope over the entire sub-basin polygon means even "mountainous" basins have moderate mean slopes — point-based intuitions about steepness do not transfer to this variable.

---

### F1.3 — Soil texture (clay, silt, sand) are the most normally distributed scalars

**Finding**: After sentinel removal, `pct_clay` (mean 19.8%), `pct_silt` (mean 30.8%), `pct_sand` (mean 49.3%) show roughly bell-shaped distributions with low skew. They sum to ~100% per basin (constrained compositional variables). 9.1% of basins are null for all three — the same 17,374 rows with -9999 sentinels.

**Implication**: These are among the most analytically tractable variables in the dataset — usable in PCA/clustering without transformation. However, their constrained sum (clay + silt + sand ≈ 100) means only two are independent. Including all three in dimensionality reduction will introduce a spurious linear dependency; one should be dropped.

---

### F1.4 — Temperature is bimodal

**Finding**: `temp_yr` and `temp_yr_upstream` show a clear bimodal distribution: a cold cluster centered around -5°C to 5°C (high-latitude and high-altitude basins) and a warm cluster centered around 20°C–25°C (tropical and subtropical basins). The trough between peaks falls roughly at 10°C–12°C.

**Implication**: Temperature does not follow a single bell curve globally — there are two environmental "worlds" by thermal regime. This bimodality will drive clustering results significantly. Any global typology will likely separate along this axis first. Variables that correlate with temperature (aridity, precip, biome) will show related structure.

---

### F1.5 — Aridity index: stored as P/PET × 100, counterintuitive name

**Finding**: `ari_ix_sav` (api key: `aridity`) is the Global Aridity Index (Zomer et al.), stored as P/PET × 100. Global median = 68 (P/PET = 0.68, semi-arid). P95 = 212 (P/PET = 2.12, moderately humid). Values above 100 indicate humid conditions (P > PET). The tail extends to ~1000 (wet tropics). Despite its name, higher values = wetter — it is a humidity index.

**Implication**: Do not interpret raw values as ratios — divide by 100 for P/PET. The "cap at 100" mentioned in the BasinATLAS catalog refers to the source product's raw ratio cap (P/PET = 100), stored as 10,000 — essentially never reached. The semi-arid global median is consistent with the biome distribution (deserts dominant by basin count). Codebook updated to reflect correct units and scale.

---

### F1.6 — Discharge variables are extreme right-skew; heavy-tailed

**Finding**: `discharge_yr`, `discharge_min`, `discharge_max` have skewness values of 41.6, 45.1, and 34.0 respectively. The median annual discharge is ~5.7 m³/s but the mean is 264.7 m³/s — pulled far right by large river systems. The Amazon and Congo alone drive the tail.

**Implication**: Raw discharge values are not useful in PCA or clustering without log-transformation. Even after log-transform, extreme outliers (large tropical rivers) may form their own cluster. Discharge is best interpreted as a presence/magnitude variable; the distinction between "small stream" and "large river" matters more than precise magnitude differences.

---

### F1.7 — Karst, permafrost, and wetlands are globally sparse; treat as flags

**Finding**: `karst` has 81.9% zero values (degenerate by heuristic). `karst_upstream` has 73.3% zeros, `permafrost_extent` 77.1%, `wet_pct_grp1` 56.9%, `wet_pct_grp2` 71.1%. These are real phenomena but absent for the majority of basins.

**Implication**: These variables carry meaningful signal where they are non-zero, but including them as continuous variables in global PCA/clustering will not work — the near-zero mass dominates. Consider binary encoding (present/absent) or analyzing the non-zero subset separately. Karst and permafrost in particular are strong environmental signals for the minority of basins where they occur.

---

### F1.8 — PNV shares are compositionally degenerate; majority class is sufficient

**Finding**: The PNV diversity chart shows ~95,000 basins with Shannon entropy ≈ 0 (single dominant class), a secondary cluster around 1.0 bit (two roughly equal classes), and a sparse long tail. The dominant class share chart shows the overwhelming majority of basins above the 95% threshold — one PNV class covers >95% of the basin area for most basins.

**Implication**: The full `pnv_shares` compositional object adds negligible information over `pnv_majority` for the vast majority of basins. For global analyses, use `pnv_majority` (categorical). The `pnv_shares` field is potentially useful only for identifying ecotone/transition basins, which form a small minority and could be flagged separately.

---

### F1.9 — Categorical variables: all high entropy; deserts and xeric systems dominate by count

**Finding**: All nine categorical variables have normalized entropy 0.748–0.958 — none are degenerate in the categorical sense. However, dominant classes reveal a consistent pattern: Deserts & Xeric Shrublands is the top biome (36,023 basins); Xeric freshwaters and endorheic basins is the top freshwater habitat type (43,609); Unconsolidated Sediments is the top lithology (52,788). Climate stratum is the most evenly distributed (entropy 0.958, 125 classes). Wetland class has 49.2% null — nearly half of basins unclassified.

**Implication**: The dataset is globally representative but skews arid by basin count — consistent with the aridity and biome scalar findings. Historical scholarship concentrates in non-desert environments, so the basin-count distribution is not the same as the scholarship-relevant distribution (this will be examined in Task 6). Climate stratum is the most discriminating categorical variable. Wetland class null rate should be investigated — it likely reflects genuine absence but the boundary between "no wetland" and "unclassified" is worth clarifying.

---

### F1.10 — Terrestrial ecoregion count skewed by large high-latitude basins

**Finding**: Of 784 terrestrial ecoregions, East Siberian taiga leads by basin count (5,654 basins). High-latitude boreal and tundra ecoregions dominate the top ranks not because they are the most common environment but because L8 sub-basins in Siberia and northern Canada are physically large polygons, generating more basin-count entries per unit area than tropical sub-basins.

**Implication**: Ecoregion basin counts reflect polygon size as much as environmental prevalence. When comparing ecoregion representation, area-weighted counts would be more meaningful than raw basin counts. This applies to any L8-level frequency analysis: large cold basins are over-counted relative to their ecological significance for human settlement.
