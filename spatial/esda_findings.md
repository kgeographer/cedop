# ESDA Findings Log

Running record of findings from the spatial statistics (ESDA) phase. Notebooks in `notebooks/edop/spatial/`, outputs in `spatial/`.

Each entry: **Date · Variable/Scale · Method · Finding · Implication**

---

## Aridity — `ari_ix_sav` (P/PET × 100, local basin average)

### ARI.1 — Global Moran's I: aridity is near-maximally clustered at both scales

**Date**: 2026-05-14 (L6), 2026-05-15 (L8)
**Notebooks**: `01_aridity_l6_moran.ipynb`, `02_aridity_l8_moran.ipynb`
**Method**: Queen contiguity weights, row-standardised; 999 permutations; `np.random.seed(42)`

**Finding**:
| Scale | Basins | Moran's I (raw) | Moran's I (log) | Δ (raw→log) | p-value | z-score |
|-------|--------|-----------------|-----------------|-------------|---------|---------|
| L6    | 16,397  | 0.9628 | 0.9731 | +0.0103 | 0.001 | 195.64 |
| L8    | 190,675 | 0.9889 | 0.9924 | +0.0035 | 0.001 | 754.92 |

Log transform sensitivity narrows at finer resolution (Δ 0.010 → 0.004): at L8 each basin is more internally homogeneous, so the right-skewed tail exerts less leverage on the spatial correlation structure. The raw-vs-log distinction is practically irrelevant at L8 for aridity.

Both p-values are floored at 0.001 (1/999 permutations). The z-score increase from 196 to 755 is a sample-size artifact (permutation variance narrows as n grows), not a substantive finding — compare I values directly.

**Implication**: Aridity will anchor the high end of the coherence spectrum. Any variable with I > 0.95 behaves like aridity — large-scale climate gradient dominates, LISA map is geographically interpretable at continental scale. I < 0.7 or so will indicate structural difference worth investigating.

---

### ARI.2 — Scale effect confirmed: I increases with finer resolution

**Date**: 2026-05-15
**Finding**: I rises from 0.9628 (L6) to 0.9889 (L8), Δ = +0.0261. Direction is consistent with the expected mechanism: smaller basins sit more firmly inside individual climate zones, so each basin's value more closely tracks its immediate neighbours. At L6, large basins span climate gradients and their averaged values decouple slightly from adjacent-basin averages.

**Implication**: For smooth large-scale climate variables (aridity, temperature, precipitation), expect I to increase monotonically with resolution. This is a baseline expectation; departure from it for other variables is informative.

---

### ARI.3 — Distribution shifts toward wetter at finer resolution

**Date**: 2026-05-15
**Finding**:
| Statistic | L6 | L8 |
|---|---|---|
| Mean | 84.2 | 95.3 |
| Median | 65.0 | 68.0 |
| Max | 2101 | 2167 |
| % below humid threshold (65) | 49.5% | 47.8% |

Mean increases by ~11 units; median shifts modestly. Finer resolution preferentially resolves wet-extreme locations (coastal margins, riparian corridors, windward mountain slopes) that were averaged into drier neighbours at L6. The same mechanism shifts `% below humid threshold` from 49.5% to 47.8%.

**Implication**: For right-skewed variables, finer resolution selectively inflates the upper tail. This is an artefact of aggregation geometry, not a real environmental change. Do not interpret distributional differences across scales as substantive without checking this mechanism.

---

### ARI.4 — LISA cluster-core percentages are scale-stable; outlier percentages are not

**Date**: 2026-05-15
**Finding**:
| Class | L6 (n) | L6 (%) | L8 (n) | L8 (%) |
|-------|--------|--------|--------|--------|
| HH    | 753    | 4.6%   | 7,174  | 3.8%   |
| LL    | 4,927  | 30.0%  | 58,862 | 30.9%  |
| HL    | 225    | 1.4%   | 413    | 0.2%   |
| LH    | 0      | 0.0%   | 0      | 0.0%   |
| NS    | 10,492 | 64.0%  | 124,226| 65.2%  |

