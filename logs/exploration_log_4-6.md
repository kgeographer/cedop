## 2026-04-19 · Task 4 · Correlation structure within and across bands

**Method**: `notebooks/edop/explore/04_correlation_matrix.ipynb` · L8: 190,675 basins · 37 scalar variables · Spearman rank correlation (pairwise complete observations) · outputs: `04_correlation_matrix.csv`, `04_correlation_heatmap.png`, `04_high_correlation_pairs.csv`

---

### F4.1 — s/u pair redundancy: local and upstream climate variables are globally near-identical

**Finding**: The three climate s/u pairs are the most correlated in the entire matrix: `aridity` / `aridity_upstream` r = 0.984; `precip_yr` / `precip_yr_upstream` r = 0.987; `temp_yr` / `temp_yr_upstream` r = 0.989. Human variable pairs follow: `human_footprint_09` / `human_footprint_09_upstream` r = 0.951; `cropland_extent` / `cropland_extent_upstream` r = 0.950. These are not independent variables — globally, local and upstream values are nearly interchangeable for these variables.

**Implication**: The global near-identity of s/u pairs is consistent with F3.1 (median divergence = 0 for all pairs). For the majority of basins, including both local and upstream versions of the same climate or land-use variable in PCA adds a near-duplicate dimension without new information. In dimensionality reduction, one member of each s/u pair should be dropped — retain whichever is more theoretically motivated (upstream for process-aware characterization, local for site description). The divergence value itself (u−s or log₂(u/s)) may be more useful than either raw value for capturing the signature's distinctive content.

---

### F4.2 — Temperature internal redundancy; four variables behave as one

**Finding**: `temp_yr`, `temp_min`, `temp_max`, and `temp_yr_upstream` form the tightest cluster in the matrix. All six pairwise correlations exceed r = 0.77; four of six exceed r = 0.88. The highest: `temp_yr` / `temp_yr_upstream` = 0.989, `temp_yr` / `temp_min` = 0.963, `temp_min` / `temp_yr_upstream` = 0.954. The exception: `temp_min` / `temp_max` = 0.771 — seasonal range is partially independent of mean. Visible on the heatmap as the dark red 4×4 block in the Band C region.

**Implication**: For PCA or any dimensionality reduction, including all four temperature variables contributes three near-redundant dimensions. A single temperature variable (most likely `temp_yr`) represents the cluster; `temp_max` is the most independent of the four (lowest average r with others) and could be retained as a second temperature dimension if capturing thermal range is analytically important. `temp_yr_upstream` adds negligible information over `temp_yr` globally (r = 0.989) and can be dropped from dimensionality reduction — its signal is already in `temp_yr`.

---

### F4.3 — Discharge cluster redundancy; discharge_max proxies network size

**Finding**: `discharge_yr`, `discharge_min`, and `discharge_max` are strongly mutually correlated: yr/max r = 0.967; yr/min r = 0.933; max/min r = 0.855. Additionally, `discharge_max` / `river_area_upstream` r = 0.937 — the peak discharge of a basin is almost perfectly predicted by its total upstream network area. `discharge_yr` / `river_area_upstream` r = 0.886. These hydrological size variables form a single redundant cluster.

**Implication**: Only one discharge variable is needed in dimensionality reduction — `discharge_yr` is the natural choice (most commonly reported, best-studied). `river_area_upstream` is nearly redundant with `discharge_max` and represents the same underlying quantity (drainage network magnitude). The three discharge variables + `river_area_upstream` can be treated as four measures of one latent variable: basin hydrological size. Retain one; note the others as alternative representations.

---

### F4.4 — Human variables split into two sub-clusters: intensity and development

