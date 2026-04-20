EDOPS Exploration Phase — Tasks 1–6 Synthesis
Compiled 20 April 2026. Compressed study guide consolidating the exploration-phase work: framework-level claims established across tasks, task-by-task synthesis with paired reading priorities from method_references.md, open methodological items pending resolution, and structural bridge to the forthcoming Band F temporal characterization. Intended to support deeper ingestion of the findings during self-education on statistical methodology, and to serve as seed context for future Opus conversations on the project. The full exploration_log.md and edops_opus_commentary.md remain the archival sources of detail; this document is the distillation.
Structure: Part A (framework-level claims) → Part B (task-by-task synthesis) → Part C (pending state) → Part D (Band F bridge).

---

## Part A — Framework-Level Claims from Tasks 1-6

The six exploration tasks produced 36 findings at varying weights. Most are task-level observations about specific variables or variable groups. Three cross-task observations function at a different level — they frame how the characterization as a whole should be read, and they shape every downstream analytical choice: correspondence testing design, PCA and variable selection, rubric construction, methodology-paper framing. Each is supported by findings from multiple tasks rather than resting on any single result. Part B treats the task-level findings with reading pairings; the three claims here are the stable intellectual content that the rest of the document elaborates.

### 1. The global basin distribution is continuous, with categorically distinct extremes.

Supporting findings: F5.2, F5.1, F5.3, F5.6 (primary); F1.7, F3.1 (adjacent structure).

Density-based clustering (HDBSCAN, min_cluster_size=1000) found only two groups in the global basin population: Greenland-and-similar-glaciated-Arctic environments (4,856 basins) and a single catch-all encompassing most of the world's landmass (114,009 basins), with 37.7% of basins unclustered as noise. With one exception — the glaciated Arctic — there are no sharp density peaks in environmental feature space corresponding to distinct basin types. Variation grades from one environment to another without gaps.

K-means clustering on Band A+B+C variables, given no geographic input, nevertheless produces a global map that recognizably reconstructs Earth's biome geography (Sahara, Sahel transition, Amazonian and Congolese tropics, Andes and Himalayan high-elevation belts, boreal zone, Australian interior). Geographic coherence validates that the variables carry real environmental structure, but the coherence is necessary, not sufficient — the clusters are useful analytical cuts, not natural kinds. Three karst clusters distributed across the temperature gradient (F5.3) illustrate this: karst geology produces distinctive environmental positions that cross-cut climate types, creating structure but not discrete biome types.

Consequence: any typology imposes discrete cuts on a continuous surface. Twenty clusters is working typology at exploration-phase resolution, not a defensible published typology; k selection will need principled justification (silhouette analysis, gap statistic, or substantive communicability — probably 8-12 for humanities-facing use). Correspondence-test results against cluster membership need to distinguish real extremes (permafrost, hyperarid, glaciated Arctic) from artificial slices of a gradient.

Caveat: the continuity claim currently rests on one HDBSCAN configuration. Before publication, parameter robustness (varying min_cluster_size, min_samples) and feature-space robustness (raw vs. PCA-reduced) need confirmation. The claim is probably right — the k-means visual supports it — but it should be treated as provisional at framework weight until tested.

### 2. Basin count is not basin importance.

Supporting findings: F1.10, F3.1, F5.4 (primary); F2.1, F2.2 (adjacent).

The BasinATLAS dataset has structural biases in how basin counts are distributed that do not correspond to environmental or historical importance. Three distinct mechanisms produce this:

*Geometric scale effects.* L8 sub-basin polygons are physically larger at high latitudes than in the tropics. East Siberian taiga leads all terrestrial ecoregions by basin count with 5,654 basins — not because boreal environments are the most common setting for human settlement, but because Siberian L8 polygons are large. Area-weighted ecoregion counts would produce a substantively different ranking.

*Network topology.* The basin network has a tree topology with most leaves at the headwater end. Headwater basins, where upstream footprint approximately equals local footprint, numerically dominate; outlet basins, where upstream and local environments diverge most, are rare by count but disproportionately important historically. This is why the s/u divergence is a tail phenomenon globally — the tail is not rare because divergence is rare in analytically interesting places, but because headwaters outnumber outlets.

*Cluster-assignment artifacts.* Large river systems are split across many L8 sub-basins, each carrying the upstream discharge signal. The "large rivers" k-means cluster (km=17, 5,416 basins, mean discharge 11× global mean) is partly an artifact of this representation — a site in km=17 is classified by its regional river system's network position, not its local environmental character.

