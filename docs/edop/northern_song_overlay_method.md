# Northern Song Polity–Basin Overlay: Method and Rationale

*Documenting the areal interpolation demonstration produced 08 Feb 2026*

---

## 1. Objective

Demonstrate how EDOP's basin-level environmental data can be aggregated to characterize the environmental signature of a historical polity — and how that signature changes as the polity's territory expands or contracts over time. The Northern Song dynasty (962–980 CE) was chosen because it has three distinct territorial phases in the Cliopatria dataset, is well-known to the target audience (historians, spatial humanities researchers), and its southward expansion crosses a dramatic environmental gradient from arid continental north to humid subtropical south.

## 2. Data Sources

### Polity geometries
- **Table**: `gaz.clio_polities` (Cliopatria/Seshat dataset)
- **Columns**: `name`, `fromyear`, `toyear`, `geom` (MultiPolygon, EPSG:4326)
- Northern Song has 6 rows in the database, but only 3 distinct geometries:
  - 961–962 CE (identical geometry, compact northern territory)
  - 970 CE (southward expansion into Sichuan and middle Yangtze)
  - 980–1018 CE (identical geometry, full extent including southern China)
- We selected **962, 970, 980** as representative of the three distinct territorial phases.

### Environmental data
- **Table**: `public.basin08` (HydroATLAS level 08)
- **Resolution**: ~190,675 sub-basins globally, median area ~200 km²
- **Geometry**: `geom` (MultiPolygon, EPSG:4326)
- Each basin carries ~47 environmental attributes organized into four persistence bands (A–D)

## 3. Choice of Signature Variables

From the full EDOP signature (47 fields across 4 bands), 9 numerical fields were selected for this demonstration. The selection criteria were:

1. **Representativeness across bands**: fields from Bands A, B, and C (Band D excluded as anachronistic for a 10th-century polity)
2. **Continuous numerical values**: suitable for area-weighted averaging (categorical fields like biome or lithology class require different aggregation)
3. **Likely to show spatial variation across the Northern Song territory**: the north–south environmental gradient in eastern China spans arid steppe to subtropical monsoon

### Selected fields

**Band A — Physiographic bedrock** (geologically stable, relevant at any time scale)
- `ele_mt_smn` → Elevation min (m): basin floor elevation
- `ele_mt_smx` → Elevation max (m): basin ridge elevation
- `slp_dg_sav` → Slope average (°): terrain ruggedness

**Band B — Hydro-climatic baselines** (stable over centuries to millennia)
- `dis_m3_pyr` → Discharge (m³/s): annual river discharge
- `run_mm_syr` → Runoff (mm/yr): annual surface runoff
- `gwt_cm_sav` → Groundwater table depth (cm): subsurface water availability

**Band C — Bioclimatic proxies** (modern measurements used as spatial proxies; values are contemporary, not reconstructions of 10th-century conditions)
- `tmp_dc_syr` → Temperature (°C, stored as °C×10): annual mean temperature
- `pre_mm_syr` → Precipitation (mm/yr): annual precipitation
- `ari_ix_sav` → Aridity index: ratio of precipitation to potential evapotranspiration (higher = wetter)

### Why aridity index for map coloring

Aridity was chosen as the choropleth variable because:
- It is a single scalar that integrates temperature and precipitation into a moisture availability metric
- It shows the most dramatic and visually legible gradient across the Northern Song territory
- It directly conveys the "environmental enhancement" story: the Song gained access to dramatically wetter territory as it expanded south

### Epistemic caveat

All Band B and C values are modern measurements. They serve as proxies for *relative spatial variation* — the north is drier than the south today, and was drier than the south in 970 CE — but they are not reconstructions of 10th-century absolute values. Band A values (elevation, slope) are genuinely stable over historical timescales.

## 4. Spatial Intersection Method

For each of the 3 polity time-slices:

