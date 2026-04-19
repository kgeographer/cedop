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

---

### F2.7 — Methodological caveats on the N-artifact classification and std_shift threshold

**Finding** (review note): Two limits of the Task 2 classification scheme warrant flagging before any paper-writing use of these results. (1) The L6 sample is 16,397 basins vs. L8's 190,675 — an 11.6× ratio. Standardized mean shifts computed across these different-sized samples have different statistical power characteristics. Variables classified as "N-artifacts" (discharge_yr, discharge_min, dist_sink — F2.5) were flagged as *possibly* confounded by smaller-N rather than confirmed to be so. A permutation or bootstrap test would be needed to formally distinguish "apparent shift due to smaller sample" from "real shift that is harder to detect with fewer observations." (2) The std_shift threshold of 0.1 for the stable/scale-sensitive boundary is a reasonable heuristic but a heuristic. No variables in this dataset sit conspicuously near 0.1, so edge cases are not acute here, but any dichotomous classification of this kind has a fuzzy boundary that warrants visual inspection of borderline cases before treating the classification as definitive.

**Implication**: F2.3–F2.6 findings are reliable for characterization purposes. For any methodology paper, the N-artifact cases should either be formally tested or explicitly flagged as provisional classifications pending a more rigorous comparison. The stable/scale-sensitive dichotomy should be presented as a heuristic summary, not a sharp boundary.

---

## 2026-04-19 · Task 3 · Local/upstream divergence distribution

**Method**: `notebooks/edop/explore/03_su_divergence.ipynb` · L8: 190,675 basins · 9 s/u pairs · divergence metric: log₂(u/s) for ratio pairs (aridity, precip, slope, river_area); u−s for difference pairs (temp, wetland, karst, cropland, human footprint) · outputs: `03_su_divergence_summary.csv`, `03_su_divergence_ecdf.png`

---

### F3.1 — Median divergence is zero for all nine pairs; s/u duality is a tail phenomenon

**Finding**: For every s/u variable pair, the global median divergence is exactly 0 — local and upstream values are identical at the 50th percentile. The interquartile range (p25–p75) is also at or near zero for six of nine pairs. Strong divergence is concentrated in the tails: p95+ for most variables, p99+ for the strongest cases. By basin count, most L8 sub-basins are headwaters or near-headwaters whose upstream footprint is approximately equal to their local footprint.

**Implication**: The s/u duality is not a generic feature of the dataset; it is a signal that fires in specific basin positions. A large divergence value is itself a meaningful finding — it identifies a basin that sits at an environmental boundary between local conditions and its upstream source region. For the majority of basins, reporting s and u separately adds no information. For the minority where they diverge, the divergence is the environmentally distinctive fact. This has direct implications for how the signature should be presented: the divergence magnitude (not just the u value) is the contribution.

---

### F3.2 — Temperature divergence is directionally asymmetric: upstream is almost always colder

**Finding**: `temp_yr` divergence (u−s, °C) is strongly left-skewed. Only 8.2% of basins have upstream warmer than local; 91.8% have upstream colder or identical. The cold tail is heavy: p05 = −3.13°C, p01 = −7.2°C. The warm tail is short: p95 = +0.2°C, p99 = +1.3°C. This is the most directionally asymmetric of all nine pairs.

**Implication**: The asymmetry is physically consistent: tributaries and upstream sub-basins are overwhelmingly at higher elevation than lowland outlet basins. Where the signature shows a large negative temp divergence, the basin sits in a lowland receiving cold-source water from mountain headwaters — a hydrologically distinctive position. The Tigris/Euphrates and Nile are canonical cases of this pattern. A rare positive divergence (warm upstream) would signal a thermally unusual configuration worth investigating.

---

### F3.3 — Aridity and precipitation divergence: moderate symmetric tails; 30% of basins receive upstream moisture