**Finding**: Band D contains two near-redundant sub-clusters. Sub-cluster 1 (human intensity): `pop_density`, `human_footprint_09`, `human_footprint_09_upstream`, `cropland_extent`, `cropland_extent_upstream` — all pairwise r = 0.72–0.95. Sub-cluster 2 (economic development): `gdp_avg` / `human_dev_idx` r = 0.910. The two sub-clusters are weakly to negatively correlated with each other: `gdp_avg` / `human_footprint_09` r = −0.307; `gdp_avg` / `pop_density` r = −0.452. High GDP/HDI areas are not the same as densely populated or heavily farmed areas — wealthy but sparsely settled economies (Northern Europe, North America) drive the negative cross-cluster correlation.

**Implication**: The two human sub-clusters measure different things and should not be collapsed. Sub-cluster 1 (intensity) captures anthropogenic landscape modification — agriculture, settlement, infrastructure. Sub-cluster 2 (development) captures economic modernity. For PCA, retain one variable from each sub-cluster: `human_footprint_09` from sub-cluster 1 (composite index), `gdp_avg` or `human_dev_idx` from sub-cluster 2. The negative cross-cluster correlation is itself a finding: intensive land use and economic development are not the same axis, and confusing them in a rubric would produce misleading environmental characterizations.

---

### F4.5 — Cross-band: soil texture co-varies with temperature; a weathering signal

**Finding**: The strongest cross-band correlations in the matrix involve soil texture (Band B) and temperature (Band C). `pct_clay` / `temp_min` r = 0.754; `pct_clay` / `temp_yr` r = 0.710; `pct_clay` / `temp_yr_upstream` r = 0.703. Inverse for silt: `pct_silt` / `temp_min` r = −0.701; `pct_silt` / `temp_yr` r = −0.658. Sand is less strongly correlated with temperature. Also: `pct_clay` / `permafrost_extent` r = −0.582 (warm soils have more clay; permafrost regions less). Visible on the heatmap as a red rectangle crossing the Band B soil-texture rows into the Band C temperature block.

**Implication**: This is a pedogenic signal, not a methodological artifact. Chemical weathering (which produces clay minerals) is temperature-dependent — hot, humid tropical environments produce deep, clay-rich soils; cold, high-latitude or high-altitude environments are dominated by physical weathering (which produces silt and sand from parent rock). The B×C correlation encodes a fundamental climate-soil feedback that operates over geological timescales. Practically: `pct_clay` is not an independent variable for PCA relative to temperature. Including both adds limited new information in warm-climate basins, though they diverge in cold or arid regions where weathering regimes differ.

---

### F4.6 — Cross-band: runoff and aridity are climate-determined; Band B partially redundant with Band C

**Finding**: `runoff` (Band B) / `aridity` (Band C) r = 0.782; `runoff` / `aridity_upstream` r = 0.775; `runoff` / `precip_yr` r = 0.774; `runoff` / `precip_yr_upstream` r = 0.760. Runoff is more strongly correlated with the climate variables than with most of its Band B neighbors. `discharge_yr` / `precip_yr` r = 0.544; `discharge_yr` / `aridity` r = 0.496.

**Implication**: Runoff is largely predictable from precipitation and aridity — it measures what is left after evapotranspiration, which is climate-driven. For dimensionality reduction, runoff does not add substantial new information beyond what aridity and precipitation already encode, except at the margin (where local geology, soil permeability, and land cover modify the climate signal). It may be worth retaining as a Band B representative if the goal is to have hydrology represented independently of climate, but its inclusion should be flagged as partially redundant.

---

### F4.7 — Permafrost as cross-band bridge: cold = uninhabited = high silt

**Finding**: `permafrost_extent` correlates negatively with the entire Band D human cluster: `pop_density` r = −0.512; `human_footprint_09` r = −0.534; `human_footprint_09_upstream` r = −0.557; `cropland_extent` r = −0.437; `cropland_extent_upstream` r = −0.452. It also correlates negatively with `pct_clay` (r = −0.582, Band B) and strongly negatively with all temperature variables (r = −0.688 to −0.720, Band C). In the heatmap: permafrost appears as a blue stripe running across both the Band C temperature block and the Band D human block.