Consequence: any global statistic computed by averaging over basins is implicitly weighted by these factors. MAUP has three distinct facets here requiring consistent treatment, not a single issue to be acknowledged and moved past. Correspondence testing using cluster membership needs rubric-level clarity on what "membership in cluster X" means — local environmental character, network position, or polygon-size-weighted ecoregion membership.

### 3. Cultural datasets have divergent environmental biases.

Supporting findings: F6.1, F6.2, F6.3, F6.4, F6.5.

Cultural correspondence datasets do not sample environmental space uniformly, and their biases point in different directions. D-PLACE over-samples tropical wet mountains at 3.65× (reflecting 19th-20th century fieldwork access patterns and population density), and severely under-samples cold and hyperarid environments — Arctic highland at 0.01×, hyperarid desert at 0.11×, cold boreal at 0.16×. WH Cities over-samples regulated river corridors at 5.55× (reflecting civilizational biases in UNESCO nomination patterns), with six cluster types having zero representation and the single largest global cluster (tropical humid, 9.49% of basins) containing only 1.16% of WHC entries.

The biases are not convergent. Combining D-PLACE and WHC broadens coverage but does not resolve their shared cold/arid blind spot. Blank spots on coverage maps have heterogeneous causes: sampling reach, population sparsity, and colonial destruction of source populations are three mechanisms, all producing the same visible absence, with different interpretive implications. The Argentine Pampas/Patagonia blank in D-PLACE reflects the Conquest of the Desert — people existed, were documented incompletely, and were exterminated before systematic fieldwork. The Northwest North American coverage by contrast reflects rugged geography slowing colonial advance sufficiently for Boas-era documentation to occur. Null correspondence results in under-represented regions cannot be interpreted as evidence against environmental correspondence; absence of data is the explanation.

Consequence: correspondence testing must be power-stratified by cluster, restricted to environmental space where the cultural dataset has adequate representation. The operational framing this licenses is stronger and more specific than "environmental signatures correlate with cultural patterns" — it is "signatures correlate with cultural patterns within the environmental envelope of the cultural dataset used." Different datasets validate rubrics over different envelopes; they are complementary, not substitutable. Characterizing these biases quantitatively against the environmental cluster baseline (rather than against population or political boundaries as most bias discussions do) is itself a methodological contribution.

Draft of Parts B, C, D below. Total comes to ~3,800 words combined with A — slightly over the 3,500 target but within range; the material needs what it needs. Offer to package as a file at the end.

---

## Part B — Task-by-Task Synthesis

Each task is treated compactly: the framing claim it established, the findings that carry the most weight (not all findings), methodological forks and pending decisions, and reading priorities from `method_references.md` paired with specific findings.

### Task 1 — Marginal distributions

The task characterized the global distribution of every scalar variable at L8 plus frequency and entropy for categorical variables. Three findings from the set of ten bear weight at framework level.

F1.4 established that global temperature is bimodal — a cold-regime peak (−5 to 5°C, high-latitude and high-altitude basins) and a warm-regime peak (20–25°C, tropical and subtropical). This is not primarily a finding about temperature; it is a methodological fork. Any PCA on raw temperature will have its first component pick up the bimodality and be difficult to interpret as a smooth gradient. Resolution options include regime-stratified analysis (separate PCAs for cold and warm clusters, using bimodality as stratification variable) or mixture modeling with posterior regime-probability assignment per basin. The choice needs to be made before formal PCA, not discovered during it.

F1.7 flagged that karst (82% zero), permafrost (77% zero), wetlands (57–71% zero), and reservoirs are globally sparse. These variables carry strong signal where they fire but have near-zero mass for the majority of basins. Standard continuous-variable machinery (PCA, correlation matrices, k-means) will wash out their signal or distort results. The methodological move is two-tier: treat dense variables with continuous methods, treat sparse variables as binary presence/absence flags or analyze their non-zero subset separately. This compounds with F4.7's later finding that permafrost operates as a cross-band integrator — when it fires, it organizes structure across temperature, soil, and human variables simultaneously.

F1.10 is the most paper-relevant finding in Task 1. East Siberian taiga leads all terrestrial ecoregions by basin count with 5,654 basins, not because boreal environments are environmentally common, but because L8 sub-basin polygons are physically larger at high latitudes. This is MAUP-in-action at demonstration weight and supports framework claim 2.

