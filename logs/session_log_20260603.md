# Session Log — 03 June 2026

## Participants
Karl Grossner, Claude Sonnet 4.6 (CC)

## Context
Follow-on session to Explorer build. Goals: begin Regions tab, deploy to server.
Session pivoted significantly: color scheme fixes, deployment work, and a strategic
decision to retool the Explorer map renderer before proceeding with Regions.

---

## 1. Color scheme fixes — Explorer Map tab

Identified that the choropleth color scheme violated the universal cartographic rubric
(warm/dry = red, cold/wet = blue) in three ways:

**Band A–E temperature variables** (`temperature_annual`, `temperature_min`,
`temperature_max`): the diverging renderer in `makeColorFn` was producing warm=BLUE,
cold=RED. Fixed by using `1 - t` in the RDBU interpolation, giving positive
(warm) = RED, negative (cold) = BLUE.

**Aridity index** (`aridity_index`, P/PET): was rendering with VIRIDIS sequential
(yellow=humid, purple=arid). Switched to RDBU sequential so low P/PET (arid) = RED,
high P/PET (humid) = BLUE. Aridity_index is always non-negative so required a special
case in `makeColorFn` (keyed by schema_key).

**Precipitation** (`precipitation_annual`): same treatment as aridity — added to the
moisture special case. Low precipitation = RED, high = BLUE.

**LMR PDSI and precip anomaly**: the LMR renderer (`renderLMRChoropleth`) used `1 - t`
for all LMR variables, which is correct for temperature (warm=RED) but wrong for PDSI
and precip (wet should be BLUE, not RED). Split: `lmr_temp_anomaly` keeps `1 - t`;
PDSI and precip anomaly use `t` directly (drought/dry = RED, wet = BLUE). Legend bar
and text labels updated per variable via a `reverseBar` parameter.

All fixes in `app/templates/explorer.html`. Confirmed correct rendering in browser
(Temperature monthly maximum screenshot shows hot regions deep red, as expected).

---

## 2. Deployment to edops.kgeographer.org

### Static assets (gitignored — rsync required)
Explorer requires files that are not in git (`app/static/explorer/` and `output/` are
gitignored). Transferred to server before deploy:
- `output/edop/esda/lisa_classifications.parquet` (107 MB) — LISA endpoint
- `app/static/explorer/lmr_notches.geojson` (6.2 MB) — LMR choropleth
- `app/static/explorer/countries_110m.geojson` (283 KB) — borders overlay
- `app/static/explorer/hyde_tiles/` (332 MB, 64k tiles) — HYDE Band T

### Issues encountered
1. **Main not pushed**: `git pull` on server fetched GitHub, not local main (26 commits
   ahead of origin). Deploy silently landed old code. Fixed by `git push origin main`
   first.
2. **pyarrow missing**: LISA endpoint crashed (500) because `pyarrow` was not installed
   in the server virtualenv. Fixed: `pip install pyarrow` in `/home/karlg/envs/cedop/`.

### Deploy sequence (correct order)
```
git push origin main          # always push first
rsync gitignored assets       # static files, parquet
ssh kgeographer-1
  cd /var/www/cedop && git pull
  sudo systemctl restart cedop
```

---

## 3. Strategic decision: MapLibre retool

### Problem
Explorer variable queries taking ~10 seconds on server (vs. 2–3 s locally). Root
cause: `/api/explorer/values` returns full GeoJSON (geometry + values) for all basins
— ~15–20 MB per request for L6, ~150 MB for L8. Caching was discussed but rejected
as a bandaid.

### Decision
Replace Leaflet with **MapLibre GL JS** on the Explorer page. Defer Regions tab
until retool is complete.

**Architecture**:
- Pre-generate `basin06.pmtiles` once with tippecanoe (geometry only, hybas_id as
  feature ID). Static file, rsync to server, never changes.
- `/api/explorer/values` strips geometry — returns flat `{hybas_id: value}` dict
  (~0.3 MB gzipped vs. 15–20 MB GeoJSON). Same for categorical endpoint.
- MapLibre renders PMTiles; choropleth applied via `setFeatureState` + paint
  expressions. Sub-second variable switch.
- LMR, HYDE, eVolv2k, country borders carry over as GeoJSON/raster sources.
- Left panel, histogram, header strip, Band T controls: unchanged.

**Branch**: `maplibre` (created from `main`).

### Phases planned
- Phase 0: tippecanoe → basin06.pmtiles (Karl runs locally)
- Phase 1: backend endpoint simplification (values + categorical response shapes)
- Phase 2: MapLibre frontend (replace Leaflet rendering, feature-state choropleth)
- Phase 3: test + verify, rsync pmtiles to server

Work begins next session.
