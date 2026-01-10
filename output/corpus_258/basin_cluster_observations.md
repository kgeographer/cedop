# Basin Cluster Analysis: Observations and Interpretation

**Date:** 9 January 2026
**Author:** Claude Code (Opus 4.5)
**Context:** EDOP project - Environmental Dimensions of Place

---

## Overview

190,675 sub-basins from HydroATLAS level 8 were clustered into 20 environmental types using K-means on 98 features derived from bands A-D (physiographic, hydro-climatic, bioclimatic, and anthropocene markers). The resulting clusters were then cross-referenced with 254 World Heritage Cities to explore how heritage designation patterns relate to global environmental geography.

---

## Key Finding: Selection Bias in Heritage Designation

The most striking result is the extreme concentration of WHC cities in a single environmental cluster:

| Cluster | Pattern | Cities | % of WHC |
|---------|---------|--------|----------|
| 0 | Temperate continental | 102 | 40.2% |
| 11 | Mediterranean | 52 | 20.5% |
| 16 | Tropical coastal | 20 | 7.9% |
| All others | Various | 80 | 31.5% |

**Cluster 0 alone contains more WHC cities than all other 19 clusters combined (excluding Mediterranean).**

This does not reflect where cities exist globally—it reflects where UNESCO/OWHC heritage designation has historically focused.

---

## Cluster Distribution Analysis

### Clusters with High City Counts

| Cluster | Label | Basin Count | City Count | Example Cities |
|---------|-------|-------------|------------|----------------|
| 0 | Temperate continental | 18,256 | 102 | Paris, Berlin, Vienna, Kyoto, Prague, Seoul |
| 11 | Mediterranean | 9,279 | 52 | Fez, Granada, Damascus, Dubrovnik, Jerusalem |
| 16 | Tropical coastal | 18,967 | 20 | Singapore, Zanzibar, Salvador, Bridgetown |
| 6 | Subtropical seasonal | 6,898 | 16 | Havana, Istanbul, Jaipur, Mexico City |
| 8 | Semi-arid highlands | 12,424 | 13 | Ouro Preto, Harar, Yazd, San Miguel de Allende |

### Clusters with Zero Cities

| Cluster | Label | Basin Count | Environmental Characteristics |
|---------|-------|-------------|------------------------------|
| 1 | Arctic highlands | 1,230 | Avg temp -14.8°C, 1892m elevation |
| 4 | Hot desert | 11,836 | Avg temp 23.6°C, 58mm precip/yr, aridity index 3 |
| 9 | Arctic alpine | 1,229 | Avg temp -19.8°C, 3202m elevation |
| 15 | Subarctic continental | 3,121 | Avg temp -16.2°C, 1939m elevation |
| 18 | Cold semi-arid | 3,297 | Avg temp -7.7°C, 436mm precip/yr |

These empty clusters represent environments where:
1. Human settlement is sparse or absent
2. Cities exist but are not in the OWHC network
3. Heritage designation processes have not reached these regions

---

## Interpretive Observations

### 1. The Temperate "Sweet Spot"

Cluster 0 captures the environmental conditions that historically supported:
- Agricultural surplus (adequate rainfall, moderate temperatures)
- Dense settlement patterns
- State formation and monumental architecture
- The urban traditions that produced UNESCO-recognized heritage

This is not coincidental—it represents the environmental niche where European, East Asian, and parts of South Asian civilization cores developed.

### 2. Mediterranean as Second Core

Cluster 11 (Mediterranean) shows a similar pattern. The classical antiquity heritage (Greece, Rome, Phoenicia) plus Iberian, Moroccan, and Levantine cities cluster tightly in this environmental type. Notably, Valparaíso (Chile) and Zacatecas (Mexico) fall here too—Mediterranean-analog climates in the Americas.

### 3. Tropical Underrepresentation

Cluster 16 (Tropical coastal) has nearly as many basins as Cluster 0 (18,967 vs 18,256) but only 20 cities vs 102. This 5:1 disparity suggests:
- Tropical urban heritage is underrepresented in OWHC
- Colonial-era port cities dominate the tropical list (Singapore, Salvador, Zanzibar)
- Indigenous tropical urbanism (less monumental, more organic) may not fit UNESCO criteria

### 4. The "Empty" Clusters Tell a Story