**Implication**: Permafrost is a cross-band integrator: it encodes cold climate (C), physically-weathered soils (B), and absence of human settlement (D) in a single variable. Its correlations are not coincidences but reflect a coherent environmental syndrome — the high-latitude/high-altitude biome where climate, pedology, and human geography all co-vary. This makes permafrost a potentially powerful typological discriminator for clustering (Task 5), even though it is zero for 77% of basins (F1.7). When it fires, it organizes structure across multiple bands simultaneously.

---

### F4.8 — Band E (dist_sink) is structurally independent

**Finding**: `dist_sink` (flow distance to marine outlet) has no correlation above |r| = 0.41 with any other variable. Its strongest correlations: `elev_min` r = 0.408 (higher minimum elevation → farther from coast, expected); `discharge_yr` r = 0.270; `discharge_min` r = 0.280. All others are r < 0.25. The dist_sink row/column appears as a largely neutral (pale) stripe in the heatmap.

**Implication**: Coastality is structurally independent from climate, terrain, hydrology, and human variables — it adds a genuinely orthogonal dimension to the signature. A basin 5,000 km from the ocean is not systematically different in temperature, rainfall, or human footprint from a coastal basin — the position in the drainage network is a separate axis. This validates the prospectus claim that coastality is a "first-class signature component" — it is not captured by any other variable in the dataset.

---

### F4.9 — PCA exclusion candidates: variables redundant at |r| > 0.9

**Finding**: Eleven variable pairs exceed |r| = 0.9 (full list in `04_high_correlation_pairs.csv`). Grouped by redundancy cluster, the recommended exclusions for any PCA or clustering are: (1) from the climate s/u pairs, drop `temp_yr_upstream`, `precip_yr_upstream`, `aridity_upstream` — retain local values; (2) from the discharge cluster, drop `discharge_min` and `discharge_max` — retain `discharge_yr`; (3) drop `river_area_upstream` (r = 0.937 with `discharge_max`); (4) from human footprint, drop `human_footprint_09_upstream` — retain local; (5) drop `cropland_extent_upstream` — retain local; (6) drop `human_dev_idx` — retain `gdp_avg`. These six drops reduce the 37-variable set to 31 without losing substantial information.

**Implication**: The 31-variable reduced set retains one representative per redundant cluster and eliminates the most egregiously collinear variables. A further reduction to ~20 variables would require judgment calls about which cross-band redundancies to address (soil texture vs. temperature, runoff vs. aridity). That reduction decision belongs in Task 5 design, not Task 4 characterization — document it there with explicit rationale.

---

## 2026-04-19 · Task 5 · Geographic pre-clustering

**Method**: `notebooks/edop/explore/05_preclustering.ipynb` · L8: 190,675 basins · 20 Band A+B+C variables (post-F4.9 reductions) · log1p + StandardScaler normalization · k-means k=20 (n_init=10) + sklearn HDBSCAN (min_cluster_size=1000, min_samples=50) · outputs: `05_kmeans_global_map.png`, `05_hdbscan_global_map.png`, `05_kmeans_cluster_summary.csv`, `05_cluster_comparison.png`, `05_cluster_assignments.csv`

---

### F5.1 — k-means global map: clusters recover recognizable environmental zones without geographic input

**Finding**: The k-means global map shows strong geographic coherence — contiguous regional blocks aligning with known environmental zones — despite the algorithm receiving no geographic coordinates, only environmental variables. Major correspondences: cold permafrost clusters concentrate in Siberia, northern Canada, and high-altitude interiors; hyperarid clusters (km=2, precip=37mm/yr) cover Sahara, Arabian Peninsula, central Australia, and Atacama; tropical wet clusters (km=0, precip=2,049mm/yr) cover the equatorial belt; tropical wetland clusters (km=5) appear in Amazon and Congo floodplains; mountain-specific clusters appear along the Andes, Himalayas, Rockies, and Ethiopian Highlands. Similar-colored basins appear on different continents when their environmental signatures match.

