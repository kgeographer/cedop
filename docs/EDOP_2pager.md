# EDOP: Environmental Dimensions of Place

## A Platform for Spatial Humanities Research

### What is EDOP?

EDOP (Environmental Dimensions of Place) is a web-based platform that assigns standardized environmental "signatures" to any location on Earth. By integrating global datasets on climate, hydrology, terrain, and land cover, EDOP enables researchers to characterize places by their physical geography and explore relationships between environment and human activity across space and time.

The platform is designed for historians, archaeologists, geographers, and other humanities scholars who work with place-based data but lack easy access to environmental context. Rather than requiring GIS expertise or large dataset downloads, EDOP provides this context through a simple web interface and API.

### How It Works

EDOP draws on **BasinATLAS**, a global hydrological dataset that divides Earth's land surface into ~190,000 sub-basins at approximately 100-1000 km² resolution. Each basin carries nearly 300 environmental attributes covering:

- **Physiography**: elevation, slope, terrain roughness
- **Hydrology**: precipitation, runoff, groundwater depth, river discharge
- **Climate**: temperature regimes, aridity, frost days, potential evapotranspiration
- **Land cover**: forest, cropland, wetland, urban extent
- **Soils**: clay/sand content, organic carbon, water holding capacity

EDOP normalizes and organizes these into a 47-field "signature" grouped by temporal persistence—from geological features that change over millennia to land use patterns that shift within decades.

Given any coordinates, EDOP returns the environmental signature for that location, enabling systematic comparison across sites.

### Current Capabilities

**Environmental Similarity Analysis**
EDOP computes similarity between places based on their full environmental signatures. For the 258 UNESCO World Heritage Cities, this reveals non-obvious groupings: Timbuktu clusters with Khiva and Zabid (arid trade cities); Bruges with Lübeck and Novgorod (temperate mercantile ports). These patterns emerge from environment alone, without cultural or historical input.

**Integration with D-PLACE**
The pilot integrates 1,291 ethnographically documented societies from D-PLACE (Database of Places, Language, Culture, and Environment). Users can filter societies by cultural attributes—subsistence strategy, religious beliefs, domestic organization—and see their distribution across environmental zones. Early exploration shows expected patterns (intensive agriculture concentrates in warm, seasonally wet environments) and surfaces questions for further investigation (societies with moralizing high gods occur in significantly drier environments than those without).

**Environmental Clustering**
Using dimensionality reduction and clustering on the full signature space, EDOP identifies 20 distinct environmental types globally—"Cold high plateau," "Hot subhumid lowland," "Warm semi-arid upland," etc. These clusters group places by environmental similarity regardless of geographic proximity, enabling comparison of analogous environments across continents.

**Bioregion Integration**
EDOP incorporates the OneEarth bioregion framework, allowing navigation from global realms down to individual ecoregions. Wikipedia-derived summaries provide ecological context for each of the 847 ecoregions.

### Research Applications

EDOP is designed to support questions like:

- How do environmental constraints shape settlement patterns, subsistence strategies, or trade networks?
- Which historical sites share environmental conditions, and what might that suggest about parallel adaptations?
- How does environmental context vary across a cultural region, migration route, or imperial extent?
- What environmental niches supported particular forms of social organization?

The platform does not answer these questions directly—it provides the environmental data layer that makes them tractable.

### Technical Details

- **Backend**: Python/FastAPI with PostgreSQL/PostGIS
- **Data sources**: HydroSHEDS BasinATLAS, OneEarth Bioregions, D-PLACE, Wikipedia
- **Access**: Web interface for exploration; REST API for programmatic access
- **Deployment**: Currently running as a pilot at [URL]

### Status and Next Steps

EDOP is in active development as a pilot project. Current work focuses on:

- Expanding cultural database integrations beyond D-PLACE
- Adding historical climate reconstructions for paleoenvironmental queries
- Developing case studies with domain experts
- Exploring connections to existing gazetteers and linked data infrastructure

We welcome collaboration with researchers who have place-based datasets that could benefit from environmental context, or domain expertise that could guide the platform's development.

---

*EDOP is developed by Karl Grossner at the World Historical Gazetteer project. For more information or to discuss collaboration, contact [email].*
