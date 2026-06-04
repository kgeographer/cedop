# Session Log — 01 June 2026

## Participants
Karl Grossner, Claude Sonnet 4.6 (CC)

## Context
First session on the new Explorer page feature. CHAR phase is complete; `main` branch at start; new `explorer` branch created at end of session. Design document is `docs/design/EDOPS_explorer_cc_prompt.md`; wireframe is `docs/design/images/explorer_wireframe_v0.3.png`.

---

## 1. LISA Parquet Inventory

### Task
Determine exactly what per-basin LISA classification data exists on disk and what is missing, ahead of Explorer build.

### Findings
Three parquet files in `output/edop/`:

**`esda/lisa_classifications.parquet`** — 7,866,866 rows × 7 cols (`variable`, `scale`, `hybas_id`, `lisa_class`, `p_value`, `local_I`, `quad`):
- **L8: complete** — 41 variables × 190,675 basins (all scalar A–D variables from sweep)
- **L6: nearly absent** — only 3 variables (`ari_ix_sav`, `dist_sink`, `dor_pc_pva`) × 16,397 basins

**`spatial/bivariate_redundancy.parquet`** — 2,097,425 rows, L8 only, 11 bivariate pairs. Not used by Explorer.

**`spatial/band_t_native_lmr_lisa.parquet`** — 59,088 rows, Band T (LMR) only at native 2° grid. Not used by Explorer static-band view.

### Key gap
L6 LISA sweep was never run to completion for most variables. Full L6 sweep (same 41 variables + `tmp_dc_smn` + `tmp_dc_smx` which were missed) needed before the Explorer's LISA toggle works at L6. Added to Explorer task list.

### Codebook cross-check
13 implemented variables are absent from the LISA parquet: 10 categorical IDs (handled via join-count stats, not Moran's I), 2 missed continuous scalars (`tmp_dc_smn`, `tmp_dc_smx`), and 1 boolean (`coast_flag`). No upstream (`u`) columns were swept — sweep was `s`-only.

---

## 2. Explorer page — Steps 1–3

### Route changes (`app/web/pages.py`)
- `/sandbox` → 301 redirect to `/sandbox/lookup`
- `/sandbox/lookup` → existing `sandbox.html` (unchanged)
- `/sandbox/explorer` → new `explorer.html`

### Sandbox header update (`app/templates/sandbox.html`)
Breadcrumb changed from `EDOPS / Sandbox` to `EDOPS / Sandbox: **Lookup** | Explorer` with Explorer as a link. Small cross-link added below the place lookup card: "Want to see how variables distribute globally? → Open Explorer".

### Explorer skeleton (`app/templates/explorer.html`)
New standalone template (same Bootstrap/Leaflet/GA4 head as sandbox.html):
- 25% / 75% two-column layout
- **Left column**: search box, All/Implemented/Planned radio group (btn-group), class dropdown with `?` tooltip, accordion placeholder (dashed border, 500px)
- **Right column**: Map / Diagnostics (disabled) / Compare (disabled) tab bar; control strip with s/u/Δ toggle (hidden), Values/LISA toggle, L6/L8 radio; variable header strip; live Leaflet OSM map at global zoom; histogram strip placeholder (~110px, dashed border)
- Placeholder areas use `ex-placeholder` class (dashed border, centered label) so proportions are visible without data

---

## Next
- Step 4: add Leaflet map (already present in skeleton — confirm tile layer and bounds on review)
- Left column: populate accordion from codebook (`/api/explorer/codebook` endpoint)
- L6 LISA sweep: rerun `12_spatial_moran.py --l6-only` to fill gap in parquet
- Resolve categorical variable rendering design (left-column screen real estate, legend cardinality)
