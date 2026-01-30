# CLAUDE.md

Read this first when starting a Claude Code session.

## Project Overview

**CEDOP (Computing Place)** is an umbrella project for environmental and cultural analytics in spatial humanities research. It currently contains:

- **EDOP (Environmental Dimensions of Place)**: A Python/FastAPI web application providing environmental analytics. It exposes global physical geographic and climatic data from BasinATLAS as normalized "environmental signatures" for any location, with integrations to D-PLACE cultural data, OneEarth ecoregions, World Historical Gazetteer, and World Heritage Cities.

- **CDOP (Cultural Dimensions of Place)**: Future module for cultural/historical analytics (placeholder).

## Quick Start

```bash
pip install fastapi uvicorn psycopg[binary] python-dotenv certifi
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Requires `.env` with `PGHOST`, `PGPORT`, `PGDATABASE` (default: cedop), `PGUSER`, `PGPASSWORD`, `WHG_API_TOKEN`.

## Architecture

```
app/
├── main.py              # FastAPI app init
├── settings.py          # Environment config
├── api/routes.py        # All REST endpoints (~30 routes)
├── db/
│   ├── connection.py    # Centralized db_connect() function
│   └── signature.py     # Core signature query logic
├── web/pages.py         # Jinja2 template routes
├── templates/           # HTML (index.html is main UI)
└── static/              # CSS, JS, vendor assets

scripts/
├── edop/                # EDOP data pipelines, clustering, corpus generation
│   └── corpus/          # Wikipedia harvesting and summarization
├── cdop/                # CDOP scripts (future)
└── shared/              # Shared utilities
    ├── db_utils.py      # Centralized db_connect() for scripts
    └── utils.py         # Common utilities

sql/
├── edop/                # EDOP schema definitions
├── cdop/                # CDOP schemas (future)
└── shared/              # Shared schemas (ecoregions, cliopatria)

output/
├── edop/                # EDOP artifacts (PCA, clusters, embeddings)
└── cdop/                # CDOP outputs (future)

metadata/*.tsv           # Lookup tables for categorical fields
```

### UI Tabs

- **Main**: Coordinate/place lookup → environmental signature
- **Basins**: Presents 20 clusters of the 190k sub-basins and lists of contained WH cities.
- **Ecoregions**: OneEarth hierarchy browser (Realm → Subrealm → Bioregion → Ecoregion)
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

## Testing

```bash
curl http://localhost:8000/api/health
curl "http://localhost:8000/api/signature?lat=16.76618535&lon=-3.00777252"  # Timbuktu
```

## Session Context Files

For context when resuming work, read these files:

- **`docs/EDOP_LOG.md`** - High-level development journal with dated entries (features, decisions, findings)
- **`prompts/seed-prompt-ongoing.md`** - Running prompt/context notes

Detailed per-session logs in `logs/session_log_*.md` can be consulted if needed but aren't required for initial context.

## External Dependencies

- **WHG** (World Historical Gazetteer): Place resolution
- **OpenTopoData / Open-Meteo**: Point elevation
- **D-PLACE**: Cultural/anthropological database
- **OneEarth**: Ecoregion taxonomy and metadata