Five clusters have zero WHC cities. These are not devoid of human presence—they include:
- Hot deserts (cluster 4): 11,836 basins, but no WHC cities
- Arctic/subarctic zones (clusters 1, 9, 15, 18)

This absence reflects both genuine settlement sparsity AND the Euro-Mediterranean bias in heritage listing.

### 5. Outlier Clusters Reveal Distinctive Niches

Some small clusters capture very specific environmental-cultural patterns:
- **Cluster 7** (Major river floodplains, 3 cities): Cairo, Bolgar, Pyay—all on major rivers, all ancient urban sites
- **Cluster 13** (High Andes, 2 cities): Cusco, Potosí—extreme altitude Andean urbanism
- **Cluster 14** (Mexican highlands, 5 cities): Oaxaca, Puebla, Guanajuato—Mesoamerican highland tradition

---

## Methodological Notes

### Feature Space
98 dimensions derived from:
- 31 numerical variables (temperature, precipitation, elevation, discharge, etc.)
- 15 PNV (potential natural vegetation) share columns
- 52 one-hot encoded categoricals (lithology, biome, climate zone)

### Clustering Approach
- MiniBatch K-means (k=20)
- StandardScaler normalization
- 10 random initializations, best inertia selected
- Convergence at step 60/5720

### Limitations
1. Cluster labels are interpretive, derived from city distributions—not ground-truthed
2. k=20 is arbitrary; different k values would yield different groupings
3. One-hot encoding of high-cardinality categoricals may over-weight those features
4. The WHC city list itself is biased; using it to label clusters propagates that bias

---

## Implications for EDOP

1. **Selection bias is real and measurable.** Any analysis using WHC cities as a sample should acknowledge this.

2. **Swappable city lists are essential.** The current architecture (persisted `cluster_id` on basins) supports this—alternative gazetteers can be overlaid without re-clustering.

3. **Environmental clusters reveal cultural patterns.** The clustering was purely environmental, yet the city distributions show clear cultural-historical groupings (Mediterranean antiquity, temperate Europe, Mesoamerican highlands, etc.).

4. **Future work should include underrepresented regions.** Adding cities from non-OWHC sources would test whether the empty clusters are truly devoid of heritage or just under-documented.

---

## Summary Table

| Cluster | Label | Basins | Cities | Notes |
|---------|-------|--------|--------|-------|
| 0 | Temperate continental | 18,256 | 102 | Euro/East Asian core |
| 1 | Arctic highlands | 1,230 | 0 | Too cold for dense settlement |
| 2 | Desert/arid | 16,632 | 10 | Oasis cities (Khiva, Bam, Jeddah) |
| 3 | Volcanic/tectonic highlands | 2,902 | 11 | Andes, Armenia, Bali |
| 4 | Hot desert | 11,836 | 0 | Sahara/Arabian core |
| 5 | Subarctic/boreal | 11,686 | 3 | Norway only |
| 6 | Subtropical seasonal | 6,898 | 16 | Monsoon Asia, Caribbean, Mexico |
| 7 | Major river floodplains | 812 | 3 | Cairo, Bolgar, Pyay |
| 8 | Semi-arid highlands | 12,424 | 13 | Brazil, Ethiopia, Mexico, Iran |
| 9 | Arctic alpine | 1,229 | 0 | Extreme cold + altitude |
| 10 | Tropical plateau | 10,235 | 6 | Brasília, Huế, Kandy |
| 11 | Mediterranean | 9,279 | 52 | Classical antiquity core |
| 12 | Nordic fjord/coastal | 3,121 | 3 | Norway, Finland |
| 13 | High Andes | 788 | 2 | Cusco, Potosí |
| 14 | Mexican highlands | 1,230 | 5 | Mesoamerican tradition |
| 15 | Subarctic continental | 3,121 | 0 | Siberia/Canada interior |
| 16 | Tropical coastal | 18,967 | 20 | Colonial ports, SE Asia |
| 17 | Sahel/tropical dry | 19,025 | 7 | Timbuktu, Agadez, Dakar |
| 18 | Cold semi-arid | 3,297 | 0 | Central Asia steppe |
| 19 | Central Asian steppe | 14,462 | 1 | Turkistan only |

---

*This document represents analytical observations from an AI collaborator and should be reviewed critically by domain experts.*
