# Session Log — 21 May 2026

## Participants
Karl Grossner, Claude Sonnet 4.6 (CC), Claude Opus 4.7 (Phase 4 planning, async)

## Context
`esda` branch. Continuation from 2026-05-19 session. Phase 3 CHAR: within-band bivariate redundancy. Phase 4 design and planning.

---

## 1. Phase 3 CHAR — `15_bivariate_redundancy.ipynb`

Notebook written and executed for all 11 high-correlation pairs (r > 0.9 from F4.9) at L8. Two groups:

**S/U pairs (5):** tmp_dc_syr×uyr, pre_mm_syr×uyr, ari_ix_sav×uav, hft_ix_s09×u09, crp_pc_sse×use

**Same-band non-S/U pairs (6):** dis_m3_pyr×pmn, dis_m3_pyr×pmx, dis_m3_pmx×ria_ha_usu, hdi_ix_sav×gdp_ud_sav, tmp_dc_syr×smn, tmp_dc_smn×uyr

### Bugs fixed during execution
- `Moran_BV.__init__()` does not accept `seed=` kwarg in this esda version → replaced with `np.random.seed(SEED)` before each call
- `fig.savefig()` failed with `FileNotFoundError` because Jupyter kernel runs from notebook directory, not repo root → patched Cell 2 to derive `REPO_ROOT` from `cwd`: `_cwd if (_cwd/'spatial').exists() else _cwd.parents[2]`
- `REPO_ROOT` not in kernel after partial re-run → patched Cell 19 to use `PARQ_OUT.parent` instead

### Full I_BV reference grid (L8, p=0.001 for all)

**S/U pairs:**

| Pair | I_BV | HL% | LH% | NS% |
|---|---|---|---|---|
| T_yr s×u | 0.989 | 0.2 | 0.0 | 38.0 |
| P_yr s×u | 0.963 | 0.2 | 0.0 | 49.1 |
| Ari s×u | 0.978 | 0.3 | 0.0 | 60.1 |
| HFT s×u | 0.826 | 0.3 | 0.3 | 48.1 |
| Crop s×u | 0.867 | 0.1 | 0.4 | 39.9 |

**Same-band non-S/U:**

| Pair | I_BV | HL% | LH% | NS% |
|---|---|---|---|---|
| Dis_yr × Dis_min | 0.525 | 1.9 | 3.5 | 52.1 |
| Dis_yr × Dis_max | 0.538 | 0.4 | 3.8 | 59.8 |
| Dis_max × RiverArea_u | 0.455 | 0.4 | 3.6 | 71.8 |
| HDI × GDP | 0.587 | 4.5 | 0.0 | 50.6 |
| T_yr × T_min | 0.969 | 0.2 | 0.0 | 39.1 |
| T_min × T_yr_u | 0.965 | 0.2 | 0.0 | 38.0 |

### Key findings (BVR.1–7 in `logs/esda_findings.md`)

- S/U divergence globally rare (0.2–0.6%); anthropogenic pairs (HFT, Crop) show most
- Discharge I_BV (0.45–0.54) falls below univariate I (~0.56): seasonal regime geography is independent spatial signal not captured by annual mean
- Discharge LH >> HL in all three pairs: perennial baseflow (Dis_min) and flood-pulse (Dis_max) transitions map to different geographic zones
- Temperature triple (T_yr, T_min, T_yr_u) spatially interchangeable — nearly identical LISA distributions
- HDI×GDP: HL=8,566 basins (4.5%), LH=7 (0.004%) — development geography one-directional

### Outputs
- `notebooks/edop/spatial/15_bivariate_redundancy.ipynb`
- `output/edop/spatial/bivariate_redundancy.parquet` (2,097,425 rows)
- `output/edop/spatial/bivariate_redundancy_counts.csv`
- `spatial/15_bivariate_redundancy_su.png`, `spatial/15_bivariate_redundancy_sb.png`

---

## 2. Design discussion

### Geographic determinism
Karl raised the tension between accumulating evidence of environment-development correlation and the academic prohibition on deterministic language, tracing the prohibition to the contamination of legitimate structural-ecological claims by early 20th century racial determinism (Huntington et al.). Agreed that the modern evidence (Sachs, Diamond, Hibbs-Olsson) is functionally deterministic in framing but uses probabilistic hedges for social reasons. EDOPS data contributes to this body of evidence. The heterodox position: the hedge is primarily a social norm, not an epistemic requirement.

### No variable pruning from signature
**Explicit design decision:** no EDOPS signature variables will be removed based on global spatial co-variation. Global bivariate concordance characterises the typical relationship; at L8 basin scale, variables that covary globally may carry distinct local information. The HL/LH divergence zones — often the ecologically and historically most interesting configurations — are where this matters most. Phase 3 findings are documentation, not a pruning pass. Saved to memory: `project_no_variable_pruning.md`.

### Band T / comparability
Karl clarified: Band T and Bands A–E are already fully separated in the EDOPS design; no "mixing" risk exists at the characterization level. For CHAR, each dataset should be characterized in its own terms at its native resolution. The basin-projection question is downstream of CHAR, not part of it.

---

## 3. Phase 4 planning — Band T native-unit characterization

CC provided high-level framing for LMR/HYDE approach: characterize LMR via temporal volatility and epoch-windowed means at native 2° grid; characterize HYDE as epoch trajectory of spatial autocorrelation. Karl took this to Opus for planning conversation.

**Result:** `prompts/cc_band_t_native_prompt.md` — new Phase 4 operational prompt drafted by Opus 4.7. This supersedes the Phase 4 design-memo scope in `cc_char_completion_prompt.md`.

**Call on design memo:** `docs/design/lmr_hyde_esda_design.md` not created — the new prompt resolves all design questions in operational form; a separate memo would be redundant.

---

## Next

- **Phase 4 CHAR (new session):** `cc_band_t_native_prompt.md` — three sub-phases:
  - 4a: `16a_band_t_native_choropleths.ipynb` — visual EDA, choropleth series
  - 4b: `16b_band_t_native_esda.ipynb` — spatial autocorrelation at native grids
  - 4c: `16c_band_t_native_cross_temporal.ipynb` — HYDE persistence + LMR MCA–LIA dipole
- **Phases 5–6 CHAR** (after Phase 4): position attribute spec, CHAR appendix
- **Then: `polity` phase**
