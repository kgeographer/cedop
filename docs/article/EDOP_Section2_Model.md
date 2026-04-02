# 2. The EDOP Model

EDOP models environmental context as a constructed, parameterized representation rather than a fixed set of attributes. At its core, the model defines how environmental information is selected, structured, and aggregated to produce a signature for a given place or region. These choices—spatial units, scale, variables, and process treatment—are explicit and configurable.

## 2.1 Spatial Units and Neighborhood Definition

EDOP adopts hydrological sub-basins (HydroATLAS) as primary units because they encode physical relationships (notably drainage and flow) rather than arbitrary administrative boundaries. However, “neighborhood” is a parameter: alternatives include buffers, ecoregions, or historically derived geometries. Different choices yield different aggregations and interpretations.

## 2.2 Scale and Sensitivity

HydroATLAS provides multiple basin levels (resolutions). Scale selection shapes the resulting description: coarse scales smooth variability; fine scales may amplify noise. EDOP treats scale as variable, enabling multi-scale signatures and explicit assessment of scale sensitivity (i.e., incorporating MAUP into the analysis rather than hiding it).

## 2.3 Variables and Dimensional Structure

Signatures combine variables spanning climate, hydrology, terrain, vegetation, and land cover (primarily from HydroATLAS and related sources). To enable comparison, EDOP transforms this heterogeneous space into a continuous vector space (e.g., PCA), supporting similarity via distance metrics (e.g., cosine). Variable selection and transformation are parameterized to emphasize different environmental facets.

## 2.4 Local and Relational Environmental Context

EDOP distinguishes between local conditions (attributes of the containing unit) and relational conditions derived from spatial connections. For hydrology, this includes upstream basins. Aggregating upstream attributes produces what a location “receives” from its catchment. The divergence between local and upstream conditions can be analytically meaningful.

## 2.5 Network Structure and Environmental Flow

Using the directed basin graph (upstream/downstream links), EDOP traverses drainage networks to aggregate attributes along flow paths. Current implementations include simple (area- or unweighted) summaries, with extensions to distance-weighted aggregation and decay functions that reflect diminishing influence with network distance.

## 2.6 Parameterization and Model Space

EDOP exposes key elements as parameters:

- spatial units / neighborhood definition
- scale (basin level)
- variable selection and weighting
- transformation method (e.g., PCA configuration)
- inclusion and treatment of relational components (e.g., upstream)
- aggregation/decay functions for network effects

Different settings produce different signatures for the same place. EDOP is designed to explore this model space rather than fix a single “correct” configuration.