**Implication**: Geographic coherence without geographic input is a validation of the signature variables — they carry sufficient environmental information to reconstruct approximate biome geography. This is necessary but not sufficient validation: a bad variable set could produce geographically coherent but environmentally meaningless clusters. The coherence confirms the variables are measuring real structure, but the cluster boundaries are imposed cuts on a continuous surface (see F5.2) and should not be treated as natural types except at the extremes.

---

### F5.2 — HDBSCAN finds one natural cluster: Greenland; global basin distribution is continuous

**Finding**: HDBSCAN (min_cluster_size=1000) produced 2 clusters and 37.7% noise (71,810 unclustered basins). Cluster 1 (4,856 basins) isolates Greenland and similar glaciated/periglacial Arctic environments. Cluster 0 (114,009 basins) is a single massive catch-all encompassing most of the world's landmass. The remaining 37.7% of basins are structurally ambiguous in HDBSCAN's density framework. Reducing min_cluster_size to 500 or adjusting min_samples would increase cluster count but at the cost of more noise — the fundamental result is robust: the global basin population does not contain sharply bounded natural types.

**Implication**: With one exception (glaciated Arctic environments), global basin character is a continuum. There are no sharp density peaks in environmental feature space corresponding to distinct basin types — the variation grades from one environment to another without gaps. This has two implications: (1) k-means clusters are working typology, not natural kinds — the cuts are analytically useful but arbitrary; (2) HDBSCAN is not the appropriate method for global basin typology at this dimensionality. The dimensionality issue is secondary: even with PCA reduction, the underlying continuity of the global basin distribution would likely produce a similar result. The commit is k-means for downstream use; HDBSCAN findings should be reported in any methods paper as evidence for the continuity claim.

---

### F5.3 — Three karst clusters span the temperature gradient; karst is a cross-cutting typological axis

**Finding**: Three of the 20 k-means clusters are karst-dominated, distributed across the full temperature range: km=4 (cold, −8°C, karst=76%, permafrost=69% — cold karst highlands, likely Tibet/Qinghai margins); km=18 (warm, 15°C, karst=66%, humid, precip=1,073mm — warm humid karst, likely southern China/Southeast Asia); km=7 (hot, 22°C, karst=81%, arid — hot dry karst, Middle East/North Africa). The global mean karst coverage is ~10%; these clusters run 7–8× above that.

**Implication**: Karst geology creates a distinctive environmental signature that overrides climate in the clustering — even though karst% is one variable among 20, it pulls basins into separate clusters when it is extreme enough. This confirms F1.7 (karst as a flag variable rather than continuous) and suggests that for future typology work, karst presence should be treated as a stratifying variable, not just another input dimension. The three karst clusters also represent three genuinely different environmental conditions despite sharing the same geology — karst is a substrate that interacts differently with cold/wet/dry regimes, and any rubric that treats karst as a single type would miss this.

---

### F5.4 — Special clusters: large rivers, regulated rivers, and flat tropical lowlands

**Finding**: Three clusters are defined by extreme single-variable values rather than a coherent environmental syndrome. **km=17** (n=5,416): mean annual discharge 5,693 m³/s (11× global mean), reservoir volume 33,432 km³ — the large river systems cluster dominated by Amazon, Congo, Ganges, and Mississippi basin sub-basins. **km=8** (n=8,524): discharge 581 m³/s, reservoir volume 6,592 km³ — heavily regulated rivers with major dam infrastructure. **km=14** (n=7,276): slope 1.21° (flattest cluster), elevation range 34m — tropical lowland deltas and coastal plains, structurally flat.

