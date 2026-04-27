# EDOPS Typology Characterization Plan

*Draft — April 2026*
*Companion to `data_exploration.md` and `exploration_bandT.md`; covers per-band typology development.*

> **Scope**: This document supersedes the deferred Task 12 (Anthromes) from the Band T plan. The case for adopting Anthromes as a signature field has been considered and rejected: it is informationally redundant with the continuous HYDE fields that Band T already returns, structurally brittle at class boundaries under HYDE's reconstruction uncertainty, temporally coarse (six time slices) in a way that contradicts the rest of Band T, and conceptually in tension with EDOPS's process-aware framing. In its place, this plan develops a data-driven per-band typology native to EDOPS, organized as Tasks 13–22.

---

## Purpose

Tasks 1–11 characterized the EDOPS signature variable-by-variable: distributions, missingness, divergence, correlation, an exploratory composite clustering (Task 5), and the temporal layers (Tasks 7–11). The composite k=20 clustering from Task 5 was useful as exploration but is not the right typological output for the service. Two reasons. First, it merged Bands A, B, and C into a single feature space, blurring band-specific structure that the rest of the architecture treats as separately scoped. Second, it produced cluster identifiers (cluster 14, cluster 7) without labels — categorical assignments without semantic content.

The typology phase produces what should be the canonical typological output of EDOPS: per-band clusters with deliberate labels, a band-tuple representation as a derived signature field, and a validation pass against well-documented historical landscapes. The output is both substantive (typologies and labels usable by the narrative layer and by user-facing API responses) and methodological (a documented procedure, with sensitivity analyses, suitable for citation in the methods paper).

The deeper purpose: the typology is the bridge between continuous signature values and human-readable interpretation. A signature with seventy fields is not interpretable to anyone in raw form. A signature that comes with a tuple `[A-3, B-7, C-2, D-1]` and a per-band glossary of what those positions mean is interpretable to anyone willing to read the glossary. This is what Anthromes was attempting to provide; this plan provides it without inheriting Anthromes's structural problems.

---

## Architectural Note: Regimes, Not Modes

A clarification, learned from re-examining Task 5 results, that motivates the methods choices below.

Bands A, B, and C across the global L8 basin population exhibit real environmental regime structure — distinct types corresponding to recognized environmental zones, recoverable as clusters from variables alone. This is what the Task 5 k=20 result demonstrated visually: clusters that received no spatial input formed geographically coherent regions on the global map, because the variables themselves are spatially autocorrelated and thus encode regime structure that is gradient-smooth across geographic space.

The smoothness of regime *boundaries* is a separate property from the existence of *regimes*. Density-based methods (HDBSCAN) detect modes — regions of feature space surrounded by lower density — and at the global scale, with the L8 basin sample dominated by headwater basins along regime transitions, those modes do not separate sharply enough to be detectable. The Task 5 HDBSCAN result (one well-separated mode for glaciated Arctic environments; the rest classified as a single bulk cluster with 38% noise) is consistent with regimes that exist but transition smoothly. Partitioning methods (k-means) impose cuts on a continuous-but-structured space, and that is the appropriate tool for this structure: regimes that grade into each other, rather than density modes that cluster apart.

The geographic coherence visible in the L8 map is an emergent property of the input variables. It is not a property of the clustering algorithm, which received no coordinates. It does not survive at L6, where larger basin polygons average across regimes and produce composite signatures whose cluster membership is unstable. This is itself a finding — typologies are scale-bound, and the scale at which a typology is computed must be reported alongside its definitions.

The implication for this phase: per-band typologies should be developed at L8, with sensitivity analysis at L6 to characterize how robust each cluster is to the scale change. k-means is the working method; HDBSCAN may be useful as a diagnostic for which clusters have detectable density structure (those clusters can be reported with stronger claims) versus which are partition-cuts on a smooth gradient (those need to be described as such). The typology is a useful descriptive instrument either way; honesty about which kind of cluster a given cell is matters for how the label communicates.

---

## Per-Band Task Plan

The four bands have different intrinsic structure and require somewhat different decisions. Recommended sequencing: **Band A first** (cleanest variable set, fewest decisions, builds workflow), **Band C second** (temperature bimodality is a known structural feature; serves as a test of whether the methods can recover it), **Band B third** (size/network-position confounds need handling), **Band D last** (orthogonal sub-clusters are the most analytically delicate). Tasks 18–22 follow the per-band tasks.