**Finding**: `aridity` and `precip_yr` have nearly identical divergence distributions (high correlation, expected from shared underlying hydrology). Both show moderate, roughly symmetric tails: aridity p95 = +0.555 log₂ (upstream 1.47× wetter), p05 = −0.15. Precipitation p95 = +0.393 log₂, p05 = −0.159. About 30–31% of basins have upstream wetter than local; 69–70% have local wetter or identical.

**Implication**: Positive aridity/precipitation divergence (wetter upstream) is the characteristic signature of exotic river systems — rivers that originate in humid mountains and flow into arid lowlands. About one-third of all basins globally have some degree of this pattern. The claim that "Ur is a distinctive exotic-river case" requires placing Ur in this distribution — whether it falls at p90, p95, or p99 determines how distinctive the claim is. That analysis requires the place-percentile output from Cells 8–10 (not yet run).

---

### F3.4 — Slope divergence: widest environmental tails; upstream-steeper pattern common

**Finding**: `slope` has the widest ratio-pair tails: p95 = +2.32 log₂ (upstream 5× steeper than local), p99 = +4.59 (24× steeper). The negative tail is also significant: p01 = −1.81 (local 3.5× steeper than upstream). 31% of basins have upstream steeper than local — the same proportion as aridity and precip, suggesting a structural correlation: steep upstream terrain drives both cold temperatures and concentrated precipitation.

**Implication**: Large positive slope divergence identifies piedmont and alluvial-fan basins — locally flat terrain at the base of steep upstream catchments. This is an important class for historical settlement (Ur, Nippur, the Indus cities all sit on alluvial plains fed by mountain catchments). The combination of steep-upstream + cold-upstream + wet-upstream is the signature of the exotic river basin type; Task 4's correlation matrix should confirm these variables co-vary.

---

### F3.5 — Human footprint and land use: local concentration is the dominant pattern

**Finding**: `human_fp_09`, `cropland`, `wet_pct_g1`, and `karst` all show left-skewed divergence distributions: local values exceed upstream values for 80–90% of basins. `human_fp_09` has the largest absolute divergence values of the difference pairs: p01 = −113 index points (local footprint 113 points above upstream), p95 = +23. Cropland: p01 = −33%, p95 = +6%. Wetlands: p01 = −82%, p95 = +3%.

**Implication**: Human activity, agriculture, and wetland occurrence are predominantly local phenomena — they occur in lowland, accessible basin positions and are absent or reduced in upstream catchments. The left skew means that for most historically significant sites, local human footprint exceeds upstream footprint: the settlement IS the concentration. Cases where upstream footprint exceeds local (13–20% of basins) could identify downstream agricultural peripheries or basins where agricultural land is disproportionately concentrated in headwater valleys — a less common but analytically interesting configuration.

---

### F3.6 — River area divergence: a network-geometry artifact, not an environmental variable

**Finding**: `river_area` has extreme ratio tails: p95 = +6.68 log₂ (upstream network 102× larger than local basin river area), p99 = +9.18 (575× larger). The distribution is driven by basin position in the drainage network: headwater basins have u≈s (log₂≈0), while basins near major river mouths have upstream network areas orders of magnitude larger. 44.5% of basins show upstream-greater — higher than any other pair.

**Implication**: River area divergence measures network position, not environmental character. Including it in a divergence ranking alongside climate or terrain variables is misleading. For the signature, `river_area` (local) and `river_area_upstream` are better treated as independent descriptors of local channel size and network magnitude respectively, not as a local/upstream pair in the divergence sense. Flag for any future dimensionality-reduction work: these two variables are not measuring the same phenomenon at different scales.

---

### F3.7 — Timbuktu: extreme exotic moisture at p99.9, Inner Niger Delta wetland position

**Finding**: Timbuktu (hybas_id 1080561810, up_area 379,818 km²). Dominant divergence signals, ranked by deviation from median: `precip_yr` log₂(u/s) = 2.369 (upstream 5.1× wetter, **p99.9**); `aridity` = 2.385 (upstream 5.2× more humid, **p99.8**); `slope` = 3.585 (upstream 12× steeper, p97.9); `human_fp_09` = +31 (local footprint higher, p96.7); `wet_pct_g1` = −56% (local 56% more wetland than upstream, **p2.2**). Temperature divergence is modest: −1.6°C upstream colder (p11.4).

