# Session Log — 06 June 2026

## Participants
Karl Grossner, Claude Sonnet 4.6 (CC)

## Context
New work strand: Cliopatria polity viewer. Karl is authoring an updated project summary
and had questions about existing data/citations along the way. Main session output is a
working polity viewer page (`/polities`) backed by three new API endpoints.

---

## 1. Housekeeping / research questions

- **Aridity index map series (Northern Song)** — Karl concerned the color mapping might
  be reversed. Confirmed correct: `edops_polity_maps.py` line 44 uses `RdYlBu` (unreversed),
  so red = low AI = arid, blue = high AI = humid. Maps accurately show Song expansion
  southward into more humid territory.

- **Codebook promoted**: `edops_codebook_v03_draft.tsv` → `edops_codebook_v03.tsv`
  (both files still present; v03 is canonical going forward).

- **s/u variable count**: 37 BasinATLAS variables carry both local (s) and upstream (u)
  values across Bands A–D, covering elevation, terrain, geology, cryosphere, soils,
  surface water, wetlands, groundwater, inundation, moisture balance, precipitation,
  temperature, vegetation, human presence, land use, and water management.

- **Elevation source**: point elevation uses OpenTopoData (Mapzen DEM, ~30m) primary,
  Open-Meteo elevation API fallback. Both live at query time. BasinATLAS `ele_mt_*`
  covers basin-averaged elevation separately.

- **Temporal dataset citations** (from `docs/edop/prospectus_20260509.md`):
  - LMR v2.1: Tardif et al. 2019, *Climate of the Past* 15, 1251–1273. doi:10.5194/cp-15-1251-2019
  - HYDE 3.4: Klein Goldewijk et al. 2017, *Earth System Science Data* 9(2), 927–953.
    (Note: citation title says "HYDE 3.2" — may be a copy-paste artifact; verify against paper)
  - eVolv2k v4: Sigl & Toohey 2024, PANGAEA. https://doi.org/10.1594/PANGAEA.971968

- **Ruth Mostern's dataset**: Yellow River Database, from her Tracks of Yu project.
  China environmental events data; candidate for Phase 4 correspondence testing.

---

## 2. Cliopatria polity viewer — Phase 1 complete

### DB smoke tests (all passing)
- Search (`ILIKE '%q%'` on distinct non-component names): 24ms
- Slice list (136 Ottoman rows): 8.6ms
- GeoJSON fetch by id: avg 6 kB, p95 23 kB, max 161 kB (British Colonial Empire at peak)
- All well within acceptable range for individual on-demand fetches

### Three new API endpoints (`app/api/routes.py`)
- `GET /api/polity/search?q=X[&year=Y]` — debounced autocomplete; leaf polities only
  (`NOT is_component`); returns name, first/last year, slice count; min 2 chars, max 40 results
- `GET /api/polity/slices?name=X` — all time slices for a named polity; no geometry;
  returns id, fromyear, toyear, area_km2, seshatid, invalid_source_geom, memberof, components
- `GET /api/polity/geom?id=N` — GeoJSON Feature for a single slice by row id;
  6-decimal precision; includes all properties

### New page route (`app/web/pages.py`)
- `/polities` → `cliopatria.html`

### Template (`app/templates/cliopatria.html`)
Two-column layout:
- **Search bar** (full width, top): debounced input → dropdown with name, era, slice count
- **Left (~65%)**: MapLibre OSM base map + temporal controls strip below
  - Prev / Play (placeholder) / Next buttons + year slider + slice counter
  - Slider updates label while dragging; fetches geometry on release (mouseup)
  - Play button reserved at 55% opacity with tooltip "coming soon"
- **Right (~35%)**: info panel
  - Header: polity name, date range, area, seshatid
  - `memberof` note shown only for true composites (singleton-self suppressed:
    if `memberof[0] === '(' + name + ')'` → hidden)
  - Invalid geometry warning if `invalid_source_geom = true`
  - Wikipedia summary via REST API (`/api/rest_v1/page/summary/{title}`) — extract +
    thumbnail; welcome blurb shown before selection
  - Seshat data section placeholder (reserved for future population)

### Design decisions
- **GeoJSON per slice, not PMTiles**: polity geometries fetched one at a time on demand —
  no need for tile serving at this scale (single feature, 6 kB avg)
- **basin06.pmtiles for future basin overlay (Phase 2)**: API returns hybas_id array;
  client highlights against already-loaded tiles via feature-state — no geometry transfer
- **Overlaps (ST_Intersects) for basin association** (Phase 2): chosen over centroid-within
  for display; area-weighted intersection deferred to Phase 3 signature computation
- **ST_Intersects on invalid geometries**: to be tested before Phase 2 implementation

---

## Seshat context for future work

- Seshat databank is at https://seshat-db.com/ (not seshatdatabank.info)
- Per-polity landing pages exist at `https://seshat-db.com/core/polity/{N}` for 800+
  polities, but the numeric ID is not stored in `gaz.clio_polities` or `seshat.*` — would
  need to be mapped if direct linking is wanted