---

### Task 13 — Per-band variable preparation and parameter selection

This is foundational and applies to all four per-band tasks. Output is a documented set of variables, normalizations, and clustering-parameter choices used uniformly across Tasks 14–17.

**Method**: For each band, list the within-band variables retained after the F4.9 redundancy pruning. Apply within-band a second pass of redundancy review (any pair with |r| > 0.85 within a band reviewed for whether to drop one). Decide normalization per variable: log1p for right-skewed, StandardScaler throughout, quantile normalization for cases where tail separation matters more than monotone transformation. Decide null/sentinel handling per variable: median imputation, zero imputation, or row exclusion. For each band, compute internal validity indices (silhouette, Calinski-Harabasz, gap statistic) across k = 4 to k = 30 and produce an elbow/silhouette plot to inform k selection.

**Substantive questions**: Does each band have an indicated k from validity indices, or are the indices flat (in which case k selection is partly judgment)? Are there variables where the within-band redundancy review surfaces additional drops not visible in the global F4.9 pass? Do the indices indicate that some bands should be stratified before clustering (Band B large-network basins; Band D orthogonal axes)?

**Artifact**: `notebooks/edop/explore/13_typology_preparation.ipynb`. Per-band variable list with normalization and null-handling notes. Validity-index plots for each band across the k range. A documented recommendation for k per band (with range, not a single number) and any stratification recommendations.

---

### Task 14 — Band A physiographic typology

Band A is the cleanest band: terrain and substrate variables that are time-stable over centuries to millennia, no human content, no temporal scoping. Likely smaller k than Band C (fewer independent terrain regimes globally).

**Method**: Cluster L8 basins on the Band A variables (post-Task 13 selection and normalization) at k values within the indicated range. For each k tested, generate the global map, the per-cluster centroid table, and a sample of exemplar basins (5 most central, 5 most peripheral within-cluster) per cluster. Compare to the indicated k from validity indices. Commit to a single k with justification.

**Substantive questions**: Do the clusters recover recognized physiographic types (alluvial lowland, dissected upland, plateau, mountain, coastal lowland, karst regions)? Are there clusters that don't correspond to any conventional physiographic type — and if so, are they real (e.g., a tropical-low-relief-but-substrate-rich type) or are they method artifacts? How sensitive is the resulting typology to small k changes (k vs. k+1) — do cluster boundaries shift smoothly or do entire types appear/disappear?

**Artifact**: `notebooks/edop/explore/14_band_a_typology.ipynb`. Final cluster map. Per-cluster centroid table with distinguishing features (top-N variables vs. global mean by effect size). Per-cluster exemplar list (10 basins each). Provisional cluster names (refined in Task 19). Documented k choice.

---

### Task 15 — Band C bioclimatic typology

Band C contains the temperature bimodality (F1.4) and the aridity continuum, both of which are strong structuring axes. Run after Band A as a methodological test: if the clustering doesn't recover the cold/warm split as a primary boundary, something is wrong with the preparation pipeline.

**Method**: Same procedure as Task 14, on Band C variables. Specific check: does the resulting typology have a clean cold/warm partition near the temperature-bimodality trough (~10–12°C, F1.4)? Plot cluster assignments against the temperature distribution and confirm.

**Substantive questions**: Beyond the cold/warm partition, what additional structure emerges — Mediterranean climates, monsoon regimes, polar deserts, humid tropics, cold-arid continental interiors? Does the aridity continuum produce graded clusters (each successive cluster a step along the gradient) or do clusters group around regional aridity-level "modes"? How does the typology handle the continental-interior-cold cluster (Siberia, central Asia) vs. high-altitude cold (Tibet, Andes) — are these the same bioclimatic type or different ones?

**Artifact**: `notebooks/edop/explore/15_band_c_typology.ipynb`. Same outputs as Task 14, plus a cold/warm partition confirmation plot. Cluster distinguishing features should foreground temperature, precipitation, aridity, and seasonality variables.

---

### Task 16 — Band B hydrological typology

Band B is structurally complicated by the discharge-network-position confound (F5.4): large-river basins inherit the same upstream discharge values whether they sit at a Mississippi confluence or an Amazonian floodplain, which pulls them into clusters defined by network position rather than local environment. This needs explicit handling.

