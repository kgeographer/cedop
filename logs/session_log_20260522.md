# Session Log — 22 May 2026

## Participants
Karl Grossner, Claude Sonnet 4.6 (CC)

## Context
`esda` branch. Continuation from 2026-05-21 session. Phase 4a CHAR: Band T native-unit visual EDA — `16a_band_t_native_choropleths.ipynb`. Execution prompt: `prompts/cc_band_t_native_prompt.md`.

---

## 1. Phase 4a CHAR — `16a_band_t_native_choropleths.ipynb`

Notebook executed in full. All LMR and HYDE choropleth series produced, stats persisted to CSV, findings cell completed (BT4A.1–BT4A.5).

### Technical issues resolved during session

**Mollweide projection for HYDE global maps (Cell 14)**:  
Cell 14 still used the old PlateCarree + `imshow` multi-panel layout from before projection was settled. Updated to match the LMR approach: Mollweide + `pcolormesh` with 0.5° subsample (every 6th native 5-arcmin cell → ~260k display points). Native arrays preserved in `crop_grids`/`graz_grids` for regional zooms and 4b.

**New function signature for HYDE global helper**:  
`plot_hyde_global` signature changed from `(grids, var_label, fname)` → `(grids, var_label, subfolder, file_prefix)`. Writes one PNG per epoch to `output/edop/spatial/<subfolder>/`. Calls in Cells 15 and 17 updated.

**Zoom function signature mismatch (Cell 16/18 TypeError)**:  
`plot_hyde_zoom` updated to 9-arg signature `(..., subfolder, fname)`. Cell 18 had the new call but the kernel still held the old 8-arg definition from the previous Cell 16 run — raised `TypeError: takes 8 positional arguments but 9 were given`. Fix: re-run Cell 16 to redefine, then Cell 18 succeeds.

**Zoom files in wrong directory**:  
First run of Cell 16 wrote zoom PNGs to `output/edop/spatial/` root (old `OUT_DIR / fname` path). Moved to `hyde_cropland/` via bash and updated Cell 16 to write to `out / fname` (subfolder-aware). Duplicate named files from old naming convention (`16a_hyde_cropland_zoom_*.png`) also present in subfolder; new names are `cropland_zoom_*.png`.

**Missing HYDE stats (Cell 12b added)**:  
Cell 12 printed cropland non-zero fractions only and did not persist to disk. Added Cell 12b after Cell 12: computes non-zero % and total km² for both cropland and grazing at all 8 epochs, writes `hyde_epoch_stats.csv`. Runs from in-memory `hyde_df`, no re-query needed.

**LMR land mask — confirmed deferred to 4b**:  
Karl asked whether the LMR land mask (~5,000 L8-basin-bearing cells, per F10.5) had been skipped. Confirmed: mask is not needed for 4a visual EDA (LMR ocean values are real and correctly plotted). It will be applied in 4b to restrict Moran's I computation to land cells relevant to EDOPS basin signatures. Notebook header documents this explicitly.

### Outputs produced

**LMR** (6 epochs each, Mollweide, anomaly vs 0–1998 CE mean):
- `output/edop/spatial/lmr_temperature/temperature_{0ce,1000ce,1500ce,1900ce,mca,lia}.png`
- `output/edop/spatial/lmr_pdsi/pdsi_{0ce,1000ce,1500ce,1900ce,mca,lia}.png`
- `output/edop/spatial/lmr_temperature_regional_means.csv`
- `output/edop/spatial/lmr_pdsi_regional_means.csv`

**HYDE** (8 epochs each, Mollweide global + 3 regional zooms at 1000/1900/2000 CE):
- `output/edop/spatial/hyde_cropland/cropland_{8000bce,4000bce,1000bce,0ce,1000ce,1500ce,1900ce,2000ce}.png`
- `output/edop/spatial/hyde_cropland/cropland_zoom_{fertile_crescent,north_china_plain,mesoamerica}.png`
- `output/edop/spatial/hyde_grazing/grazing_{8000bce,...,2000ce}.png`
- `output/edop/spatial/hyde_grazing/grazing_zoom_{fertile_crescent,north_china_plain,mesoamerica}.png`
- `output/edop/spatial/hyde_epoch_stats.csv`

### Key findings (BT4A.1–BT4A.5, full text in notebook findings cell)

**BT4A.1 — LMR temperature**:
- LIA is the strongest signal: NH −0.19 K, Arctic −0.47 K (Arctic/NH ratio 2.5×). Cooling concentrated in subarctic Eurasia along the tree-ring proxy band, not uniform NH cooling — first-class proxy-network bias caveat.
- MCA registers negative throughout (NH −0.07, Arctic −0.10) relative to 0–1998 baseline. The small warm patch over Greenland/Iceland is overwhelmed in the zonal mean. MCA ≠ "Medieval Warm Period" in LMR.
- 0 CE artifact: NH +0.14, Arctic +0.26 — almost certainly model-prior dominance at low proxy density, not Roman Warm Period signal.
- SH signal weak (≤ 0.04 K) at all epochs except 1900 CE (−0.08).