**Implication**: The large-river and regulated-river clusters are partially artifacts of the basin-count representation: large river systems are split into many L8 sub-basins, each carrying the upstream discharge signal, which concentrates them in a cluster that is really a "position in large drainage network" type rather than a local environmental type. For any correspondence testing that uses cluster membership to situate historical sites, these three clusters require special interpretive care — a site in km=17 is being classified by the regional river system it sits within, not its local environment. This is not wrong, but it should be stated.

---

### F5.5 — Comparison with existing workbench clustering: ARI=0.179, variable-set difference is the driver

**Finding**: Adjusted Rand Index between the new k-means (20 variables, Bands A+B+C) and the existing workbench `cluster_id` (bands A–D, includes human variables) = 0.179. This is substantially above chance (0.0) but far from perfect agreement (1.0). The contingency heatmap shows: a small number of extreme-environment old clusters map cleanly to specific new clusters (dark blue cells — the permafrost and hyperarid cases are stable); most mid-range old clusters spread diffusely across multiple new clusters.

**Implication**: The two clusterings agree on the environmental extremes (where the signal is strong enough to dominate regardless of variable set) but diverge significantly in the middle of the distribution, where Band D human variables were reshaping cluster boundaries in the old result. This answers the question raised in the exploration plan: the difference between the two clusterings is primarily driven by variable set, not by random initialization or different underlying structure. Including human variables (Band D) in the old clustering pulled mid-range basins into groupings reflecting agricultural and settlement patterns rather than purely physical environment. For the use scenarios driving this project — situating historical settlements within their physical environmental context, and testing correspondence between environmental signatures and cultural patterns — Band D inclusion is structurally inappropriate: it makes human presence a feature of the "environmental type," which then gets used to interpret where humans are. That is circular. Band D variables are outcomes to be explained by environmental context, not inputs to it. The A+B+C-only clustering is the correct instrument for correspondence testing; Band D belongs in the analysis only as a dependent variable or secondary descriptor, not as a typology input.

---

### F5.6 — Method resolution: commit to k-means; normalization decision documented

**Finding**: k-means (k=20) is the working typology for all downstream exploration and correspondence work. HDBSCAN is rejected for global basin typology at this resolution on the grounds that: (1) the global basin distribution is fundamentally continuous (F5.2), making density-based cluster detection largely futile; (2) 37.7% noise is not analytically useful for a typology that needs to situate every site; (3) the two clusters HDBSCAN found (Greenland + rest-of-world) provide no discrimination within the historically relevant portion of the basin distribution. Normalization: log1p applied to all non-negative right-skewed variables (terrain, hydrology, aridity, precipitation, sparse indicators); StandardScaler applied throughout; temperature (can be negative) receives StandardScaler only. Median imputation for the ~9% null rate in soil texture variables and ~4% in slope/gradient. k=20 retained to enable comparison with existing workbench result; this choice is arbitrary and should be revisited before any formal typology is published.

---

## 2026-04-19 · Task 6 · Geographic coverage and sampling-bias characterization

**Method**: `notebooks/edop/explore/06_coverage_sampling_bias.ipynb` · D-PLACE (6,408 societies with coordinates) and WH Cities (258) assigned to k-means clusters via PostGIS nearest-basin lookup (`basin08.geog` column + GIST index). Distribution comparison and log₂ representation ratios computed against global basin baseline (190,675 L8 basins). Outputs: `06_coverage_distribution.csv`, `06_dplace_cluster_assignments.csv`, `06_representation_ratios.png`, `06_coverage_map.png`.

---

### F6.1 — D-PLACE over-samples tropical wet mountains (3.65×); all cold and arid types severely under-sampled

**Finding**: D-PLACE has a single strongly over-represented cluster — "Tropical wet mountains" (5.9% of global basins, 21.6% of D-PLACE societies; ratio 3.65×). Ten clusters are under-represented at ratio < 0.5, including Arctic highland (0.01×), hyperarid desert (0.11×), cold boreal (0.16×), cold karst highland (0.23×). Cool temperate lowlands (7% of global basins, the second-largest cluster) is at 0.40×.