**Method**: Two passes. First, run the standard k-means clustering on the full Band B variable set. Identify whether any clusters are dominated by network-position artifacts (high mean discharge, high upstream river area, mixed local environments). Second, stratify: separate basins into "large-network" (e.g., upstream contributing area > 100,000 km²) and "local-only" sub-populations, cluster each independently, and compare the two-pass typology to the single-pass result. Commit to whichever is more interpretable.

**Substantive questions**: Are the network-position-driven clusters in the single-pass result a problem (basins of clearly different local environment lumped together) or a feature (signaling that this basin is part of a major drainage system, regardless of its local conditions)? Do the local-only clusters from the stratified pass recover recognizable hydrological types (perennial humid streams, ephemeral arid washes, glacial-melt rivers, lake-dominated systems)? For each cluster, what fraction of its basins also fall in a single Band C cluster — i.e., how much hydrology is climate-determined vs. climate-independent?

**Artifact**: `notebooks/edop/explore/16_band_b_typology.ipynb`. Single-pass and stratified-pass cluster maps. Discussion of which is committed to and why. Per-cluster centroid + exemplars as in Tasks 14–15. A note on the network-position handling that future API documentation will need to explain.

---

### Task 17 — Band D anthropogenic typology

Band D has two semi-orthogonal sub-clusters (F4.4): intensity (population density, human footprint, cropland) and development (GDP, HDI). Treating them as one feature space produces compound clusters where neither axis is cleanly readable. The plan is to cluster each sub-cluster separately and report a Band D *pair* rather than a single cluster.

**Method**: Define Sub-band D-int (intensity: pop_density, human_footprint_09, cropland_extent) and Sub-band D-dev (development: gdp_avg, human_dev_idx). Cluster each sub-band independently with appropriate k. Report Band D as a pair `(D-int-x, D-dev-y)`.

A second consideration: Band D is the band where temporal scoping matters most. Static BasinATLAS Band D values reflect ~2000–2010 conditions and are not appropriate baselines for pre-industrial historical queries. The clustering in this task is on the static values; a parallel epoch-conditioned clustering using Band T HYDE values is queued as Task 22. Task 17's typology is correct for present-day signatures and for documenting the contemporary global pattern; users querying historical periods will need the HYDE-driven typology from Task 22.

**Substantive questions**: Does the intensity clustering recover recognizable patterns (industrial-developed, dense-agricultural, sparse-pastoral, wilderness)? Does the development clustering separate the developed economies from the developing ones cleanly, or are the boundaries fuzzy? Are there cells in the (D-int × D-dev) tuple grid that are empty (e.g., high-development + low-intensity) and is the empty cell itself a finding? How does the joint Band D pair correspond to the Anthromes classes that this plan replaces — does it recover comparable structure or substantively different structure?

**Artifact**: `notebooks/edop/explore/17_band_d_typology.ipynb`. Two cluster maps (D-int and D-dev). Joint occupancy table for the (D-int × D-dev) grid. Centroid + exemplars per sub-cluster. Note on temporal scoping and the queued Task 22 work.

---

### Task 18 — Cross-band sensitivity analysis

Per-band typologies should be tested for robustness across the design choices that went into them. This is the analogue of the variable-selection sensitivity work the prospectus commits to as a designed feature of signature output.

**Method**: For each per-band typology from Tasks 14–17, re-run with three perturbations: (1) basin level (L6 instead of L8); (2) normalization (quantile normalization instead of log1p+StandardScaler for the heavy-tailed variables); (3) sample restriction (basins above a minimum upstream area threshold instead of all basins). For each perturbation, compute the Adjusted Rand Index between the perturbed typology and the committed typology. Identify clusters that are stable (high ARI contribution across perturbations) versus clusters that are method-dependent (low ARI contribution).

**Substantive questions**: Which clusters are stable across all three perturbations? These have the strongest claim to capturing real environmental regimes. Which clusters appear/disappear under perturbation? These are method-dependent partitions of a continuous gradient and need to be labeled as such. Does L6 produce a different number of clusters at the indicated-k from validity indices, and what does that say about scale-dependence of the typology?