HH and LL percentages are nearly identical across a 11.6× increase in basin count — the large arid and humid zones fill the basin set proportionally at both resolutions.

HL absolute count roughly doubles (225→413) but percentage drops 1.4%→0.2%, because the HL features (river corridors, coastal strips) are geographically fixed and do not scale with basin count. HL percentage is thus not comparable across scales; absolute counts or per-km² density are the right comparison.

LH=0 at both scales. No statistically significant dry outliers within humid surroundings exist for aridity at either resolution.

**Implication**: When building the characterisation table, report HL/LH absolute counts alongside percentages. Percentage-only comparison across scales is misleading for the outlier classes.

---

### ARI.5 — MAUP: HH fringe contracts at finer resolution (Pacific Northwest case)

**Date**: 2026-05-15
**Finding**: The HH (humid cluster core) footprint in the US Pacific Northwest / British Columbia is visibly smaller at L8 than at L6. At L6, large basins average across the wet coastal slopes and transitional terrain, producing a solid HH block. At L8, the Cascade rain shadow resolves as individual dry sub-basins; their presence in the queen neighbourhood of adjacent wet basins drops the spatial lag below the significance threshold, so the fringe of the HH zone contracts to NS. Only the unambiguous coastal core remains classified HH.

**Implication**: This is the Modifiable Areal Unit Problem (MAUP) in a geographically concrete form. For variables with sharp local gradients (mountain rain shadows, coastlines, river/desert contrasts), HH/LL cluster footprints will shrink at finer resolution even when the large-scale climate pattern is unchanged. Cluster-core percentage is robust for continent-scale features but not for features near topographic discontinuities. The Pacific Northwest is an extreme case; the Andes, Ethiopian Highlands, and Horn of Africa are candidates for similar behaviour in other variables.

---

## Discharge — `dis_m3_pyr` (mean annual discharge, m³/s, cumulative)

No upstream variant — the variable is already a cumulative upstream aggregate. Log transform canonical: raw skewness ~41, Δ(log−raw) = +0.18. Notebooks: `03_discharge_l6_l8_moran.ipynb`.

---

### DIS.2 — Global Moran's I: network topology produces substantially lower autocorrelation than climate gradients

**Date**: 2026-05-16
**Method**: Queen contiguity, row-standardised, 999 permutations, seed=42, log(1+x) transform

| Scale | Basins | I (raw) | I (log) | Δ (log−raw) |
|-------|--------|---------|---------|-------------|
| L6 | 16,397 | 0.3986 | 0.5822 | +0.1836 |
| L8 | 190,675 | 0.3689 | 0.5629 | +0.1941 |

**Finding**: Discharge I_log is ~0.41 below aridity at both scales (aridity L6=0.9731, L8=0.9924). Adjacent basins share aridity values tightly because they occupy the same climate zone; they share discharge values far more loosely because they may drain into completely different river systems separated by a watershed divide.

**Implication**: The I gap between discharge and aridity is an empirical measure of the difference between climate-gradient and network-topology spatial structure. Discharge will anchor the moderate-I range of the characterisation spectrum; aridity anchors the high end.

---

### DIS.3 — Log transform is not cosmetic for discharge: Δ(log−raw) = +0.18

**Date**: 2026-05-16
**Finding**: For aridity, raw vs log differed by 0.010 — effectively irrelevant. For discharge, the log transform raises I by +0.184 (L6) and +0.194 (L8), changing the interpretation from "weakly autocorrelated" to "moderately autocorrelated." In raw space, the Amazon outlet (~200,000 m³/s) dominates the spatial variance calculation and suppresses the global I. Log-transforming compresses the tail and gives equal weight to spatial patterns across all orders of magnitude of discharge.

**Rule**: For any variable with skewness > ~5, treat the raw and log I values as measuring different things. The log version measures the spatial pattern of proportional variation; the raw version reflects extreme-outlier geometry. Log is canonical for LISA.

