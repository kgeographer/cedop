# EDOP: Environmental Dimensions of Place
*Prospectus — updated April 2026. Seeded from working outline v3 (February 2026); prior additions and refinements marked* **[NEW]** *or* **[REVISED]***

*EDOP is a research program developed by Karl Grossner under the aegis of the Institute for Spatial History Innovation (ISHI), University of Pittsburgh, directed by Ruth Mostern. Development is supported by ISHI beginning April 2026.*

---

## 1. Overview

Environmental Dimensions of Place (EDOP) is a computational service for generating standardized, reproducible environmental "signatures" for geographic locations. The core objective is to operationalize environmental context in a form suitable for comparative analysis, linking and integration with cultural datasets, and exploratory modeling of relationships between environmental patterns and human phenomena.

EDOP is designed as infrastructure: a generalizable method for computing environmental descriptors of place at multiple spatial scales. A working prototype has been implemented and is publicly accessible. This prospectus describes the full design intent; the current prototype implements a working subset. Sections describing capabilities not yet implemented are marked with an asterisk [*].

EDOP is one module of the broader **Computing Place** research initiative, paired with a **CDOP** (Cultural Dimensions of Place) module. The two are related but distinct in scope: EDOP's use of cultural datasets (settlement records, ethnographic societies, historical polities) is instrumental — these serve as external probes for validating environmental signature quality, not as objects of cultural inquiry in themselves. CDOP addresses the cultural inquiry directly: investigating relationships between cultural practices and environmental settings. Development of the two modules proceeds at independent paces.

---

## 2. Conceptual Premise

EDOP takes as a formative premise that each inhabited area of the Earth lies within or is itself a cultural landscape, in much the same sense described by geographer Carl Sauer a century ago (1925). In this framing, physical geography and ecological characteristics (i.e. landscape) are the setting for human activity (i.e. culture), in a continually evolving bi-directional relationship. This close association is well-known to environmental historians, archaeologists, and many others studying the past in the humanities and social sciences. That said, environmental context is typically invoked qualitatively in cultural, historical, and archaeological research.

EDOP treats environmental context as a computable, multidimensional construct derived from globally consistent geospatial datasets. In this framework, place descriptions include a computable vector of environmental dimensions extracted from standardized environmental variables. These dimensions include, for example:

- Hydrological indicators
- Climate variables
- Terrain metrics
- Land cover or ecoregional classification
- Bioclimatic indices

The resulting "signature" is not a classification label but a structured representation of environmental conditions. These can in turn be expressed in natural language summaries, as required for some applications.

