# CLAUDE.md

Read this first when starting a Claude Code session.

## Project Overview

**Computing Place (CEDOP)** is an umbrella project for environmental and cultural analytics in spatial humanities research. It currently contains:

- **EDOP (Environmental Dimensions of Place)**: A Python/FastAPI web application providing environmental analytics. It exposes global physical geographic and climatic data from BasinATLAS as normalized "environmental signatures" for any location, with integrations to D-PLACE cultural data, OneEarth ecoregions, World Historical Gazetteer, and World Heritage Cities.

- **CDOP (Cultural Dimensions of Place)**: In development. Will add semantic and anthropological dimensions through ethnographic datasets and text embeddings.

## Quick Start

```bash
pip install fastapi uvicorn psycopg[binary] python-dotenv certifi geopandas
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Requires `.env` with `PGHOST`, `PGPORT`, `PGDATABASE` (default: cedop), `PGUSER`, `PGPASSWORD`, `WHG_API_TOKEN`.

## Architecture

```
app/
├── main.py              # FastAPI app init ("Computing Place")
├── settings.py          # Environment config
├── api/routes.py        # All REST endpoints (~30 routes)
├── db/
│   ├── connection.py    # Centralized db_connect() function
│   └── signature.py     # Core signature query logic
├── web/pages.py         # Jinja2 template routes
├── templates/
│   ├── base_cedop.html  # Base template for splash/about pages
│   ├── base.html        # Base template for EDOP app (includes Leaflet)
│   ├── index.html       # Computing Place splash page (cedop.kgeographer.org/)
│   ├── edops.html       # EDOPS landing page (edops.kgeographer.org/)
│   ├── sandbox.html     # EDOPS researcher sandbox
│   ├── workbench.html   # Computing Place Workbench (formerly edop.html)
│   └── about.html       # About page with architecture diagram
└── static/
    ├── css/site.css     # All custom styles
    ├── js/main.js       # Workbench JavaScript
    └── images/          # Logos, tile images

scripts/
├── edop/                # EDOP data pipelines, clustering, corpus generation
│   ├── explore/         # Data exploration phase scripts (see docs/edop/data_exploration.md)
│   ├── corpus/          # Wikipedia harvesting and summarization
│   ├── polity_basin_overlay.py  # Areal interpolation demo (Northern Song, original)
│   └── edops_polity_maps.py    # Parameterized polity choropleth generator (1–3 years, static + HYDE vars)
├── cdop/                # CDOP scripts
└── shared/              # Shared utilities
    ├── db_utils.py      # Centralized db_connect() for scripts
    └── utils.py         # Common utilities

notebooks/
└── edop/
    └── explore/         # Exploration phase notebooks

sql/
├── edop/                # EDOP schema definitions
├── cdop/                # CDOP schemas
└── shared/              # Shared schemas (ecoregions, cliopatria)

output/                  # Regenerable artifacts (gitignored)
├── edop/
│   └── explore/         # Exploration phase outputs
└── cdop/                # ICH extractions, etc.

logs/
├── session_log_YYYYMMDD.md  # Daily work logs
└── exploration_log.md       # Accreting findings log for data exploration phase

