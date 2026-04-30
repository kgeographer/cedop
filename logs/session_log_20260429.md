# Session Log — 2026-04-29

## Branch: sigrefine01

## What was completed today

### 1. DB connection reliability fix
`scripts/shared/db_utils.py` and `app/db/connection.py` both updated to use an explicit `load_dotenv` path relative to `__file__`, so `.env` is found regardless of working directory. Removed implicit reliance on port 5432 default — DB is on port 5435. Both tested and confirmed.

### 2. HYDE 3.4 database pipeline (commit 8366f74)

**Schema** (`sql/edop/create_hyde_cells.sql`):
- `temporal.hyde_times`: 128-row lookup, step_idx → year_ce (astronomical)
- `temporal.hyde_cells`: 2,215,829 rows; cell_id, geom (Polygon 4326), area_km2, cropland[], grazing[], pasture[], rangeland[] (real[], 128 time steps each)

**Load script** (`scripts/edop/load_hyde_cells.py`):
- Reads 4 NetCDF files in lat strips of 200 rows (~900MB peak)
- Inserts 2,215,829 cells in 5,000-row batches; total load 23.7 min
- Computes area_km2 via `ST_Area(geom::geography) / 1e6` after insert
- Builds GIST index on `geom`, functional GIST index on `ST_Centroid(geom)`, runs `ANALYZE`

**Key finding**: without the functional centroid index, spatial join does a full seq scan (6.7s). With it: ~640ms cold-cache, ~300ms warm-cache for an L8 basin. L6: ~30ms. Window size (3–128 steps) barely affects cost — spatial join dominates.

### 3. Query design notebook (`notebooks/edop/hyde_query_design.ipynb`)
13 cells: connection verification, time axis display, basin id resolution, cell counts, step-count-per-window table, aggregation queries at L8/L6 (narrow/broad/full), polygon proxy query (Cliopatria simulation), response shape validation, timing summary.

### 4. `app/db/hyde.py`
Two public functions:
- `get_hyde_land_use(lat, lon, from_year, to_year, level=8)` — resolves hybas_id from point, then aggregates
- `get_hyde_land_use_for_basin(hybas_id, from_year, to_year, level=8)` — direct hybas_id interface for scripts/tests

Response structure per epoch:
```json
{
  "year_ce": 1000,
  "cropland_km2": 0.079, "grazing_km2": 4.705,
  "pasture_km2": 0.0, "rangeland_km2": 4.705,
  "basin_area_km2": 573.4, "n_cells": 7,
  "cropland_pct": 0.01, "grazing_pct": 0.82,
  "pasture_pct": 0.0, "rangeland_pct": 0.82
}
```
`_pct` = variable_km2 / basin_area_km2 × 100 (spatial coverage of basin, not a cell average).
SQL uses `::float8` throughout — psycopg3 returns native Python floats, no Decimal issues.

### 5. Wired into routes.py
`get_hyde_land_use` imported and called in Band T block. Result stored at `profile_groups["T"]["hyde_land_use"]`. Confirmed live via curl at Timbuktu 1000–1200 CE.

### 6. Exploration log findings F8.8–F8.10 added to Task 8
- F8.8: HYDE temporal resolution structure (millennial/centennial/decadal/annual); BCE caveat
- F8.9: spatial join performance; functional index requirement; timing results
- F8.10: response shape validated; notes-in-payload principle extends to HYDE

## Key decisions made

- **Option A confirmed**: return all overlapping epochs within window (not single nearest)
- **pct semantics**: fraction of basin area covered, not cell average
- **No pre-materialized basin→cell lookup needed**: live spatial query ~640ms cold-cache is acceptable
- **Band C land_cover_id/name already present** — was not a pending item after all
- **SQL uses `::float8`** to avoid Decimal type from psycopg3

## Completed later in session (sigrefine01 → main, deployed)

### 7. Band D — pasture_extent (commit 15459f0)
- `pst_pc_sse`/`pst_pc_use` added to both persist_rev1 view SQL files
- Views dropped and recreated in local DB (no dependents)
- `SIGNATURE_SQL_TMPL` and `PROFILE_GROUPS["D"]` updated in `signature.py`
- Confirmed in API: Timbuktu `pasture_extent: 3, pasture_extent_upstream: 3`

### 8. HYDE heterogeneity stats added to hyde.py (commit 15459f0)
- `_AGG_SQL` extended with `STDDEV_POP` for all 4 variables + `percentile_cont(0.1/0.9)` for cropland and grazing
- `_build_epochs` switched from positional tuple unpacking to `dict_row` cursor
- Heterogeneity fields (`_std`, `_p10`, `_p90`) emitted only when `n_cells > 1`
- Kaifeng example: `grazing_std=1.094` vs mean cell 0.67 km² — confirms patchy Sahel signal

### 9. Codebook v02 (commit 15459f0)
- `metadata/edops_codebook_v02.tsv` created from v01
- `pasture_pct` → `implemented` + api_key_s/u filled
- 4 new Band T rows: `hyde_cropland`, `hyde_grazing`, `hyde_pasture`, `hyde_rangeland`
- `signature.py` codebook pointer updated to v02
- All 13 tests pass

### 10. Band T accordion redesign (commit 0493ef7)
Three top-level tabs: **Climate (LMR 2.1)** / **Land use (HYDE 3.4)** / **Volcanic events (eVolv2k)**
- LMR quality note and grid-cell header moved inside Climate tab
- Volcano table moved to its own tab
- HYDE tab: two SVG sparklines — cropland bar chart with p10/p90 band; stacked grazing bar (pasture/rangeland split) with p10/p90 band on total
- Band interpretation: tall light band above short bar = patchy; band flush with bar = uniform. Kaifeng 1000–1100 CE clearly shows agricultural expansion (patchy → uniform cropland over one century)
- vMax clipping fix (commit after review): p90 projected values included in vMax so bands are never clipped at chart ceiling
- Tooltips reworded to explain patchy-vs-uniform interpretation

### 11. data_sources fix (commit c08317b)
- `land_use_temporal: "HYDE 3.4 (Klein Goldewijk et al. 2017); 10000 BCE–2023 CE; ~10 km resolution"` added to signature payload `data_sources`

### 12. Prospectus v29 Apr (commit b50c953)
New file `docs/edop/prospectus_20260429.md` (Apr 16 file untouched). Additions flagged `[Rev. 29 Apr]`:
- HYDE 3.4 as third temporal enrichment dataset
- LMR implementation status, 1000–1850 CE baseline convention, geographic proxy bias as first-class limitation, eVolv2k/LMR decoupling principle
- HYDE within-basin heterogeneity design rationale; Kaifeng example
- New subsection: qualifying notes as first-class payload content
- Section 7: LMR precision ceiling (~200 km), HYDE/EarthStat divergence, population density status — all deferred to Oct 2026 expert meeting
- Section 8: HYDE added to temporal enrichment novelty claim
- Section 10: October 2026 ISHI expert meeting named as formal forum for deferred questions

### 13. Merge and deploy
- sigrefine01 merged to main (fast-forward), pushed
- Hetzner: `git pull` → view recreation → hyde_times + hyde_cells pg_dump/restore (2,215,829 rows, both GIST indexes confirmed) → `systemctl restart cedop`
- Production verified: `pasture_extent: 3`, `pasture_extent_upstream: 3`, `HYDE epochs: 3` at Timbuktu 1000–1200 CE
