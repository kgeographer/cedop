# Session Log — 17 May 2026

## Participants
Karl Grossner, Claude Sonnet 4.6 (CC), Claude Opus 4.7 (consulted async)

## Context
esda branch. Previous session completed discharge notebook (03) and established esda_findings.md. This session: strategic discussion on ESDA value/scope; Phase 1 univariate sweep of all Band A–D variables; Phase 2 spatial typology notebook with extended conceptual discussion; Phase 3 bivariate T×P exemplar notebook — sign-off point for Phase 4.

---

## 1. Strategic discussion — ESDA value for EDOPS objectives

Karl raised the question: how does ESDA drive the actual research objectives (variable selection for social phenomena; rubric for variable selection by question type)?

**Conclusions**:
- ESDA has two genuine payoffs: (a) a redundancy map — identifying which variables are spatially collinear and informationally interchangeable vs. genuinely distinct; (b) LISA classes as structural position descriptors (HH/LL/HL/LH/NS contextualises a basin's value within the global pattern, enabling questions like DIS.1's interfluve/settlement question)
- ESDA does not directly drive the rubric — domain knowledge and correspondence tests do more work there
- Karl raised and Opus 4.7 affirmed that global concordance is not a valid redundancy filter: two variables can co-vary globally but decouple meaningfully within specific regions. The right tool is local bivariate Moran's I, not global I_BV as a scalar. CC's earlier "use one, drop the rest" framing was wrong and is not carried forward

**Practical implication**: Phase 1 sweep should be inclusive — exclude only categoricals, monthly arrays, and string fields. "Likely correlated" is not a valid exclusion criterion at the univariate stage.

---

## 2. Phase 2 plan established — `prompts/SpatialESDA_Phase2.md`

Opus generated a four-phase plan:
- Phase 1: univariate sweep Bands A–D → variable_characterization.csv + lisa_classifications.parquet
- Phase 2: spatial typology notebook (profile space plot, first-cut group assignment)
- Phase 3: exemplar bivariate — temperature × precipitation at L6 (sign-off point before Phase 4)
- Phase 4: selected bivariate pairs

Phase naming: `x_spatial` → `esda`, `x_polity` → `polity` (to match git branch names).

---

## 3. Phase 1 sweep — `scripts/edop/esda/12_spatial_moran.py`

### Variable list
40 Band A–D continuous variables. All "likely correlated" exclusions removed per Opus's redundancy argument. `snd_pc_sav` (sand) included — compositional constraint only applies in multivariate models, not univariate ESDA. `dor_pc_pva` (degree of regulation) added at Karl's request — of significant interest for users studying water management.

### Script issues found and fixed
1. **Missing pyarrow**: `save_staging` failed silently on every variable. Fix: `check_dependencies()` at startup fails fast with install instruction before any data is loaded.
2. **Write ordering bug**: `append_csv` ran before `save_staging`, so checkpoint marked variables as done even when staging failed. Fix: staging written first, CSV appended only after both succeed.
3. **BasinATLAS -9999 sentinel**: masked in `prepare_values` as `vals[vals == -9999] = np.nan` before scale_factor and before log-transform decision. Sentinel must be masked before the `min ≥ 0` check, or variables like `snw_pc_syr` are incorrectly excluded from log transform and their I values destroyed (snw I: 0.021 → 0.975 after fix). Confirmed in basin06: slp (302), sgr (412), cly/slt/snd/soc (757 each), snw (5).
4. **Output path**: moved from `output/edop/explore/` to `output/edop/esda/` to match phase organisation.
5. **Script location**: `scripts/edop/esda/` not `scripts/edop/explore/` — explore was the EDA phase.

### Results
Full L6+L8 sweep completed. See SW.1–3 in `spatial/esda_findings.md` for complete table and findings.

Key findings:
- 36/40 variables ↑ (I increases with finer resolution); 4 ↓ (dis annual, dis min, dor, silt≈flat)
- Discharge monthly max ↑ despite annual/min ↓ — three mechanisms in one variable family
- Band C ceiling at L8: PET/tmp/snw/ari/aet all ≥ 0.992
- Band D (HDI 0.987, GDP 0.943) as spatially autocorrelated as climate — wealth clusters continentally as strongly as PET
- Erosion rate largest scale gain (Δ+0.181); dor_pc_pva highest outlier% (5.93%)

---

---

## 4. Phase 2 — Spatial typology notebook (`04_spatial_typology.ipynb`)

### Threshold adjustment
`OUTLIER_HIGH` raised from 2.50 → 3.00 in Cell 8. Effect: `dis_m3_pmx` (outlier%=2.67) moved from local-anomaly to mixed; `ria_ha_ssu` (outlier%=3.52%) remains sole local-anomaly member. `dor_pc_pva` (5.93%) is caught by the network-topology rule first (Δ_I = −0.053) and never reaches the outlier test.

**Final group counts**: continental-gradient=21, mixed=15, network-topology=3, local-anomaly=1.

### Cell numbering
Convention clarified: `# Cell N` counts ALL cells (markdown + code) from top. Applied retroactively to notebook 04 (Cells 2, 3, 5, 6, 8, 9, 10, 11). Previous notebooks already had this convention.

### Outputs
`spatial/first_cut_typology.csv` saved with OUTLIER_HIGH=3.00 results.

### Extended conceptual discussion — typology semantics and rubric design

Karl raised questions about what the typology group labels actually do for variable selection. Key points resolved:

1. **What the groups do**: They characterise the *type of spatial claim* a variable supports — continental-gradient for macro-environment positioning, network-topology for river-hierarchy positioning, local-anomaly for point-feature signals. The groups are not redundancy filters; they describe what question a variable answers.

2. **Historical validity axis**: Bands A–D were developed without distinguishing historical from modern validity. Provisional ratings established:
   - Band A (topography, slope, stream gradient): stable on geological timescales
   - Band B (soils, hydrology, wetlands, glaciers): stable-to-variable; `dor_pc_pva` modern-only
   - Band C (climate): pattern-stable proxies — spatial pattern valid historically; point values not
   - Band D (HDI, GDP, NLI, HFT): modern only; historical versions in Band T / HYDE

3. **Environment/culture boundary**: Karl raised Ruth's position that land use IS the environment (physically present), complicating a simple environment vs. culture split. Proposed resolution: replace environment/culture binary with *process origin × timescale* matrix. The lower-left diagonal (physical/geological × geological timescale) is unambiguously environment; the upper-right (human-agency × centennial) is where Ruth's position has force.

4. **Expert system risk**: A full decision-tree rubric (question type × temporal register × spatial group × origin × timescale stability) is qualitatively different from a two-page researcher guide — closer to an inference engine, with corresponding maintenance and explainability costs.

### Design document
`docs/design/variable_selection_rubric_issues.md` drafted. Status: discussion draft for 3-way follow-up with Opus 4.7 after Phase 3. Six sections: spatial typology semantics, historical validity ratings, environment/culture boundary, expert system risk, questions for Opus, deferred ecoregion↔EDOPS correspondence test.

---

## 5. Phase 3 — Bivariate T×P exemplar notebook (`05_bivariate_TP_l6.ipynb`)

### Purpose
Validation test: the T×P coupling structure is well-understood before computing. Phase 3 confirms that regional stratification recovers the known geography (Mediterranean decoupling, cold-arid co-clustering, monsoon heterogeneity) that the global scalar I_BV would obscure.

### Global results
- I_BV(T→P) = +0.315, p=0.001 — globally warm = wet (tropics vs poles axis)
- LISA: HL dominant (18.2%, hot deserts) despite positive I_BV; HH=15.7%, LL=14.0%, LH=1.0%
- Positive global I_BV reflects poles-vs-tropics gradient; HL documents the hot-desert decoupling

### Regional stratification
| Region | n | I_BV | p | Key LISA class | Result |
|---|---|---|---|---|---|
| Mediterranean | 140 | −0.250 | 0.001 | HL 12.1% | Sign reversal confirmed |
| Monsoon Asia | 957 | −0.046 | 0.076 | HL 22.2% | Not significant; HL > HH |
| Tibetan/cold-arid | 331 | +0.608 | 0.001 | LL 26.6% | Cold-dry co-clustering |

**Mediterranean sign reversal** (I_BV = −0.25 vs global +0.315): the single most important result of Phase 3. Within a 140-basin geographic zone the T×P relationship is not just weaker than the global value — it is inverted. Summer drought mechanism: warm season is dry; cooler winters bring cyclonic rain.

**Monsoon Asia negative result**: Indomalaya as a realm is too internally heterogeneous to show coherent T×P coupling. Very wet coastal/windward zones (HH) and hot-dry interior basins (HL) partially cancel; I_BV not significant. Useful for Phase 4 design — Indomalaya should be subdivided, not treated as a single zone.

**Tibetan LL dominance**: altitude drives cold and dry simultaneously → strongest regional I_BV (+0.61) in the dataset for this pair.

### Bugs encountered and fixed
1. **eco847 join produced 0 rows**: `JOIN public.eco847 g ON g.eco_id = e.eco_id` with `ST_AsText(g.geom)` caused a silent 0-row result. Fix: use `ST_AsText(e.geom)` from `gaz."Ecoregions2017"` directly; remove eco847 join.
2. **Mediterranean = 0 basins (centroid approach)**: Mediterranean ecoregion polygons are narrow coastal scrubland zones; L6 basin centroids sit far inland (e.g., Po basin centroid in Alps). Fix: switch from `predicate='within'` on centroids to `predicate='intersects'` on full basin polygons. Mediterranean: 0 → 140 basins.
3. **RuntimeWarning: invalid value in divide (Cell 11)**: 284 island basins have zero permutation variance → z_sim = 0/0. Harmless — they land as NS.

### Ecoregion/bioregion terminology clarification
`eco847` = RESOLVE/WWF 2017 Ecoregions (847 units, uses `biome_name` column) — not the same as OneEarth. The workbench ecoregion tab draws from `gaz.Ecoregions2017` / `gaz.Bioregions2023` / `gaz.Subrealm2023` / `gaz.Realm2023` — the OneEarth hierarchy. Regional stratification in notebook 05 correctly uses OneEarth geographic subrealms for geographic precision (not biome-thematic dispersal).

### Outputs
- `spatial/bivariate_TP_global.png` — global LISA map
- `spatial/bivariate_TP_regions.png` — 3-panel regional maps
- `spatial/esda_findings.md` BV.1–BV.6 added

### Phase 3 verdict: **pass** — proceed to Phase 4

---

## Next

- Phase 4: selected bivariate pairs (Karl sign-off required before starting)
- Design document discussion with Opus 4.7 (`docs/design/variable_selection_rubric_issues.md`)
- `polity` branch after ESDA complete