**Implication**: Timbuktu is in the top 0.1% of all basins globally for upstream moisture divergence — this is not a moderate exotic-river signal but an extreme one. The Niger's headwaters in the Fouta Djallon highlands (~2,000 mm/yr precipitation) feed into the hyper-arid Saharan basin (~200 mm/yr locally). The simultaneously low wetland-divergence percentile (p2.2) is not paradoxical — it confirms Timbuktu's position at the edge of the Inner Niger Delta, where Niger water creates one of Africa's largest wetland complexes locally, producing a wetland concentration that exceeds the upstream average. The signature is: extreme upstream moisture delivery + local wetland terminus + local human concentration. Temperature divergence is slight because the Niger headwaters are not high-altitude cold sources — the exotic character is purely hydrological, not thermal.

---

### F3.8 — Ur: dual asymmetry — upstream agricultural core, local marsh terminus

**Finding**: Ur (hybas_id 2080818060, up_area 456,772 km²). `aridity` log₂(u/s) = 2.070 (upstream 4.2× more humid, **p99.6**); `precip_yr` = 1.457 (upstream 2.75× wetter, p99.5); `temp_yr` = −6.0°C (upstream 6°C colder, p1.6); `wet_pct_g1` = −46% (local 46% more wetland, p3.0); `karst` = +16% (upstream more karst, p95.6). The surprises: `human_fp_09` = −64 index points (upstream footprint **64 points higher** than local, p2.5); `cropland` = −45% (upstream **45% more cropland**, p0.4).

**Implication**: Ur occupies a structurally distinctive position in the Tigris–Euphrates drainage. Two divergence signals point in opposite directions simultaneously. The moisture/temperature signals (aridity p99.6, temp p1.6) confirm the classic exotic-river pattern: cold, wet Zagros and Taurus headwaters draining into a hyper-arid lowland. The human and cropland signals reverse: Ur's local basin is the southern marshland terminus (Mesopotamian marshes), while the upstream basin encompasses the Tigris–Euphrates agricultural heartland — Baghdad, the Fertile Crescent irrigation zone, the full Mesopotamian agricultural core. At the time of Ur's florescence, the upstream was already intensively farmed; Ur itself sat at the wetland edge. The karst signal (upstream more karst, p95.6) reflects Zagros/Taurus limestone terrain. The combination — upstream wetter + upstream colder + upstream more agricultural + local more wetland — is a compact environmental description of what Ur was: a marsh-edge settlement at the foot of a massive agricultural and hydraulic system.

---

### F3.9 — Kaifeng: extreme topographic discontinuity, inverted moisture gradient

**Finding**: Kaifeng (hybas_id 4080602410, up_area 734,701 km²). `slope` log₂(u/s) = 6.492 (upstream **91× steeper**, **p99.9**); `temp_yr` = −8.8°C (upstream 8.8°C colder, p0.6); `human_fp_09` = −85 (upstream footprint 85 points higher, p1.6); `cropland` = −48% (upstream 48% more cropland, p0.3). Crucially: `precip_yr` log₂(u/s) = −0.393 (local **1.3× wetter** than upstream, p1.8); `aridity` = +0.084 (effectively zero divergence, p79.0).

**Implication**: Kaifeng has a fundamentally different divergence profile from Timbuktu and Ur. The dominant signal is topographic, not hydrological: the Yellow River descends from the Tibetan Plateau through the Loess Plateau onto the North China Plain, producing the most extreme slope divergence of the three sites (p99.9, upstream 91× steeper). The cold upstream (-8.8°C, p0.6) follows from altitude. But the moisture gradient runs in the opposite direction from the other two: Kaifeng is wetter locally than upstream, because the East Asian monsoon delivers increasing precipitation eastward toward the coast while the Yellow River headwaters lie in the rain-shadow interior. The cropland and human-footprint inversions (upstream more agricultural, p0.3 and p1.6) reflect the Loess Plateau and Wei River valley agricultural landscape, which has been intensively farmed for millennia — the upstream here is not wilderness but the older, denser agricultural core from which the Yellow River civilizations descended. Kaifeng's position on the North China Plain gives it local agricultural productivity but the plain was settled later and less intensively than the upriver valleys. The signature is: extreme topographic descent, cold source, wetter locally (monsoon), and agricultural antiquity concentrated upstream.