Reading priorities, in order of urgency for self-education:
- *Fotheringham & Wong 1991* on MAUP in multivariate analysis — pairs with F1.10; short, paper-length, the foundational direct citation you will need
- *Greenacre 2021* or the accessible chapters of *Pawlowsky-Glahn 2015* on compositional data — pairs with F1.3 (clay/silt/sand sum to 100%); needed before any PCA includes soil texture variables
- *Bishop 2006 Ch. 9* on mixture models — pairs with F1.4; gives you the quantitative tool to confirm bimodality and assign regime probabilities

### Task 2 — Missing-data and scale patterns

The task produced a three-way variable classification that upgrades the prospectus's single-sentence MAUP acknowledgment to an empirically grounded methodological finding: 27 variables stable across L8/L6, three geometrically scale-sensitive (elevation extremes, discharge max, river area), one topologically scale-sensitive (`dist_sink`).

F2.1 is the subtle-but-important observation that null rates *decrease* at L6 because larger polygons are more likely to overlap source-dataset footprints — this is coverage geometry, not data-quality improvement. Most analysts would note the lower null rate and move on; catching the mechanism matters for any cross-level analytical claim.

F2.3 is the strongest operational guardrail in the exploration log: `river_area` at L6 is not a scaled version of L8 — it is a structurally different quantity (polygon-level network area vs. sub-basin local area, differing by roughly an order of magnitude in mean). Cross-level comparisons of this variable will produce wrong results if treated as equivalent. This warrants a schema-level annotation flagging the variable as scale-incomparable, not just log-file documentation.

F2.6 licenses most of what comes downstream: 27 of 38 variables — including all climate, soil, and socioeconomic variables — are level-invariant. The D-PLACE correspondence experiment, the PCA work, and most signature analytical content can be conducted at either L8 or L6 without cross-level comparability concerns. Scale-sensitivity is primarily a hydrological-geometry problem concentrated in a small, well-characterized subset.

F2.7 is honest methodological flagging: the N-artifact classification (distinguishing apparent shift due to smaller L6 sample from real shift that is harder to detect) is currently provisional, and the 0.1 std-shift threshold for the stable/scale-sensitive boundary is a heuristic. For paper-writing, these need either formal testing (permutation or bootstrap) or explicit provisional framing.

Reading priorities:
- *Fotheringham & Wong 1991* — the same priority applies here as for Task 1
- *Goodchild 2011 "Scale in GIS: An overview"* — pairs with F2.1, F2.3; short, lineage-appropriate for citation
- *Wong 2009* handbook chapter for MAUP remediation approaches — mid-length review

### Task 3 — s/u divergence distribution

The task characterized the s/u duality empirically for the first time and established its role in the signature architecture.

F3.1 is the load-bearing finding for the entire s/u-as-contribution argument: median divergence is exactly 0 for all nine s/u pairs globally. The duality is not a generic feature — it is a tail phenomenon. For most basins (headwaters, near-headwaters), s and u carry redundant information. For a minority at specific drainage positions (outlet basins, piedmont sites, confluence locations), divergence is the signature's most informative dimension. This directly supports framework claim 2 and reframes how the s/u duality is described in the prospectus: the divergence magnitude, not the raw s and u values, is the contribution.

F3.6 is the methodological-honesty finding: `river_area` divergence measures network position, not environmental character, and should not be included in divergence rankings alongside climate or terrain variables. Treating river_area local and upstream as independent descriptors of channel size and network magnitude — not as a divergence pair — is the correct handling.

F3.7–F3.9 are the worked examples: Timbuktu at p99.9 on upstream-moisture divergence, Ur at p99.6 on aridity divergence with the Band D caveat noted in Part C, Kaifeng at p99.9 on slope divergence with inverted monsoon-driven moisture gradient. The three sites occupy extreme positions in structurally different ways. F3.10's generalization from these three to "no single exotic-river template" overreaches the evidence — three cases chosen for distinctiveness cannot support a typology claim. F3.10 should be read as "three worked examples illustrating distinct fingerprint regimes"; the empirical typology question (whether divergent-tail basins cluster into a small number of recognizable types or scatter continuously) is worth running as a follow-up.

Reading priorities:
- No specific statistical methodology reading is urgent for Task 3 — the ECDF and percentile analysis is standard distributional work
- *Jolliffe 2002* on PCA becomes relevant for the variable-selection question raised by F3.1: in PCA, drop both s and u as redundant and retain only the divergence metric, or keep one of each pair? Worth thinking through before Task 5 extension or formal PCA

### Task 4 — Correlation structure

The task identified which variables are genuinely independent signals and which are near-duplicates, producing a variable-selection framework that licenses subsequent PCA and clustering work.

