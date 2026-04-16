# Cultural Datasets for EDOPS Evaluation

## Role in the Research Program

EDOPS generates structured environmental signatures for any location on Earth — characterizing the physical, hydrological, bioclimatic, and coastal conditions of a place and its upstream catchment. A central research question is whether these signatures correspond meaningfully with human settlement patterns, subsistence strategies, and social complexity.

Three complementary datasets provide the cultural side of this evaluation:

- **D-PLACE** — ethnographically documented societies, primarily pre-industrial, global coverage
- **Seshat** — historically documented polities, state-level complexity over deep time, spatially linked via Cliopatria
- **HYDE** — gridded historical population and land use reconstruction, 10,000 BCE to 2016 CE, global continuous coverage

Together they span from prehistoric hunter-gatherers to modern empires, from individual society locations to globally continuous population surfaces, enabling evaluation across the full range of human-environment relationships in space and time.

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

---

## HYDE
### History Database of the Global Environment

**Source**: Utrecht University / PBL Netherlands Environmental Assessment Agency (Klein Goldewijk et al.) · Free
**Scope**: Global · 10,000 BCE to 2016 CE · 5 arcminute resolution (~9 km at equator)

HYDE provides modeled reconstructions of historical population and land use as global gridded surfaces at discrete time steps (decadal from 1700 CE; century or millennium intervals before that). Unlike D-PLACE and Seshat, HYDE is not limited to documented societies or matched polities — it provides an estimate for every cell on Earth, making it the only evaluation dataset with complete spatial coverage.

### Key Variables

| Category | Variables |
|----------|-----------|
| **Population** | `popc` — total population count per cell; `popd` — population density (persons/km²); `rurc` — rural; `urbc` / `uopp` — urban |
| **Cropland** | `cropland` — total; `ir_norice` / `rf_norice` — irrigated/rainfed non-rice; `ir_rice` / `rf_rice` — irrigated/rainfed rice |
| **Pasture & Grazing** | `pasture`, `grazing`, `rangeland`, `conv_rangeland` |
| **Aggregates** | `tot_irri`, `tot_rainfed`, `tot_rice`, `shifting` |

### Uncertainty Structure

Each time step is distributed in three variants: **base** (best estimate), **lower**, and **upper** (uncertainty bounds). Pre-1700 CE reconstructions carry substantial uncertainty, increasing toward deeper prehistory. For evaluation purposes, the `base` variant is used.

### Role in Evaluation

HYDE's distinctive contribution is **global, continuous population coverage** across deep time. Where D-PLACE and Seshat sample specific societies and polities, HYDE allows evaluation at the level of all ~190,000 basin08 sub-basins simultaneously: does EDOPS environmental signature predict HYDE population density globally at a given century? This is a more demanding test than matched-sample experiments, and more robust to selection bias.

A secondary use is **land use as cultural outcome**: irrigated cropland (`tot_irri`) is a direct indicator of hydraulic agriculture — the subsistence strategy most closely tied to riverine environmental affordance. Correlating EDOPS upstream water variables with HYDE irrigation extent tests the signature's ability to predict the most environmentally grounded form of human land transformation.

**Note on conceptual framing**: HYDE encodes what humans *did* with their environment (population density, land transformation) rather than what the environment afforded. This places it squarely on the culture→environment axis that EDOP does not model directly, but which is central to CDOP. The evaluation use is directional: EDOP signature predicts HYDE outcome, not the reverse.

---

## Combined Evaluation Framework

| Dimension | D-PLACE | Seshat | HYDE |
|-----------|---------|--------|------|
| **Unit** | Ethnographic society | Historical polity | Grid cell (5') |
| **Scale** | Band → chiefdom → state | State → empire | Global continuous |
| **Time depth** | Ethnographic present (1850–1940) | ~3000 BCE to ~1900 CE | 10,000 BCE to 2016 CE |
| **Spatial link** | Direct lat/lon → EDOPS basin | Cliopatria polygon → EDOPS basin | Global raster → basin centroid |
| **Records** | 1,291 (EA) to 6,684 (all datasets) | 329 matched to spatial data | ~190,000 basin08 centroids |
| **Key cultural signal** | Subsistence type, kinship, settlement | Territory, population, complexity | Population density, land use |
| **Quantitative variables** | Subsistence % (Binford); population (EA202) | Territory (km²), population (time series) | `popc`, `popd`, `tot_irri` (continuous) |
| **Coverage bias** | Ethnographic record sampling bias | State-level societies; documentary record | Model uncertainty pre-1700 CE |
| **EDOP cross-check** | D-PLACE env vars vs. EDOPS signatures | Cliopatria spatial extent vs. EDOPS basin profile | EDOPS signature vs. HYDE population globally |

The three datasets together span the full range of human social organization and spatial coverage — from individual mobile foragers to globally continuous population surfaces, from prehistoric chiefdoms to modern empires — providing a robust and complementary basis for evaluating whether EDOPS environmental signatures correspond with the scale, type, and trajectory of human settlement and complexity.