metadata/*.tsv           # Lookup tables for categorical fields
```

### Page Routes

- `/` — Computing Place splash (cedop.kgeographer.org) or EDOPS landing (edops.kgeographer.org) — host-based
- `/edops` — EDOPS landing page
- `/sandbox` — EDOPS researcher sandbox (primary tool)
- `/workbench` — Computing Place Workbench (experimental demonstrators)
- `/edop` — 301 redirect to `/workbench` (legacy URL preservation)
- `/about` — Architecture diagram

### Sandbox (`/sandbox`) — Primary Researcher Tool

- WHG place lookup (reconcile+extend, zoom ≥ 4) → candidate markers → basin assignment → neighborhood map
- Level 08/06 toggle: switching always lands on Map tab; re-fetches preview + sig if sig exists
- Band A–T signature accordion; Signature/Analysis tabs disabled until sig fetched
- Analysis α tab: water provenance, s/u divergence table, scale mismatch alert
- Band T temporal: PDSI / Temperature / Precipitation SVG charts + volcanic events
- Ecoregion → Wikipedia modal; LLM narrative button
- Example selector: Timbuktu (1100–1200), Rome (0–300), Kaifeng (1000–1100) at L8/L6
- API Guide modal in header

### Workbench (`/workbench`) — Experimental Demonstrators

- **Main**: Place lookup → signature (Bands A–T)
- **Basins**: 20 PCA-derived environmental clusters of 190k sub-basins + WH cities
- **Ecoregions**: OneEarth hierarchy browser (Realms → Ecoregions)
- **Societies**: 1,291 D-PLACE societies with subsistence/religion filters
- **WH Cities**: 258 World Heritage Cities with env + semantic similarity
- **WH Sites**: 20 World Heritage pilot sites with env + semantic similarity

### Key Endpoints

```
/api/signature?lat=X&lon=Y[&bands=ABCDET&from_year=N&to_year=N&level=6|8]
                              Environmental signature. Single call handles all bands including F.
                              Response: meta (version, timestamp, query, data_sources) + profile_groups A–T.
                              Band T requires from_year+to_year (0–1998 CE); stored at profile_groups["T"].
                              Flat basin fields excluded by default; profile_groups is canonical.
/api/temporal?lat=X&lon=Y&year_start=N&year_end=N
                              LMR v2.1 PDSI + eVolv2k volcanic events (legacy; prefer /api/signature?bands=T)
/api/basin-preview?lat=X&lon=Y
                              Containing basin + adjacent basins + river lines for neighborhood map
/api/basin-preview?lat=X&lon=Y[&level=6|8]
                              Containing basin + adjacent basins + river lines for neighborhood map (default level 8)
/api/whg-reconcile?q=X[&size=N&bounds=GeoJSON]
                              WHG reconcile+extend pipeline: fetches 50, filters noisy namespaces (wd:/gn:/osm:),
                              returns top N. Requires viewport bounds (zoom ≥ 4) for useful ranking.
/api/eco/wikitext?eco_id=N    Pre-summarized Wikipedia text + URL for an ecoregion
/api/resolve?name=X           Place name resolution (WHG API — legacy; prefer /api/whg-reconcile)
/api/societies                D-PLACE societies with filters
/api/eco/*                    Ecoregion hierarchy and geometries
/api/whc-*                    World Heritage Cities data
/api/similar, /api/similar-text   Pilot site similarity
```

## Deployment

- **URLs**: `cedop.kgeographer.org` (Computing Place) and `edops.kgeographer.org` (EDOPS service) — both SSL via certbot, same server
- **Server**: Hetzner CPX32, Nuremberg — `kgeographer-1` (46.225.125.25), Ubuntu 24.04, Nginx reverse proxy → Gunicorn on port 8001
- **Service**: `cedop.service` (systemd), virtualenv at `/home/karlg/envs/cedop/`
- **Working dir**: `/var/www/cedop`
- **Database**: `cedop` (PostgreSQL 17/PostGIS)
- **Deploy**: `ssh kgeographer-1`, then `git pull` + `sudo systemctl restart cedop`
- **Also hosted**: `glos.kgeographer.org` (Flask, port 8002), `linkedpaths.kgeographer.org` (static)
- **Migration log**: `sysop/hetzner_migration_log.md`

## Database Notes

- `public.basin08`: 190,675 sub-basins, `hybas_id`, `geom` (MultiPolygon 4326), 47+ signature fields
- `gaz.clio_polities`: Cliopatria polities — columns are **lowercase** (`fromyear`, `toyear`, `name`, `geom`)
- Temperature fields (`tmp_dc_*`) stored as °C × 10; divide by 10 for display
- Pass PostGIS geometries as WKT via `ST_GeomFromText()`, not EWKB hex (endian issues with psycopg3)

## Testing

```bash
curl http://localhost:8000/api/health
curl "http://localhost:8000/api/signature?lat=16.76618535&lon=-3.00777252"  # Timbuktu
```

## Sandbox / Researcher Tool

`/sandbox` is the primary design and demonstration interface (`app/templates/sandbox.html`). Current capabilities:
- WHG place lookup (reconcile+extend pipeline, zoom ≥ 4, viewport bounds) → candidate markers → basin assignment → neighborhood preview map
- Level 08/06 toggle (`#sb-level`): switching re-fetches neighborhood always, sig only if one exists; no tab jumping
- Band A–T signature with schema_key labels; sig heading shows place name + active level
- Analysis α tab: water provenance classification, s/u divergence table, scale mismatch alert
- Band T temporal: PDSI / Temperature / Precipitation tabs with SVG bar charts + volcanic events
- Ecoregion clickable in summary panel → Wikipedia modal (pre-summarized, 97% coverage)
- LLM narrative interpretation button

Key design docs:
- **`docs/design/scenarios.md`** — User profiles (user00=Karl, user01=humanities researcher, user02=Federico) and scenarios driving design. **Read before any sandbox UI work.**
- **`docs/design/prelim_notes.md`** — Earlier screen requirement notes (superseded by scenarios.md)
- **`docs/edop/edops_schema.json`** — Signature schema: current API output (status=implemented) + planned fields. Real Timbuktu values as examples. Note: `app/static/api_guide.html` is a narrative guide for external API users (Federico et al.) — needs update after 2026-04-16 payload changes.
- **`metadata/edops_codebook_v02.tsv`** — Field reference: schema_key, friendly_name, units, basin08_col_s/u, **api_key_s/u** (added 2026-04-12), notes. Loaded at startup by `signature.py` to generate accordion labels. Versioned: v01, v02 in `metadata/`; next draft will be `v03_draft.tsv`.

## Session Context Files

- **`docs/edop/prospectus_20260429.md`** — Current authoritative research direction document (living prospectus, updated from outline v3 Feb 2026). Prior versions archived as `prospectus_20260407.md`, `prospectus_20260419.md`. Blog post master: `docs/blog/computing_place_prospectus.md`.

## Data Exploration Phase

The next major work phase is systematic characterization of the EDOPS signature dataset before any correspondence testing, PCA, or rubric design. See **`docs/edop/exploration_*.md`** for the full task lists, conventions, and guardrails. Exploration now expanding to spatial-specific measures, External work in GeoDa will inform direction and specifics currently outlined in spatial/spatial_plan.md

Key locations:
- **Scripts**: `scripts/edop/explore/` — numbered exploration scripts
- **Notebooks**: `notebooks/edop/explore/`
- **Outputs**: `output/edop/explore/` (gitignored)
- **Findings log**: `logs/exploration_log.md` — accretes findings over time; do not confuse with daily session logs

Tasks 1–6 complete (2026-04-19). Findings in `logs/exploration_log.md` (F1.1–F6.5).

Tasks 1–6 complete (static bands A–E). Tasks 7–11 complete (Band T, 2026-04-25/27, branch explore02).

Completed static (Tasks 1–6): (1) marginal distributions, (2) missing-data patterns, (3) local/upstream divergence + reference site percentiles, (4) full Spearman correlation matrix, (5) geographic pre-clustering (k-means k=20, committed as working typology), (6) coverage/sampling-bias characterization (D-PLACE + WH Cities vs. global basin distribution).

Completed Band T (Tasks 7–11): (7) eVolv2k v4 distribution and aggregation design — vssi_min=5.0 confirmed, three aggregations recommended, hemispheric filtering ruled out, eVolv2k/LMR decoupling flagged. (8) HYDE 3.4 per-epoch distributions — signal emergence characterized, 1000 BCE established as global land-use baseline, population density reliability caveat documented, BCE climate gap flagged. (9) HYDE basin aggregation and s/u characterization — polygon-interior confirmed, cropland/grazing s/u divergence characterized, EarthStat vs HYDE spatial allocation divergence documented, reference site trajectories validated. (10) LMR v2.1 structure — file layout (time=2001, MCrun=20, lat=91, lon=180), anomaly-not-absolute framing confirmed, funnel effect characterised (reliable window ~700–1900 CE), temporal variance dominates geographic (PDSI 76%, air 68%, prate 93%), within-run spread 4.6× across-run std, Band C orthogonal to LMR (r≈0), L8→LMR mapping 190,675 basins → 4,999 cells. (11) LMR period/volcanic fingerprints — MCA/LIA temperature signals marginal at global scale but directionally present at NH locations; reliable pre-industrial (1000–1850 CE) confirmed as baseline convention; LMR cannot quantify volcanic forcing below ~50 Tg (eVolv2k/LMR decoupling confirmed); Samalas 1257 detectable at Central Europe (−0.43 K) and Kaifeng (attenuated, delayed); LMR proxy network geographic bias documented as first-class API limitation.

Key open design questions logged (F8.5, F8.6, F9.6, F11.4, F11.6): (a) Band C is silently wrong for BCE queries — needs `climate_note` disclosure; (b) population density may not belong in an environmental signature; (c) EarthStat/HYDE spatial divergence at agricultural hotspot sub-basins; (d) Pinatubo calibration text for narrative layer prompt; (e) LMR geographic proxy bias disclosure for API docs — all flagged for October 2026 expert meeting or pre-release documentation.

Task 12 (Anthromes categorical typology) deferred indefinitely — not a current goal. Correspondence testing deferred until polity phase complete.

## Current Work — `esda` branch, as of 2026-05-21

### Completed 2026-05-03
- Sandbox example selector bug fixed; GA4 analytics added; repo cleanup; api_guide fixes; 19/19 tests passing
- See `logs/session_log_20260503.md`

### Completed 2026-05-04
- `docs/edop/prospectus_20260503.md`: new draft — worked examples genre, three-phase trajectory, audience scope, spatial characterization report bullet ([Rev. 03 May]); Sections 9–10 renumbered
- Cliopatria EDA: `data/cliopatria/cliopatria_eda.md` — entity taxonomy, three-level counting (1,522 names / 11,178 configs / 12,987 slices), singleton-self clarification, query design rubric
- `gaz.clio_polities` schema fixes: empty strings → NULL; `is_component` boolean; `geom_og` archive + `invalid_source_geom` flag (invalid geoms NOT repaired — for Cliopatria team); `memberof`/`components` → `text[]`
- See `logs/session_log_20260504.md`

### Completed 2026-05-14
- New machine setup: PGPORT 5435→5432 in `.env` + 20 scripts; 19/19 tests passing; branch `post_move`
- `notebooks/edop/spatial/01_aridity_l6_moran.ipynb`: global Moran's I, Moran scatter plot, LISA, cluster map, log-transform sensitivity check
- **Key result**: aridity at L6, I=0.963 (raw) / 0.973 (log); LL=30.0%, HH=4.6%, HL=1.4%, LH=0%
- **Critical finding**: weights must be built with `Queen.from_dataframe(gdf, use_index=True)` keyed by hybas_id — GAL files from GeoDa carry wrong row ordering (produced I=0.364, mottled map)
- See `logs/session_log_20260514.md`

### Completed 2026-05-15
- `notebooks/edop/spatial/02_aridity_l8_moran.ipynb`: scale comparison notebook complete — same routine as L6 at 190k basins
- **Key results**: aridity at L8, I=0.989; LL=30.9%, HH=3.8%, HL=0.2%, LH=0%; scale effect confirmed (+0.026 vs L6)
- **M5 benchmarks**: weights build 4m39s, LISA 20s — pipeline is fully interactive at L8 (not "walk away")
- **Scale findings**: cluster-core % stable across scales; outlier % not comparable (HL absolute count doubles, % collapses due to 11.6× denominator growth); MAUP HH fringe contraction at Pacific NW rain shadow
- `spatial/esda_findings.md` established — accreting findings log for ESDA phase (parallel to `logs/exploration_log.md`)
- Branch renamed `spatial01` → `esda`
- See `logs/session_log_20260515.md`

### Completed 2026-05-16
- `notebooks/edop/spatial/03_discharge_l6_l8_moran.ipynb`: both scales in single notebook
- **Key results**: discharge I_log=0.582 (L6) / 0.563 (L8) — ~0.41 below aridity; scale direction reverses (↓); LH class appears; LH grows 22.5× vs 11.6× basin count (watershed-divide effect)
- Phase names standardised: `x_spatial` → `esda`, `x_polity` → `polity`; `spatial/esda_findings.md` DIS.1–6 entries added
- See `logs/session_log_20260516.md`

### Completed 2026-05-17
- `scripts/edop/esda/12_spatial_moran.py`: Phase 1 univariate sweep — 40 Band A–D variables × L6+L8
- `notebooks/edop/spatial/04_spatial_typology.ipynb`: Phase 2 typology — OUTLIER_HIGH→3.00; group counts: continental-gradient=21, mixed=15, network-topology=3, local-anomaly=1; `spatial/first_cut_typology.csv`
- `notebooks/edop/spatial/05_bivariate_TP_l6.ipynb`: Phase 3 bivariate T×P — I_BV=+0.315 global; Mediterranean I_BV=−0.250 (sign reversal); Tibetan I_BV=+0.608 (LL); Monsoon Asia NS (p=0.076)
- `docs/design/variable_selection_rubric_issues.md`: design doc on typology semantics, historical validity, environment/culture boundary, expert system risk — for Opus 4.7 discussion
- SW.1–3, METH.4, BV.1–6 added to `spatial/esda_findings.md`
- **Key methodological finding**: Mediterranean I_BV = −0.25 (sign reversal vs global +0.315) validates Karl's correction: global concordance scalar is not a valid redundancy filter
- `notebooks/edop/spatial/06_bivariate_phase4_l6.ipynb`: Phase 4 — 5 bivariate pairs; global maps complete; regional analysis (Cells 15–17) deferred
- **Redundancy tiers**: near-redundant (tmp×snw −0.865, pre×aet +0.863); genuinely distinct (hdi×gdp +0.581, ari×pre +0.578, ele×slp +0.423)
- **Key finding**: African Plateau dominates ele×slp HL class (not Tibetan as predicted); LISA class = global structural position not absolute character (BV.13)
- **EDOP/CDOP boundary**: Band D (hdi/gdp) LISA patterns require historical-institutional context — opt-in for historical queries
- BV.7–13 added to `logs/esda_findings.md`
- See `logs/session_log_20260517.md`

### Completed 2026-05-19
- `notebooks/edop/spatial/06_bivariate_phase4_l6.ipynb` Cells 15–17: Phase 4 regional analysis complete — 3×5 I_BV grid across Mediterranean, Monsoon Asia, Tibetan/cold-arid
- **Key finding**: tmp×snw near-redundancy collapses to NS in Tibetan (I_BV −0.865 → −0.005); ele×slp sign-reversal in Tibetan; pre×aet and ari×pre stable across all regions
- **Key finding**: HL patch in pre×aet Mediterranean = Lebanese mountains/Syrian coastal range (not Anatolian highlands as initially labelled)
- BV.14–19 added to `logs/esda_findings.md`; Cell 18 summary updated
- CHAR completion plan (`prompts/cc_char_completion_prompt.md`) reviewed; psycopg3 integer-NULL→0 bug documented; path corrections applied
- `notebooks/edop/spatial/13_categorical_coherence.ipynb`: Phase 1 CHAR — join-count spatial coherence for lith_class (16 cls), pnv_majority (15 cls), wetland_class (12 cls, n=96,884 subset)
- All 43 class-variable combinations significant at p=0.001; local coherence 90.8%–99.5% across all classes
- **esda bug**: `Join_Counts_Local` IndexError with islands (Python 3.14); fallback: row-stochastic W·y ≥ 0.5 majority-match
- `output/edop/spatial/13_categorical_coherence.csv`; `spatial/13_categorical_cluster_maps.png`
- CAT.1–8 added to `logs/esda_findings.md`
- See `logs/session_log_20260519.md`

### Completed 2026-05-21
- `notebooks/edop/spatial/15_bivariate_redundancy.ipynb`: Phase 3 CHAR — bivariate LISA for 11 high-r pairs (5 s/u + 6 same-band non-s/u) at L8
- **Key finding**: s/u divergence <1% globally; anthropogenic pairs (HFT, Crop) show most
- **Key finding**: discharge I_BV (0.45–0.54) < univariate I — seasonal regime geography is independent spatial signal; LH >> HL in all discharge pairs
- **Key finding**: temperature triple (T_yr, T_min, T_yr_u) spatially interchangeable
- **Key finding**: HDI×GDP HL=8,566 vs LH=7 — development geography one-directional
- **Design decision**: no variables removed from signature based on global co-variation — see `memory/project_no_variable_pruning.md`
- BVR.1–7 added to `logs/esda_findings.md`
- `output/edop/spatial/bivariate_redundancy.parquet` (2,097,425 rows), `bivariate_redundancy_counts.csv`
- Phase 4 CHAR re-framed with Opus: Band T characterized at native resolution (not basin-aggregated)
- `prompts/cc_band_t_native_prompt.md`: operational Phase 4 prompt (supersedes Phase 4 of `cc_char_completion_prompt.md`)
- `docs/design/lmr_hyde_esda_design.md` **not created** — new prompt resolves all design questions in operational form
- See `logs/session_log_20260521.md`

### Completed 2026-05-22
- `notebooks/edop/spatial/16a_band_t_native_choropleths.ipynb`: Phase 4a CHAR — LMR + HYDE choropleth series (Mollweide), epoch stats CSVs, findings BT4A.1–BT4A.5
- `notebooks/edop/spatial/16b_band_t_native_esda.ipynb`: Phase 4b CHAR — Moran's I + LISA at native grids
  - LMR (4,924 land cells, 2° grid): temperature I=0.931–0.974; PDSI I=0.856–0.888; all p=0.001; 59,088 LISA rows
  - HYDE (2.2M cells, 5-arcmin): Moran's I sweep complete; LISA intractable (2,247s/epoch); pilot LISA retained
  - **Headline**: cropland I 0.59→0.92 over 6,000 years; grazing starts at 0.91 (biome-constrained from outset)
- Outputs: `band_t_native_moran.csv` (26 rows), `band_t_native_lmr_lisa.parquet` (59,088 rows), `band_t_native_hyde_lisa_pilot.csv`
- BT4B.1–BT4B.3 added to `logs/esda_findings.md`; see `logs/session_log_20260522.md`

### Next: Phase 4c CHAR — Band T cross-temporal (paused)
- `16c_band_t_native_cross_temporal.ipynb` — HYDE persistence map + LMR MCA–LIA dipole structure
- Key conventions: LMR at 2° native grid; HYDE at 5-arcmin native; longitude wrap in queen weights

**Then: Phases 5–6 CHAR** (position attribute spec, CHAR appendix) per `prompts/cc_char_completion_prompt.md`

**Then: `polity` phase** (after esda complete)
- Summary tuples per basin [A-3, B-2, ..., T-7]
- Polity payload management: area-weighted signatures for polygon queries (Cliopatria/Seshat)
- Scale sensitivity: L6 vs L8 for polity signatures
- Tentative D-PLACE correspondence tests
- `scripts/edop/edops_polity_maps.py`: parameterized choropleth generator; extend as needed

**Polity map script** (`scripts/edop/edops_polity_maps.py`):
- `--polity`, `--years` (1–3), `--variable` (static Band A–C or hyde_cropland/grazing/pasture/rangeland)
- Demonstrated: Northern Song aridity, Kingdom of Denmark cropland, Roman Empire cropland
- HYDE note: values already km² in DB — `SUM(hc.field[step])` / `SUM(hc.area_km2)` × 100

## External Dependencies

- **WHG** (World Historical Gazetteer): Place resolution
- **OpenTopoData / Open-Meteo**: Point elevation
- **D-PLACE**: Cultural/anthropological database
- **OneEarth**: Ecoregion taxonomy and metadata