---

### DIS.4 — Scale direction reversal: discharge I decreases with finer resolution (opposite of aridity)

**Date**: 2026-05-16
**Finding**:

| Variable | L6 I (log) | L8 I (log) | Δ scale | Direction |
|---|---|---|---|---|
| Aridity | 0.9731 | 0.9924 | +0.019 | ↑ finer = higher I |
| Discharge | 0.5822 | 0.5629 | −0.019 | ↓ finer = lower I |

At finer resolution, more adjacent basin pairs straddle watershed divides. At L6, large basins average over enough terrain that the discharge contrast across a divide is partially smoothed. At L8, small basins right at a divide are unambiguously on opposite sides with sharply different discharge, pulling I down. Climate gradients have no equivalent "divide" — aridity transitions smoothly, so finer resolution only increases within-zone coherence.

**Implication**: Scale direction is a variable-type diagnostic. Variables driven by smooth spatial processes (climate) will generally show I increasing with resolution. Variables driven by network or discontinuous processes (drainage topology, geology) may show I decreasing. This axis should be included in the characterisation table.

---

### DIS.5 — LISA class structure: HH ≈ LL symmetry, LH class appears

**Date**: 2026-05-16
**Finding** (L6, log-transformed):

| Class | n | % | vs aridity L6 |
|---|---|---|---|
| HH | 3,346 | 20.4% | aridity 4.6% |
| LL | 3,107 | 18.9% | aridity 30.0% |
| HL | 124 | 0.8% | aridity 1.4% |
| LH | 300 | 1.8% | aridity 0.0% |
| NS | 9,520 | 58.1% | aridity 64.0% |

HH ≈ LL (near parity) vs aridity's strong LL dominance (30% vs 4.6%). In log-discharge space the world is more symmetrically divided between river systems and arid/endorheic interiors than between humid and arid climate zones.

LH appears at 1.8% — a class impossible for aridity (no dry outliers within humid climate zones) but natural for discharge: small endorheic or rain-shadow basins embedded within high-flow surroundings, isolated upland headwaters adjacent to large mainstem basins.

NS fills interfluves (land between river systems disconnected from major drainage), not gradient transition zones as in aridity.

---

### DIS.6 — Scale effects on LISA classes: HH/LL reversal, LH grows faster than basin count

**Date**: 2026-05-16
**Finding** (cross-scale comparison, log-transformed):

| Class | L6 % | L8 % | Δ | L6 n | L8 n | ratio |
|---|---|---|---|---|---|---|
| HH | 20.4 | 15.6 | −4.8 | 3,346 | 29,819 | 8.9× |
| LL | 18.9 | 23.5 | +4.6 | 3,107 | 44,890 | 14.4× |
| HL | 0.8 | 0.3 | −0.4 | 124 | 626 | 5.0× |
| LH | 1.8 | 3.5 | +1.7 | 300 | 6,752 | 22.5× |
| NS | 58.1 | 56.9 | −1.1 | — | — | — |

Basin count grows 11.6×. LH grows 22.5× — the only class that outpaces the basin count increase. This is the watershed-divide effect made explicit: at L8, many more small basins sit at the edge of major river systems with high-discharge queen-neighbours. HH/LL reversal across scales (L6: HH>LL; L8: LL>HH) as proliferating small headwater/endorheic basins push LL ahead.

For aridity by contrast: HH and LL percentages barely move across scales (large climate zones are resolution-stable); LH stays at 0.0%.

**Implication**: For discharge, outlier-class percentages are strongly scale-dependent and should not be compared across L6/L8 without considering the absolute counts. LH% at L8 is ~2× L6 not because there are twice as many "rivers-in-desert" but because finer resolution resolves twice as many watershed-divide positions.

---

### DIS.1 — Research question: interfluve NS zones and settlement patterns

