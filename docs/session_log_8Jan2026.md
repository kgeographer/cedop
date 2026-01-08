# Session Log: 8 January 2026

## Objective
Complete the environmental analysis pipeline for 258 World Heritage Cities by merging WHG coordinate data into `wh_cities`, assigning basin_ids, generating environmental signatures, and running PCA/clustering.

---

## 1. Updated `wh_cities` Table with Geometry and Basin IDs

**Script:** `scripts/update_wh_cities_geom.py`

### Data Merge Process
Joined three data sources to populate geometry:
```
whc_258_geom.tsv (WHG_internal_id → lon, lat)
    ↓ join via
whc_id_lookup.html (WHG_internal_id → whc_id)
    ↓ parse whc_id to integer
wh_cities.id
```

### Schema Changes
```sql
ALTER TABLE wh_cities ADD COLUMN geom geometry(Point, 4326);
ALTER TABLE wh_cities ADD COLUMN basin_id INTEGER;
```

### Results
| Metric | Count |
|--------|-------|
| Total cities | 258 |
| Geometries added | 258 |
| Basin IDs assigned | 254 |
| Missing basin (islands) | 4 |

**Cities without basin_id** (small islands outside HydroATLAS coverage):
- Angra do Heroísmo, Portugal (Azores)
- Cidade Velha, Cape Verde
- Levuka, Fiji
- St. George's, Bermuda

---

## 2. Created WHC Environmental Matrix Schema

**SQL:** `sql/whc_matrix_schema.sql`

Created parallel tables to the pilot (edop_*) schema:
- `whc_matrix` — 893 feature columns (27 numerical + 15 PNV + 847 tec categorical)
- `whc_pca_coords` — PCA coordinates (50 components)
- `whc_pca_variance` — Explained variance per component
- `whc_similarity` — Pairwise environmental similarity
- `whc_clusters` — K-means cluster assignments

---

## 3. Populated Environmental Matrix

**Script:** `scripts/populate_whc_matrix.py`

### Process
1. Load 254 cities with basin_id from `wh_cities`
2. Query basin08 for each city's basin environmental data
3. Normalize using existing `edop_norm_ranges` (global min/max)
4. Insert into `whc_matrix`

### Results
```
254 cities × 893 features
```

**Sample normalized values:**
| City | Country | n_temp_yr | n_precip_yr | n_elev_min |
|------|---------|-----------|-------------|------------|
| Agadez | Niger | 0.932 | 0.014 | 0.176 |
| Dakar | Senegal | 0.892 | 0.057 | 0.102 |
| Harar Jugol | Ethiopia | 0.795 | 0.083 | 0.325 |
| Timbuktu | Mali | 0.937 | 0.012 | 0.103 |

---

## 4. PCA and K-means Clustering

**Script:** `scripts/whc_pca_cluster.py`

### Configuration
- PCA: 50 components (max)
- K-means: k=10 clusters
- Similarity: Top 20 PCA components for distance calculation

### Variance Explained
```
  PC    Variance    Cumulative
  --    --------    ----------
   1      4.29%       4.29%
   2      3.60%       7.88%
   3      3.21%      11.10%
   4      3.09%      14.19%
   5      2.34%      16.53%
  ...
  10      1.46%      24.35%
```

With 893 features, variance is more distributed than the 20-site pilot. ~50 components needed for 80% variance.

### Environmental Clusters

| Cluster | Size | Profile | Example Cities |
|---------|------|---------|----------------|
| 1 | 49 | Mediterranean/dry temperate | Fez, Algiers, Rome, Aleppo, Jerusalem |
| 2 | 21 | Arid/desert | Timbuktu, Khiva, Damascus, Marrakesh |
| 3 | 15 | Northern Europe/cold | Stockholm, Tallinn, Riga, St. Petersburg |
| 4 | 22 | High altitude/continental | Cusco, Lijiang, Quito, Potosí, Sanaa |
| 5 | 22 | Tropical/warm wet-dry | Zanzibar, Mombasa, Dakar, Harar, Jaipur |
| 6 | 55 | Central Europe temperate | Vienna, Prague, Bruges, Salzburg, Bern |
| 7 | 4 | Major river floodplains | Cairo, Luang Prabang, Pyay, Bolgar |
| 8 | 39 | East Asia monsoon | Seoul, Kyoto, Nara, Suzhou, Hanoi |
| 9 | 26 | Tropical wet | Singapore, Malacca, Galle, Hội An |
| 10 | 1 | Outlier (fjord/extreme precip) | Bergen |

### Similarity Examples

**Most similar pairs:**
| City 1 | City 2 | Distance | Notes |
|--------|--------|----------|-------|
| Biertan | Sighișoara | 0.00 | Same basin, Romania |
| Split | Trogir | 0.00 | Same basin, Croatia |
| Amsterdam | Beemster | 0.00 | Same basin, Netherlands |
| Lima | Rimac | 0.00 | Same basin, Peru |

**Cities most similar to Timbuktu (environmental):**
1. Khiva, Uzbekistan (dist=4.61)
2. Zabid, Yemen (dist=5.52)
3. Damascus, Syria (dist=5.90)
4. Erbil, Iraq (dist=6.13)
5. Aktau, Kazakhstan (dist=6.45)

All arid zone cities — clustering captures climate-environment relationships well.

---

## Persisted Data Summary

| Table | Rows | Description |
|-------|------|-------------|
| wh_cities | 258 | + geom, basin_id columns |
| whc_matrix | 254 | Environmental feature vectors |
| whc_pca_coords | 254 | 50 PCA components per city |
| whc_pca_variance | 50 | Explained variance |
| whc_similarity | 32,131 | Pairwise distances (upper triangle) |
| whc_clusters | 254 | Cluster assignments |

---

## Files Created

```
scripts/
├── update_wh_cities_geom.py    # Merge geometry + assign basin_id
├── populate_whc_matrix.py      # Environmental matrix population
└── whc_pca_cluster.py          # PCA + clustering + similarity

sql/
└── whc_matrix_schema.sql       # WHC environmental analysis tables

output/corpus_258/
└── env_clusters.png            # Cluster visualization (PC1 vs PC2)
```

---

## Next Steps

- [ ] Persist wiki/semantic data from `output/corpus_258/` to database:
  - `band_embeddings.json` → whc_band_embeddings table
  - `band_summaries.json` → whc_band_summaries table
- [ ] Cross-analysis: environmental clusters vs. text embedding clusters
- [ ] UI integration for band-specific similarity
- [ ] Add remaining categorical columns to whc_matrix (fec, cls, glc, etc.)