F4.1 is the empirical ground under F3.1's tail-phenomenon claim: the three climate s/u pairs correlate at r = 0.984–0.989 globally. Local and upstream climate values are nearly interchangeable for most basins; the divergence is the informative dimension. F4.1 and F3.1 are the same structural fact observed through two lenses, not independent convergent evidence — worth remembering for paper-writing so the two findings are not presented as independently corroborating the same claim.

F4.4 is the most interpretively consequential finding: Band D splits into two sub-clusters — intensity (population density, human footprint, cropland) and development (GDP, HDI) — that correlate *negatively* with each other. High-GDP areas are not high-footprint areas; intensive land use and economic modernity point in opposite directions globally (Scandinavia and Canada vs. South Asia and sub-Saharan Africa). Any rubric or narrative using "human impact" as a single construct implicitly chooses one or the other. This has direct implications for CDOP-facing work when that phase begins.

F4.8 confirms the prospectus claim that coastality is a first-class signature component: `dist_sink` has no correlation above |r| = 0.41 with any other variable in the dataset. Coastality adds genuinely orthogonal information. This is the quantitative basis for treating it as a structural axis rather than a secondary descriptor.

F4.9 synthesizes the operational consequences: six variables to drop for PCA at |r| > 0.9 threshold, reducing the 37-variable set to 31 without substantial information loss. Further reduction requires cross-band judgment calls that belong in Task 5 design.

Reading priorities:
- *Jolliffe 2002* on PCA — pairs with F4.1, F4.9; canonical for variable selection and component interpretation
- *Everitt & Hothorn 2011* on applied multivariate analysis — pairs with F4.4's sub-cluster structure and the general cross-band question; accessible entry point

### Task 5 — Geographic pre-clustering

The task established a working typology and surfaced the continuity claim that anchors framework claim 1. Two structural observations deserve highlighting beyond what Part A covered.

F5.5's ARI-0.179 finding between the A+B+C clustering and the previous workbench A–D clustering is not primarily a clustering-stability result — it is an argument about input validity. The previous clustering included Band D human variables, which made human presence a feature of "environmental type" that was then used to interpret where humans are. That is circular for correspondence testing. Band D variables belong in the analysis as dependent variables or secondary descriptors, not as typology inputs. This is a framework-weight methodological commitment, not a task-level finding.

F5.6 commits to k-means over HDBSCAN for the working typology and documents normalization choices (log1p + StandardScaler for non-negative right-skewed variables, StandardScaler only for temperature given its bimodal range). The k=20 choice is explicitly flagged as arbitrary and requiring revisiting before any published typology. The probable final range is 8–12 for humanities-facing communicability, possibly hierarchical (top-level types with sub-clusters) to serve both analytical detail and user communication.

Open questions pending from Task 5 are collected in Part C.

Reading priorities:
- *Everitt, Landau, Leese & Stahl 2011 Cluster Analysis* — canonical clustering reference; pairs with F5.6
- *Campello, Moulavi & Sander 2013* and *McInnes et al. 2017* on HDBSCAN — pairs with F5.2; needed to defend the rejection of HDBSCAN for this data
- *Bishop 2006 Ch. 9* — relevant here as mixture-model alternative to k-means

### Task 6 — Coverage and sampling-bias

The task's core findings (F6.1–F6.5) are covered in framework claim 3 of Part A. The operational conclusion — the D-PLACE correspondence experiment should be power-stratified by cluster and restricted to environmental space where the cultural dataset has adequate representation — is the methodological commitment this task produced.

F6.4's distinction between three mechanisms of under-representation (sampling reach, population sparsity, colonial destruction of source populations) is worth naming separately as a methodological point, because it changes how null correspondence results should be interpreted. A null result in the Pampas region is not ecologically meaningful — it is evidence of the Conquest of the Desert, not of environmental disconnect. This is the kind of reading that will land with humanities audiences and signals that EDOPS engages seriously with the limits of its source datasets.

Reading priorities for when the D-PLACE experiment is designed:
- *Legendre & Legendre 2012 Ch. 10* on matrix correlations — pairs with Mantel test design; canonical how-to reference, including partial Mantel tests
- *Guillot & Rousset 2013* critique of Mantel tests, and *Legendre, Fortin & Borcard 2015* response — read together; anticipates reviewer concerns
- *Cliff & Ord 1981*, *Anselin 1995* on spatial autocorrelation — pairs with prospectus §7 acknowledgment; becomes relevant when correspondence claims are made across basins

---

## Part C — Pending State

Working items, not prose. These are loose ends from the exploration phase that need resolution but were not urgent enough to block Tasks 1–6.