**BT4A.2 — LMR PDSI**:
- All regional zonal means ≤ 0.03 units. PDSI has no coherent hemispheric signal at epoch timescales; content is in geographic (spatial) patterns, not zonal averages.
- LIA spatial pattern (Karl's map read): SW/Central Asia dry; N. Atlantic/N. Europe wet; Sub-Saharan Africa and parts of S. America wet — heterogeneous, offsetting regionally.
- PDSI and temperature patterns are geographically distinct: independent spatial information in the two Band T variables.

**BT4A.3 — HYDE cropland**:
- Both sanity checks pass: 4000 BCE shows Fertile Crescent/Yangtze hotspots only; 1000 CE shows developed footprints in Mediterranean, Indus/Ganges, N. China, Mesoamerica.
- 8000 BCE degenerate (0.27% non-zero); all other epochs above 5% threshold.
- Post-1500 acceleration: 1.5× growth per 500 years pre-1500 → 3.3× in 400 years post-1500. Dominant trajectory shape.

**BT4A.4 — HYDE grazing**:
- Grazing consistently 1.2–2.7× cropland total area throughout. Earliest large footprint ratio (4000 BCE: 2.7×) reflects pastoralism preceding intensive cultivation.
- 8000 BCE degenerate (1.35% non-zero).
- Notable anomaly: grazing non-zero % *drops* 1900→2000 CE (64.16% → 58.77%) while total km² more than doubles (15.6M → 32.8M). Intensification + marginal-land abandonment in HYDE model; flagged for 4b interpretation.

**BT4A.5 — Pipeline**:
- Both LMR and HYDE pipelines confirmed and documented with row counts, rasterization timing, and output paths.

---

---

## 2. Phase 4b CHAR — `16b_band_t_native_esda.ipynb`

Notebook executed in full. LMR Moran's I + LISA complete; HYDE Moran's I sweep complete; HYDE LISA pilot run (intractable for full sweep). Findings BT4B.1–BT4B.3 written.

### Technical issues and decisions

**RuntimeWarning suppression**: `warnings.filterwarnings("ignore", message="invalid value encountered")` added to Cell 2 (esda `seI_sim` divide-by-zero in near-zero anomaly epochs — harmless, p-values from permutation rank not z-score). Applied after Cell 9 had already run; kernel already held results.

**Cell 9 LISA output appeared incomplete**: RuntimeWarning stderr interleaved with stdout in Jupyter, making epoch print lines invisible. Confirmed complete: `len(lmr_lisa_rows)` = 59,088 = 4,924 × 12.

**Cell 10 redesigned** (trajectory bar chart → 2×2 grid): Original bar chart showed flat wall of red bars (all I ~0.93–0.97, all significant). Replaced with: top row = zoomed line plots with annotated I values; bottom row = 100% stacked bar of LISA class composition per epoch. LISA composition charts showed the actual story (HH/LL/NS shifts across epochs).

**HYDE LISA intractable**: Pilot LISA (cropland 1000 CE) took 2,247s (~37 min) — permutation matrix 999 × 2.2M cells ≈ 17 GB RAM, caused disk swap. Full sweep projected at 8.9 h. Decision: drop LISA from sweep; run Moran's I only. Cells 14–15 updated accordingly. Pilot LISA counts retained for structural characterisation (`band_t_native_hyde_lisa_pilot.csv`).

**Cell 16 epoch ordering bug**: Pilot result (cropland 1000 CE) prepended to `hyde_moran_rows` before sweep, so it appeared first in the chart. Fixed by sorting rows into `HYDE_CHRON` order before plotting.

**HYDE LISA pilot interpretation**: LL=59.1% flagged as zero-inflation artifact — 73.9% of cells have zero cropland, so LL overwhelmingly identifies contiguous non-agricultural zones, not agricultural geography. HH=5.7% (~126k cells) is the substantive class.

**LMR PDSI vs temperature I**: Karl asked about the consistent PDSI < temperature I gap (0.04–0.09). Confirmed as a known climate property: moisture fields have shorter spatial correlation length scales than thermal fields at all scales (orographic effects, storm tracks, ENSO), reflected in both real observations and WMO network design guidelines. LMR methodology amplifies the difference (temperature proxies have longer correlation length scales than moisture proxies).

**HYDE cropland/grazing zero-sum question**: Not zero-sum globally — both expand at the expense of natural vegetation. Total agricultural land grows from ~350k km² (4000 BCE) to ~48M km² (2000 CE). Competition is local (pastoral-to-arable transitions); the global constraint is total habitable land (~130M km²), not a cropland/grazing budget.

### Outputs produced

- `output/edop/spatial/band_t_native_moran.csv` — 26 rows (12 LMR + 14 HYDE), all p=0.001
- `output/edop/spatial/band_t_native_lmr_lisa.parquet` — 59,088 rows, 17.7 MB
- `output/edop/spatial/band_t_native_hyde_lisa_pilot.csv` — HYDE pilot LISA class counts (5 rows)
- `output/edop/spatial/lmr_moran_trajectory.png` — 2×2 LMR I trajectory + LISA composition
- `output/edop/spatial/hyde_moran_trajectory.png` — HYDE I trajectory (cropland + grazing)

### Key findings (BT4B.1–BT4B.3, full text in notebook findings cell and esda_findings.md)

**BT4B.1 — LMR temperature**: I range 0.931–0.974; LIA lowest (regional NH cooling breaks global coherence); 0 CE LL=39.6% (proxy-sparse model prior artifact); LIA HH > LL despite cooling; temperature LH=0 in all epochs.

**BT4B.1 — LMR PDSI**: I range 0.856–0.888, consistently below temperature; MCA lowest and most diffuse (highest NS%); PDSI HL peaks at LIA/1900 CE.

**BT4B.2 — HYDE pilot**: 2.2M cells, queen weights 9s. LISA intractable; LL=59.1% zero-inflation artifact; HH=5.7% = genuine agricultural cores.

**BT4B.3 — HYDE sweep headline**: Cropland I rises 0.59 (4000 BCE) → 0.92 (2000 CE); grazing starts already at 0.91 (4000 BCE) and stays there throughout. Gap closes by 2000 CE. Cropland required ~6,000 years to achieve the spatial coherence pastoralism had from the outset.

---

## Next

- **Phase 4c** (paused): `16c_band_t_native_cross_temporal.ipynb` — HYDE persistence map + LMR MCA–LIA dipole structure.
