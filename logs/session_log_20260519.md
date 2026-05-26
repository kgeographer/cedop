# Session Log — 19 May 2026

## Participants
Karl Grossner, Claude Sonnet 4.6 (CC), Claude Opus 4.7 (consulted async)

## Context
`esda` branch. Previous session (05-17) completed Phase 4 bivariate global maps and deferred regional analysis. This session: Phase 4 regional analysis; CHAR completion prompt review; Phase 1 CHAR categorical spatial coherence notebook.

---

## 1. Phase 4 regional analysis — `06_bivariate_phase4_l6.ipynb` Cells 15–17

Completed the deferred regional analysis for all five bivariate pairs across three regions (Mediterranean, Monsoon Asia / Indomalaya, Tibetan/cold-arid). Full 3×5 I_BV reference grid:

| Pair | Global | Mediterranean | Monsoon Asia | Tibetan |
|---|---|---|---|---|
| tmp×snw | −0.865 | −0.671 * | −0.413 * | −0.005 NS |
| ele×slp | +0.423 | −0.141 * | +0.347 * | −0.141 * |
| ari×pre | +0.578 | +0.743 * | +0.643 * | +0.638 * |
| pre×aet | +0.863 | +0.836 * | +0.829 * | +0.853 * |
| hdi×gdp | +0.581 | +0.581 * | +0.567 * | — |

Key findings (BV.14–19 in `logs/esda_findings.md`):

- **tmp×snw** near-redundancy collapses to NS (p=0.459) in Tibetan/cold-arid — both carry distinct information for high-altitude sites despite being globally near-redundant. Rubric implication: `snw` is NOT redundant with `tmp` in Tibetan/cold-arid zones.
- **ele×slp** sign-reversal in Tibetan (−0.141): plateau mechanism (high ele, gentle slp) inverts the mountain-building expectation. Mediterranean also NS. Both context-dependent.
- **ari×pre** amplified in all three regions vs. global (+0.578 → 0.64–0.74); no reversal. Most regionally stable "genuinely distinct" pair.
- **pre×aet** most stable pair overall (global 0.863 → 0.829–0.853 across all three regions). Mediterranean patch: orange HL cluster in Lebanese mountains / Syrian coastal range — orographic rainfall surrounded by dry Syrian interior. (Initial identification as Anatolian highlands was wrong; Karl corrected.)
- **Cross-regional synthesis**: pre×aet and ari×pre are regionally stable; tmp×snw and ele×slp are context-dependent (tier assignment carries a regional qualifier for polity-phase signatures).

---

## 2. CHAR completion prompt review — `prompts/cc_char_completion_prompt.md`

Opus 4.7 generated a 6-phase CHAR completion plan. CC reviewed and raised the following:

- **Phase 1 (categoricals)**: `Join_Counts_Local` availability should be confirmed before writing notebook — flagged as potential issue (confirmed problematic: see §3 below).
- **Phase 3 (bivariate redundancy)**: `ria_ha_ssu/usu` appears as two rows (row 69) in the codebook for a single variable (river area). Needs clarification before Phase 3.
- **Phase 2 (`dist_sink_km`)**: good catch — F4.8 covered correlation orthogonality but not spatial autocorrelation. Likely needs log-transform.
- **Band T issues**: deferred to Phase 4 design memo as specified.

Path corrections applied: `logs/esda_findings.md` (not `spatial/esda_findings.md`) and `docs/design/SpatialESDA_Phase2.md` (not `spatial/SpatialESDA_Phase2.md`).

---

## 3. Phase 1 CHAR — `13_categorical_coherence.ipynb`

### Notebook structure
Three categorical variables: `lith_class` (16 classes, n=190,675), `pnv_majority` (15 valid classes, n=190,675), `wetland_class` (12 classes, n=96,884 subset).

Wetland subset uses dedicated Queen weights `w_wet` (n=96,884, 1,096 islands, built in 64.6s). Full weights `w_full` (190,675, 568 islands) used for lith and pnv.

### Bug: psycopg3 integer NULL → int64 0 sentinel

`wet_cl_smj` column has SQL NULLs for non-wetland basins (49% of rows). psycopg3 loads integer columns with NULLs as int64 dtype (not nullable), so `.isna()` returns zero for all rows — the NULLs arrive as `0` instead of `NaN`. A `.notna()` filter produced all 190,675 rows instead of the expected ~96,884.

**Fix**: replaced `.notna()` with `.isin(wet_lu['id'].tolist())` — filters on known valid class IDs (1–12). Result: 96,884 basins as expected. **This applies to any integer categorical column loaded from the DB via psycopg3.**

### Bug: `esda.Join_Counts_Local` IndexError with islands

`Join_Counts_Local._statistic()` drops islands from the LJC array (size 190,107 = 190,675 − 568), but `_crand_plus` iterates over the full `z` array (size 190,675), raising `IndexError: index 190107 is out of bounds for axis 0 with size 190107`. This is a library bug in esda / Python 3.14.

**Fallback**: row-stochastic `W @ y` gives each basin the fraction of its Queen neighbours sharing class y. Threshold ≥ 0.5 (majority match) → "locally coherent"; < 0.5 → "isolated/edge". Deterministic, no p-value. Defensible given the overwhelming global z-scores.

### Global join-count results

All 43 class-variable combinations significant at p=0.001 (maximum resolution with 999 permutations). Z-scores: lith 296–723, pnv 448–638, wetland 222–519. No class fails significance.

### Local coherence results (neighbor-match)

| Variable | Range | Lowest class | Highest class |
|---|---|---|---|
| lith_class | 90.8%–99.5% | Basic Plutonic (PB) 90.8% | Ice/Glaciers (IG) 99.5% |
| pnv_majority | 93.0%–98.8% | Polar/rock/ice 93.0% | Desert 98.8% |
| wetland_class | 91.5%–99.5% | Lake 91.5% | 25-50% wetland 99.5% |

### Key findings (CAT.1–8 in `logs/esda_findings.md`)

- All three variables are appropriate EDOPS signature fields; none fail coherence.
- Lower-coherence classes are geologically / ecologically interpretable (isolated plutonic intrusions, fragmented montane habitats, scattered lake features) — real transition zones, not noise.
- `lith_class` map confirms geological province structure is preserved at L8 — the variable is a regional-scale descriptor, not a per-basin independent draw.
- **Scale implication**: categorical variables behave as region-selectors in the slider interface.

### Outputs
- `notebooks/edop/spatial/13_categorical_coherence.ipynb`
- `output/edop/spatial/13_categorical_coherence.csv` (43 rows: variable × class, global JC stats + local coherence)
- `spatial/13_categorical_cluster_maps.png`
- CAT.1–8 appended to `logs/esda_findings.md`

---

## Next

- Phase 2 CHAR: `14_dist_sink_esda.ipynb` — `dist_sink_km` univariate ESDA
- Then Phases 3–6 per `prompts/cc_char_completion_prompt.md`
