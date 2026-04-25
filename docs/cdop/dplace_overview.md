# D-PLACE Data Overview

**D-PLACE** (Database of Places, Language, Culture, and Environment) aggregates cross-cultural anthropological and environmental data for ethnographically documented societies worldwide. All data is available via [d-place.org](https://d-place.org) and the [D-PLACE GitHub organization](https://github.com/D-PLACE) in CLDF format.

This document summarizes the datasets available in Computing Place's local `dplace` schema (loaded from CLDF v3.3.0).

---

## Cultural Datasets

### Ethnographic Atlas (EA)
**Source**: Murdock et al. 1999
**Societies**: 1,291 (global coverage)
**Variables**: 94 (ordinal and categorical)
**Focal period**: Typically 1850–1940 ("ethnographic present")

The EA is the broadest cross-cultural dataset, covering subsistence economy, kinship and marriage, community organization, politics, labor division, housing, and ritual across all world regions. It is the primary cultural dataset used in Computing Place.

**Variable categories**: Subsistence & Economy · Kinship & Marriage · Community Organization & Settlement · Politics & Leadership · Labour & Gender · Ritual · Population

**Example variables**:
| ID | Variable | Type |
|----|----------|------|
| EA001 | Subsistence economy: gathering | Ordinal |
| EA002 | Subsistence economy: hunting | Ordinal |
| EA003 | Subsistence economy: fishing | Ordinal |
| EA005 | Subsistence economy: agriculture | Ordinal |
| EA030 | Settlement pattern | Categorical |
| EA034 | High gods: presence and activity | Categorical |
| EA042 | Subsistence economy: predominant type | Categorical |
| EA066 | Community size | Ordinal |
| EA070 | Political succession | Categorical |
| EA202 | Population | Continuous |

---

### Standard Cross-Cultural Sample (SCCS)
**Source**: Murdock & White 1969
**Societies**: 186 (statistically controlled, one per culture area)
**Variables**: 1,781 (the largest variable set in D-PLACE)
**Focal period**: Varies by society

The SCCS is a methodologically controlled subset of the EA designed to minimize Galton's problem (autocorrelation from cultural diffusion). Its much larger variable set extends into childhood and life cycle, conflict, cognition, ecology, and many detailed subsistence and political variables not coded in the EA.

**Variable categories**: Subsistence · Economy · Labour · Ecology · Politics · Kinship · Marriage · Childhood & Life cycle · Conflict · Ritual · Cognition

**Example variables**:
| ID | Variable | Type |
|----|----------|------|
| SCCS1 | Intercommunity trade as food source | Ordinal |
| SCCS10 | Animals hunted | Categorical |
| SCCS100 | Food collection: sexual division of labor | Categorical |
| SCCS208 | Slavery | Ordinal |
| SCCS1000 | Enculturative continuity for boys | Ordinal |
| SCCS1157 | Warfare frequency | Ordinal |

---

### Binford Hunter-Gatherer Dataset
**Source**: Binford 2001, *Constructing Frames of Reference*
**Societies**: 339 (hunter-gatherers globally; strong coverage of Australia, northern North America)
**Variables**: 40 (continuous and categorical)
**Focal period**: Varies; mostly 19th–early 20th century

Compiled specifically to study hunter-gatherer behavioral diversity in relation to environment. Variables include subsistence economy proportions (gathering, hunting, fishing), group mobility and size, demography, domestic organization, and political structure. Environmental data for Binford societies is supplied via D-PLACE's shared environmental datasets (ecoclimate, MODIS, etc.), not Binford's own variables.

**Variable categories**: Subsistence & Economy · Population & Demography · Settlement & Mobility · Kinship & Marriage · Politics · Anthropometry

**Example variables**:
| ID | Variable | Type |
|----|----------|------|
| B001 | Subsistence economy: gathering (% dependence) | Continuous |
| B002 | Subsistence economy: hunting (% dependence) | Continuous |
| B003 | Subsistence economy: fishing (% dependence) | Continuous |
| B007 | Area occupied by ethnic group (km²) | Continuous |
| B008 | Population density (persons/km²) | Continuous |
| B013 | Number of moves per year | Continuous |
| B014 | Distance moved per year (km) | Continuous |
| B029 | Jurisdictional hierarchy | Categorical |

---

### Western North American Indians (WNAI)
**Source**: Jorgensen 1980, *Western Indians*
**Societies**: 172 (western North America only)
**Variables**: 429

Dense regional coverage of western North America. Notably includes species presence/absence inventories: specific plant species (oaks, pines, cacti, food plants), sea mammals, land mammals, fish (including salmon runs), and birds — making it the most ecologically detailed dataset in D-PLACE for its region.

**Variable categories**: Ecology (species inventories) · Subsistence · Community organization · Politics · Life zones

---

### Carneiro Dataset (4th and 6th Editions)
**Source**: Robert L. Carneiro
**Societies**: 127 (4th ed.) / 74 (6th ed.)
**Variables**: 354 / 618

Focused on social complexity and agricultural evolution. Emphasizes presence/absence of agricultural techniques, soil management, irrigation, land tenure, craft specialization, political hierarchy, and warfare. The 6th edition expands and revises the 4th.

**Example variables**:
| ID | Variable | Type |
|----|----------|------|
| CARNEIRO4_001 | Agriculture present | Categorical |
| CARNEIRO4_006 | Animal-drawn plow | Categorical |
| CARNEIRO4_007 | Fertilization of land | Categorical |
| CARNEIRO4_025 | Irrigation | Categorical |

---

### Cross-Cultural Music Corpus (CCMC)
**Source**: Bertolo et al. 2023
**Societies**: 410
**Variables**: 1 (annotation of 1,000+ audio recordings)

Audio corpus with annotated recordings from societies worldwide; behavioral context, region, and language tagged. Not directly relevant to environmental analytics but potentially useful for CDOP's cultural signal layer.

---

## Environmental Datasets

All environmental values are **pre-extracted at each society's documented location** (point samples). They cover ~1,988 societies across EA, Binford, SCCS, and WNAI datasets.

| Dataset | Source | Variables | Coverage |
|---------|--------|-----------|----------|
| ecoClimate | Lima-Ribeiro et al. 2015 (CCSM model, 1900–1949 baseline) | 10 | ~1,988 societies |
| GMTED2010 | USGS Global Terrain Elevation Data | 2 | ~1,988 societies |
| GSHHS | Wessel & Smith 2015 | 1 | ~1,988 societies |
| MODIS NPP | NASA TERRA/MODIS (2000–2016) | 5 | ~1,987 societies |
| Jenkins et al. | Terrestrial vertebrate diversity 2013 | 3 | ~1,958–1,971 societies |
| Kreft & Jetz | Vascular plant diversity 2007 | 1 | ~1,963 societies |
| TEOW | Olson et al. 2001 terrestrial ecoregions | 2 | ~1,987–1,988 societies |

### Environmental variable list

**Climate** (ecoClimate, 1900–1949 baseline):
- Annual mean temperature (°C)
- Annual temperature variance
- Temperature constancy, contingency, predictability (Colwell 1974)
- Monthly mean precipitation (ml/m²/month)
- Annual precipitation variance
- Precipitation constancy, contingency, predictability (Colwell 1974)

**Physical landscape** (GMTED2010 / GSHHS):
- Elevation (m above sea level)
- Slope (mean incline, degrees)
- Distance to coast (km)

**Ecosystem productivity** (MODIS, 2000–2016):
- Monthly mean net primary production (gC/m²/month)
- Annual NPP variance
- NPP constancy, contingency, predictability (Colwell 1974)

**Biodiversity** (Jenkins et al. / Kreft & Jetz):
- Amphibian species richness
- Bird species richness
- Mammal species richness
- Vascular plant species richness

**Biome / Ecoregion** (Olson et al. 2001):
- Biome classification (14 global biomes)
- Ecoregion classification

---

## Cross-Dataset Linkage

Societies across datasets are linked via the `xd_id` field — a cross-dataset identifier that allows the same real-world society to be joined across EA, SCCS, and Binford records. For example, the !Kung appear in EA, SCCS, and Binford under the same `xd_id`, enabling combined variable queries.

Example societies appearing in three or more datasets:

| Society | EA | SCCS | Binford |
|---------|-----|------|---------|
| !Kung | ✓ | ✓ | ✓ |
| Copper Inuit | ✓ | ✓ | ✓ |
| Montagnais | ✓ | ✓ | ✓ |
| Dakelh | ✓ | — | ✓ |

---

## Relationship to EDOPS

D-PLACE societies serve as a **labeled dataset** for environmental-cultural correspondence analysis. The 1,291 EA societies (and 339 Binford societies) have been spatially joined to EDOPS's BasinATLAS basin grid, enabling EDOPS environmental signatures to be compared against D-PLACE cultural codings.

EDOPS complements and extends D-PLACE's own environmental data:

| Dimension | D-PLACE | EDOPS |
|-----------|---------|-------|
| Coverage | ~1,988 society locations | 190,675 basins (global) |
| Climate | ecoClimate point sample (10 vars) | WorldClim local + upstream (Band C) |
| Hydrology | — | Discharge, runoff, groundwater, wetlands (Band B) |
| Physiography | Elevation, slope (point sample) | Elevation range, gradient, lithology, karst (Band A) |
| Coastality | Distance to coast | Flow distance to outlet, endorheic flag, outlet type (Band E) |
| Biodiversity/NPP | 9 variables | — (gap) |
| Seasonality | Colwell indices for temp, precip, NPP | — (gap; candidate for future addition) |
| Upstream context | None | Local/upstream duality throughout |
| Temporal | — | LMR v2.1 paleoclimate + eVolv2k (Band T) |

**License**: All D-PLACE datasets are CC-BY-NC-4.0 (non-commercial use).
