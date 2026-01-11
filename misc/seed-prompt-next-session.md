# EDOP Session Seed Prompt

## Project Overview

EDOP (Environmental Dimensions of Place) is a Python/FastAPI proof-of-concept for ISHI/Pitt and KNAW/CLARIAH. It provides environmental "signatures" for any geographic location using BasinATLAS data (190k level-8 sub-basins, 1,565 features). The project combines:

- **Environmental analysis**: PCA + clustering of basin features
- **Text/semantic analysis**: Wikipedia-derived embeddings for World Heritage sites/cities
- **Web UI**: Leaflet map with signature display, similarity queries, cluster visualization

## Current State (as of 11 Jan 2026)

Key accomplishments:
- 20 WH sites pilot with full environmental + text similarity
- 258 WH cities scaled up with environmental + semantic clustering
- 190k basins clustered (k=20) using full 1,565-dim signatures

## Context Files (read these to get current)

1. **`docs/edop_database_schema.md`** — All database tables (source + result), relationships, feature dimensions
2. **`docs/EDOP_LOG.md`** — Chronological work log (newest first), high-level summary per day
3. **`docs/session_log_11Jan2026.md`** — Most recent detailed session (basin clustering pipeline)
4. **`misc/seed-prompt-ongoing.md`** — Project context, UI structure, research findings

## Pending Work

- [ ] Build `edop_gaz` table + autocomplete UI for place lookup
- [ ] WHG API integration (paused — endpoint doesn't return coords for candidates)
- [ ] Compare simplified vs full basin clustering
- [ ] Cross-analysis: environmental vs text clusters

## Quick Start

```bash
# Run dev server
uvicorn app.main:app --reload --port 8000

# Test signature endpoint
curl "http://localhost:8000/api/signature?lat=16.766&lon=-3.007"
```