**Implication**: D-PLACE ethnographic coverage reflects fieldwork access patterns and population density, not environmental prevalence. Mesoamerican, Andean, and SE Asian societies dominate. Cold and hyperarid environments are structurally absent from correspondence testing using D-PLACE alone.

---

### F6.2 — WH Cities is dominated by regulated river corridors (5.55×); a civilization-geography bias

**Finding**: WH Cities has three over-represented clusters: "Regulated rivers" (4.47% global → 24.81% WHC; ratio 5.55×), "Warm humid karst" (3.27×), and "Tropical wet mountains" (2.68×). Six cluster types have zero WHC representation: warm semi-arid, cold boreal, subarctic wetlands, northern peatlands, cold karst highland, Arctic highland. "Tropical humid" — the single largest global cluster at 9.49% of all basins — has only 1.16% of WH Cities (ratio 0.12×).

**Implication**: WH Cities is a *river-corridor civilization* artifact: the Nile, Tigris-Euphrates, Indus, Yellow River, Rhine and analogous regulated systems account for a disproportionate share. Sub-Saharan Africa and Amazonia are essentially absent — a known critique of UNESCO designation patterns quantified here. "Regulated rivers" and "Warm humid karst" are the clusters with greatest WHC statistical power for correspondence testing.

---

### F6.3 — D-PLACE and WH Cities have divergent biases; they sample different parts of the environmental space

**Finding**: The two scholarship datasets concentrate in different clusters. D-PLACE over-samples tropical mountains (ethnographic reach); WHC over-samples river corridors and karst (monumental urbanism). Cool temperate lowlands are under-sampled by D-PLACE (0.40×) but near-proportional in WHC (1.60×), reflecting European academic bias in UNESCO nominations but relative absence from the fieldwork tradition. Neither dataset covers cold or hyperarid environments.

**Implication**: For correspondence testing, the two datasets are complementary rather than redundant. Combining them broadens coverage but does not resolve the shared cold/arid blind spot. Any rubric developed from a dataset skewed toward one cluster type should be validated against the other before generalization.

---

### F6.4 — Coverage map confirms D-PLACE has impressive global reach but Argentina/Pampas is a notable blank

**Finding**: The global coverage map (`06_coverage_map.png`) shows D-PLACE societies spread across six continents with dense coverage in sub-Saharan Africa, SE Asia, North America, and Amazonia. A striking blank appears across Argentina (Pampas, Patagonia) and parts of the southern cone. Northwest North America is well covered.

**Implication**: The Argentine gap reflects colonial erasure before the ethnographic moment — the Conquest of the Desert (1870s–80s) decimated Tehuelche, Mapuche, and Querandí populations before systematic fieldwork was possible. The Ethnographic Atlas and HRAF had no data to draw from. This contrasts with the Northwest US, where rugged geography (Coast Range, dense rainforest, fjords) slowed colonial advance sufficiently for Boas-era documentation (1880s–1900s) to occur. D-PLACE blank spots have heterogeneous causes: sampling reach, population sparsity, and colonial destruction of source populations are distinct mechanisms that should not be conflated in interpreting under-representation.

---

### F6.5 — Clusters with correspondence-testing power vs. clusters with no statistical basis

**Finding**: Clusters where both D-PLACE and WHC ratios are near zero (Arctic highland, cold boreal, subarctic wetlands, northern peatlands, cold karst highland) represent environments where no statistical correspondence testing is feasible with current datasets. These account for ~20% of global basin area. Clusters with strong signal in both datasets: tropical wet mountains, regulated rivers, warm humid karst. Clusters with signal in one only: hot wet tropics and tropical humid (D-PLACE only); cool temperate lowlands (WHC slightly).

**Implication**: Power analysis should precede any correspondence test design. Do not report null results for cold/arid environments as evidence against environmental correspondence — absence of data is the explanation.
