# Cultural Datasets for EDOPS Evaluation

## Role in the Research Program

EDOPS generates structured environmental signatures for any location on Earth — characterizing the physical, hydrological, bioclimatic, and coastal conditions of a place and its upstream catchment. A central research question is whether these signatures correspond meaningfully with human settlement patterns, subsistence strategies, and social complexity.

Two complementary datasets provide the cultural side of this evaluation:

- **D-PLACE** — ethnographically documented societies, primarily pre-industrial, global coverage
- **Seshat** — historically documented polities, state-level complexity over deep time, spatially linked via Cliopatria

Together they span from prehistoric chiefdoms to modern empires, from hunter-gatherer bands to bureaucratic states, enabling evaluation across a wide range of human-environment relationships.

---

## D-PLACE
### Database of Places, Language, Culture, and Environment

**Source**: [d-place.org](https://d-place.org) · CC-BY-NC-4.0
**Scope**: 1,291–6,684 societies depending on dataset · Global · Focal years typically 1850–1940

D-PLACE provides cross-cultural coded observations for ethnographically documented societies. Its societies are spatially joined to EDOPS basin signatures, enabling direct comparison of environmental profiles with cultural patterns.

### Primary Dataset: Ethnographic Atlas (EA)
1,291 societies · 94 variables · Global coverage

| Category | Example Variables |
|----------|------------------|
| **Subsistence & Economy** | Dependence on gathering, hunting, fishing, animal husbandry, agriculture (% scale); predominant subsistence type |
| **Settlement** | Settlement pattern (nomadic → complex permanent); community size |
| **Kinship & Marriage** | Descent system; marriage transactions (bride price, dowry); domestic organization |
| **Politics & Leadership** | Jurisdictional hierarchy; political succession; class distinctions |
| **Labour & Gender** | Sexual division of labor across 20+ subsistence activities |
| **Ritual & Religion** | High gods: presence and moral involvement |
| **Population** | Population size of ethnic group |

### Additional Datasets

| Dataset | Societies | Variables | Distinctive Content |
|---------|-----------|-----------|---------------------|
| **SCCS** (Standard Cross-Cultural Sample) | 186 | 1,781 | Statistically controlled sample; extended coverage of conflict, cognition, childhood, ecology |
| **Binford** (Hunter-Gatherers) | 339 | 40 | % dependence on gathering/hunting/fishing; mobility, group size, area; strong Australia + N. America coverage |
| **WNAI** (Western North American Indians) | 172 | 429 | Species presence/absence inventories (plants, mammals, fish, sea mammals); life zones |
| **Carneiro** (4th + 6th eds.) | 127–74 | 354–618 | Agricultural techniques, irrigation, soil management, social complexity, warfare |

### Environmental Variables (pre-extracted at society locations)
All ~1,988 societies across EA, Binford, SCCS, and WNAI have D-PLACE environmental values available for cross-validation against EDOPS:

- **Climate** (ecoClimate, 1900–1949): annual mean temperature, precipitation, and Colwell seasonality indices (constancy, contingency, predictability) for both
- **Terrain**: elevation, slope
- **Productivity** (MODIS NPP): monthly net primary production + Colwell indices
- **Biodiversity**: amphibian, bird, mammal, and vascular plant species richness
- **Biome / Ecoregion**: Olson et al. 2001 classification

---

## Seshat
### Global History Databank

**Source**: [seshat.info](https://seshat.info) · Academic use
**Scope**: 329 polities matched to Cliopatria spatial data · Global · ~3000 BCE to ~1900 CE

Seshat codes social complexity variables for historical polities at century-scale resolution, with temporal ranges (year_from / year_to) per observation. In Computing Place, Seshat data joins to **Cliopatria** (`gaz.clio_polities`) — a spatial table of ~15,690 historical polity polygons — via a shared identifier, enabling EDOPS basin signatures to be linked to polity-level complexity measures over time.

**329 distinct polities** in Cliopatria have Seshat data; **200** have quantitative population estimates.

### Social Complexity Variables (77 variables, 9 subsections)

| Subsection | Key Variables | Polities Covered |
|------------|--------------|-----------------|
| **Social Scale** | Polity territory (km²), polity population | 281–296 |
| **Hierarchical Complexity** | Administrative levels, settlement hierarchy, military levels, religious levels | 264–306 |
| **Information** | Written records, script type, phonetic/alphabetic writing, religious literature, sacred texts, practical literature, fiction, history, calendar, coinage, paper currency | 260–314 |
| **Law** | Formal legal code, courts, judges, professional lawyers | 286–293 |
| **Bureaucracy** | Full-time bureaucrats, specialized government buildings, examination system, merit promotion | 262–288 |
| **Professions** | Professional soldiers, professional priesthood, full-time artisans, merchants | 263–289 |
| **Transport Infrastructure** | Roads, bridges, canals, ports, couriers | 263–293 |
| **Specialized Buildings** | Irrigation systems, markets, ceremonial sites, communal buildings, burial sites | 245–318 |
| **Special-purpose Sites** | Burial sites, ceremonial sites, irrigation systems | 245 |

### General Variables (23 variables)
Identity, religion and religious tradition, language family, capital city, degree of centralization, suprapolity relations, preceding/succeeding entities.

---

## Combined Evaluation Framework

| Dimension | D-PLACE | Seshat |
|-----------|---------|--------|
| **Unit** | Ethnographic society | Historical polity |
| **Scale** | Band → chiefdom → state | State → empire |
| **Time depth** | Ethnographic present (1850–1940) | ~3000 BCE to ~1900 CE |
| **Spatial link** | Direct lat/lon → EDOPS basin | Cliopatria polygon → EDOPS basin |
| **Polities / societies** | 1,291 (EA) to 6,684 (all datasets) | 329 matched to spatial data |
| **Key cultural signal** | Subsistence type, kinship, settlement | Territory, population, complexity levels |
| **Quantitative variables** | Subsistence % (Binford); population (EA202) | Territory (km²), population (time series) |
| **Environmental cross-check** | D-PLACE env vars vs. EDOPS signatures | Cliopatria spatial extent vs. EDOPS basin profile |

The combined record spans the full range of human social organization — from mobile foragers to industrial empires — across all world regions, providing a robust basis for evaluating whether EDOPS environmental signatures correspond with the scale, type, and trajectory of human settlement and complexity.