**[NEW]** EDOP is positioned in explicit contrast to commercial geographic enrichment services (e.g. Esri's ArcGIS Enrichment Service), which augment point locations with attribute values from overlapping layers but do not consider conditions at a distance or the directional, process-mediated flows that connect a location to its surroundings. EDOP's goal is *process-aware environmental characterization* — what a place experiences, not merely what surrounds it. This distinction constitutes a methodological novelty relative to current commercial and open-source tools.

---

## 3. Units of Analysis

EDOP accommodates two primary input types:

### A. Area-based units [*]

For polygons (e.g. administrative regions, historical polities, archaeological territories), the environmental signature is computed across the defined spatial extent using area-weighted aggregation over hydrologic basin units (HydroATLAS; level 08, ~190k sub-basins).

**[REVISED]** Rather than returning only an area-weighted mean vector, EDOP returns a *distribution* over intersecting basin signatures — including quantiles of each variable and, optionally, a clustering of intersecting basins into environmental sub-zones. A single summary vector remains available as a convenience, but is explicitly flagged as a lossy reduction. This preserves within-unit environmental variation (e.g. north/south gradients, highland/lowland contrasts) that is often of direct historical interest and is lost in scalar summaries.

### B. Point-based locations

For point locations (e.g. settlements, heritage sites, ethnographic societies), a neighborhood must be defined explicitly [*]. The default neighborhood model uses hydrologic basin containment at a specified HydroATLAS level, which provides physically grounded, globally consistent spatial envelopes. Alternative models include:

- Fixed-radius buffers
- Ecological zones
- Other analytically justified spatial envelopes

**[REVISED]** Basin level selection is a methodological choice with direct consequences for signature content. Level 10 (small sub-basins, typically tens of km²) is the appropriate default for point inputs; level 08 is more appropriate for larger area inputs. The scale-sensitivity of any given signature — how much it changes across basin levels — is itself an informative property of the location, particularly for settlements at environmental boundaries (confluences, piedmont edges, coastal zones), and is reported alongside the signature.

Neighborhood definition is treated as a transparent, swappable parameter rather than a technical default. Edge cases — confluence cities, coastal settlements, polities spanning major basin boundaries — are documented explicitly as instances requiring particular care.

**[NEW]** A systematic scale sensitivity study is planned as a first analytical output, examining how signatures vary across basin levels for a set of representative point locations. This constitutes a natural first paper contribution, with methodological implications for all downstream uses of the service.

---

## 4. Variable Selection and Dimensional Structure

EDOP relies on globally available, spatially consistent environmental datasets. Primary sources include HydroATLAS (hydrological and climate variables at multiple basin levels), digital elevation models (terrain metrics), and established ecoregion frameworks (One Earth, WWF). Because such datasets contain hundreds of potentially collinear variables, the service includes:

- Statistical screening to reduce redundancy
- Dimensionality reduction (e.g. principal components analysis or related methods)
- Optional banding or stratification for interpretability

The goal is a compact, interpretable environmental signature that preserves meaningful environmental gradients — where "meaningful" is operationally defined through validation against independent signals (e.g. semantic similarity of place descriptions and expert evaluation) rather than assumed from the variable set alone.

**[NEW]** HydroATLAS provides, for most variable categories, both a local value (`s`: conditions within the sub-basin only) and an upstream catchment value (`u`: area-weighted accumulation across all upstream contributing basins). This local/upstream duality is a first-class architectural feature of EDOP signatures, not merely a data detail. The contrast between `s` and `u` for a given variable is itself environmentally meaningful: a settlement where local aridity (`s`) diverges sharply from upstream catchment aridity (`u`) occupies a qualitatively different environmental position than one where the two converge.

**[NEW]** Beyond the pre-computed `u` values, the HydroATLAS basin network encodes explicit upstream-downstream topology via `hybas_id` and `next_down` fields, which form a crawlable directed acyclic graph. This enables computation of *distance-stratified upstream profiles* not available in the standard dataset — for instance, near-upstream aggregates (within N hops or K km of flow distance) weighted to reflect proximity rather than contributing area. The `next_sink` field (terminal drainage outlet) provides a free macro-watershed partition key useful for similarity queries and traversal validation. Distance-weighted upstream profiling is designated as a named research extension (see Section 7).

---

## 5. Outputs

For any given place, EDOP produces:

- A structured environmental signature vector, including local (`s`) and upstream (`u`) values for applicable variables **[REVISED]**
- A three-tier spatial stratification: local, near-upstream, full-upstream, for key variables [*] **[NEW]**
- Summary statistics of underlying variables [*]
- Dimension scores [*]
- Optional categorical banding
- Machine-readable output suitable for downstream analysis
- **[NEW]** A brief natural language interpretation of the signature, generated by LLM from the structured values and the signature algorithm's parameters, suitable for non-specialist users of gazetteer and cultural heritage platforms [*]

---

## 6. Broader Research Context

EDOP is conceived as one component of a Computing Place framework, paired with a Cultural Dimensions of Place (CDOP) module. Together they draw on structured cultural datasets (e.g. ethnographic variables, heritage classifications, textual corpora) to enable systematic investigation of questions such as:

- Do cultural traits cluster in particular environmental regimes?
- How do environmental gradients correspond to linguistic, social, or economic variation?
- How stable are environmental signatures across historical change?

Environmental signatures define bounded possibility spaces — what natural settings afford and constrain — while cultural agency determines which possibilities are realized. The Computing Place framework supports comparative analysis without asserting causation.

---

## 7. Methodological Challenges

Key challenges include:

- **Scale and neighborhood definition:** Basin level selection and boundary sensitivity (MAUP) require systematic evaluation, not assumed defaults. Scale-sensitivity reporting is a designed feature of the signature output. **[REVISED]**

- **Local vs. upstream environmental character:** The `s`/`u` duality in HydroATLAS introduces a structured form of spatial context that must be handled explicitly in signature design and communicated clearly in outputs. **[NEW]**

- **Distance-weighted upstream exposure [*]:** Pre-computed `u` values weight upstream basins by contributing area, not flow distance. A location's actual environmental exposure to upstream conditions attenuates with distance, and different processes (water quality, sediment, temperature) have different characteristic decay distances. Implementing process-specific, distance-weighted upstream profiles via network traversal is a designated research extension, suitable for collaboration with a GIScience partner or graduate student. This constitutes the most direct response to Goodchild's observation about exposome modeling and action-at-a-distance. For a POC, topological depth from the recursive catchment traversal (steps upstream in the `next_sink` graph) provides a tractable proxy for distance decay; exponential decay over depth (`exp(-λ × depth)`) is preferable to inverse-depth and introduces a tunable parameter suitable for sensitivity analysis. Metric flow distance — cumulative segment length along the drainage network — is the rigorous version and is achievable via the HydroRIVERS polyline dataset (currently loaded but not yet integrated into signature computation). HydroRIVERS also carries channel-level attributes (discharge estimates, upstream drainage area, river length) that represent a distinct signature dimension — the river system itself, not merely the surrounding basin envelope — and constitute a natural second-phase enrichment of the signature. **[NEW]**

- **Process-type typology for spatial influence [*]:** Following Goodchild (pers. comm., 2026), environmental influence on a place operates through distinct process geometries — hydrological (network-constrained, upstream), atmospheric (directional, Euclidean decay), acoustic (Euclidean, rapid decay), social/acquaintance (network-structured). A full exposome model would implement separate influence functions for each process type. The hydrological case is the most tractable given available data and is the designated first implementation. **[NEW]**

- **Spatial autocorrelation:** Globally gridded environmental variables are inherently spatially autocorrelated, which affects both variable selection and the validity of downstream comparative analysis. This requires explicit treatment rather than acknowledgment in passing.

- **Variable selection bias:** The choice of input variables shapes what environmental gradients are recoverable, independent of dimensionality reduction.

- **Interpretability of reduced dimensions:** PCA components are not inherently interpretable; validation against independent signals is needed to confirm that reduced dimensions correspond to environmentally meaningful gradients.

- **Temporal mismatch:** Contemporary environmental datasets are used as baselines for analyses that are often historical. Physiographic features (drainage networks, terrain, climate regimes) are largely stable over centuries to millennia and defensible as historical baselines, while anthropogenically sensitive variables (land cover, human pressure indices) require explicit qualification and period-specific handling.

- **Risk of reifying environmental context as causal:** Addressed through the bounded possibility space framing, but requiring vigilance in documentation and communication.

---

## 8. Intended Positioning

EDOP is proposed as:

- A service layer usable by digital humanities and cultural heritage platforms
- A methodological contribution to GIScience and spatial analysis
- A research tool for investigating environment–culture relationships

**[NEW]** EDOP's novelty relative to existing geographic enrichment tools lies in three features: (1) multi-scale, basin-level environmental characterization with explicit uncertainty and variation reporting; (2) structural use of local/upstream duality as a signature component; and (3) a designed pathway toward process-aware, distance-weighted environmental exposure modeling. The first is immediately implementable; the second is partially implemented; the third is a named research agenda. Together they constitute a coherent and extensible contribution that is not replicated by current commercial or open tools.

In short, EDOP is not a classificatory scheme but a computational infrastructure for environmental characterization. Credibility in both GIScience and humanities venues requires that methodological assumptions be explicit, documented, and subject to sensitivity testing — a standard the project aims to meet.

---

## 9. Signature Validation via Settlement Correspondence **[NEW]**

A central methodological question — whether the environmental signatures are capturing something real about place, or are artifacts of variable selection and dimensionality reduction — requires external validation. One principled approach exploits the known correspondence between environmental conditions and human settlement patterns across deep history.

The logic is explicitly instrumental rather than deterministic: if EDOP signatures encode meaningful environmental information, then basins with signatures similar to known major settlement hearths should themselves appear in the historical record as settled or environmentally significant. Failure of this correspondence is diagnostic — it suggests the signature is missing dimensions that mattered to settlement; success increases confidence in signature construction. The model is being used as a *probe for the data*, not as a claim about behavioral causation.

This validation approach also provides a principled objective function for parameter tuning. Currently, attribute selection and basin scale choices are reasoned but not optimized against any criterion. With settlement correspondence as an external signal, questions become testable: Does adding a given variable class improve correspondence? Does changing basin level (HydroATLAS Pfafstetter level 08 vs. 10) sharpen or blur the signal? Does distance-decay weighting of upstream contributions change which basins surface as high-potential? Each is a sensitivity experiment with a measurable outcome.

**Candidate validation datasets:**

- *Early urban hearths* (unambiguous positives): A small set of well-documented river-basin civilizations (Fertile Crescent, Indus, Yellow River, Niger Inland Delta, etc.) provides high-confidence basin-level positive cases with minimal modern confounding, as all predate industrial infrastructure. The Reba et al. historical urban population dataset (6,000 years of georeferenced urban centers) offers a broader and more global positive-case set.
- *Seshat/Cliopatria polities*: The ~15,690 temporally scoped historical polities offer graduated complexity scores that could be correlated with signature characteristics across a complexity spectrum, not just empire-scale cases. This extends validation from binary (settled/unsettled) to ordinal (complexity level), enabling richer analysis.
- *D-PLACE ethnographic societies*: The 1,291 documented societies provide the lower end of the complexity spectrum and link environmental signatures to specific cultural practices and subsistence strategies.

Modern population rasters (e.g. Natural Earth urban coverage) are less suitable as primary validation because modern settlement reflects path dependency, industrial infrastructure, and political history as much as environmental suitability. They may be useful as a *negative filter* — basins heavily urbanized today but not historically could be flagged for careful handling, since development may have altered their hydrological signatures.

The unit-of-analysis question must be resolved before any validation experiment: a settlement point falls in one basin, but the settlement system it anchored typically spread across several. The appropriate unit is likely the upstream catchment — the full set of basins draining through or near the settlement's outlet point — aggregated by the distance-weighted scheme described in Section 7. This alignment between validation design and signature construction is methodologically coherent and should be made explicit.

---

## 10. Basin Neighborhoods and Drainage Topology **[NEW]**

The `next_sink` field in the HydroATLAS basin table (`basin08`) identifies the downstream receiving basin for each sub-basin, forming a directed acyclic graph over the ~190,000 basin units. This topology enables principled spatial grouping that follows actual hydrological connectivity rather than arbitrary spatial buffers — which is the appropriate kind of neighborhood for a service grounded in process-aware environmental characterization.

Three neighborhood types are directly derivable from the graph:

**Immediate siblings:** All basins whose `next_sink` points to the same outlet — hydrological tributaries sharing a confluence. Retrievable with a single non-recursive query.

**Upstream catchment:** Recursive traversal of all basins that eventually drain through a given pour point. This reconstructs the full watershed above any outlet and corresponds most closely to the environmental territory of a river-basin civilization. In PostgreSQL this is a recursive CTE:

```sql
WITH RECURSIVE upstream AS (
  SELECT hybas_id, next_sink, 1 AS depth
  FROM basin08
  WHERE hybas_id = :target_id
  UNION ALL
  SELECT b.hybas_id, b.next_sink, u.depth + 1
  FROM basin08 b
  JOIN upstream u ON b.next_sink = u.hybas_id
)
SELECT * FROM upstream;
```

The `depth` counter (steps upstream from the pour point) serves as the basis for distance-decay weighting of upstream signature contributions. It is a topological rather than metric measure; metric flow distance requires routing along HydroRIVERS polylines, which is the designated rigorous extension.

**Downstream corridor:** Following `next_sink` chains from a basin toward the ocean reconstructs the river system membership — relevant for queries about connectivity and downstream exposure.

The `next_sink` terminal field additionally partitions all basins into macro-watershed groups at no computational cost, useful as a similarity-query filter and traversal sanity check.

For signature aggregation over an upstream catchment, distance-weighted averaging using normalized inverse-depth or exponential decay weights (`exp(-λ × depth)`) is the POC implementation. The decay parameter `λ` is tunable and its sensitivity to settlement correspondence outcomes constitutes a research experiment. Area weighting alone — the implicit assumption in HydroATLAS pre-computed `u` values — treats a headwater basin identically to an immediately upstream neighbor, which is the assumption this framework explicitly relaxes.

Spot-checking a known river system (e.g., retrieving the full upstream catchment for the Tigris-Euphrates outlet basin) before building aggregation logic is recommended to calibrate expected catchment sizes at level 08.

---

*Sauer, C. O. (1925). The morphology of landscape. In Foundation Papers in Landscape Ecology (2007), 36–70.*