- Immediate design decision: Seshat data is handled locally (from the `seshat` schema)
  rather than linking out, because the medium-term goal is correlation analysis between
  Seshat social complexity variables and EDOPS environmental signatures. The viewer's
  General + Social tabs are the first step toward that — making the data visible per polity
  as a precursor to systematic cross-dataset analysis. This is a Phase 4 activity
  (correspondence testing) and follows Phase 3 (aggregation / area signatures).

---

## Planned: geometry history outlines (Phase A)

When viewing any slice N, MapLibre should show outlines of all prior *distinct* geometries
(identified by MD5 geom hash) accumulated behind the current filled polygon. At step 3 of
Northern Song you'd see outlines of groups A and B; at step 4, A+B+C; at step 5/6, A+B+C+D.
History accumulates at every step, not just the last.

Implementation:
- Add `geom_hash` + `geom_group` integer to `/api/polity/slices` via SQL window function
- Client caches GeoJSON per distinct geom_group as user steps through
- MapLibre history-outline layer updated on each step
- Outlines progressively lighter/more transparent for older groups (TBD)

Seshat diff highlighting (Phase B) deferred — needs separate design pass, especially for
single-seshatid polities where year_from matching is required (Northern Song case).

---

## Open / next steps

- **Phase 2**: basin06 overlay toggle — `/api/polity/basins?id=N` returning hybas_id array;
  test ST_Intersects on invalid geom rows first
- **Play animation**: wire up the reserved play button
- **Seshat data**: populate right panel placeholder when Seshat per-polity data is integrated
- **Navigation link**: add `/polities` to main nav across sandbox pages

---

## 3. Phase A — geometry history outlines (complete)

Visual logic settled after iteration: all history fills at flat `fill-opacity: 0.07`, all
at the same blue as the current polygon. Stacking is the mechanism — overlapping fills from
multiple prior steps accumulate and darken, so persistent core territory appears darkest and
newly-acquired fringe appears lightest. Dashed outlines (`line-dasharray: [4, 3]`) mark each
prior step boundary uniformly at `line-opacity: 0.55`.

Hover tooltip on history polygons: `queryRenderedFeatures` collects all overlapping history
features at cursor point, sorts by `age` descending, shows the **oldest** group's date range
— semantically "this territory has been held since at least X."

---

## 4. Seshat period-shift detection (complete — General tab)

### DB analysis: Northern Song and Holy Roman Empire

Systematic queries against `seshat.general` and `seshat.social` for two test polities
revealed:

- **Temporal sparsity**: the vast majority of Seshat variables carry no `year_from`/`year_to`
  subdivision within a given seshatid. Northern Song: 2 of 52 social rows have year
  annotations (point estimates at 1000 and 1100 CE). HRE `de_empire_1`: 1 of 68 social rows.
  General table: 0 year-annotated rows for both polities. Within-seshatid diff is not viable
  with current data.

- **Coverage asymmetry**: later seshatid periods often have much sparser social data than
  earlier (HRE `de_empire_2`: 1 social row vs `de_empire_1`'s 68). Diffing social across
  transitions would be misleading — shows data gaps as historical change.

- **The 107**: of 1,522 leaf polities in Cliopatria, 632 (42%) have any Seshat link;
  107 of those 632 (17%) have multiple distinct seshatids (period shifts). These include
  Ottoman Empire (5), Kingdom of France (6), Papal States (6), Byzantine Empire (3),
  Kingdom of England (4), Yamato (3), USA (3).

### Implementation

- `original_name` added to `GENERAL_FIELDS` in `/api/polity/seshat` endpoint
- Client detects `_hasIdShift` (>1 distinct seshatid in slice list) at polity selection
- `diffGeneral()` compares prev/curr general dicts; skips `duration`, `preceding_entity`,
  `succeeding_entity` (transition metadata)
- On seshatid transition: dark navy banner — "Seshat period shift" / from→to period names /
  field change count; changed rows flash amber with "was: X" note; added rows green,
  removed rows red strikethrough
- General tab is now the **default tab** (was Wikipedia)
- Social tab diff deferred — data coverage too asymmetric to be reliable

---

## 5. Organizational memo

`data/cliopatria/cliopatria_viewer_memo.md` — draft document covering: what was built,
data sparsity findings, seshatid/slice temporal mismatch, coverage statistics, EDOPS scope
vs. viewer scope, and the institutional picture (CEDOP / ISHI / Seshat). Intended for
discussion with Ruth Mostern and eventually the Seshat team. See that file for detail.

---

## Remaining threads (clio branch)

- **Basin06 overlay** (Phase 2): test `ST_Intersects` on invalid geom rows before wiring
  toggle; `/api/polity/basins?id=N` → hybas_id array → PMTiles feature-state highlight
- **Social tab diff**: deferred until fuller Seshat download (Warfare, Religion, Economy
  variables not yet in local DB)
- **Navigation link**: add `/polities` to main nav
- **Play animation refinements**: speed control, loop option
- **Seshat numeric URL mapping**: `seshat-db.com/core/polity/{N}` IDs not stored — would
  need a mapping table if direct linking is wanted
- **EDOPS signature tab** (Phase 3+): once aggregation built, viewer gains environmental
  profile for current territory