**Artifact**: `notebooks/edop/explore/18_typology_sensitivity.ipynb`. ARI matrix per band per perturbation. Per-cluster stability scores. A short note on which clusters survive as "robust types" vs. "boundary partitions" — this distinction will inform labeling in Task 19.

---

### Task 19 — Labeling: exemplars, literature, and LLM-assisted candidates

Cluster labels are not afterthoughts. A labeled typology is what the narrative layer can use; an unlabeled one is what the methods paper documents and no one cites. The goal is per-cluster labels of the form "alluvial lowland with major exotic-river hydrology" rather than "Band A cluster 4."

**Method**: Three sequential passes per cluster.

*Pass 1 — Quantitative description (mechanical)*: Centroid profile, distinguishing features, within-cluster spread, percentile range each centroid value occupies relative to the global distribution. This is purely descriptive and is computed from Tasks 14–17 outputs without subject-matter input.

*Pass 2 — Geographic/environmental labeling (data-driven)*: For each cluster, compute spatial summary statistics over named geographic units. Which ecoregions does this cluster predominantly occupy (top 5 by basin count and by area-weighted basin count)? Which biomes? Which named regions (continent, major basin, named mountain system)? A cluster that is 80% in Amazon + Congo + Ganges + Mississippi sub-basins labels itself "alluvial lowland of major continental river systems."

*Pass 3 — Historical/cultural labeling (LLM-assisted candidate generation, human selection)*: For each cluster, assemble a structured prompt containing the centroid profile (Pass 1), the geographic summary (Pass 2), 10 exemplar basins (5 most central, 5 most peripheral), and a list of geographical/historical literature terms relevant to the regions the cluster occupies. Ask the LLM (Claude or comparable) to generate 3–5 candidate labels with rationale per candidate. Human (KG, with consultation as needed) selects from the candidates or rejects all and writes the label directly. Labels are committed to a per-band glossary file.

**Substantive questions**: For each cluster, is one literature term clearly the right name, are several plausible candidates competing, or is the cluster a genuinely novel composite that needs a coined name? For clusters that don't have an established term in the literature, what's the principle — descriptive composition ("hyperarid alluvial terminus on exotic-river system"), regional anchor ("Sahel-type semi-arid grassland"), or process-defining feature ("upstream-decoupled lowland")? Are there clusters where the LLM-generated candidates systematically miss the right term — a sign that the cluster is in a region where the LLM has weaker scholarly coverage and human input is needed?

**Artifact**: `notebooks/edop/explore/19_typology_labeling.ipynb`. Per-cluster Pass 1 + Pass 2 outputs. LLM-prompt template and a transcript of the candidate-generation pass per cluster. Final per-band glossary file (`docs/edop/typology_v1.md`) with cluster identifier, name, definition, exemplars, and a one-paragraph description per cluster.

---

### Task 20 — Tuple representation and signature integration

The band-tuple `[A-x, B-y, C-z, D-w]` is the derived signature output that makes the typology usable. This task designs its representation in the API, its storage, and the auxiliary fields needed to make it interpretable.

**Method**: Define the tuple schema. Per-band cluster identifier strings (e.g., `A-3`, `B-7`) with a typology-version field (e.g., `typology_v1.0`) so future re-clustering doesn't break existing signature consumers. Add per-band centroid-distance fields as soft-membership indicators — a basin near the centroid of A-3 and a basin at the boundary with A-7 both read as `[A-3, ...]` but the centroid-distance distinguishes them. Specify wildcard query semantics for the API (`tuple=[A-3, *, *, *]` returns all basins of physiographic type A-3 regardless of other bands). Specify the JSON field positions in the signature output (top-level `tuple` field, with `tuple_distances` companion).

**Substantive questions**: Of the (k_A × k_B × k_C × k_D) total tuple cells, how many are actually populated by basins in the global L8 set? Empty cells correspond to environmental combinations that don't occur on Earth (or don't occur at the L8 grain) — this is itself a finding and should be reported. Of the populated cells, how skewed is occupancy — how many tuples are common (>1000 basins) vs. rare (<10 basins)? Common tuples can carry strong narrative descriptions; rare tuples should be flagged as unusual configurations. For trajectory analysis (UC-10 territorial expansion), what's the right way to express tuple changes over a polygon's time slices — a sequence of tuples, a transition matrix, or a single composite "trajectory tuple"?