---

### F3.10 — Comparative: three sites, three divergence types; no single exotic-river template

**Finding**: Timbuktu, Ur, and Kaifeng each fall in the extreme tail (p95+) for at least one divergence variable, confirming that historically significant exotic-river settlements are not in the modal basin class. But their divergence profiles are structurally different: Timbuktu's signal is pure moisture delivery (upstream precipitation p99.9, aridity p99.8) with minimal temperature divergence; Ur's signal is moisture plus thermal plus a social reversal (upstream agricultural core); Kaifeng's dominant signal is topographic (slope p99.9) with inverted moisture gradient (locally wetter). No single variable captures all three. The s/u divergence is multidimensional, and different river systems produce distinctive divergence signatures.

**Implication**: The s/u duality's contribution is not reducible to a single "exotic river index." Different environmental mechanisms produce different divergence fingerprints. A composite divergence profile — which variables diverge, in which direction, and by how much — is more informative than any single divergence score. This has direct implications for how the signature is used in correspondence testing and in the narrative layer: the divergence profile should be described per-variable, not collapsed. Practically, this also means the three example sites should not be treated as equivalent instances of the same type — they should be used to illustrate different divergence regimes.

---

## 2026-04-19 · Task 4 · Correlation structure within and across bands

**Method**: `notebooks/edop/explore/04_correlation_matrix.ipynb` · L8: 190,675 basins · 37 scalar variables · Spearman rank correlation (pairwise complete observations) · outputs: `04_correlation_matrix.csv`, `04_correlation_heatmap.png`, `04_high_correlation_pairs.csv`

---

### F4.1 — s/u pair redundancy: local and upstream climate variables are globally near-identical

**Finding**: The three climate s/u pairs are the most correlated in the entire matrix: `aridity` / `aridity_upstream` r = 0.984; `precip_yr` / `precip_yr_upstream` r = 0.987; `temp_yr` / `temp_yr_upstream` r = 0.989. Human variable pairs follow: `human_footprint_09` / `human_footprint_09_upstream` r = 0.951; `cropland_extent` / `cropland_extent_upstream` r = 0.950. These are not independent variables — globally, local and upstream values are nearly interchangeable for these variables.

**Implication**: The global near-identity of s/u pairs is consistent with F3.1 (median divergence = 0 for all pairs). For the majority of basins, including both local and upstream versions of the same climate or land-use variable in PCA adds a near-duplicate dimension without new information. In dimensionality reduction, one member of each s/u pair should be dropped — retain whichever is more theoretically motivated (upstream for process-aware characterization, local for site description). The divergence value itself (u−s or log₂(u/s)) may be more useful than either raw value for capturing the signature's distinctive content.

---

### F4.2 — Temperature internal redundancy; four variables behave as one

**Finding**: `temp_yr`, `temp_min`, `temp_max`, and `temp_yr_upstream` form the tightest cluster in the matrix. All six pairwise correlations exceed r = 0.77; four of six exceed r = 0.88. The highest: `temp_yr` / `temp_yr_upstream` = 0.989, `temp_yr` / `temp_min` = 0.963, `temp_min` / `temp_yr_upstream` = 0.954. The exception: `temp_min` / `temp_max` = 0.771 — seasonal range is partially independent of mean. Visible on the heatmap as the dark red 4×4 block in the Band C region.

