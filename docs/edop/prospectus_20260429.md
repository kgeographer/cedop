# EDOP: Environmental Dimensions of Place
*Prospectus — 29 April 2026*

*EDOP is a research program conceived and developed by Karl Grossner, now proposed to be supported and maintained by the Institute for Spatial History Innovation (ISHI), University of Pittsburgh (Ruth Mostern, Director) beginning May 2026.*

---

> **Revision note — 29 April 2026**
> This version revises the 16 April prospectus following completion of the Band T data exploration phase (Tasks 7–11: eVolv2k, HYDE, LMR structure and fingerprints) and the sigrefine01 implementation sprint. Principal changes: (1) HYDE 3.4 added as the third temporal enrichment dataset in Section 3; (2) the 1000–1850 CE baseline convention for Band T anomaly reporting established and documented; (3) LMR geographic proxy bias named as a first-class API limitation; (4) eVolv2k/LMR decoupling principle stated explicitly; (5) a new paragraph articulating the "qualifying notes as first-class payload content" design principle; (6) three additions to Section 7 (LMR spatial precision ceiling, HYDE/EarthStat divergence, population density status); (7) minor updates to Sections 8 and 10. The Band T implementation is now live: LMR v2.1, eVolv2k v4, and HYDE 3.4 are all operational in the `/api/signature` endpoint. Revised passages are flagged with `[Rev. 29 Apr]`.

> **Revision note — 16 April 2026**
> This version revises the 07 April prospectus following the loading of two concrete evaluation datasets into the project database: D-PLACE CLDF v3.3.0 (6,684 societies; 1,291 Ethnographic Atlas societies with full spatial linkage to basin08) and the Seshat Global History Databank (621 polities; 329 matched to Cliopatria polygon boundaries via `seshatid`). Section 6 is updated to name Seshat explicitly as the polygon-level evaluation dataset, add a fifth validation experiment (Seshat polity correspondence), and note the methodological implication of Seshat's predominantly binary variable structure. The D-PLACE experiment note is updated to reflect that the full-scale run is now materially feasible. Revised passages are flagged with `[Rev. 16 Apr]`.

> **Revision note — 07 April 2026**
> This version revises the 04 April prospectus in response to conceptual clarifications reached during the first public presentation of Computing Place (06 April 2026) and subsequent reflection. The principal changes concern: (1) the framing of EDOP as a *research instrument* rather than a predictive model; (2) the role and logic of validation — including a substantial rewrite of Section 6; (3) the relationship between settlement correspondence and signature quality; and (4) the approach to variable selection ("rich but bounded"). Revised passages are flagged with `[Rev. 07 Apr]`.

---

## 1. Overview

Environmental Dimensions of Place (EDOP) is a computational service for generating standardized, reproducible environmental "signatures" for geographic locations. The core objective is to operationalize environmental context in a form suitable for comparative analysis, linking and integration with cultural datasets, and exploratory modeling of relationships between environmental patterns and human phenomena.