**Artifact**: `notebooks/edop/explore/20_tuple_representation.ipynb`. Tuple-cell occupancy table. Schema specification document for the tuple field in the signature JSON. A worked example for 5–10 basins showing the tuple alongside the continuous signature, illustrating how the two representations relate.

---

### Task 21 — Validation against documented historical landscapes

The existence-proof for the typology: do well-documented historical landscapes fall into clusters whose labels match what historians of those landscapes would say?

**Method**: Assemble a list of 10–12 documented historical landscapes spanning regions and biomes: Mesopotamian alluvium (Ur, Lagash, Babylon), Yellow River loess/alluvial (Anyang, Kaifeng), Indus alluvium (Mohenjo-daro, Harappa), Mediterranean coastal (Athens, Carthage), Andean altiplano (Cuzco, Tiwanaku), Mesoamerican plateau (Teotihuacan, Tenochtitlan), Sahel pastoral (Timbuktu, Gao), monsoon Asia rice country (Hanoi, Ayutthaya), medieval Northwest European (London, Paris in their basin context), Ethiopian highland (Aksum, Lalibela), Polynesian island (representative Hawai'i, Society Islands sites). For each, identify the L8 basin, retrieve the tuple, and check against documented characterizations from the regional historical/geographical literature.

**Substantive questions**: For each landscape, does the tuple match the historical characterization? Where there's mismatch, is the mismatch in the typology (cluster boundary in the wrong place), in the labels (cluster identity is right but the name doesn't communicate), or in the historical interpretation (the literature characterization itself is contested)? Are there landscapes where the tuple is interpretable but the historical characterization is in a vocabulary the typology doesn't capture (cultural-historical terms vs. environmental terms)? How many of the 10–12 landscapes pass cleanly, how many require refinement, and what does the residual say about gaps in the typology?

**Artifact**: `notebooks/edop/explore/21_typology_validation.ipynb`. Per-landscape table: landscape, basin id, tuple, literature characterization, agreement assessment. A short narrative writeup of the validation pass suitable for inclusion in the methods paper. Recommendations for typology refinement, if any.

---

### Task 22 (deferred) — Band T data-driven HYDE typology

The static Band D typology in Task 17 is correct for present-day queries but inappropriate for pre-industrial historical queries. A parallel typology using Band T HYDE land-use fields (cropland, grazing, urban, population density) at queried epochs replaces the Anthromes role for historical anthropogenic characterization.

**Specifics to be designed before notebook implementation**, after Tasks 13–21 are complete and the typology methodology is stable. Likely shape: per-epoch clustering of HYDE-aggregated basin values, with the central design question being whether to (a) cluster on per-basin time-averaged HYDE and express each (basin, epoch) as position relative to those centroids, (b) cluster on the pooled (basin × epoch) population and accept that types are time-varying, or (c) cluster per-epoch separately and track basin movement between typologies. Approach (a) is the closest analogue to Tasks 14–17 and is the recommended starting point.

The output is an additional tuple position — `[A-x, B-y, C-z, D-w(static), T-q(epoch)]` — or, equivalently, a temporal-aware Band D position that replaces the static one for historical queries.

**Artifact target**: `notebooks/edop/explore/22_band_t_typology.ipynb` (specifics pending).

---

## Cross-Task Synthesis Questions

These are not separate tasks but synthesis questions to consider once 13–21 are complete:

**Tuple cell occupancy structure**: The empty cells in the tuple grid are environmental combinations that don't occur on Earth (or aren't sampled at L8). What does the structure of empty cells say about which environmental dimensions are coupled vs. independent? If `[A-3, *, C-2, *]` is heavily populated for many B and D values but `[A-3, B-7, C-2, *]` is empty across all D, that's a coupling between Band A and Band B that the per-band clustering treated as independent.

**Robust-types vs. partition-cuts in the labels**: Task 18 distinguishes clusters that are stable across perturbations from clusters that are method-dependent partitions of a smooth gradient. The labels should communicate this distinction. Robust types can carry strong claims ("this is an alluvial lowland system"); partition-cut clusters need hedged labels ("this is in the wetter end of the temperate-continental gradient"). The narrative layer's use of labels needs to respect this distinction.

