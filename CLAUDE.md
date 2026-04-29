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
│   └── polity_basin_overlay.py  # Areal interpolation demo
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
- **`metadata/edops_codebook.tsv`** — Field reference: schema_key, friendly_name, units, basin08_col_s/u, **api_key_s/u** (added 2026-04-12), notes. Loaded at startup by `signature.py` to generate accordion labels.

## Session Context Files

- **`logs/CEDOP_LOG.md`** — Development journal with dated entries
- **`prompts/seed-prompt-ongoing.md`** — Running prompt/context notes
- **`docs/edop/prospectus_20260416.md`** — Current authoritative research direction document (living prospectus, updated from outline v3 Feb 2026). ISHI-supported program as of Apr 2026. Core conceptual framing: *process-aware environmental characterization* — what a place experiences through directed spatial processes. Key features: (1) local/upstream `s`/`u` duality as first-class signature feature; (2) distance-weighted upstream profiling via `next_down` DAG; (3) coastality (`dist_sink`, outlet type) as first-class signature component; (4) settlement correspondence as external validation objective (Section 9); (5) drainage topology implementation (Section 10); (6) temporal enrichment via LMR v2.1 and eVolv2k v4. Use cases driving design: `docs/edops_use_cases.md`. Prior versions archived as `prospectus_20260402.md`, `prospectus_20260403.md`. Blog post master: `docs/blog/computing_place_prospectus.md`.

## Data Exploration Phase

The next major work phase is systematic characterization of the EDOPS signature dataset before any correspondence testing, PCA, or rubric design. See **`docs/edop/exploration_*.md`** for the full task lists, conventions, and guardrails.

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

Next: Task 12 (Anthromes categorical typology — design specifics TBD before notebook). **Do not** start correspondence testing until Task 12 scoped.

## Current Work — sigrefine01 branch (as of 2026-04-29)

Signature refinement phase. HYDE 3.4 land-use pipeline complete and live in Band T API (commit 8366f74).

**HYDE implementation complete**:
- `temporal.hyde_cells` (2,215,829 rows) + `temporal.hyde_times` (128 steps) loaded and indexed
- `app/db/hyde.py`: `get_hyde_land_use(lat, lon, from_year, to_year, level)` — per-epoch dicts with `_km2` and `_pct` fields; `_note` carries temporal resolution disclosure
- `app/db/connection.py` and `scripts/shared/db_utils.py`: explicit `load_dotenv` path; DB on port 5435
- Wired into `routes.py` → `profile_groups["T"]["hyde_land_use"]`
- Exploration log F8.8–F8.10 added

**Remaining on this branch** (in order):
1. Band D: add `pasture_extent` (EarthStat L09) — codebook entry + `signature.py` query
2. Codebook (`metadata/edops_codebook_v01.tsv`): 4 new HYDE rows (cropland, grazing, pasture, rangeland)
3. Sandbox (`app/templates/sandbox.html`): surface HYDE epochs in Band T accordion
4. Prospectus update: qualifying-notes-as-first-class-content principle; 1000–1850 CE baseline convention
5. Server deploy: merge sigrefine01 → main → push → `git pull` + restart on kgeographer-1

**Note**: Band C `land_cover_id/name` is already in the payload — was there all along, not a pending item.

See `logs/session_log_20260429.md` for full detail.

## External Dependencies

- **WHG** (World Historical Gazetteer): Place resolution
- **OpenTopoData / Open-Meteo**: Point elevation
- **D-PLACE**: Cultural/anthropological database
- **OneEarth**: Ecoregion taxonomy and metadata
