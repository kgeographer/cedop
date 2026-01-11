# EDOP Database Schema Reference

*Last updated: 11 January 2026*

This document provides a reference for all database tables in the EDOP project to reduce context-building time between Claude Code sessions.

---

## SOURCE DATA TABLES

### Public Schema

| Table | Purpose | Rows |
|-------|---------|------|
| `basin08` | BasinATLAS raw data for level 8 sub-basins + `cluster_id` (added 9 Jan) | 190,675 |
| `eco847` | Ecoregions 2017 (eco_id, eco_name, biome, realm, geom) | 847 |
| `wh_cities` | World Heritage cities (OWHC members) + geom, basin_id | 258 |

### Gaz Schema (Gazetteers)

| Table | Purpose | Rows |
|-------|---------|------|
| `gaz.admin0` | Global countries | 242 |
| `gaz.admin1` | Global 1st level admin areas | 294 |
| `gaz.ccodes` | 2-letter ISO country codes → name lookup | — |
| `gaz.dkatlas` | Places from DK Atlas of World History | 10,669 |
| `gaz.dkatlas_geom` | DK Atlas rows with geometry | 6,566 |
| `gaz.pleiades` | Pleiades gazetteer dump Jan 2026 (34,315 w/coords) | 41,833 |
| `gaz.wh2025` | 2025 World Heritage list | 1,248 |
| `gaz.wh_cities` | Duplicate of World Heritage cities | 258 |

---

## RESULT TABLES

### 20 WH Sites Pilot (edop_* prefix)

*Created: 3-6 January 2026 | Source: docs/session_log_3Jan2026.md, session_log_5Jan2026.md, session_log_6Jan2026.md*

#### Environmental Analysis (3 Jan)

| Table | Rows | Description |
|-------|------|-------------|
| `edop_wh_sites` | 20 | Site metadata with basin FK, wiki_slug |
| `edop_norm_ranges` | 1 | Global min/max for normalization (62 values) |
| `edop_matrix` | 20 | Feature matrix (1,565 columns: 27 numerical + 15 PNV + 1,519 categorical) |
| `edop_pca_coords` | 20 | PCA coordinates (19 dims) |
| `edop_pca_variance` | 19 | Explained variance per component |
| `edop_similarity` | 380 | Pairwise Euclidean distances |
| `edop_clusters` | 20 | K-means cluster assignments (k=5) with labels |
| `edop_pca_loadings` | 950 | Top 50 loadings per component (19×50) |

#### Text Embeddings (5 Jan)

| Table | Rows | Description |
|-------|------|-------------|
| `edop_text_embeddings` | 20 | OpenAI embeddings (1536 dims), model, created_at |
| `edop_text_similarity` | 380 | Pairwise (site_a, site_b, distance, similarity) |
| `edop_text_clusters` | 20 | Cluster assignments (k=5) with distance_to_centroid |

#### Band Embeddings (6 Jan)

| Table | Rows | Description |
|-------|------|-------------|
| `edop_band_embeddings` | ~80 | Per-site per-band embeddings (20 sites × 4 bands) |
| `edop_band_similarity` | varies | Pairwise similarity by band |
| `edop_band_clusters` | varies | Cluster assignments by band |

---

### 258 WH Cities (whc_* prefix)

*Created: 8 January 2026 | Source: docs/session_log_8Jan2026.md*

#### Environmental Analysis

| Table | Rows | Description |
|-------|------|-------------|
| `whc_matrix` | 254 | Environmental feature vectors (893 columns: 27 numerical + 15 PNV + 847 TEC) |
| `whc_pca_coords` | 254 | 50 PCA components per city |
| `whc_pca_variance` | 50 | Explained variance per component |
| `whc_similarity` | 32,131 | Pairwise environmental distances (upper triangle) |
| `whc_clusters` | 254 | Environmental cluster assignments (k=10) with labels |

**Note:** 4 cities lack basin_id (small islands outside HydroATLAS): Angra do Heroísmo, Cidade Velha, Levuka, St. George's

#### Text/Semantic Analysis

| Table | Rows | Description |
|-------|------|-------------|
| `whc_band_summaries` | 1,032 | LLM-generated Wikipedia summaries (258 × 4 bands) |
| `whc_band_clusters` | 1,217 | Text embedding clusters (5 bands incl. composite, k=8) |
| `whc_band_similarity` | 12,170 | Top-10 similar cities per city per band |
| `whc_band_metadata` | 1 | Embedding model config (text-embedding-3-small) |

---

### Global Basin Clustering

#### Simplified Clustering (9 Jan)

*Source: docs/session_log_9Jan2026.md*

| Table/Column | Rows | Description |
|--------------|------|-------------|
| `basin08.cluster_id` | 190,675 | K-means cluster assignment (k=20) based on 98 features |

Clusters derived from 98 features (bands A-D): 31 numerical + 15 PNV + 52 one-hot categorical. Indexed for fast queries.

#### Full-Dimensional Clustering (11 Jan)

*Source: docs/session_log_11Jan2026.md*