**Log corrections pending:**
- F3.8 implication-clause rewrite to distinguish present-day-signature observation from ancient-condition inference. As written it reasons from Band D values to third-millennium-BCE claims, which the banding framework in the prospectus is designed to prevent. The historical claim (upstream-agricultural / local-wetland inversion for Ur's period) is correct independently; it is not evidence from the signature.
- F3.10 demotion from "no single exotic-river template" typology claim to "three worked examples illustrating distinct fingerprint regimes." The typology question is empirically open and worth running.

**Open methodological forks:**
- Bimodality handling for temperature (and likely aridity): regime-stratified analysis vs. mixture modeling with posterior regime-probability assignment. Decision needed before formal PCA.
- s/u treatment in PCA: drop one of each pair retaining the other, or drop both retaining only divergence metrics. Current commentary leans toward divergence-only but the choice is worth experimenting with.
- k selection for published typology: silhouette analysis, gap statistic, or substantive communicability target (8–12 for humanities use). Possibly hierarchical.
- Zero-inflation variables (karst, permafrost, sparse wetlands): two-tier handling is the committed approach, but the specific implementation — binary flags in the main analysis plus separate continuous analysis on the non-zero subset — needs to be settled before Task 5 extension work.
- Reservoir_vol band classification check: confirm whether it is currently leaking into the A+B+C k-means input, and if so, either correct the input or document the choice.
- Permafrost dominance test: run k-means with and without permafrost to confirm whether it is contributing or dominating. Related to the zero-inflation two-tier handling.

**Schema-refinement items from commentary, not yet in any design document:**
- `_pair_type` annotation distinguishing divergence s/u pairs from network-scale s/u pairs (F3.6)
- `_scale_sensitive` flag on hydrology-geometry variables (F2.3–F2.5)
- `_percentile` sub-fields for divergence values, providing distributional context alongside raw values (F3 synthesis)
- `divergence_summary` field idea for compact "this basin sits at p87 on aridity divergence, p2 on wetland divergence, modal everywhere else" reporting (F3.1)
- "Method literature" column added to exploration log entry template going forward, pairing with the self-education reading program

**Validation items flagged in Part A:**
- HDBSCAN parameter robustness for the continuity claim (varying min_cluster_size, min_samples)
- Feature-space robustness for the continuity claim (raw vs. PCA-reduced input)
- Permutation or bootstrap testing for the N-artifact classification in F2.7

---

## Part D — Band F Bridge

The three framework claims from Part A have direct analogs in the temporal domain, and noticing them now is cheaper than noticing them during Band F write-up.

*Framework claim 1 (continuous-plus-extremes) carries directly.* The LMR 1–2000 CE record is a continuous-plus-extremes distribution in time: long stretches of climatic stability punctuated by specific events (Medieval Quiet Period, Little Ice Age, major volcanic forcing episodes). Any typology of climate regimes across 2,000 years will face the same tension as the global basin typology — most of the distribution is continuous, a minority of epochs are categorically distinct. Methodological choices about how to characterize the time series (moving averages, regime-change detection, anomaly windows) parallel the spatial-clustering choices.

*Framework claim 2 (count-vs-importance) has two Band F analogs.* First, time-slice-count vs. time-slice-importance for LMR: a century of stability is many annual time steps; a decade of climate disruption is few steps but historically weighty. Any mean or signature computed over a query window weights them equally by default. This is MAUP-in-time, with the same structural shape as MAUP-in-space. Second, event-count vs. event-magnitude for eVolv2k: the catalog is dominated by many small eruptions, with a handful of Laki/Tambora/Huaynaputina-class events doing most of the actual climate forcing. Counting events within a query window is not the same as summing VSSI-weighted impact.

*Framework claim 3 (divergent-bias) applies to Band F dataset characterization.* LMR has known regional and temporal biases — proxy availability is not geographically uniform, and reconstruction skill varies by variable (temperature is generally better-constrained than precipitation). eVolv2k has magnitude-detection biases (smaller eruptions in remote locations are under-recorded, especially in earlier periods). These biases need to be characterized against a reference baseline before correspondence testing uses Band F as a truth source.

The first Band F characterization question is whether LMR's 1–2000 CE mean at each location systematically diverges from the BasinATLAS contemporary baseline. If substantial drift exists, the "temporal enrichment" framing in the prospectus needs qualification — you would be enriching against a baseline that already doesn't match. This is the integration-validity question, and it should come first because it affects whether the rest of Band F can do what the prospectus claims.

