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
├── web/pages.py         # Jinja2 template routes (/, /edop, /about)
├── templates/
│   ├── base_cedop.html  # Base template for splash/about pages
│   ├── base.html        # Base template for EDOP app (includes Leaflet)
│   ├── index.html       # Computing Place splash page
│   ├── edop.html        # EDOP app (tabs: Main, Basins, Ecoregions, etc.)
│   └── about.html       # About page with architecture diagram
└── static/
    ├── css/site.css     # All custom styles
    ├── js/main.js       # EDOP JavaScript
    └── images/          # Logos, tile images

scripts/
├── edop/                # EDOP data pipelines, clustering, corpus generation
│   ├── corpus/          # Wikipedia harvesting and summarization
│   └── polity_basin_overlay.py  # Areal interpolation demo
├── cdop/                # CDOP scripts
└── shared/              # Shared utilities
    ├── db_utils.py      # Centralized db_connect() for scripts
    └── utils.py         # Common utilities

sql/
├── edop/                # EDOP schema definitions
├── cdop/                # CDOP schemas
└── shared/              # Shared schemas (ecoregions, cliopatria)

output/                  # Regenerable artifacts (gitignored)
├── edop/                # PCA, clusters, embeddings, polity overlays
└── cdop/                # ICH extractions, etc.

metadata/*.tsv           # Lookup tables for categorical fields
```

### Page Routes

- `/` — Computing Place splash page (module tiles)
- `/edop` — EDOP application
- `/about` — Architecture diagram

### EDOP UI Tabs

- **Main**: Coordinate/place lookup → environmental signature
- **Basins**: 20 clusters of 190k sub-basins with WH cities
- **Ecoregions**: OneEarth hierarchy browser
- **Societies**: 1,291 D-PLACE societies with subsistence/religion filters
- **WH Cities**: 258 World Heritage Cities with clustering
- **WH Sites**: 20 World Heritage pilot sites with env/text similarity

### Key Endpoints

```
/api/signature?lat=X&lon=Y[&bands=ABCDEF&from_year=N&to_year=N]
                              Environmental signature; Band F requires from_year+to_year (0–1998 CE)
/api/temporal?lat=X&lon=Y&year_start=N&year_end=N
                              LMR v2.1 PDSI + eVolv2k volcanic events for a period
/api/basin-preview?lat=X&lon=Y
                              Containing basin + adjacent basins + river lines for neighborhood map
/api/eco/wikitext?eco_id=N    Pre-summarized Wikipedia text + URL for an ecoregion
/api/resolve?name=X           Place name resolution (WHG API)
/api/societies                D-PLACE societies with filters
/api/eco/*                    Ecoregion hierarchy and geometries
/api/whc-*                    World Heritage Cities data
/api/similar, /api/similar-text   Pilot site similarity
```

## Deployment

- **URL**: `cedop.kgeographer.org` (SSL via certbot)
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
- WHG place lookup → basin assignment → neighborhood preview map
- Band A–F signature with schema_key labels (`schema_key (db_col)` format)
- Ecoregion clickable in summary panel → Wikipedia modal (pre-summarized, 97% coverage)
- LLM narrative interpretation button

Key design docs:
- **`docs/gui/scenarios.md`** — User profiles (user00=Karl, user01=humanities researcher, user02=Federico) and scenarios driving design. **Read before any sandbox UI work.**
- **`docs/gui/prelim_notes.md`** — Earlier screen requirement notes (superseded by scenarios.md)
- **`docs/edop/edops_schema.json`** — Signature schema: current API output (status=implemented) + planned fields. Real Timbuktu values as examples.
- **`metadata/edops_codebook.tsv`** — Field reference: schema_key, friendly_name, units, basin08_col_s/u, **api_key_s/u** (added 2026-04-12), notes. Loaded at startup by `signature.py` to generate accordion labels.

## Session Context Files

- **`logs/CEDOP_LOG.md`** — Development journal with dated entries
- **`prompts/seed-prompt-ongoing.md`** — Running prompt/context notes
- **`docs/edop/prospectus_20260404.md`** — Current authoritative research direction document (living prospectus, updated from outline v3 Feb 2026). ISHI-supported program as of Apr 2026. Core conceptual framing: *process-aware environmental characterization* — what a place experiences through directed spatial processes. Key features: (1) local/upstream `s`/`u` duality as first-class signature feature; (2) distance-weighted upstream profiling via `next_down` DAG; (3) coastality (`dist_sink`, outlet type) as first-class signature component; (4) settlement correspondence as external validation objective (Section 9); (5) drainage topology implementation (Section 10); (6) temporal enrichment via LMR v2.1 and eVolv2k v4. Use cases driving design: `docs/edops_use_cases.md`. Prior versions archived as `prospectus_20260402.md`, `prospectus_20260403.md`. Blog post master: `docs/blog/computing_place_prospectus.md`.

## External Dependencies

- **WHG** (World Historical Gazetteer): Place resolution
- **OpenTopoData / Open-Meteo**: Point elevation
- **D-PLACE**: Cultural/anthropological database
- **OneEarth**: Ecoregion taxonomy and metadata