### Step 1: Find intersecting basins
```sql
SELECT b.hybas_id, b.ari_ix_sav, ...,
       ST_Intersection(b.geom, polity_geom) AS clipped_geom
FROM basin08 b
WHERE ST_Intersects(b.geom, polity_geom)
```
`ST_Intersects` identifies every basin that overlaps the polity polygon, including those only partially inside.

### Step 2: Compute intersection areas
```sql
ST_Area(ST_Intersection(b.geom, polity_geom)::geography) AS intersect_area
```
For each basin, the actual area of overlap is computed in square meters (using `::geography` for geodetic accuracy). A basin half-inside the polity boundary gets half its true area as the intersection area.

### Step 3: Compute area weights
```python
weight_i = intersect_area_i / sum(all intersect_areas)
```
Each basin's weight is its intersection area as a proportion of the total overlap area across all basins. This means:
- A basin fully contained within the polity gets weight proportional to its full area
- A basin partially inside gets weight proportional to only the overlapping portion
- All weights sum to 1.0

### Step 4: Weighted mean per variable
```python
signature_value = sum(weight_i * basin_value_i) for all intersecting basins
```
For each of the 9 signature variables, the polity's composite value is the area-weighted mean across all intersecting basins.

### Step 5: Clip geometries for visualization
The `ST_Intersection` geometry (the fragment of each basin inside the polity) is retained for map rendering. Basins are visually clipped at the polity boundary, colored by their environmental values.

## 5. Map Generation: The Slide Series

Three maps were generated with identical framing to enable slide-deck animation:

### Shared parameters
- **Spatial extent**: fixed to the bounding box of the 980 CE (largest) polity geometry, with 5% padding. All three maps show the same geographic window.
- **Color scale**: shared across all three maps. The aridity index range was computed from the 5th–95th percentile of all basin values across all three time-slices. This prevents the color mapping from shifting between slides.
- **Color map**: RdYlBu (diverging: red = arid, blue = wet)
- **Figure size**: 10×10 inches, 150 DPI

### Per-slide content
Each slide shows:
- The polity boundary for that year (dark red outline, 2.5pt)
- Clipped basin fragments within the polity, colored by aridity index
- Basin count annotation
- Empty space where the polity has not yet expanded (visible in 962 and 970)

### Animation effect
Because the extent and color scale are locked, advancing through slides produces the visual effect of:
1. **962 CE**: compact territory in the north, predominantly red/orange (arid)
2. **970 CE**: boundary expands south, blue patches appear in Sichuan basin
3. **980 CE**: full southern expansion, lower half saturated blue (wet)

## 6. Results Summary

| Year | Basins | Elev min (m) | Precip (mm/yr) | Aridity | Temp (°C) |
|------|--------|-------------|-----------------|---------|-----------|
| 962  | 1,407  | 320         | 691             | 64      | 12.5      |
| 970  | 2,506  | 498         | 828             | 80      | 12.4      |
| 980  | 4,217  | 326         | 1,117           | 102     | 14.8      |

The expansion from 962 to 980 CE tripled the number of intersecting basins, nearly doubled precipitation, increased the aridity index by 59%, and raised mean temperature by 2.3°C — all reflecting the incorporation of subtropical southern China.

## 7. Anticipated GIScience Questions

These are the questions a quantitative GIScientist (e.g., Goodchild) would likely ask, with current answers and honest assessments of where work is needed.

### Q1: What basin resolution are you using?

**Answer**: HydroATLAS level 08 — 190,675 sub-basins globally, median area ~200 km². This is one of 12 hierarchical levels available (01 = continental, 12 = headwater catchments). Level 08 was chosen as a balance between spatial detail and computational tractability.

**What's needed**: Sensitivity analysis across at least 3 levels (e.g., 06, 08, 10) to show how signature values change with resolution. This is straightforward to implement — the same intersection logic works at any level.

### Q2: How sensitive are results to resolution?

