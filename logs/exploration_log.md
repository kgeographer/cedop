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

---

## 2026-04-19 · Task 2 · Missing-data and degenerate-value patterns, L8 vs. L6

**Method**: `notebooks/edop/explore/02_missing_data.ipynb` · L8: 190,675 basins · L6: 16,397 basins · 38 scalar variables · outputs: `02_missing_data_crosstab.csv`, `02_scale_scatter.png`, `02_distribution_shift.csv`, `02_scale_sensitivity.csv`

---

### F2.1 — Null rates universally decrease at L6; soil texture most affected

**Finding**: Every variable with non-zero null rates at L8 shows lower null rates at L6. The three soil texture variables (`pct_clay`, `pct_silt`, `pct_sand`) have the largest improvement: 9.11% null at L8 vs. 4.62% null at L6 (delta −4.49%). Slope and stream gradient also improve (L8: 3.3–4.1% null; L6: 1.8–2.5% null). No variable shows higher null rates at L6.

**Implication**: Null rates decreasing at coarser resolution is paradoxical but explicable: L6 polygons are larger and more likely to overlap the source dataset's coverage area. This is a coverage geometry effect, not improved data quality. The soil texture variables' content is essentially unchanged (std_shift ≤ 0.026) — only spatial coverage improves. Null-rate comparisons between levels cannot be interpreted as data quality degradation in either direction for these variables; they reflect source-dataset footprint vs. basin polygon size.

---

### F2.2 — Zero rates reveal which variables are structurally sparse vs. scale-sensitive

**Finding**: Zero rates at L8 vs. L6 diverge in two directions. Most variables show *lower* zero rates at L6 (more non-zero basins at coarser scale), consistent with larger basin polygons capturing more of each phenomenon. Exceptions: `dist_sink` jumps from 13.69% zeros at L8 to 33.35% at L6 (+19.66%); `elev_min` rises from 6.03% to 11.29% (+5.26%). Wetland variables show the largest absolute decreases in zero rate: `wet_pct_grp1` drops −23.78%, `wet_pct_grp2` −19.19%, `karst` −12.29%, `karst_upstream` −12.09%, `reservoir_vol` −12.65%.

**Implication**: The `dist_sink` zero-rate increase at L6 is a topology artifact: L6 basins are larger and more likely to *be* terminal basins (with `dist_sink` = 0 by definition), inflating the zero count. This variable is sensitive to basin level in a structural way — the zero is not "no data" but "this is an outlet basin," and more basins qualify at L6. For spatially sparse phenomena (karst, wetlands, reservoirs), larger L6 polygons capture more non-zero signal — the variable becomes *more* informative at L6 for presence/absence purposes, though continuous values will differ.

---

### F2.3 — River area is the most scale-sensitive variable; a fundamentally different measure at L6

**Finding**: `river_area` has a standardized mean shift of 4.49 between L8 and L6 — by far the largest of any variable. L8 mean: 192.7 ha, median: 71.8 ha. L6 mean: 2,241.3 ha, median: 914.2 ha. The variable increases roughly 10-fold in mean and 13-fold in median. `river_area_upstream` shifts at 0.234 (mean doubles from 8,172 ha to 25,574 ha).

**Implication**: `river_area` at L6 is not a scaled version of L8 `river_area` — it is a structurally different quantity. The polygon area of the river network within a large L6 basin is not comparable to the local sub-basin river area at L8. Do not use `river_area` for cross-level comparisons or treat L6 values as approximations of L8. For any analysis requiring this variable, pin to a single level. Flag in any methodology document.

---

### F2.4 — Elevation extremes shift predictably with scale; a geometric consequence

**Finding**: `elev_min` shifts −0.208 std (L8 mean 445 m → L6 mean 308 m); `elev_max` shifts +0.239 std (L8 mean 1,058 m → L6 mean 1,341 m). Both shifts are in the expected direction: larger L6 basin polygons span greater elevation ranges, so their minimum is lower and their maximum is higher.

**Implication**: This is a geometric scale effect, not a data quality issue. L6 `elev_max` and `elev_min` are valid — they correctly describe the elevation range of a larger basin. But they are not interchangeable with L8 values for the same location. For a historical site query, L8 gives the local basin's elevation envelope; L6 gives a broader regional range. Both are useful, for different analytical purposes. Scale context must be stated when reporting either.

---

### F2.5 — Discharge max is scale-sensitive; discharge annual and min are N-artifacts

**Finding**: `discharge_max` shifts +0.216 std (L8 mean 516 m³/s → L6 mean 1,572 m³/s). `discharge_yr` shifts +0.173 std and `discharge_min` +0.130 std, but both are classified as N-artifacts given modest zero-rate deltas and the confound of L6's smaller sample (16,397 vs. 190,675 basins). `river_area_upstream` shifts +0.234 std (scale-sensitive).

**Implication**: Maximum discharge genuinely increases at L6 because larger basins drain larger catchments — a structural hydrological reality. Annual and minimum discharge distributions shift less conclusively; part of the apparent shift may reflect which basins are present in L6's smaller sample. For discharge variables, L8 is preferred when the analysis concerns a specific sub-basin; L6 is appropriate when regional basin-scale hydrology is the frame.

---

### F2.6 — 27 of 38 variables are stable across levels; climate and soil are level-agnostic

**Finding**: Climate variables (temperature, precipitation, aridity — local and upstream), soil texture, human footprint, GDP, cropland extent, karst, permafrost, slope, runoff, and groundwater depth all show |std_shift| < 0.1 with zero null delta. These 27 variables classify as stable across L8 and L6.

**Implication**: The signature's climatic and socioeconomic content is essentially level-invariant — the same environmental regime description applies whether queried at L8 or L6 resolution. For correspondence testing (D-PLACE, settlement patterns), these variables can be used at either level without cross-level comparability concerns. Scale-sensitivity is primarily a hydrological geometry problem, concentrated in river area and discharge max.