**Date**: 2026-05-16
**Observation**: The NS (not significant) class in the discharge LISA map represents the interfluves — land between river systems that neither accumulates high flow nor sits in an arid/endorheic zone. These are not settlement-poor: many historical societies settled interfluve margins rather than river floodplains, for defensibility, flood avoidance, and stable ground. Mesopotamia is the canonical case — the agricultural heartland was the land *between* the Tigris and Euphrates, irrigated from both but not in either floodplain. Many tell sites and ancient city locations are likely in NS or transitional basins, not HH.

**Research question**: Do Cliopatria/Seshat polities and D-PLACE societies cluster preferentially in HH (river system), NS (interfluve), or LL (arid) basins? Does the answer vary by subsistence type (agricultural vs. pastoral vs. forager)? The discharge LISA class (HH/LL/NS/HL/LH) per basin is a meaningful environmental descriptor for historical place analysis — not just the discharge value itself, but the basin's structural position in the drainage network.

**Action**: Flag for polity phase — test LISA class distribution of D-PLACE societies and Cliopatria polity centroids against global basin baseline. Subsistence type filter (D-PLACE has this) would make the test more informative.

---

## Phase 1 — Univariate sweep, Bands A–D (L6 + L8)

Script: `scripts/edop/esda/12_spatial_moran.py`. Queen contiguity weights, row-standardised, 999 permutations, seed 42. Log transform applied where skewness > 5 and min ≥ 0. BasinATLAS -9999 sentinels masked before all computation (see METH.4).

Outputs: `spatial/variable_characterization.csv` (committed), `output/edop/esda/lisa_classifications.parquet` (gitignored, 655k rows L6 / 7.6M rows L8).

---

### SW.1 — Full I spectrum and summary table

**Date**: 2026-05-17

| band | variable | friendly_name | I_L6 | I_L8 | scale_dir |
|------|----------|---------------|------|------|-----------|
| A | ele_mt_sav | Mean elevation | 0.924 | 0.970 | ↑ |
| A | ele_mt_smn | Elevation minimum | 0.884 | 0.943 | ↑ |
| A | ele_mt_smx | Elevation maximum | 0.848 | 0.933 | ↑ |
| A | slp_dg_sav | Slope | 0.805 | 0.879 | ↑ |
| A | ero_kh_sav | Erosion rate | 0.741 | 0.922 | ↑ |
| A | sgr_dk_sav | Stream gradient | 0.725 | 0.792 | ↑ |
| A | kar_pc_sse | Karst % | 0.676 | 0.820 | ↑ |
| A | gla_pc_sse | Glacier % | 0.663 | 0.820 | ↑ |
| B | swc_pc_syr | Soil water content | 0.970 | 0.992 | ↑ |
| B | slt_pc_sav | Silt % | 0.964 | 0.962 | ↓ |
| B | cly_pc_sav | Clay % | 0.902 | 0.932 | ↑ |
| B | run_mm_syr | Annual runoff | 0.874 | 0.971 | ↑ |
| B | snd_pc_sav | Sand % | 0.873 | 0.903 | ↑ |
| B | soc_th_sav | Soil organic carbon | 0.858 | 0.906 | ↑ |
| B | gwt_cm_sav | Groundwater depth | 0.824 | 0.857 | ↑ |
| B | lka_pc_sse | Lake area % | 0.684 | 0.729 | ↑ |
| B | dis_m3_pmn | Discharge monthly min | 0.614 | 0.573 | ↓ |
| B | wet_pc_sg2 | Wetland % group 2 | 0.611 | 0.705 | ↑ |
| B | wet_pc_sg1 | Wetland % group 1 | 0.598 | 0.700 | ↑ |
| B | inu_pc_smx | Inundation max | 0.589 | 0.625 | ↑ |
| B | dis_m3_pyr | Discharge annual | 0.582 | 0.563 | ↓ |
| B | dis_m3_pmx | Discharge monthly max | 0.535 | 0.559 | ↑ |
| B | ria_ha_ssu | River area (local) | 0.485 | 0.591 | ↑ |
| B | dor_pc_pva | Degree of regulation | 0.475 | 0.422 | ↓ |
| C | pet_mm_syr | PET annual | 0.988 | 0.997 | ↑ |
| C | tmp_dc_syr | Temperature annual | 0.981 | 0.996 | ↑ |
| C | snw_pc_syr | Snow cover annual | 0.975 | 0.993 | ↑ |
| C | ari_ix_sav | Aridity index | 0.973 | 0.992 | ↑ |
| C | aet_mm_syr | AET annual | 0.967 | 0.993 | ↑ |
| C | prm_pc_sse | Permafrost % | 0.959 | 0.979 | ↑ |
| C | cmi_ix_syr | Climate moisture index | 0.952 | 0.988 | ↑ |
| C | pre_mm_syr | Precipitation annual | 0.921 | 0.978 | ↑ |
| C | for_pc_sse | Forest cover % | 0.858 | 0.892 | ↑ |
| D | hdi_ix_sav | HDI | 0.987 | 0.995 | ↑ |
| D | gdp_ud_sav | GDP mean | 0.943 | 0.986 | ↑ |
| D | ppd_pk_sav | Population density | 0.862 | 0.913 | ↑ |
| D | pst_pc_sse | Pasture % | 0.860 | 0.897 | ↑ |
| D | crp_pc_sse | Cropland % | 0.849 | 0.899 | ↑ |
| D | hft_ix_s09 | Human footprint 2009 | 0.819 | 0.847 | ↑ |
| D | nli_ix_sav | Nighttime lights | 0.622 | 0.700 | ↑ |

