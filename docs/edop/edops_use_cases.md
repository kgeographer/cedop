# EDOPS Use Cases
*Draft — April 2026*

Environmental Dimensions of Place Service (EDOPS) is a computational service for generating structured environmental "signatures" for geographic locations. This document enumerates the primary use cases that drive service design. Use case requirements determine the signature algorithm, neighborhood models, output format, and API design — not the reverse.

---

## Signature Format

Signatures are serialized as **JSON documents**, not flat vectors. The signature is structured — named variable groups, local/upstream pairs, coastality component, neighborhood metadata, optional narrative — and is self-describing: a consumer can interpret values without external schema documentation. Similarity and comparison operations derive a vector from the JSON at query time, selecting whichever fields are relevant to the task at hand.

---

## Neighborhood

For point inputs, "neighborhood" is an explicit, required-or-defaulted parameter specifying the spatial extent over which the signature is computed. It is not a hidden technical default. Candidate types:

- `basin` — containing basin at HydroATLAS level L (current behavior; fast, MAUP-sensitive)
- `buffer` — fixed-radius spatial buffer, area-weighted aggregation over intersecting basins (isotropic; stable and comparable across sites)
- `upstream` — upstream catchment via recursive `next_down` traversal, exponential distance-decay weighted (process-aware; size varies with location)
- `threeTier` — composite: local (`s` values), near-upstream (N-hop decay aggregate), full-upstream (`u` values); the full picture

For polygon inputs, the polygon boundary **is** the neighborhood; the design question shifts to how intersecting basins are aggregated (mean vector, distribution, or sub-zone clustering).

The aspirational default for point inputs is `threeTier`; the current implemented default is `basin`.

---

## Coastality

Marine-outlet connectivity is a first-class signature component, not an outlier correction. It captures what a place can *reach and send* via the downstream network — a process geometry distinct from upstream exposure (what a place *receives*). Proximity to a marine outlet can constitute a critical environmental dimension for coastal and riverine locations, compensating for weak local or upstream conditions.

Coastality fields in the signature:
- **Outlet type**: `exorheic` (marine-connected) or `endorheic` (landlocked — no marine connection)
- **Flow distance to outlet** (`dist_sink`): for exorheic basins; raw value from BasinATLAS, likely log-transformed for display
- **Outlet character** *(future)*: delta, estuary, open coast

Note: endorheic basins have `dist_sink = 0` in the data but effectively infinite coastality distance; they must be handled explicitly throughout.

---

## Use Cases

### UC-1 · Single-place environmental profile
*"What did Ur's environment afford and constrain?"*

A user submits a point location (by name or coordinates) and receives a structured environmental signature characterizing the place's environmental setting. The upstream component — what flows to and through the place — is part of the basic answer, not an advanced option. Coastality is always included.

**Inputs:** point (name or coordinates), neighborhood type + parameters, band selection, narrative flag
**Outputs:** JSON signature with local/upstream pairs, coastality component, neighborhood metadata; optional natural language summary
**Users:** historians, archaeologists, heritage professionals, anyone situating a place in environmental context
**Design notes:** Narrative summary must work for non-specialists. Band selection allows temporal scoping (e.g. suppress Group D anthropogenic variables for pre-industrial queries).

---

### UC-2 · Pairwise or multi-place comparison
*"How different were Ur and Mohenjo-daro environmentally, and does that help explain their contrasting trajectories?"*

A user submits two or more places and receives their signatures side by side, with a computed difference or distance metric. The comparison is exploratory — the user brings historical knowledge of the trajectories and uses the signature contrast as a structured prompt for interpretation.

**Inputs:** 2–N points, shared neighborhood parameters, band selection
**Outputs:** signatures per place, pairwise distance/difference metrics, optional narrative contrast
**Users:** comparative historians, archaeologists
**Design notes:** Distance metric must be well-defined and interpretable; field-level differences (not just aggregate distance) are needed for substantive interpretation. Band selection matters: Group A/B for deep history, Group C/D for more recent periods.

---

### UC-3 · Find environmentally similar places
*"What other known settlements had environments most like Ur's?"*

A user submits one place (or a signature directly) and receives a ranked list of places from a target corpus with the most similar signatures. Generates hypotheses, surfaces analogues, and clarifies what is distinctive about the query place.

**Inputs:** one place or signature, corpus selection (Reba et al., D-PLACE, WHG, all basins), similarity metric, band/field selection, N results
**Outputs:** ranked list with similarity scores and brief per-place signature summaries
**Users:** historians forming hypotheses, archaeologists seeking analogues, researchers exploring environmental clusters
**Design notes:** Corpus selection is a meaningful research choice, not a UI detail. Similarity is computed over a field subset derived from the JSON — which fields participate is an explicit parameter.

---

### UC-4 · Cultural-environmental correlation study
*"Do societies with high-god religions cluster in particular environmental regimes?"*

A researcher submits a cultural dataset (D-PLACE societies, Seshat/Cliopatria polities) with a target cultural attribute and receives environmental signatures per entity, enabling correlation or clustering across environmental and cultural dimensions.

**Inputs:** cultural dataset + attribute, shared neighborhood parameters, band/field selection
**Outputs:** signature per entity, correlation statistics or cluster assignments, visualization-ready output
**Users:** researchers in spatial humanities, historical ecology, cultural anthropology; primary CDOP↔EDOP use case
**Design notes:** Consistency and reproducibility of signatures across thousands of points is paramount — neighborhood must be uniformly defined. Batch processing mode needed; single-point latency acceptable for inspection, not for corpus runs.

---

### UC-5 · Regional or polity environmental profile
*"What did the Fertile Crescent offer as a whole, and how variable was it internally?"*

