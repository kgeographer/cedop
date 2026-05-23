# CHAR Appendix: Characterization of the EDOPS Signature

*Drafted 2026-05-23 by Claude Code (Sonnet 4.6), following EDA Tasks 1–11 and ESDA work on branch `esda`. Sources: `logs/exploration_log.md` (F-numbered findings), `logs/esda_findings.md` (spatial findings), and the augmented codebook `metadata/edops_codebook_v03_draft.tsv`. Karl will edit for voice and finality.*

---

## 1. Purpose and Scope

This document closes the Characterization phase (CHAR) of EDOPS. CHAR is the umbrella term for all work that describes the EDOPS signature dataset before any correspondence testing, polity-phase analysis, or rubric design. It encompasses two coordinated work strands:

**EDA** (Exploratory Data Analysis) — eleven numbered tasks covering marginal distributions, missing-data patterns, local/upstream divergence, inter-variable correlation, geographic pre-clustering, and sampling-bias characterization for all static bands (A–E) and Band T temporal variables. Findings referenced as F1.x through F11.x in `exploration_log.md`.

**ESDA** (Exploratory Spatial Data Analysis) — systematic spatial-statistics work covering univariate spatial autocorrelation for 40+ Band A–D variables at both levels (L6 and L8), bivariate Moran's I and LISA for selected variable pairs, categorical join-count coherence for three categorical variables, and Band T spatial characterization at native grid resolution. Findings referenced as ARI, DIS, SW, BV, CAT, DSK, BVR, and BT4 entries in `esda_findings.md`.

CHAR also included five synthesis steps that produced this document and the augmented codebook:

1. Categorical spatial-coherence analysis (`notebooks/edop/spatial/13_categorical_coherence.ipynb`)
2. `dist_sink_km` univariate ESDA (`notebooks/edop/spatial/14_dist_sink_esda.ipynb`)
3. Within-band bivariate redundancy (`notebooks/edop/spatial/15_bivariate_redundancy.ipynb`)
4. Band T native-resolution characterization (`notebooks/edop/spatial/16a–16c_band_t_native*.ipynb`)
5. Per-variable position attribute specification and codebook augmentation (`notebooks/edop/explore/16_position_attribute_spec.ipynb`)

The term "phase" has been applied to many of these steps throughout the working logs. For clarity going forward: CHAR is a phase; EDA and ESDA are strands within it; individual notebooks and scripts are tasks or studies. The word "phase" should not apply below the strand level.

---

## 2. Band A — Terrain and Geology

**Distribution.** Band A variables — elevation (mean, min, max), slope, erosion rate, stream gradient, karst percentage, glacier percentage — are among the most analytically tractable in the signature. Elevation is right-skewed but not heavily so (mean 672 m, median 506 m); slope has mean 41.7°, median 20°. Karst, glacier, and permafrost are globally sparse: 82% of basins have zero karst coverage, 77% zero permafrost. These three function as flags rather than continuous gradients — meaningful when non-zero, absent for the large majority of basins.

**Spatial structure.** All Band A variables show positive spatial autocorrelation (I_L6 range 0.663–0.924) and all increase with finer resolution (scale direction ↑). Elevation is the most coherent terrain variable (I_L6 = 0.924, I_L8 = 0.970); slope is substantially lower (I_L6 = 0.805). The largest absolute scale gain in the entire 40-variable sweep belongs to erosion rate (Δ+0.181, from 0.741 at L6 to 0.922 at L8): steep and flat basins are internally ambiguous at L6 but cleanly resolved at L8.

Karst and glacier follow the same sharpening pattern (+0.16 each). Both phenomena are geologically or climatically bounded: at L6 they are smeared across basin boundaries; at L8 each sub-basin is more clearly inside or outside the geological or cryospheric zone. This behavior is consistent across all variables that mark physical boundaries rather than gradients.