I range at L6: 0.475 (degree of regulation) – 0.988 (PET). All variables show meaningful positive spatial autocorrelation; none are near zero or negative.

---

### SW.2 — Scale direction: 36 ↑, 4 ↓

**Date**: 2026-05-17

The predominant behaviour (36/40 variables) is ↑ — spatial autocorrelation increases with finer resolution, consistent with the climate-gradient mechanism established for aridity. The 4 ↓ variables all share network- or infrastructure-topology structure:

| Variable | L6 | L8 | Δ | Mechanism |
|---|---|---|---|---|
| dis_m3_pyr | 0.582 | 0.563 | −0.019 | Watershed-divide effect (established, DIS.4) |
| dis_m3_pmn | 0.614 | 0.573 | −0.041 | Same mechanism; baseflow more divide-sensitive than annual mean |
| dor_pc_pva | 0.475 | 0.422 | −0.053 | Dams are point features; at L8 a regulated basin is small and surrounded by many unregulated neighbours — point anomaly character sharpens, coherence drops |
| slt_pc_sav | 0.964 | 0.962 | −0.002 | Effectively flat; large-scale loess belts and alluvial plains are already well-captured at L6. The ↓ sign is not substantively meaningful at this magnitude |

**Rule**: scale direction ↓ is diagnostic of network/infrastructure topology, not gradient structure. Variables with ↓ direction will show I *decreasing* as resolution increases because finer scale resolves more discontinuities. All other variable types default to ↑.

---

### SW.3 — Notable within-band findings

**Date**: 2026-05-17

**Erosion rate largest absolute scale gain** (Δ+0.181): ero_kh_sav 0.741→0.922, the largest absolute increase of any variable. Erosion is slope-driven; at L8 steep and flat basins are unambiguous rather than averaged.

**Karst and glacier sharpen similarly** (Δ≈+0.16 each): geologically and climatically bounded features — karst limestone outcrops, alpine/polar ice — that are smeared across coarser basin boundaries at L6 but resolve clearly at L8.

**Discharge trio: three variables, three scale directions**:
- Annual mean ↓ (divide effect on cumulative flow)
- Monthly min ↓ (baseflow even more divide-sensitive — largest ↓ among discharge variables)
- Monthly max ↑ (peak flood pulse; at L8 small basins within a river corridor all experience the same flood event simultaneously, sharpening the HH chain along mainstems)