A user submits a polygon (historical territory, study area, administrative region) and receives a signature characterizing the region's environmental conditions, including within-region variation. A scalar summary is available but explicitly flagged as lossy.

**Inputs:** polygon geometry, band selection, aggregation mode (mean, distribution, sub-zones)
**Outputs:** mean/median signature vector; quantile distributions per variable; optional sub-zone clustering of intersecting basins
**Users:** historians working at regional scale, archaeologists, cultural geographers
**Design notes:** The polygon *is* the neighborhood — aggregation logic replaces neighborhood parameter. Whether the polygon corresponds to a natural watershed or cuts across basins arbitrarily is itself informative and should be reported.

---

### UC-6 · Settlement suitability / basin ranking
*"Which basins globally most resemble the known early urban hearths?"*

Given a set of known settlement basins as positive cases, rank all basins by signature similarity to the input set. Used for validation of signature quality and for generating archaeological hypotheses about understudied regions.

**Inputs:** one or more seed basins (or signatures), field/band selection, optional geographic filter
**Outputs:** ranked list of basins with similarity scores; optionally filtered to a study region
**Users:** researchers running validation experiments, archaeologists prospecting for unexcavated sites
**Design notes:** Computationally heavier — likely an offline/batch operation rather than a real-time endpoint. This is also the primary external validation use case for signature quality (settlement correspondence as objective function for parameter tuning).

---

### UC-7 · Historical baseline query
*"What was this place like before industrialization?"*

A user requests a signature appropriate for a pre-industrial historical period, suppressing or flagging variables that reflect modern anthropogenic conditions.

**Inputs:** point, period (broad: ancient / medieval / early modern / modern), neighborhood parameters
**Outputs:** signature with Group D variables suppressed or qualified; explicit documentation of temporal assumptions
**Users:** historians, archaeologists reasoning about past conditions from contemporary datasets
**Design notes:** This is primarily a band-selection and documentation problem, not a data problem. Physiographic and hydroclimatic variables (Groups A/B) are defensible as historical baselines; land cover and human pressure indices (Group D) require explicit qualification.

---

### UC-8 · Platform or API integration
*"I'm building a WHG place page — give me a compact environmental context for this location."*

An external platform calls EDOPS on behalf of its users, passing a geometry or identifier and receiving a compact, interpretable environmental profile suitable for display to non-specialists.

**Inputs:** coordinates or geometry, optional verbosity level
**Outputs:** compact JSON signature + brief natural language summary; schema-stable, versioned
**Users:** platform developers (WHG, heritage databases, DH tools); end users of those platforms
**Design notes:** Response must be fast and compact. Narrative summary is essential — this audience will not interpret raw values. API stability and versioning matter for institutional integration.

---

### UC-9 · Ecoregion situating and typicality
*"Is this place typical of its ecoregion, or an outlier within it?"*

A user receives the ecoregion membership of a place alongside a typicality score: how well does its signature match the environmental centroid of that ecoregion? Outlier status — being environmentally anomalous within a biome — can itself be historically significant.

**Inputs:** point, neighborhood parameters
**Outputs:** ecoregion membership (OneEarth hierarchy), typicality score, brief characterization of how the place departs from the regional norm
**Users:** ecologists, biogeographers, historians using ecoregion as a reference framework
**Design notes:** Requires a characterization of each ecoregion's environmental distribution as a precomputed reference. Outlier detection is the analytically interesting output.

---

### UC-10 · Territorial expansion and environmental trajectory
*"As the Northern Song expanded southward between 962 and 980 CE, did the environmental profile of the territory shift systematically toward wetter conditions?"*

A researcher submits a sequence of polity polygons at different dates — the territory as it existed at each time slice — and receives an environmental signature per slice. Because the underlying environmental data is a static baseline, what changes across slices is the *territory*, not the environment itself. The analytically interesting output is how the aggregate signature evolves as the polity expands or contracts: which environmental dimensions shift, and in what direction.

In the Song example, three time slices (962, 970, 980 CE) show the aridity index distribution across the expanding territory shifting dramatically southward and toward higher moisture availability — physical evidence legible as territorial motivation, or at minimum as environmental consequence of expansion choices.

**Inputs:** ordered sequence of polygon geometries with associated dates, variable or band selection, aggregation mode
**Outputs:** signature per time slice (as in UC-5); difference metrics between slices; time-series visualization of selected variables across the sequence
**Users:** historians studying territorial expansion, contraction, or reorganization; environmental historians; archaeologists tracking settlement system change
**Design notes:** The polity geometry sequence is the primary data challenge — requires temporally scoped polygon datasets (Cliopatria/Seshat have `fromyear`/`toyear` with geometries). The signature algorithm is unchanged from UC-5; what is new is the temporal sequencing and diff output. A small number of time slices (3–5) is the typical research case, not a continuous time series. This is the most compelling demonstrator use case for a humanities audience: it frames an environmental argument in terms a historian already thinks in.

---

## Design Implications Summary

| Requirement | Driven by |
|---|---|
| JSON signature format (not flat vector) | All UCs — structured, self-describing output |
| Neighborhood as explicit parameter | UC-1 through UC-4 |
| Upstream component in basic signature | UC-1 (foundational, not advanced) |
| Coastality as first-class signature field | UC-1, UC-3, UC-8 |
| Band/field selection as query parameter | UC-2, UC-4, UC-7 |
| Polygon input mode | UC-5, UC-10 |
| Temporal polygon sequence (time-sliced polity) | UC-10 |
| Batch processing mode | UC-4, UC-6 |
| Natural language summary | UC-1, UC-8 |
| Similarity metric over JSON field subset | UC-3, UC-6 |
| Ecoregion typicality scoring | UC-9 |
