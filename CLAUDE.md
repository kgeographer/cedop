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
/api/signature?lat=X&lon=Y    Environmental signature for coordinates
/api/resolve?name=X           Place name resolution (WHG API)
/api/societies                D-PLACE societies with filters
/api/eco/*                    Ecoregion hierarchy and geometries
/api/whc-*                    World Heritage Cities data
/api/similar, /api/similar-text   Pilot site similarity
```

## Deployment

- **URL**: `cedop.kgeographer.org` (SSL via certbot)
- **Server**: DigitalOcean Ubuntu droplet, Apache2 reverse proxy → Gunicorn on port 8001
- **Service**: `cedop.service` (systemd), virtualenv at `/home/karlg/envs/edop/`
- **Working dir**: `/var/www/cedop`
- **Database**: `cedop` (PostgreSQL/PostGIS)
- **Deploy**: `git pull` on droplet + `sudo systemctl restart cedop`

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

## Session Context Files

- **`docs/CEDOP_LOG.md`** — Development journal with dated entries
- **`prompts/seed-prompt-ongoing.md`** — Running prompt/context notes

## External Dependencies

- **WHG** (World Historical Gazetteer): Place resolution
- **OpenTopoData / Open-Meteo**: Point elevation
- **D-PLACE**: Cultural/anthropological database
- **OneEarth**: Ecoregion taxonomy and metadata