EDOP is designed as infrastructure: a generalizable method for computing environmental descriptors of place at multiple spatial scales. A [working prototype](https://cedop.kgeographer.org/edop) has been implemented and is publicly accessible. This prospectus describes the full evolving design intent; the current prototype implements a working subset. Sections describing capabilities not yet implemented are marked with an asterisk [*].

EDOP is one module of the broader **Computing Place** research initiative, paired with a **CDOP** (Cultural Dimensions of Place) module. The two are related but distinct in scope: EDOP's use of cultural datasets (settlement records, ethnographic societies, historical polities) is instrumental — these serve as external probes for validating environmental signature quality, not as objects of cultural inquiry in themselves. CDOP addresses the cultural inquiry directly: investigating relationships between cultural practices and environmental settings. Development of the two modules proceeds in parallel at independent paces.

## 2. Conceptual Premise

EDOP takes as a formative premise that each inhabited area of the Earth lies within or is itself a cultural landscape, in much the same sense described by geographer Carl Sauer a century ago (1925). In this framing, physical geography and ecological characteristics (i.e. landscape) are the setting for human activity (i.e. culture) in a continually evolving bi-directional relationship. This close association is well-known to environmental historians, archaeologists, and many others studying the past in the humanities and social sciences. That said, environmental context is typically invoked qualitatively in cultural, historical, and archaeological research.

EDOP treats environmental context as a computable, multidimensional construct derived from globally consistent geospatial datasets. In this framework, place descriptions can include an EDOP "signature" (EDOPS) — a structured representation of environmental conditions extracted from standardized environmental variables. These dimensions include, for example:

- Hydrological indicators
- Climate variables (baseline and historical)
- Terrain metrics
- Ecoregional classification
- Coastal and marine conditions
- Volcanic forcing events

The resulting signature is not a classification label but a structured, self-describing document (serialized as JSON) suitable for downstream analysis, comparison, and natural language interpretation.

EDOP is positioned in explicit contrast to commercial geographic enrichment services (e.g. Esri's ArcGIS Enrichment Service), which augment point locations with attribute values from overlapping layers but do not consider conditions at a distance or the directional, process-mediated flows that connect a location to its surroundings. EDOP's goal is *process-aware environmental characterization* — what a place experiences, not merely what surrounds it. This distinction constitutes a methodological novelty relative to current commercial and open-source tools.

`[Rev. 07 Apr]` EDOP is not a predictive model in the tradition of Archaeological Predictive Modeling (APM) — it is not designed to classify locations as settled vs. unsettled, or to output a probability of settlement. It is better understood as a **research instrument**: a richly parameterized environmental characterization service that researchers bring their own questions to. A historian studying Song dynasty expansion asks which environmental dimensions are salient for that question, configures the instrument accordingly, and interprets the results in light of what they already know. The instrument does not tell them what to find — it gives them new environmental handles on phenomena they are studying by other means.

## 3. The Environmental Signature

### Variable Selection and Structure

`[Rev. 07 Apr]` Variable selection follows a "rich but bounded" strategy: include all variables with a plausible theoretical connection to human activity or habitability, as indicated by prior literature on archaeological settlement predictors, environmental correlates of cultural practices (D-PLACE), and geoarchaeological consensus. This produces a richer initial signature than strictly necessary — not a kitchen sink of all available data, but a principled superset from which researchers select relevant dimensions for their questions. Variables with no conceivable mechanism connecting them to human life are excluded. Variables whose utility is speculative but theoretically motivated are included and documented as such.

The practical basis for variable selection is the full HydroATLAS (BasinATLAS) variable set, cross-referenced against the archaeological settlement prediction literature (elevation, slope, distance to water, soil quality, flood exposure, vegetation) and against the environmental variables used in D-PLACE cross-cultural analyses (temperature, precipitation, aridity, net primary productivity, ecoregion). Variables identified in both sources have the strongest claim; variables identified in one and motivated theoretically by the other are strong candidates. The resulting set is documented in `metadata/basin08_columns.json` with group, local/upstream availability, and rationale notes.

EDOPS relies on globally available, spatially consistent environmental datasets. Primary sources include HydroATLAS (hydrological and climate variables at multiple basin levels), digital elevation models (terrain metrics), and the ecoregion frameworks developed by One Earth. The temporal enrichment layer draws on the Last Millennium Reanalysis v2.1 (Tardif et al. 2019) for continuous historical climate (1–2000 CE) and eVolv2k v4 (Sigl & Toohey 2024) for volcanic forcing annotation (500 BCE–1900 CE). Phase 2 coastal enrichment will add ICOADS marine climate data and seafloor topography for signatures where adjacent sea conditions are environmentally significant. Because such datasets contain hundreds of potentially collinear variables, the service applies:

- Statistical screening to reduce redundancy
- Dimensionality reduction (e.g. principal components analysis or related methods)
- Optional banding or stratification for interpretability

Variables are grouped in four temporally scoped "bands" that correspond to relative persistence and applicability to successive historical eras: *A — Physiographic bedrock*, *B — Hydroclimatic baselines*, *C — Bioclimatic proxies*, *D — Anthropocene markers*. This banding allows for a relatively coarse temporal scoping of queries: analyses of pre-industrial periods can suppress or qualify Group D variables, which reflect modern land cover and human pressure.

The goal is a compact, interpretable signature that preserves meaningful environmental gradients — where "meaningful" is operationally defined through validation against independent signals rather than assumed from the variable set alone.

### Process Orientation

What distinguishes EDOP signatures from static spatial lookups is a **process orientation**: the aim is to characterize not merely what surrounds a location, but what it *experiences* through directed spatial processes. Environmental conditions at a place are shaped by what flows to it from upstream, what it can access downstream toward the sea, and — through temporal enrichment — what climatic conditions prevailed during a given historical period. The following sections elaborate the principal spatial process dimensions implemented or planned in the service.

### Local and Upstream Duality

HydroATLAS provides, for most variable categories, both a local value (`s`: conditions within the sub-basin only) and an upstream catchment value (`u`: area-weighted accumulation across all upstream contributing basins). This local/upstream duality is a first-class architectural feature of EDOP signatures. The contrast between `s` and `u` for a given variable is itself environmentally meaningful: a settlement where local aridity (`s`) diverges sharply from upstream catchment aridity (`u`) occupies a qualitatively different environmental position than one where the two converge.

The Tigris-Euphrates basin illustrates this clearly: Ur's local environment is hyper-arid (~94mm/yr precipitation), but its upstream catchment receives substantially more, sustaining the riverine flow that made the site viable. That divergence is not a nuance of the data — it is the central environmental fact about alluvial civilizations.

Beyond the pre-computed `u` values, the HydroATLAS basin network encodes explicit upstream-downstream topology via `hybas_id` and `next_down` fields, forming a crawlable directed acyclic graph. This enables computation of *distance-stratified upstream profiles* not available in the standard dataset — near-upstream aggregates weighted to reflect proximity rather than contributing area. Distance-weighted upstream profiling is a designated research extension (see Section 7).

### Downstream Connectivity and Coastality

The upstream dimension captures what flows *to* a place. A complementary dimension captures what a place can *reach and send* — its connectivity to the sea via the downstream drainage network. This coastality dimension is not incidental: for many historically significant locations, marine access is the primary environmental affordance, not a secondary feature.

The conceptual core of coastality is what may be called **terrestrial-marine decoupling**: in coastal environments, marine affordance and terrestrial affordance are independent dimensions that can point in opposite directions. Settlement viability is a function of their combination, not either alone.

The Yaghan (Yamana) of Tierra del Fuego present this case in its sharpest form. Their territory — the Beagle Channel and the Cape Horn archipelago — has among the most forbidding terrestrial signatures in the inhabited world: extreme temperature variability, minimal agricultural potential, very low BasinATLAS viability scores. A purely terrestrial EDOP signature would predict very low settlement potential. The Yaghan occupied this territory for millennia, because the marine affordance is extraordinary: the Malvinas Current brings cold, nutrient-rich water through highly productive fjord systems, sustaining dense shellfish, pinnipeds, and fish concentrations. They were essentially aquatic in their subsistence. The terrestrial signature is not wrong — it correctly characterizes terrestrial conditions, but it is blind to the dimension that actually mattered.

Coastality operates through three distinct modes that should not be conflated:

- **Hydrologic connectivity**: position within the drainage graph relative to a marine outlet — captured by `dist_sink` (flow distance to terminal outlet) and outlet type (exorheic / endorheic / terminal lake). Endorheic basins have no marine connection by definition and must be handled explicitly throughout.
- **Ecological influence**: marine productivity accessible from the location — driven by continental shelf width, upwelling zones, and major current systems. These extend beyond BasinATLAS and require external datasets [*].
- **Human accessibility**: practical interaction with the sea — harbor morphology, navigable channel availability, coastal shelter. Highly context-dependent [*].

What is immediately implementable from existing data: flow distance to marine outlet (`dist_sink`), outlet type classification, and topological depth from coast (hop count via `next_down`). These constitute the first phase of coastality integration. For Phase 2, ICOADS (NCEI/NCAR) — a gridded monthly marine climate dataset at 2°×2° back to 1800 covering SST, air temperature, pressure, and wind — is the designated source for ecological marine influence at coastal locations. Seafloor topography, specifically the distinction between continental shelf settings (shallow, biologically productive, historically accessible) and deep-water adjacency, is a further Phase 2 candidate; placeholder fields in the signature schema anticipate both additions.

Together, the upstream and downstream dimensions frame a complete positional description within the hydrological graph: what a place receives from above, and what it can reach below.

### Temporal Scope and Historical Depth

Most global environmental datasets, including BasinATLAS, are contemporary and not ideally suited for analyses that are often historical. For EDOPS, this temporal mismatch is addressed in two ways beyond the persistence bands described above. First, the banding structure itself provides coarse temporal scoping: physiographic and hydroclimatic variables (Groups A and B) are largely stable over centuries to millennia and are defensible as historical baselines; Group D variables require exclusion or explicit qualification for pre-modern use. Second, and more directly, EDOPS will integrate historical climate data from two established datasets identified through the program's partnership with environmental historians at ISHI:

**Last Millennium Reanalysis v2.1** `[Rev. 29 Apr — implemented]` (Tardif et al. 2019) is now the operational primary temporal enrichment layer, live in the `/api/signature` endpoint (Band T). A spatially gridded (2°×2°), annually resolved paleoclimate reanalysis covering 0–1998 CE, drawn from a 20-member ensemble, it provides the continuous climate context that the signature most needs when a query is placed in historical time. Variables include Palmer Drought Severity Index (PDSI), surface air temperature, and precipitation rate. Systematic exploration of the dataset structure (Task 10) established its key properties: temporal variance dominates geographic variance for all three variables (PDSI 76% temporal, temperature 68%, precipitation 93%), confirming that Band C and Band T are genuinely non-redundant; within-run spread (~4.6× across-run std) is the appropriate uncertainty field; and the spatial precision ceiling is approximately 200 km — LMR is a regional climate signal, not a local one, a limitation that must be stated explicitly in outputs. The reconstruction is most reliable in the window 700–1900 CE; the compressed variance of early centuries (0–700 CE) reflects sparse proxy coverage rather than a climate signal, and is disclosed to API consumers as a fidelity note.

A critical geographic limitation `[Rev. 29 Apr]`: LMR proxy networks are systematically denser in Europe and North America than in East Asia, South Asia, or the Southern Hemisphere. The stronger European reconstruction signal reflects better-constrained estimation, not necessarily stronger physical forcing. For Song dynasty China, Mesopotamian, and African research use cases, LMR outputs carry meaningfully greater uncertainty than European queries at the same period. This geographic proxy bias is surfaced as a first-class qualifying note in every Band T payload response, not relegated to documentation.

Based on systematic exploration (Task 11), a **recommended baseline window of 1000–1850 CE** has been established for Band T anomaly reporting `[Rev. 29 Apr]`. This window avoids the sparse-proxy funnel effect (pre-700 CE), the Medieval–LIA transition ambiguity, and the 20th-century industrial warming signal. It is the reliable pre-industrial operating zone for LMR and is the stated convention in API documentation.

**eVolv2k v4** `[Rev. 29 Apr — implemented]` (Sigl & Toohey 2024) is now the operational volcanic forcing annotation layer, live alongside LMR in Band T. It provides 256 eruptions from ~500 BCE–1900 CE with stratospheric sulfur injection magnitudes (VSSI in Tg), eruption latitude, hemispheric asymmetry, and tephra confirmation. The threshold default is 5.0 Tg (confirmed by distributional analysis as the appropriate API default; 10 Tg would exclude historically significant events including Krakatoa and Kuwae). The Medieval Quiet Period (950–1100 CE) and the Samalas eruption of 1257 CE (59 Tg, the largest in the catalog) are both directly visible in Band T outputs and directly relevant to scholarship on Song-era expansion and collapse.

A design principle established through the Band T implementation `[Rev. 29 Apr]`: **eVolv2k and LMR are non-substitutable and are deliberately decoupled**. eVolv2k returns volcanic events for BCE queries even when LMR data is unavailable (LMR coverage begins at 0 CE). Conversely, LMR cannot recover volcanic cooling signatures below approximately 50 Tg VSSI at basin scale — a known limitation of ensemble reanalysis methods confirmed by Task 11 analysis. The Pinatubo eruption (~20 Tg → ~0.5°C observed cooling) serves as the appropriate calibration reference for the narrative interpretation layer, not as an LMR-detectable signal.

**HYDE 3.4** `[Rev. 29 Apr — implemented]` (Klein Goldewijk et al. 2017) is now the third temporal enrichment dataset, live in Band T as of April 2026. Unlike LMR and eVolv2k, which describe climate and volcanic forcing, HYDE 3.4 characterizes land-use history: cropland, total grazing land, managed pasture, and extensive rangeland as fractional basin area at each HYDE epoch. Coverage spans 10,000 BCE–2023 CE at approximately 10 km (5 arcmin) resolution. HYDE's temporal resolution is irregular — millennial in the deep BCE, centennial to 1700 CE, decadal to 1950, annual thereafter — and this structure is disclosed in every Band T response rather than smoothed by interpolation: the API returns all overlapping HYDE epochs within the query window, making the resolution structure visible to the consumer.

A key design feature distinguishes the HYDE implementation from a naive basin-average approach: within-basin cell heterogeneity is returned alongside basin totals. Standard deviation and p10/p90 percentiles of per-cell values are included when a basin contains more than one HYDE cell, enabling distinction between *patchy* land use (high spread, concentrated in a few cells) and *uniform* land use (low spread, evenly distributed). For example, Kaifeng (Northern Song, 216 cells, 15,347 km² basin) shows high cropland heterogeneity at 1000 CE (basin total ~4%, but p90 cell equivalent ~18%) collapsing to low heterogeneity at 1100 CE (~18% basin total, tight band) — a signal consistent with a century of agricultural intensification spreading from established farming cores across previously uncultivated basin cells.

Band T (HYDE temporal) and Band D (EarthStat static, ~2000 CE calibration) are explicitly non-redundant: they answer different questions at different temporal granularities and must not be treated as interchangeable. A known methodological challenge is spatial divergence between the two at agricultural hotspot sub-basins (e.g. 3× difference at Ur for 2000 CE), reflecting genuine spatial allocation uncertainty in modeled historical land use rather than a data error. This divergence is flagged for domain expert review at the October 2026 ISHI expert meeting.

### Qualifying Notes as First-Class Payload Content `[Rev. 29 Apr]`

A design principle articulated during the Band T implementation phase applies across all bands, not only Band T: **qualifying notes are first-class API payload content**. The service is responsible for disclosing the epistemic status of its outputs — temporal scope mismatches (Band C WorldClim data reflects contemporary climate, not historical; Band D EarthStat is calibrated ~2000 CE; HYDE resolution is era-dependent), geographic reconstruction biases (LMR proxy density), and data-source limitations (LMR spatial precision ceiling, eVolv2k detection threshold). These disclosures are returned as `_note` fields on the relevant bands or layers in the JSON payload; consuming applications surface them; the API owns the framing.

The design stance is: notes inform, they do not gatekeep. A user querying Band C for a BCE site receives both the contemporary baseline (useful as a reference) and an explicit disclosure that it reflects contemporary climate, not the conditions of the query period. The decision to use or discount that information belongs to the researcher, not the API. This principle must be stated explicitly in API documentation and in published examples: qualifying notes are a normal, expected part of the response, not error conditions or exceptional commentary.

## 4. Spatial Neighborhoods and Units of Analysis

### The Neighborhood Problem

For a given location, "the environment" is not self-defining. The spatial extent over which environmental variables are aggregated — the *neighborhood* — is a methodological choice with direct consequences for signature content. EDOP treats neighborhood type as a transparent, explicit parameter rather than a hidden default. The choice of neighborhood model is itself a research decision, and scale sensitivity (how much signatures change across neighborhood definitions) will be a designed output of the service.

### Point Locations

For point inputs (settlements, heritage sites, representative points for indigenous societies), several neighborhood models will be available:

- **Containing basin**: the HydroATLAS sub-basin at a specified Pfafstetter level that contains the point. Fast and globally consistent; sensitive to basin boundary placement (a classic MAUP problem). Level 10 (typically tens of km²) is likely the appropriate default for point inputs; Level 08 is more appropriate for regional aggregation.
- **Fixed-radius buffer**: area-weighted aggregation over all basins intersecting a defined radius. Isotropic (direction-invariant), stable, and comparable across sites regardless of basin network structure.
- **Upstream catchment**: recursive traversal of all basins draining through the point's containing basin, weighted by distance from the outlet. Process-aware and hydrologically grounded; size varies greatly with position in the network (a headwater point vs. a lowland river site). Distance-decay weighting (exponential decay over upstream depth) is preferred over flat area-weighting, which treats a headwater basin identically to an immediately upstream neighbor.
- **Three-tier composite**: local (`s` values), near-upstream (N-hop decay aggregate), and full-upstream (`u` values) — the intended mature output, providing a structured picture of the location's position within its hydrological context.

The HydroATLAS basin network — a directed acyclic graph over ~190,000 sub-basins linked by `next_down` fields — provides the topological foundation for the upstream and three-tier models. This graph also enables downstream traversal to the marine outlet, which underlies the coastality measures described in Section 3. Endorheic basins (n=31,021; closed basins with no marine outlet) must be excluded from any upstream traversal or coastality computation.

Edge cases requiring particular care: confluence cities (sitting at the junction of two drainage systems), coastal settlements (where the local basin is tiny but marine adjacency is the dominant feature), and polities spanning major basin divides. These are documented as instances where neighborhood definition has the most consequence.

### Area-Based Units

For polygon inputs (historical polities, administrative regions, designated study areas), the polygon boundary defines the neighborhood. The design question shifts to aggregation: rather than returning only an area-weighted mean vector, EDOP will return a *distribution* over intersecting basin signatures — including quantiles of each variable and, optionally, a clustering of intersecting basins into environmental sub-zones. A scalar summary will remain available but explicitly flagged as a lossy reduction. This preserves within-unit environmental variation (north/south gradients, highland/lowland contrasts) that is often of direct historical interest.

An analytically interesting variant is the temporal sequence of polygon inputs: the same polity at successive dates, as its territory expanded or contracted. Computing signature distributions at each time slice and differencing them reveals how the aggregate environmental profile of the territory changed — which can serve as physical evidence for, or against, environmentally motivated expansion. The Northern Song dynasty's southward territorial expansion between 962 and 980 CE provides a worked example: aridity index distributions shift markedly toward higher moisture availability as the territory expanded into wetter southern regions, consistent with a plausible environmental motivation.

## 5. Outputs

For any given place, the EDOPS will produce:

- A structured environmental signature, serialized as JSON, including local (`s`) and upstream (`u`) values for applicable variables
- Coastality fields: outlet type, flow distance to marine outlet, topological depth from coast
- A three-tier spatial stratification: local, near-upstream, full-upstream, for key variables [*]
- Summary statistics of underlying variables [*]
- Dimension scores from dimensionality reduction [*]
- Optional categorical banding
- Machine-readable output suitable for downstream analysis and similarity computation
- A brief natural language interpretation of the signature, generated by an LLM, suitable for non-specialist users of gazetteer and cultural heritage platforms

JSON serialization is intentional: the signature is structured (named variable groups, local/upstream pairs, coastality component, neighborhood metadata) and self-describing. A consumer can interpret values without external schema documentation. Similarity and comparison operations derive a vector from the JSON at query time, selecting whichever fields are relevant to the task.

## 6. Validation `[Rev. 07 Apr — substantially revised]`

A central methodological question — whether EDOP signatures are capturing something real about place — requires external validation. The nature and limits of that validation are discussed here.

### EDOP as Research Instrument

EDOP signatures cannot be evaluated for quality in the abstract — quality is always relative to a purpose and a research question. EDOP is better understood as a **research instrument** than a predictive model: a configurable environmental characterization that researchers bring their own questions to. A historian asks which combination of environmental dimensions illuminates a phenomenon they are studying; the instrument does not prescribe the answer.

This framing has a direct consequence for validation: the instrument is validated through *accumulating use*, not by passing a single benchmark test. A well-designed instrument is one that:

- Captures real environmental structure (internally consistent, globally reproducible)
- Enables meaningful comparison across locations and periods
- Surfaces structure — similarities and differences — that researchers did not already know
- Generates productive residuals: cases where the signature fails to explain a known cultural outcome, pointing toward missing dimensions or genuine culture-overrides-environment phenomena

Both successful correspondences and productive residuals are findings. Neither invalidates the instrument.

### Settlement Correspondence as Existence Proof

`[Rev. 07 Apr]` An earlier version of this prospectus framed settlement correspondence as providing "a principled objective function for parameter tuning" — the logic being that variables which improve settlement prediction are better variables. This framing has been revised.

Settlement prediction (classifying locations as settled vs. unsettled) is not the right optimization target for EDOP. EDOP is not an Archaeological Predictive Model. Settlement correspondence is better understood as an **existence proof**: initial evidence that the signature captures something meaningful about habitability, presented to establish the instrument's non-triviality. It is a demonstration, not a feedback loop.

The more useful validation question is: *do similar signatures co-occur with similar cultural outcomes more often than chance?* This is a weaker and more honest claim than "the signature predicts settlement," and it is testable across diverse datasets without committing to a single predictive target.

### Parameter Choice and Research Question Rubrics

`[Rev. 07 Apr]` Parameters are not tuned globally to optimize a single metric. They are chosen *for research questions*:

- "What are the environmental conditions shared by early agricultural societies?" → bands A+B+C, s+u, basin level 08, LMR window 6000–4000 BCE
- "Which WHC cities share upstream climate profiles?" → band C upstream only, level 08
- "What is the local physiographic context of this polity?" → band A, s-only, level 10

A key output of the validation program is a **parameter rubric**: empirically grounded guidance on which parameter combinations produce coherent results for which types of questions. This rubric emerges from testing rather than being specified in advance. Cases where adding a variable or changing a parameter *degrades* correspondence are as informative as cases where it improves it.

### Planned Validation Experiments

**D-PLACE correspondence experiment**: A sample of D-PLACE societies (target: ~30, globally distributed) will have signatures generated at basin levels 06, 08, 09, and 10, using band combinations A, B, C, and composites. For each configuration, pairwise environmental similarity will be compared to pairwise subsistence similarity (D-PLACE categorical variables). The correlation between similarity matrices — tested against a permutation null — addresses: (a) whether any environmental signature correlates with subsistence patterns at better than chance; (b) which basin level produces the strongest signal; (c) which band combination is most predictive; and (d) whether s+u signatures outperform s-only. Consistent outlier pairs (environmentally similar but subsistence-dissimilar, or vice versa) are examined qualitatively for residual structure.

`[Rev. 07 Apr]` Temporal matching is a required element of this experiment: signatures should be extracted for the period of documented society occupation, not the present-day baseline. LMR v2.1 enables this for societies documented within the 1–2000 CE range.

`[Rev. 16 Apr]` The D-PLACE CLDF v3.3.0 dataset is now loaded in full into the project database (`dplace` schema), with 1,291 Ethnographic Atlas societies spatially linked to basin08 via `dplace.society_basin`. The `main_focal_year` field in `dplace.societies` provides the temporal anchor for LMR extraction. The "~30 societies" initial target was conservative — the infrastructure now supports running the full corpus. The initial experiment will begin with a globally stratified subsample to establish parameter sensitivity, then scale to the full EA set.

**Seshat polity correspondence** `[Rev. 16 Apr]`: The Seshat Global History Databank is now loaded into the project database (`seshat` schema: 544 polities in `seshat.general`, 621 in `seshat.social`, covering 23 and 77 variables respectively). Of these, 329 polities match Cliopatria polygon boundaries via `gaz.clio_polities.seshatid`, providing temporally scoped polygons (each row carries `year_from`/`year_to`) that can be submitted to EDOP as area inputs.

The Seshat experiment complements D-PLACE on two dimensions: (1) the unit of analysis is a historical *polity* (polygon, temporally bounded) rather than an ethnographic point society; and (2) the target variables are social complexity indicators rather than subsistence categories.

Variable types in Seshat differ structurally from D-PLACE and the experimental design must account for this. Approximately 72 of 77 social complexity variables are binary — coded `present` / `absent` (with `unknown` and `uncoded` as missing-data states). The remaining variables with meaningful numeric range are: `polity_territory`, `polity_population`, `population_of_the_largest_settlement`, `administrative_level`, `military_level`, `settlement_hierarchy`, `religious_level`, and `largest_communication_distance`. Two distance metrics follow from this structure:

- For binary variable sets, pairwise **Hamming distance** (proportion of variables that differ) produces the similarity matrix for Mantel-type permutation tests.
- For the continuous/ordinal variables, standard Euclidean or Spearman correlation against environmental signature vectors is appropriate.

The most theoretically motivated correlations are: does environmental signature (particularly the s/u aridity contrast, terrain variability, and upstream catchment size) predict polity territory, population, or administrative hierarchy depth? These three are the highest-variance Seshat variables and have the most direct theoretical connection to environmental carrying capacity.

The temporal dimension is directly supported: a polity's `year_from`/`year_to` range maps to an LMR extraction window, enabling signatures anchored in the documented period of the polity rather than the contemporary baseline. The combination of Cliopatria polygon geometry and Seshat temporal scoping makes this experiment a worked example of the temporal-sequence polygon analysis described in Section 4.

**Settlement hearth correspondence**: Signatures for well-documented early urban hearths (Fertile Crescent, Indus, Yellow River, Niger Inland Delta) are compared to global basin signature distributions. Do the most similar basins globally appear in the historical record as settled or environmentally significant? This is the existence-proof test. Its purpose is demonstration, not parameter tuning.

**Anomaly structure as signal**: Settlements in low-viability terrestrial environments (the Yaghan case; Pacific island settlements; oasis cities in endorheic basins) should appear as anomalies in any terrestrial-only model. Mapping anomaly structure against coastality dimensions tests the coastality component directly: do terrestrial anomalies resolve when coastality fields are added?

**Worked historical examples**: A small number of well-documented historical processes — where environment-culture linkage is independently attested — will be developed as demonstration cases showing what the instrument makes visible that was previously uncharacterized. The Northern Song southward expansion (wetness gradient, 962–980 CE) is the first candidate. Two or three additional cases from different regions and periods are needed before the October 2026 presentation.

### Scope Limitation: Culture Acting on Environment

`[Rev. 07 Apr]` A question raised at the first public presentation (06 April 2026): can EDOP characterize cases where *culture reshapes environment* — the Sauer axis of culture acting on landscape? The Yellow River deforestation→sedimentation→course instability sequence is the canonical example.

EDOP as currently designed characterizes the environmental conditions that cultures *encountered*, not the environmental transformations that cultures *produced*. BasinATLAS variables are contemporary snapshots; they do not encode historical process records of anthropogenic landscape change. This is a principled scope limitation, not an oversight. The temporal enrichment layers (LMR, eVolv2k) partially address it by enabling comparison of signatures across periods — if hydrology fields diverge between periods in ways correlated with known deforestation events, that is circumstantial evidence of the culture→environment axis appearing in the data. But EDOP cannot directly model anthropogenic landscape transformation. That dimension is a candidate for future development, potentially in coordination with paleoecological or historical land-use datasets.

## 7. Methodological Challenges

- **Scale and neighborhood definition**: Basin level selection and boundary sensitivity are indicative of the Modifiable Areal Unit Problem (MAUP) and require systematic evaluation. Scale-sensitivity reporting is a designed feature of the signature output. A systematic study of how signatures vary across basin levels and neighborhood types for a representative set of locations is planned as an initial analytical output and likely first paper contribution.

- **Local vs. upstream environmental character**: The `s`/`u` duality introduces a structured form of spatial context that must be handled explicitly in signature design and communicated clearly in outputs.

- **Distance-weighted upstream exposure**: Pre-computed `u` values weight upstream basins by contributing area, not flow distance. A location's actual environmental exposure to upstream conditions attenuates with distance, and different processes have different characteristic decay distances. Implementing process-specific, distance-weighted upstream profiles via network traversal is a designated research extension, suitable for collaboration with a GIScience partner or graduate student.

- **Process-type typology for spatial influence**: Following Goodchild (pers. comm., 2026), environmental influence on a place operates through distinct process geometries — hydrological (network-constrained, upstream), atmospheric (directional, Euclidean decay), acoustic (Euclidean, rapid decay), social/acquaintance (network-structured). A complete implementation would model each process type with its own spatial influence function. The hydrological case is the most tractable given available data and is the designated first implementation.

- **Temporal mismatch**: Contemporary environmental datasets are used as baselines for analyses that are often historical. The variable banding structure addresses this partly (Groups A/B are defensible historical baselines; Group D requires explicit qualification). A more direct resolution — LMR v2.1 for continuous annual climate and eVolv2k for volcanic event annotation, both covering the 1–2000 CE range of the project's primary use cases — is a planned program of work rather than a hypothetical. The residual challenge is the sub-1 CE range and the integration of marine temporal context (ICOADS) for coastal signatures.

- **Spatial autocorrelation**: Globally gridded environmental variables are inherently spatially autocorrelated, which affects both variable selection and the validity of downstream comparative analysis. This requires explicit treatment.

- **Interpretability of reduced dimensions**: PCA components are not inherently interpretable; validation against independent signals is needed to confirm that they correspond to environmentally meaningful distinctions.

- **Risk of reifying environmental context as causal**: Addressed through the bounded possibility space framing — environmental signatures define what settings afford and constrain; cultural agency determines which possibilities are realized — but requiring vigilance in documentation and communication.

- **LMR spatial precision ceiling** `[Rev. 29 Apr]`: LMR v2.1's 2°×2° grid maps approximately 39 sub-basins per cell at L8 (p95: 74 basins). The spatial precision ceiling is approximately 200 km — LMR is a regional signal, not a local one. Signature queries return the nearest LMR cell value; sub-cell variation is not resolved. This ceiling is appropriate for most historical queries (which concern regional climate regimes, not sub-basin microclimate) but must be stated explicitly. The implication: two settlements separated by less than ~200 km receive identical LMR values, and their Band T differentiation depends entirely on the static Band A–E signature.

- **HYDE/EarthStat spatial divergence** `[Rev. 29 Apr]`: Band T (HYDE 3.4 temporal) and Band D (EarthStat static, ~2000 CE) are non-redundant but at agricultural hotspot sub-basins can diverge significantly in cropland spatial allocation — up to 3× at Ur for the 2000 CE calibration epoch. This reflects genuine spatial disaggregation uncertainty in modeled historical land use, not a data error, and is a known limitation of both datasets. Both are included in the signature with appropriate notes; the divergence is formally deferred to the October 2026 expert meeting for domain expert review.

- **Population density in an environmental signature** `[Rev. 29 Apr]`: Whether population density belongs in a physically oriented environmental instrument is an open design question. It is retained in Band D provisionally and surfaced in the API payload with a note; it is explicitly excluded as a classification feature for validation experiments (circular with respect to settlement correspondence). The question of whether demographic variables are properly environmental or properly cultural — and whether their inclusion biases the instrument toward the phenomena it is meant to evaluate — is deferred to the October 2026 expert meeting.

## 8. Positioning and Contribution

EDOP is proposed as:

- A service layer usable by digital humanities and cultural heritage platforms
- A methodological contribution to GIScience and spatial analysis
- A research tool for investigating environment–culture relationships

EDOP's novelty relative to existing geographic enrichment tools lies in four features: (1) multi-scale, basin-level environmental characterization with explicit uncertainty and variation reporting; (2) structural use of local/upstream duality as a signature component, with a principled extension toward process-aware, distance-weighted upstream exposure; (3) first-class treatment of coastality as a dimension complementary to, and decoupled from, terrestrial signatures; (4) genuine historical depth through integration of three temporal enrichment datasets — paleoclimate reanalysis (LMR v2.1, 0–1998 CE), volcanic forcing annotation (eVolv2k v4, ~500 BCE–1900 CE), and land-use history (HYDE 3.4, 10,000 BCE–2023 CE) — enabling place signatures anchored in specific historical periods rather than the contemporary baseline alone `[Rev. 29 Apr]`. Together these constitute a coherent and extensible contribution not replicated by current commercial or open tools.

EDOP is not a classificatory scheme, instead a computational infrastructure for environmental characterization. Credibility in both GIScience and humanities venues requires that methodological assumptions be explicit, documented, and subject to sensitivity testing — a standard the project aims to meet.

## 9. Broader Research Context

EDOP is conceived as one component of the **Computing Place** framework, paired with a Cultural Dimensions of Place (CDOP) module. Together they support systematic investigation of questions such as:

- Do cultural traits cluster in particular environmental regimes?
- How do environmental gradients correspond to linguistic, social, or economic variation?
- How stable are environmental signatures across historical change?

Environmental signatures define bounded possibility spaces — what natural settings afford and constrain — while cultural agency determines which possibilities are realized. The Computing Place framework supports comparative analysis without asserting causation.

`[Rev. 07 Apr]` A recurring question from humanities audiences is whether building an environmental module implies treating environment and culture as separable. It does not. Sauer's insight — and Computing Place's premise — is that they are inseparable in practice. EDOP and CDOP are a *separation of concerns* in the software engineering sense: each module is developed to a standard of rigor appropriate to its domain, and they are brought together in the Computing Place framework. Building EDOP first reflects development sequencing, not a theoretical claim that environment can be understood independently of culture.

The EDOPS element of **Computing Place** is being developed with the institutional partnership of ISHI (University of Pittsburgh), whose expertise in spatial history and whose ongoing work with the World Historical Gazetteer provides a natural integration context: Computing Place can publish environmental signatures as linked annotations keyed to WHG place identifiers, contributing to a growing ecosystem of richly described, computationally accessible historical places.

## 10. Open Architectural Questions and Prospective Extensions `[Rev. 16 Apr]`

This section collects scope extension ideas and unresolved design questions worth preserving for future consideration, without committing them to the current development roadmap. A number of open questions raised during the April 2026 exploration and implementation phase — Band D variable composition (population density, irrigated area), HYDE/EarthStat spatial divergence at agricultural hotspot basins, LMR calibration text for the narrative layer, and the threshold for asserting Band T LMR reliability — are formally deferred to the **October 2026 expert meeting at ISHI** for domain expert review. That meeting is the designated forum for translating provisional positions into stable design commitments `[Rev. 29 Apr]`. New items will be added here as they arise.

### Researcher-Contributed Regional Environmental Data

*Raised by Ruth Mostern, 16 April 2026.*

Computing Place currently assembles environmental signatures from globally consistent, centrally maintained datasets (BasinATLAS, LMR, eVolv2k, OneEarth, etc.). A natural extension — and one with significant architectural implications — would be to allow researchers to contribute high-resolution, region- and period-specific environmental data derived from their own work: paleoclimate reconstructions, regional pollen sequences, high-resolution sedimentation records, vegetation histories, and similar outputs of specialist environmental history research.

Such contributions would enrich signatures for the specific areas and periods they cover, potentially with much higher spatial and temporal resolution than global baselines. The Yellow River loess and sedimentation record is a canonical example: a dedicated reconstruction for that region would substantially improve signatures for one of the most historically significant river systems in the world.

The architectural implications are non-trivial:

- **Provenance layer**: signatures would need to distinguish global-baseline fields from contributed regional data, with source attribution per field
- **Coverage registry**: a catalog of contributed datasets specifying spatial extent, temporal range, resolution, variables, and contributor
- **Priority/fallback logic**: query logic would prefer regional data where available and fall back to global baselines outside coverage — a layered source stack rather than a single authoritative source per variable
- **Curation and quality standards**: contributed data would require vetting; not all regional reconstructions are equally reliable or methodologically consistent with global baselines

This is in effect a **federated data architecture** — Computing Place as a platform aggregating community-contributed regional enrichments on top of global baselines. It is a significant scope expansion but a compelling direction for a humanities infrastructure project with a distributed scholarly community. It is noted here for future design consideration.

---

*Sauer, C. O. (1925). The morphology of landscape. In Foundation Papers in Landscape Ecology (2007), 36–70.*