**Implication**: For PCA or any dimensionality reduction, including all four temperature variables contributes three near-redundant dimensions. A single temperature variable (most likely `temp_yr`) represents the cluster; `temp_max` is the most independent of the four (lowest average r with others) and could be retained as a second temperature dimension if capturing thermal range is analytically important. `temp_yr_upstream` adds negligible information over `temp_yr` globally (r = 0.989) and can be dropped from dimensionality reduction — its signal is already in `temp_yr`.

---

### F4.3 — Discharge cluster redundancy; discharge_max proxies network size

**Finding**: `discharge_yr`, `discharge_min`, and `discharge_max` are strongly mutually correlated: yr/max r = 0.967; yr/min r = 0.933; max/min r = 0.855. Additionally, `discharge_max` / `river_area_upstream` r = 0.937 — the peak discharge of a basin is almost perfectly predicted by its total upstream network area. `discharge_yr` / `river_area_upstream` r = 0.886. These hydrological size variables form a single redundant cluster.

**Implication**: Only one discharge variable is needed in dimensionality reduction — `discharge_yr` is the natural choice (most commonly reported, best-studied). `river_area_upstream` is nearly redundant with `discharge_max` and represents the same underlying quantity (drainage network magnitude). The three discharge variables + `river_area_upstream` can be treated as four measures of one latent variable: basin hydrological size. Retain one; note the others as alternative representations.

---

### F4.4 — Human variables split into two sub-clusters: intensity and development

**Finding**: Band D contains two near-redundant sub-clusters. Sub-cluster 1 (human intensity): `pop_density`, `human_footprint_09`, `human_footprint_09_upstream`, `cropland_extent`, `cropland_extent_upstream` — all pairwise r = 0.72–0.95. Sub-cluster 2 (economic development): `gdp_avg` / `human_dev_idx` r = 0.910. The two sub-clusters are weakly to negatively correlated with each other: `gdp_avg` / `human_footprint_09` r = −0.307; `gdp_avg` / `pop_density` r = −0.452. High GDP/HDI areas are not the same as densely populated or heavily farmed areas — wealthy but sparsely settled economies (Northern Europe, North America) drive the negative cross-cluster correlation.

**Implication**: The two human sub-clusters measure different things and should not be collapsed. Sub-cluster 1 (intensity) captures anthropogenic landscape modification — agriculture, settlement, infrastructure. Sub-cluster 2 (development) captures economic modernity. For PCA, retain one variable from each sub-cluster: `human_footprint_09` from sub-cluster 1 (composite index), `gdp_avg` or `human_dev_idx` from sub-cluster 2. The negative cross-cluster correlation is itself a finding: intensive land use and economic development are not the same axis, and confusing them in a rubric would produce misleading environmental characterizations.

---

### F4.5 — Cross-band: soil texture co-varies with temperature; a weathering signal

**Finding**: The strongest cross-band correlations in the matrix involve soil texture (Band B) and temperature (Band C). `pct_clay` / `temp_min` r = 0.754; `pct_clay` / `temp_yr` r = 0.710; `pct_clay` / `temp_yr_upstream` r = 0.703. Inverse for silt: `pct_silt` / `temp_min` r = −0.701; `pct_silt` / `temp_yr` r = −0.658. Sand is less strongly correlated with temperature. Also: `pct_clay` / `permafrost_extent` r = −0.582 (warm soils have more clay; permafrost regions less). Visible on the heatmap as a red rectangle crossing the Band B soil-texture rows into the Band C temperature block.

**Implication**: This is a pedogenic signal, not a methodological artifact. Chemical weathering (which produces clay minerals) is temperature-dependent — hot, humid tropical environments produce deep, clay-rich soils; cold, high-latitude or high-altitude environments are dominated by physical weathering (which produces silt and sand from parent rock). The B×C correlation encodes a fundamental climate-soil feedback that operates over geological timescales. Practically: `pct_clay` is not an independent variable for PCA relative to temperature. Including both adds limited new information in warm-climate basins, though they diverge in cold or arid regions where weathering regimes differ.

---

### F4.6 — Cross-band: runoff and aridity are climate-determined; Band B partially redundant with Band C