**Answer**: Not yet tested. At coarser resolution (fewer, larger basins), edge effects at the polity boundary would be larger — a single basin might span both inside and outside the polity, with the weighted average diluting the signal. At finer resolution, edge precision improves but computational cost increases and attribute reliability may decrease for very small basins.

**What's needed**: A systematic comparison showing how polity signatures change across basin levels for the same polity geometry. Ideally accompanied by a convergence analysis — at what resolution do signatures stabilize?

### Q3: How are intersecting basins weighted?

**Answer**: By intersection area. Each basin's weight is `ST_Area(ST_Intersection(basin, polity)) / total_intersection_area`. This is proper areal interpolation — partial overlaps contribute proportionally.

**What's needed**: Document whether alternative weighting schemes (e.g., by basin centroid containment, by proportion of basin inside the polity) produce materially different results. The current approach is defensible but should be compared.

### Q4: Are you normalizing by basin area within the polygon?

**Answer**: Yes. The weight is the intersection area (not the full basin area), so a large basin that barely clips the polity boundary gets minimal weight. The denominator is the sum of all intersection areas, not the polity area — meaning we're computing a weighted average over the environmental space that the polity actually covers in basin terms.

**Subtlety to address**: There may be small gaps between basins (HydroATLAS basins don't perfectly tile the Earth's surface in all areas), and conversely the polity boundary may extend into ocean or areas without basin coverage. The current approach silently ignores uncovered areas. This should be documented and quantified.

### Q5: Are you propagating uncertainty?

**Answer**: No. The current implementation treats each basin's attribute values as exact and computes a single weighted mean. There is no uncertainty band on the output.

**What's needed**: At minimum, report the weighted standard deviation alongside the weighted mean for each variable — this captures the internal variability. More rigorously, if HydroATLAS provides attribute uncertainty estimates, those could be propagated through the weighted average. The distributional approach discussed in `docs/edop/polity_signature_distributions.md` is one response to this concern.

### Q6: How stable is the aridity index across HydroATLAS versions?

**Answer**: Unknown. We use BasinATLAS v1.0 (the current and only public release as of 2026). The aridity index (`ari_ix_sav`) is derived from global climate datasets (WorldClim, CGIAR-CSI) that have their own version histories.

**What's needed**: Document the upstream data sources and their vintage. Acknowledge that the aridity index is a derived product with its own aggregation assumptions. If future HydroATLAS versions are released, a version comparison would be valuable.

### Q7: What happens if you use raster zonal stats directly instead of pre-aggregated basin values?

**Answer**: The current approach uses HydroATLAS's pre-aggregated basin-level values rather than computing zonal statistics from raw rasters. This is a deliberate design choice:

- **Reproducibility**: basin-level values are fixed, published, and citable
- **Consistency**: all EDOP users get the same values for the same basin
- **Practicality**: no need to maintain and process multi-terabyte raster datasets

The trade-off is that we inherit HydroATLAS's aggregation assumptions (how they summarized raster values within each basin). For the polity overlay, this means we're computing a weighted average of weighted averages — basin values are already spatial aggregates, and we're re-aggregating them over the polity.

**What's needed**: A comparison study for a small area: compute polity-level zonal stats directly from source rasters (e.g., WorldClim precipitation) and compare with the basin-aggregated approach. This would quantify the information loss from the two-stage aggregation.

## 8. Script Reference

- **Script**: `scripts/edop/polity_basin_overlay.py`
- **Output**: `output/edop/polity_overlay/` (PNGs + CSV, gitignored)
- **Dependencies**: psycopg, geopandas, matplotlib, shapely
- **Database**: `cedop` (PostgreSQL/PostGIS), tables `public.basin08` and `gaz.clio_polities`

---

*Prepared 08 Feb 2026 as a methodological reference for the Computing Place / EDOP project. Intended audience: the author (Karl Grossner), collaborators at ISHI (Pitt), and potential reviewers including Michael Goodchild.*