**Typology vs. signature in the methods paper**: The continuous signature and the per-band typology are two views of the same underlying environmental data. The paper should explain when each is the appropriate analytical instrument — typology for situating, comparing, and querying; signature for fine-grained difference and similarity computation. Each has use cases; neither replaces the other.

---

## Cluster Numbering and Typology Versioning

k-means returns clusters with arbitrary integer labels in run order. For the tuple to function as a stable identifier across signature versions, cluster numbers must be assigned with intention and frozen. Recommended convention: cluster numbers within each band ordered by frequency (cluster 1 most common globally, cluster N rarest). Documented in the per-band glossary. Frozen in `typology_v1.0` and not changed except by explicit version bump.

Re-running clustering with different parameters and getting the same names with different numbers would be a versioning disaster. The API should always return the typology-version field alongside the tuple, and a typology version table should record what each version's cluster numbers and labels are. Future versions are additive (new versions exposed alongside old, with translation tables) until a deprecation policy is established.

This is the same discipline that the variable codebook receives. The typology is a long-lived contract with downstream users and earns the same care.

---

## What NOT to Do During Typology Development

**Don't tune cluster count or variable selection against a cultural-correspondence target.** Same guardrail as the static and Band T phases. The temptation is stronger here because typology is closer to where cultural questions live, and there's a real risk of producing clusters that look good against D-PLACE because they were quietly selected to. The typology should be defensible as an instrument for environmental characterization on its own terms. Cultural correspondence is a downstream test, not an optimization criterion.

**Don't over-name the clusters.** Each cluster gets a label that captures its dominant character, not a label that aspires to comprehensiveness. "Alluvial lowland in arid context" is useful; "alluvial lowland in arid context with significant exotic-river inflow and high local human concentration since the third millennium BCE" is a paragraph pretending to be a label, and it's wrong about most basins in the cluster. Labels are short; descriptions are long; documentation distinguishes them.

**Don't treat method-dependent partition cuts as natural types.** Task 18's sensitivity analysis exists for this reason. A cluster that exists at L8 with one normalization and disappears at L6 or with quantile normalization is a useful descriptive partition, not a natural environmental type. Labels for such clusters need hedging vocabulary; downstream uses (correspondence testing, narrative generation) need to be aware which kind of cluster they're working with.

**Don't propagate cluster identity into Band D variable selection.** F5.5 raised the circularity issue: clustering on Band D variables and then using the resulting types to interpret human presence is using human presence to define environmental types and then reading human presence off the types. The typology in this plan separates Band D from Bands A+B+C cleanly; Band D clusters describe present-day human geography conditional on the environment, and that distinction matters for how the tuple is used in correspondence work.

**Don't lock the typology before Task 21 validation.** The validation pass against documented historical landscapes is the existence proof. If multiple landscapes fail to fit clusters whose labels match historical characterization, that's evidence the typology needs revision before being committed to as `v1.0`. The version freeze comes after validation, not before.

---

## Directory Conventions

Following Phases 1 and 2:

```
notebooks/edop/explore/
  13_typology_preparation.ipynb
  14_band_a_typology.ipynb
  15_band_c_typology.ipynb
  16_band_b_typology.ipynb
  17_band_d_typology.ipynb
  18_typology_sensitivity.ipynb
  19_typology_labeling.ipynb
  20_tuple_representation.ipynb
  21_typology_validation.ipynb
  22_band_t_typology.ipynb         (deferred, specifics TBD)

output/edop/explore/
  13_*.csv  13_*.png
  ...

docs/edop/
  typology_v1.md                   (per-band glossary; output of Task 19)

logs/exploration_log.md            (continuing from Task 11)
```

Each task entry in the log follows the existing convention: Date · Task · Method · Finding · Implication.

---

*Decisions taken in this plan: Anthromes (formerly Task 12) replaced by data-driven per-band typology; per-band rather than composite clustering; k-means as committed method with HDBSCAN as diagnostic; sequential Bands A → C → B → D ordering; band-tuple as derived signature output with typology-version field; three-pass labeling (quantitative, geographic, LLM-assisted historical) with human selection in the final pass; existence-proof validation against 10–12 documented historical landscapes before version freeze. Sample sizes, k values, and stratification thresholds to be set empirically in Task 13 from validity-index analysis rather than fixed in advance.*