**Redundancy.** Elevation and slope are globally correlated (r = 0.877 for slope_avg × stream_gradient at F4.9 level, similar for ele×slp) but carry independent information at the regional scale. The bivariate ESDA established this conclusively: ele×slp global I_BV = +0.423, falling in the "genuinely distinct" tier (BV.11). The dominant HL class (high elevation, low slope neighborhood) identifies not the Tibetan Plateau as predicted, but the African Plateau — a flat continental basement sitting at 500–2000 m elevation, distinguished from mountain ranges only by the combination of both variables. A signature containing elevation alone would conflate the Tibetan Plateau with the Alps; slope alone would conflate the African Plateau with the Gangetic plain.

The Mediterranean presents a cautionary case: ele×slp is not significant there (I_BV = 0.062, p = 0.114). The realm is a heterogeneous patchwork where the continental-plateau signal that drives global coupling is absent. The Tibetan case offers a second: within the plateau, elevation and slope are anti-correlated (sign-reversed, I_BV = −0.141) because the plateau interior is flat at high altitude. Regional behavior is not derivable from global structure.

**Position attribute.** All implemented Band A variables: `percentile`, with exceptions for the sparse indicators (karst, glacier, permafrost) which nonetheless receive percentile position on non-null basins. Historical validity: `full-record` — terrain and geology are stable on human timescales. Karst, glacier, and permafrost receive the same assignment because their distributions have not substantively shifted since the Holocene. Typology: Band A variables fall predominantly in the `continental-gradient` cluster, with erosion rate and some elevation extremes assigned to `mixed`.

---

## 3. Band B — Hydrology and Soil

**Distribution.** Band B is the most internally heterogeneous band. It contains smooth large-scale fields (soil water content, silt, clay — I_L6 > 0.86), network-topology variables (discharge, degree of regulation, river area — I_L6 0.475–0.614), and intermediate wetland and groundwater fields. Discharge is extreme right-skew (skewness 34–45); the Amazon outlet alone pulls the global mean to 264.7 m³/s against a median of 5.7 m³/s. Soil texture (clay, silt, sand) is among the most normally distributed scalars in the dataset.

**Spatial structure.** Band B spans the widest I range of any band at L6 (0.475 for degree of regulation to 0.970 for soil water content). This spread reflects a genuine structural difference between two classes of Band B variable:

*Network-topology variables* (discharge, discharge min, discharge max, degree of regulation) have I values in the 0.475–0.614 range and some show scale direction ↓ (I decreases with finer resolution). The mechanism is the watershed divide: at L8, many small adjacent basins sit on opposite sides of a divide with sharply different discharge, pulling I down. Monthly minimum discharge shows the sharpest scale decrease (−0.041), because baseflow is even more divide-sensitive than annual mean. The discharge LISA class structure is also different from climate: HH ≈ LL (near parity vs aridity's strong LL dominance), and the LH class (low-discharge basin surrounded by high-discharge neighbors — isolated headwaters adjacent to large mainstems) appears at meaningful proportions and grows faster than basin count when moving to L8 (22.5× vs 11.6× basin count increase). The watershed-divide effect is the spatial signature of network topology.

*Gradient-structure variables* (soil texture, runoff, soil organic carbon, groundwater depth) behave like climate variables: I_L6 > 0.82, scale direction ↑. These variables are spatially organized by large-scale substrate and climate belts that span watershed divides without disruption.

**Redundancy.** The discharge cluster is the most internally redundant grouping in the dataset: discharge_yr × discharge_max r = 0.967; discharge_max × river_area_upstream r = 0.937. These four variables — annual discharge, monthly min, monthly max, and upstream river area — are four measures of one latent quantity (basin hydrological size). For dimensionality reduction, one is sufficient. But Phase 3 CHAR established that they are *not* spatially interchangeable: bivariate I_BV for discharge pairs (0.455–0.538) falls below the univariate Moran's I (~0.563), meaning the seasonal-regime geography that min and max capture relative to annual mean is an independent spatial signal. In particular, all three discharge pairs show LH >> HL: cold-climate and snowmelt-transition zones produce basins with low annual flow surrounded by neighbors with high peak flow, or monsoon-fed flash systems adjacent to perennial mainstems. These divergence zones are geographically real and interpretively meaningful. The four variables document the same hydrological scale, but different aspects of its seasonal structure.

**Position attribute.** Discharge variables: `log_percentile` (skewness > 5, log1p transform applied). River area, reservoir volume: `log_percentile`. Soil texture, runoff, groundwater: `percentile`. Historical validity: soil texture and groundwater `full-record`; runoff, wetland, inundation, snow cover `pre-1500 valid` (hydrological patterns stable on centennial timescales but not geological); discharge and regulation `modern-only` (dam infrastructure is contemporary).

---

## 4. Band C — Climate

**Distribution.** Band C is the most internally coherent band in the signature. Mean annual temperature is bimodal — a cold cluster (−5°C to 5°C; high-latitude and high-altitude basins) and a warm cluster (20°C to 25°C; tropical and subtropical). The trough near 10°C reflects the relative scarcity of temperate basins globally by count. Aridity index (P/PET × 100) has a global median of 68 — semi-arid — with a right tail extending to 2,100+ in the wet tropics. Higher values mean wetter. Permafrost is 77% zero at L8; snow cover 57% zero.

**Spatial structure.** Band C achieves the highest spatial autocorrelation in the dataset at L8. PET, temperature, snow cover, aridity, and AET all reach I ≥ 0.992 — effectively maximum spatial autocorrelation. At this level, the spatial pattern is fully captured at L6 already; finer resolution adds no new geographic information. Band C is the anchor of the high end of the EDOPS spatial-coherence spectrum. All Band C variables show scale direction ↑.

The key spatial finding for climate is not its coherence at scale but its regional variation in inter-variable structure. The temperature × precipitation bivariate analysis (BV.1–6) established that the global positive I_BV (+0.315: warm basins in wet neighborhoods) reverses sign in the Mediterranean (−0.250), where the summer-drought mechanism makes warm basins sit in dry neighborhoods. A global scalar would misclassify both patterns. This finding validated the methodological principle running through all subsequent ESDA: global I_BV is not sufficient as a redundancy filter, and sign reversal at the regional scale can coexist with strong global positive coupling.

**Redundancy.** The temperature cluster (temp_yr, temp_min, temp_max, temp_yr_upstream) has the tightest internal structure in the dataset: all six pairwise correlations exceed r = 0.77, four exceed r = 0.88. Phase 3 CHAR confirmed spatial interchangeability: T_yr × T_min bivariate I_BV = 0.969, T_min × T_yr_upstream = 0.965, both producing nearly identical LISA maps. All three are different names for the same spatial pattern. For the signature, this redundancy is documented but not resolved by removal: each variable carries interpretive weight for different research contexts, and removal would require user-facing decisions about which temperature metric a query returns.

The s/u pairs for climate (aridity, precipitation, temperature local vs upstream) are the most correlated in the entire dataset (r = 0.984–0.989). Phase 3 CHAR bivariate ESDA confirmed: s/u divergence is globally rare, under 0.4% of basins for temperature and precipitation. Climate s/u pairs are near-concordant everywhere because catchment-scale averaging produces upstream values that closely track local conditions for smooth spatial fields. The local/upstream duality for climate is almost entirely a tail phenomenon — meaningful at p95+ and at the reference sites (Timbuktu, Ur, Kaifeng), negligible for the median basin.

**Categoricals.** Band C categorical variables (biome, ecoregion, freshwater ecoregion, PNV majority) are excluded from join-count coherence analysis by design. These variables *are* the spatial structure they encode — testing whether biome boundaries respect biome boundaries is circular. The three tested variables (lith_class, pnv_majority, wetland_class) are independent empirical classifications. All 43 class-variable combinations are globally significant at p = 0.001 and all produce local coherence above 90%, confirming that lithological, vegetation, and wetland classifications are appropriate spatial descriptors at the L8 basin level.

**Position attribute.** Scalar climate variables: `percentile` for most (skewness typically 0.5–3.0); `log_percentile` for aridity_index and aridity_upstream (skewness > 5). Categorical climate and vegetation variables: `rarity_rank` — the percentage of globally non-null L8 basins sharing the same class. PNV shares compositional: `dominance_class` — the maximum share across all PNV classes, with documented thresholds at 60% (genuine mixture below) and 95% (monoculture above). Historical validity: climate scalars and PNV/ecoregion categoricals `pre-1500 valid` (patterns stable on centennial scales but contemporary climatology is the source); land cover and forest cover `modern-only`.

---

## 5. Band D — Human Geography

**Distribution.** Band D contains two structurally distinct sub-clusters. The intensity cluster (population density, human footprint, cropland extent, upstream versions) measures anthropogenic landscape modification. The development cluster (GDP, HDI) measures economic modernity. These two clusters are weakly to negatively correlated with each other: high-GDP areas are not the same as densely populated or heavily farmed areas (r = −0.307 to −0.452 across cluster-crossing pairs). Wealthy, sparsely settled economies (Northern Europe, North America) drive the negative cross-cluster correlation.

**Spatial structure.** Band D achieves surprisingly high spatial autocorrelation: HDI I_L6 = 0.987, I_L8 = 0.995; GDP I_L6 = 0.943, I_L8 = 0.986. These values are comparable to the Band C climate ceiling. Wealth and development cluster at continental scale as coherently as temperature and precipitation. The spatial co-clustering of Band D and Band C variables is an empirical fact — its explanation belongs to the polity phase, not CHAR.

The HDI × GDP bivariate analysis (BV.10) shows I_BV = 0.581 despite both variables having individually very high univariate I. The moderate bivariate coupling reflects real geographic divergence: Russia is HH (Soviet human capital investment relative to current market GDP); former Soviet Central Asian states are HL (education legacy, lower income); Sub-Saharan Africa is the dominant LL zone. These findings are ESDA observations, not explanations — the historical-institutional context required to explain them belongs in CDOP.

Phase 3 CHAR asymmetry finding (BVR.6): HDI × GDP shows HL = 8,566 basins (4.5%), LH = 7 basins (0.004%). High-HDI enclaves in low-GDP neighborhoods exist at significant geographic scale; the reverse is essentially absent. Wherever GDP is high, HDI follows; the inverse holds only at vanishingly small scale.

**Position attribute.** All Band D scalars: `percentile` (population density: `log_percentile`, skewness > 5). Historical validity: `modern-only` for all Band D variables. The human geography signature reflects the contemporary world — it describes where a historical site now sits, not where it was when occupied. For historical polity analysis, Band D should be treated as opt-in context, not primary environmental characterization. This is the EDOP/CDOP boundary: Band D spatial clustering is measurable by ESDA, but the explanation requires historical-cultural context that CDOP is designed to provide.

---

## 6. Band E — Coastality

**Distribution.** `dist_sink_km` (flow distance to marine outlet) has no correlation above |r| = 0.41 with any other variable in the dataset (F4.8). This structural independence is the defining property of Band E: coastality is a genuinely orthogonal dimension that the combination of terrain, hydrology, climate, and human variables does not capture. A basin 5,000 km from the ocean is not systematically different in temperature, rainfall, or human footprint from a coastal basin — network position is a separate axis.

**Spatial structure.** Despite its structural independence from other variables, dist_sink_km is itself highly autocorrelated: I_L6 = 0.904, I_L8 = 0.963, scale direction ↑. Coastal margins cluster with coastal margins; continental interiors cluster with continental interiors. The LISA structure reflects this: LL (coastal, all margins globally) = 35–37%, HH (deep-continental interiors) = 19–20%, HL (interior surrounded by coastal) = 0.01–0.00% essentially absent. The near-zero HL fraction is a diagnostic: dist_sink has no spatial anomalies in the interior direction — the coast-to-interior gradient is monotonic. A continental-interior basin cannot be surrounded by coastal basins, so the HL class is physically impossible in any systematic sense.

dist_sink_km is the most scale-stable variable in the entire sweep: Δ = +0.059 (compared to aridity's +0.026 and discharge's −0.019), and the LISA maps are geographically indistinguishable at L6 and L8. This is expected: coastality is a geometric coordinate derived from the drainage network topology, not an environmental process that responds to basin scale.

**Position attribute.** `percentile` (raw transform; skewness 1.4–1.5, below log-transform threshold). Historical validity: `full-record` — flow distance to marine outlet has not changed on human timescales. Typology: `continental-gradient`. Outlier fraction 0.44% — the lowest in the dataset, consistent with its monotonic spatial gradient.

---

## 7. Band T — Temporal

**Overview.** Band T is the only band that varies by query time rather than by query location alone. It draws on three independent sources: LMR v2.1 (paleoclimate reanalysis, 0–1998 CE, 2° grid), HYDE 3.4 (land-use reconstruction, 8000 BCE–2025 CE, 5-arcmin grid), and eVolv2k v4 (volcanic sulfate catalog, ~500 BCE–1890 CE). These sources differ in resolution, temporal coverage, and epistemological character, and must not be conflated.

**LMR structure.** LMR stores anomaly fields (departures from a model climatology prior), not absolute climate values. Temporal variance dominates geographic variance for all three LMR variables: PDSI 76%, air temperature 68%, precipitation rate 93%. This means knowing *when* a query is placed matters more than knowing *where* for characterizing LMR values. Band C provides absolute climatology; LMR provides departure from the long-run norm. The two are statistically orthogonal (r ≈ 0 at 34 sample locations) and non-redundant.

LMR exhibits a reliability gradient: pre-500 CE reconstruction amplitude is systematically suppressed by regression to the model prior when proxy networks are sparse. The reliable window is approximately 700–1900 CE. A fidelity note fires in the API response for queries with year_start < 700.

The spatial precision of LMR is approximately one 2°×2° cell (~200 km at mid-latitudes). At L8, approximately 39 sub-basins share the same LMR cell value on average. LMR cannot distinguish neighboring sub-basins climatically — it provides regional-period climate context, not local climate character.

**HYDE structure.** HYDE reconstructs land use (cropland, grazing, pasture, rangeland, urban area, population, total rice) at 5-arcmin resolution from 8000 BCE to 2025 CE. Two findings define its analytical character:

First, cropland and grazing have dramatically different spatial structures at early epochs. At 4000 BCE, grazing Moran's I = 0.91 while cropland I = 0.59 — pastoral land use follows ecological (biome) structure from the very beginning of the HYDE record. Cropland required approximately 6,000 years of intensification to achieve the spatial coherence that grazing had from early antiquity. By 2000 CE both converge near 0.92–0.93. This trajectory is the headline Band T ESDA finding: the spatial consolidation of agriculture is itself a historical pattern at continental scale.

Second, over 48% of land cells show zero cropland presence across all seven non-degenerate HYDE epochs. Nearly 30% of cells show no grazing. The non-farmed land surface is not missing data; it is genuine absence in HYDE's reconstruction. The Old World / New World contrast in agricultural persistence is the sharpest cartographic signal in the Phase 4c output: the classic Neolithic agricultural cores (Fertile Crescent, Nile, Ganges-Indus, Yellow River) show 7/7 presence; the Americas show almost entirely post-1500 CE first presence for grazing, reflecting the Columbian Exchange.

The MCA–LIA comparison at native LMR grid produced a key negative result: temperature anomaly fields for the two periods are not a dipole (r = +0.116, slope = 0.26). The PDSI fields are a partial dipole (r = −0.382). Moisture geography reorganized more coherently between climate periods than thermal geography did. For EDOPS users, this means location-specific LMR moisture anomalies carry more interpretable period-to-period information than temperature anomalies at 2° resolution.

**eVolv2k.** The catalog (256 events, VSSI ≥ 1 Tg) is 84% unnamed — ice-core-detected sulfate anomalies with no attributed source volcano. The 5 Tg default threshold captures 55 events including Krakatoa and Kuwae; 10 Tg is too high a floor. eVolv2k and LMR are independent: LMR cannot reliably quantify volcanic forcing below approximately 50 Tg, while eVolv2k carries the event record irrespective of climate reconstruction fidelity. The API returns both as complementary rather than confirmatory layers.

**Position attribute.** Band T variables: `deferred-phase4`. Position attributes for temporal variables depend on the query window, not the variable alone; they require design decisions about reference baselines and temporal percentile methods that belong to the LMR/HYDE design follow-up, not to this CHAR round.

---

## 8. Cross-Cutting Findings

### The s/u duality is a tail phenomenon, not a default feature

For every local/upstream variable pair, the global median divergence is exactly zero. The interquartile range is at or near zero for most pairs. Strong divergence is concentrated above the 95th percentile, frequently above the 99th. By basin count, most L8 sub-basins are headwaters or near-headwaters whose upstream footprint approximately equals their local footprint. The s/u duality fires in specific basin positions — where a river crosses a major environmental boundary — and is silent everywhere else.

When it fires, the divergence profile is multidimensional and site-specific. Timbuktu's signal is hydrological (upstream precipitation p99.9, aridity p99.8) with minimal temperature divergence. Ur's signal combines moisture, thermal, and social-directional reversal (upstream agricultural core). Kaifeng's dominant signal is topographic (slope p99.9, upstream 91× steeper), with an inverted moisture gradient. These three sites are not instances of the same environmental type — they illustrate three distinct divergence regimes produced by different river-system configurations.

For Phase 3 CHAR bivariate analysis: climate s/u pairs have I_BV > 0.96 and divergence rates under 0.4%. Human-land-use pairs (human footprint, cropland) show the most divergence, around 0.6%, because anthropogenic land use does not respect catchment flow direction as cleanly as physical climate gradients.

### Scale sensitivity is variable-type diagnostic

A consistent typology of scale behavior emerged from the 40-variable sweep. Continental-gradient variables (most of Band C, Band A elevation, Band B soils, Band E coastality) increase I with finer resolution — smaller basins sit more firmly inside individual climate or substrate zones. Network-topology variables (Band B discharge, degree of regulation) decrease or hold flat — finer resolution resolves more watershed-divide discontinuities. The minority of ↓ variables (four of forty: annual discharge, monthly minimum discharge, degree of regulation, silt at negligible magnitude) are the most informative cases: they signal that spatial structure in those variables is organized by drainage network geometry, not by smooth gradient fields.

MAUP effects are real but concentrated at geographic boundaries. The HH (humid cluster core) footprint in the US Pacific Northwest contracts at L8 because the Cascade rain shadow resolves as individual dry sub-basins that suppress the spatial lag of adjacent wet basins. Cluster-core percentages are resolution-stable for continent-scale features but not for features near topographic discontinuities. The practical implication: for historical site analysis, L8 gives local character; L6 gives regional typological position. Both are useful for different questions.

### Spatial redundancy and attribute-space redundancy are different things

The core methodological lesson of CHAR's ESDA strand is that high Spearman correlation between two variables does not imply spatial concordance. Temperature × precipitation has global I_BV = +0.315, sign-reversed in the Mediterranean (−0.250). Temperature × snow cover is near-redundant globally (I_BV = −0.865) but collapses to not-significant in the Tibetan/cold-arid zone, where all basins are cold and snow distribution is governed by precipitation independently. Precipitation × AET is near-redundant globally and holds in all sampled regions — the most geographically stable near-redundancy found.

The design decision reached at the end of CHAR: no EDOPS signature variables are removed based on global co-variation (F4.9, BVR.7). L8 basin signatures need local character even when globally redundant. In HL and LH divergence zones — often the ecologically and historically most interesting configurations — variables that covary globally carry distinct local information. The `high_r_partner` column in the augmented codebook records which variables share global Spearman |r| ≥ 0.90; it documents correlation structure and does not imply that any variable is expendable.

### Spatial structure is not environmental character

LISA class (HH/LL/HL/LH) identifies a basin's position in the global distribution of the variable in question, not its absolute environmental character. The Atacama (hyperarid) and the Pampas (productive temperate grassland) share LL class in the aridity×precipitation bivariate: both fall below the global humid-tropical mean on both metrics. A signature using only LISA class would conflate them. The raw variable values provide magnitude; the LISA class provides structural position. Both are needed for meaningful characterization, and the augmented codebook carries both through the `position_method` column and through the bivariate redundancy parquet.

---

## 9. What CHAR Does Not Establish

CHAR characterizes the EDOPS signature dataset. It does not validate it against external correspondence targets. Several planned work streams are deferred:

**Anthromes categorical typology.** Task 12 (anthromes classification) was deferred indefinitely. The k-means typology (k=20) from Task 5 remains the working environmental pre-clustering for downstream use.

**D-PLACE and WHC correspondence testing.** The Task 6 sampling-bias analysis established the statistical power landscape (D-PLACE over-samples tropical wet mountains 3.65×; WHC over-samples regulated river corridors 5.55×; both datasets share the cold/hyperarid blind spot). Formal correspondence tests against cultural variables — do similar environments produce similar subsistence strategies, social organization, or religious systems? — belong to the polity phase.

**Ecoregion correspondence.** Whether BasinATLAS basin-level environmental signatures correspond to OneEarth ecoregion boundaries has not been tested. The spatial coherence of ecoregion-related categoricals (biome, freshwater ecoregion) was established, but correspondence with the signature's scalar dimensions is not yet characterized.

**Band T position attributes.** The `deferred-phase4` assignment for Band T variables reflects genuine design deferral: computing percentile position within a temporal query requires decisions about reference windows and baseline conventions that remain open (see F11.2 for the established 1000–1850 CE baseline convention for LMR; HYDE baselines require analogous design work).

**LMR/HYDE formal ESDA.** The Phase 4 CHAR work characterized Band T at native grid resolution. Formal ESDA at the basin-aggregated level — bivariate LISA between Band T and Band C, temporal autocorrelation structure — remains unexecuted. The tractability analysis established that HYDE full LISA is intractable at 2.2M cells; a feasibility-limited Moran's I sweep was completed.

**Disclosure design.** Several open design questions identified during EDA (F8.5, F8.6, F9.6, F11.4, F11.6) are flagged for the October 2026 expert meeting: Band C silent error for BCE queries (patched with a qualifying note, but the underlying absence of paleoclimate data for the BCE period remains); population density in an environmental signature; EarthStat/HYDE spatial allocation divergence at agricultural hotspot sub-basins; Pinatubo calibration text for the narrative layer; LMR geographic proxy-network bias.

---

## 10. The Augmented Codebook

The per-variable reference for CHAR findings is `metadata/edops_codebook_v03_draft.tsv` (98 rows, 21 columns). It extends `edops_codebook_v02.tsv` with seven new columns documenting CHAR outputs:

- **`position_method`** — how a global-position attribute is computed for each variable (`percentile`, `log_percentile`, `rarity_rank`, `dominance_class`, `deferred-phase4`)
- **`position_notes`** — transform details, null treatment, and zero handling per variable
- **`high_r_partner`** — which other schema_key shares global Spearman |r| ≥ 0.90 (null if none). This column records global correlation structure and does not imply that any variable is expendable from the signature.
- **`typology_cluster`** — spatial autocorrelation typology from the univariate sweep (`continental-gradient`, `mixed`, `network-topology`, `local-anomaly`)
- **`scale_sensitivity_flag`** — whether the variable shows a notable I change between L6 and L8
- **`historical_validity`** — `full-record`, `pre-1500 valid`, `modern-only`, or `period-specific`
- **`informative_or_degenerate`** — distributional assessment from Task 1 EDA

The draft codebook should not be promoted to `v03` until Karl reviews and approves the column contents. The `_draft` suffix marks it as a working artifact, not a final release.

---

*CHAR is complete. The next phase is polity: area-weighted basin signatures for polygon queries (Cliopatria, Seshat), scale sensitivity for polity signatures (L6 vs L8), and tentative D-PLACE correspondence tests.*