**Finding**: `runoff` (Band B) / `aridity` (Band C) r = 0.782; `runoff` / `aridity_upstream` r = 0.775; `runoff` / `precip_yr` r = 0.774; `runoff` / `precip_yr_upstream` r = 0.760. Runoff is more strongly correlated with the climate variables than with most of its Band B neighbors. `discharge_yr` / `precip_yr` r = 0.544; `discharge_yr` / `aridity` r = 0.496.

**Implication**: Runoff is largely predictable from precipitation and aridity — it measures what is left after evapotranspiration, which is climate-driven. For dimensionality reduction, runoff does not add substantial new information beyond what aridity and precipitation already encode, except at the margin (where local geology, soil permeability, and land cover modify the climate signal). It may be worth retaining as a Band B representative if the goal is to have hydrology represented independently of climate, but its inclusion should be flagged as partially redundant.

---

### F4.7 — Permafrost as cross-band bridge: cold = uninhabited = high silt

**Finding**: `permafrost_extent` correlates negatively with the entire Band D human cluster: `pop_density` r = −0.512; `human_footprint_09` r = −0.534; `human_footprint_09_upstream` r = −0.557; `cropland_extent` r = −0.437; `cropland_extent_upstream` r = −0.452. It also correlates negatively with `pct_clay` (r = −0.582, Band B) and strongly negatively with all temperature variables (r = −0.688 to −0.720, Band C). In the heatmap: permafrost appears as a blue stripe running across both the Band C temperature block and the Band D human block.

**Implication**: Permafrost is a cross-band integrator: it encodes cold climate (C), physically-weathered soils (B), and absence of human settlement (D) in a single variable. Its correlations are not coincidences but reflect a coherent environmental syndrome — the high-latitude/high-altitude biome where climate, pedology, and human geography all co-vary. This makes permafrost a potentially powerful typological discriminator for clustering (Task 5), even though it is zero for 77% of basins (F1.7). When it fires, it organizes structure across multiple bands simultaneously.

---

### F4.8 — Band E (dist_sink) is structurally independent

**Finding**: `dist_sink` (flow distance to marine outlet) has no correlation above |r| = 0.41 with any other variable. Its strongest correlations: `elev_min` r = 0.408 (higher minimum elevation → farther from coast, expected); `discharge_yr` r = 0.270; `discharge_min` r = 0.280. All others are r < 0.25. The dist_sink row/column appears as a largely neutral (pale) stripe in the heatmap.

**Implication**: Coastality is structurally independent from climate, terrain, hydrology, and human variables — it adds a genuinely orthogonal dimension to the signature. A basin 5,000 km from the ocean is not systematically different in temperature, rainfall, or human footprint from a coastal basin — the position in the drainage network is a separate axis. This validates the prospectus claim that coastality is a "first-class signature component" — it is not captured by any other variable in the dataset.

---

### F4.9 — PCA exclusion candidates: variables redundant at |r| > 0.9

**Finding**: Eleven variable pairs exceed |r| = 0.9 (full list in `04_high_correlation_pairs.csv`). Grouped by redundancy cluster, the recommended exclusions for any PCA or clustering are: (1) from the climate s/u pairs, drop `temp_yr_upstream`, `precip_yr_upstream`, `aridity_upstream` — retain local values; (2) from the discharge cluster, drop `discharge_min` and `discharge_max` — retain `discharge_yr`; (3) drop `river_area_upstream` (r = 0.937 with `discharge_max`); (4) from human footprint, drop `human_footprint_09_upstream` — retain local; (5) drop `cropland_extent_upstream` — retain local; (6) drop `human_dev_idx` — retain `gdp_avg`. These six drops reduce the 37-variable set to 31 without losing substantial information.

**Implication**: The 31-variable reduced set retains one representative per redundant cluster and eliminates the most egregiously collinear variables. A further reduction to ~20 variables would require judgment calls about which cross-band redundancies to address (soil texture vs. temperature, runoff vs. aridity). That reduction decision belongs in Task 5 design, not Task 4 characterization — document it there with explicit rationale.