| Table | Rows | Description |
|-------|------|-------------|
| `basin08_pca_clusters` | 190,675 | K-means cluster assignment (k=20) based on full 1,565 features |

Pipeline: 1,565 features (27 numerical + 15 PNV + 1,519 one-hot categorical) → sparse matrix → PCA (150 components, 86.2% variance) → k-means (k=20).

**Output files** (in `output/`):
- `basin08_sparse_matrix.npz` — sparse feature matrix (13 MB)
- `basin08_pca_coords.npy` — PCA coordinates (109 MB)
- `basin08_pca_loadings.npy` — feature loadings
- `basin08_pca_variance.json` — variance explained per component
- `basin08_cluster_assignments.npy` — cluster labels
- `basin08_cluster_centroids.npy` — for assigning new points

---

## KEY RELATIONSHIPS

```
basin08.hybas_id ← edop_wh_sites.basin_id
basin08.hybas_id ← wh_cities.basin_id
edop_wh_sites.site_id → edop_matrix.site_id
edop_wh_sites.site_id → edop_pca_coords.site_id
edop_wh_sites.site_id → edop_similarity.site_a/site_b
edop_wh_sites.site_id → edop_clusters.site_id
wh_cities.id → whc_matrix.city_id
wh_cities.id → whc_pca_coords.city_id
wh_cities.id → whc_similarity.city_a/city_b
wh_cities.id → whc_clusters.city_id
wh_cities.id → whc_band_*.city_id
```

---

## FEATURE DIMENSIONS

### Environmental Signature (1,561 total for pilot, 893 for WHC)

| Category | Pilot (20 sites) | WHC (258 cities) | Notes |
|----------|------------------|------------------|-------|
| Numerical fields | 27 | 27 | Elevation, temp, precip, discharge, etc. |
| PNV (vegetation share) | 15 | 15 | Continuous 0-1 values |
| TEC (terrain/ecoregion) | 847 | 847 | One-hot encoded |
| FEC (freshwater ecology) | 426 | — | Not yet added to WHC |
| CLS (climate) | 110 | — | Not yet added to WHC |
| GLC (land cover) | 126 | — | Not yet added to WHC |

### Text Embedding (1,536 dimensions)

- Model: OpenAI `text-embedding-3-small`
- 4 semantic bands: history, environment, culture, modern
- Composite: all bands concatenated before embedding

---

## EXAMPLE QUERIES

```sql
-- Sites most similar to a given site (environmental)
SELECT b.name_en, ROUND(distance::numeric, 2)
FROM edop_similarity s
JOIN edop_wh_sites a ON a.site_id = s.site_a
JOIN edop_wh_sites b ON b.site_id = s.site_b
WHERE a.name_en = 'Timbuktu'
ORDER BY distance LIMIT 5;

-- All sites in a cluster
SELECT s.name_en, c.cluster_id
FROM edop_clusters c
JOIN edop_wh_sites s ON s.site_id = c.site_id
WHERE c.cluster_id = 4;

-- WHC cities similar to Timbuktu (semantic)
SELECT c.title, s.similarity
FROM whc_band_similarity s
JOIN wh_cities c ON c.id = s.city_b
WHERE s.city_a = (SELECT id FROM wh_cities WHERE title ILIKE '%timbuktu%')
  AND s.band = 'composite'
ORDER BY s.similarity DESC
LIMIT 10;

-- Cities in a basin cluster type
SELECT c.title, c.country
FROM wh_cities c
JOIN basin08 b ON c.basin_id = b.hybas_id
WHERE b.cluster_id = 11;  -- Mediterranean cluster
```

---

## PENDING WORK

- [ ] Add FEC, CLS, GLC categorical columns to `whc_matrix` (currently 893 cols, target ~1,561)
- [ ] Compute per-band environmental similarity (bands A-D) for UI dropdowns
- [ ] Cross-analysis: environmental clusters vs. text embedding clusters

---

## SESSION LOG INDEX

| Date | Focus | Key Outputs |
|------|-------|-------------|
| 3 Jan 2026 | 20 WH sites environmental signatures + PCA | `edop_wh_sites`, `edop_matrix`, `edop_pca_*`, `edop_similarity`, `edop_clusters` |
| 4 Jan 2026 | UI: cluster badges, similarity button, color-coded markers | *UI features only* |
| 5 Jan 2026 | 20 WH sites text embeddings | `edop_text_embeddings`, `edop_text_similarity`, `edop_text_clusters` |
| 6 Jan 2026 | 20 WH sites band embeddings | `edop_band_embeddings`, `edop_band_similarity`, `edop_band_clusters` |
| 7 Jan 2026 | 258 WHC text pipeline (file output) | Files: `output/corpus_258/` |
| 8 Jan 2026 | 258 WHC environmental + text to DB | `whc_matrix`, `whc_pca_*`, `whc_clusters`, `whc_band_*` |
| 9 Jan 2026 | UI polish, basin clustering (190k), Basins tab | `basin08.cluster_id`, new API endpoints |
| 11 Jan 2026 | Full 1,565-dim basin clustering pipeline | `basin08_pca_clusters`, output files |