**Band C ceiling at L8**: PET, temperature, snow, aridity, AET all reach I ≥ 0.992 at L8 — effectively maximum spatial autocorrelation. These variables have no meaningful variation left to resolve at finer scale; they are already near-perfectly spatially locked.

**Silt anomaly within soil texture**: clay ↑ (+0.030) and sand ↑ (+0.030) but silt ↓ (−0.002). Silt is associated with large-scale loess deposits and river floodplains that are geomorphic features captured at L6. Clay and sand have more local substrate determinants that resolve sharper at L8.

**Band D as high as Band C**: HDI (0.987/0.995) and GDP (0.943/0.986) reach values comparable to PET and temperature. Wealth and development autocorrelate at continental scale as strongly as climate. The spatial co-clustering of D and C variables at L6 is an empirical fact; its interpretation belongs to the polity phase, not here.

**dor_pc_pva highest outlier%**: 5.93% at L6 — the highest outlier percentage in the sweep. Degree of regulation is a point-feature variable; its HL pattern (one regulated basin surrounded by unregulated neighbours) is more prevalent than for any other variable. Potentially the most spatially locally-specific signal in the dataset.

---

## Methods and conventions

### METH.1 — Never use GeoDa GAL files for PySAL weights

**Date**: 2026-05-14
**Finding**: `basin06_queen.gal` (exported from GeoDa) produced I = 0.364 and a mottled, geographically uninterpretable LISA map. Correct result (I = 0.963) only obtained with `Queen.from_dataframe(gdf, use_index=True)` keyed by `hybas_id`. GeoDa GAL files use GeoDa's internal sequential row index as keys, not the basin primary key, causing misalignment between the weights matrix and the data array.

**Rule**: Always build weights in Python from the GeoDataFrame with `use_index=True`. Treat any existing GAL file as unusable.

---

### METH.2 — `plt.show()` blocks inline rendering in PyCharm Jupyter

**Date**: 2026-05-15
**Finding**: Cells with `plt.show()` produce print output but no inline plot. Removing `plt.show()` allows `%matplotlib inline` to render figures automatically at cell end. This is consistent with PyCharm's Jupyter backend behaviour — `plt.show()` clears the figure before the inline backend captures it.

**Rule**: Never add `plt.show()` to notebook plot cells. End with `plt.tight_layout()` and any print statements; let `%matplotlib inline` handle display.

---

### METH.3 — M5 performance benchmarks for spatial operations

**Date**: 2026-05-15
**Machine**: Apple M5, 2026

| Operation | L6 | L8 |
|---|---|---|
| Queen weights build | not timed | 4m 39s |
| Global Moran's I (999 perms) | ~seconds | 3s |
| LISA (999 perms) | ~seconds | 20s |
| LISA cluster map render | ~seconds | not timed |

L8 LISA at 20s is far faster than anticipated (estimated 1–2 hours). The M5 is effectively interactive for all operations in this pipeline. Update any documentation that still refers to L8 as "kick it off and walk away."

---

### METH.4 — BasinATLAS -9999 sentinel destroys Moran's I even in small numbers

**Date**: 2026-05-17
**Finding**: BasinATLAS stores NoData as integer -9999. In `snw_pc_syr`, only 5 out of 16,397 basins (0.03%) carried this sentinel. Treated as real values, they produced z-scores of ≈ −500, pulling the Moran scatter slope to near zero (I = 0.021 instead of the correct 0.975). The sentinel also blocked the log-transform path (`min ≥ 0` check fails at -9999), compounding the error.

Affected columns confirmed in basin06: `snw_pc_syr`, `slp_dg_sav`, `sgr_dk_sav`, `cly_pc_sav`, `slt_pc_sav`, `snd_pc_sav`, `soc_th_sav` (sentinel counts 5–757).

**Rule**: Mask `vals[vals == -9999] = np.nan` before any computation, before applying scale factors. One sentinel in 16k basins is enough to invalidate a spatial statistic. Previously noted in EDA phase but not carried into ESDA scripts — now enforced in `12_spatial_moran.py`.
