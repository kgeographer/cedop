Title: Computing Place: Toward Systematic Environmental Characterization for Cultural Research
Date: 2026-04-04
Slug: computing-place-prospectus
Summary: A full description of the Computing Place initiative — EDOP environmental signatures, CDOP cultural dimensions, methodology, validation approach, and current state as of April 2026.
Category: research
Tags: place, landscape, culture, environment, geohumanities, EDOP, CDOP
Author: Karl Grossner
Status: published

## 1. Introduction

"One has not fully understood the nature of an area until one has learned to see it as an organic unit, to comprehend land and life in terms of each other."

-- Carl Sauer (1925). *Morphology of Landscape*.

The Computing Place initiative introduced here was originally motivated by geographer Carl Sauer's canonical paper *Morphology of Landscape*. In it, he asserted that "...area or landscape is the field of Geography, because it is a naively given important section of reality, not a sophisticated thesis." He introduced to American geographers the term "cultural landscape" as a translation of "Kulturlandschaft," a conceptual framing well-known to German geographers at the time. Its content, he wrote, is found "...in the physical qualities of area that are significant to man and in the forms of his use of the area, in facts of physical background and facts of human culture." But Sauer sought to constrain the discipline to one direction of analysis: "...we are not concerned in geography with the energy, customs, or beliefs of man but with man's record upon the landscape."

<img src="{static}/images/CP_logo.jpg" style="height:180px; float:right; margin:0 0 1em 1.5em;">I wondered what Sauer might have done if some of the now common technological tools and methods had been available to him, and I thought that given sufficient "facts of physical background and facts of human culture," both directions of analysis are possible and warranted. Sauer did allow that the relations between environment and culture are bi-directional, but left the cultural elements to anthropology. Generously, but I think short-sightedly.

Historians, archaeologists, and anthropologists invoke environmental context constantly, but almost always qualitatively. What would it mean to make those invocations in some degree computable and reproducible? Computing Place envisions digital infrastructure--data and software tools--that supports both directions of inquiry.

Cultural analysis with a geographic lens in this context requires a solid environmental data foundation. Computing Place development is organized around two components, *Environmental Dimensions of Place* (EDOP) and *Cultural Dimensions of Place* (CDOP). EDOP is naturally the first priority because the environmental foundation must precede the cultural analysis. Most of what follows describes work in progress towards an EDOP "signature," computable for any given terrestrial location. The overall project is designed to surface patterns and expose what can and cannot be characterized computationally, without presupposing results.

## 2. What "computing place" means, and what it doesn't

The subject matter of Computing Place is indeed well-trodden intellectual terrain. Scholars in history, anthropology, archaeology, environmental history, historical ecology, and geography have long studied the relations between environment and culture. Computing Place aims at novel methodology--to make many of those relations formally computable and develop tools and features for an accessible and open web platform. EDOP signatures are reproducible environmental characterizations that can be compared systematically across thousands of locations and time periods, linked to cultural datasets from the CDOP component, and tested against independent evidence.

While there are clear relations between cultural phenomena of all kinds and their environmental settings, the Computing Place project deliberately steers clear of environmental determinism. An underlying premise is that while environment generally defines what activities a geographic area affords and constrains, culture determines which possibilities are realized.

## 3. The environmental signature concept

### 3.1 Signature structure

For any terrestrial location, the EDOP service delivers a structured set of environmental values drawn from multiple global datasets. The core source is the <a href="https://www.hydrosheds.org/hydroatlas" target="_blank">Global BasinATLAS</a> dataset, which compiles hydro-environmental attributes in a consistent, globally applicable format. In the initial prototype 47 of BasinATLAS's 281 attributes are grouped into four "persistence bands" reflecting relative temporal validity — described below. Beyond the banded baseline, the full signature will also include upstream catchment aggregates, downstream connectivity measures (coastality), and period-specific historical climate context; these are developed in the sections that follow. Signature requests can include values from any combination of bands and non-core sources:

- **A - Physiographic bedrock (millennia)** *[elevation, slope, stream gradient, lithology, karst extent]*. Indicative of the energy cost of movement, defensive advantages of terrain, and raw materials available for construction and agriculture, stable over millennia.

- **B - Hydro-climatic baselines (centuries)** _[discharge, basin area, groundwater depth, natural vegetation potential, soil texture]_. The potential of a landscape; while specific values fluctuate over time, the relative hierarchy (e.g., "Basin A is always wetter than Basin B") is usually stable across historical eras.

- **C - Bioclimatic proxies (decadal/cyclical)** _[precipitation, temperature, aridity, wetland extent, permafrost, ecoregion membership]_. Potentially useful as a baseline "modern average" of values. Interpretation typically requires accounting for known historical anomalies.

- **D - Anthropocene markers (last 50-100 years)** _[reservoir volume, land cover, cropland/pasture, pop density, human footprint, GDP/HDI]_. Typically omitted from signature requests for most historical contexts.

What distinguishes an EDOP signature from a simple attribute lookup is a process orientation: the aim is to characterize not merely what surrounds a location but what it *experiences* through directed spatial processes. This operates in both directions along the drainage network. Upstream, a **local/upstream duality** captures what flows *to* a place: BasinATLAS provides, for most climate and hydrological variables, both a local value (conditions within the immediate sub-basin) and an upstream catchment value (area-weighted accumulation across all contributing basins). The contrast between these two is itself environmentally meaningful — often more so than either value alone. Downstream, a complementary dimension — **coastality** — captures what a place can *reach*: its connectivity through the drainage network to the sea, and the character of the marine setting it accesses. Both directions are developed further in §4.

Ancient Ur illustrates this: its signature query returns 94mm/yr local precipitation and an aridity index of 5 — hyper-arid, barely inhabitable on its own terms. But the upstream catchment feeding it averages over 400mm/yr. That fourfold divergence between local and upstream is not a data quirk; it is the central environmental fact about alluvial civilizations. A settlement where those two values converge occupies a qualitatively different environmental position than one where they diverge. The divergence magnitude is itself a characterization of the place.

### 3.2 Signature extents

The EDOP service (EDOPS hereafter) will provide signatures for any terrestrial location, given as geographic coordinates. An integrated component facilitates place name resolution using the API of <a href="https://whgazetteer.org" target="_blank">World Historical Gazetteer</a>. If coordinates are of a representative point, for example of a settlement, site, or anthropological observation, the signature returned will be that of a single containing basin--normally less than useful. Environmental context is not intrinsic to a point; it is a modeled neighborhood, therefore EDOPS will treat neighborhood definition as a transparent, swappable parameter, offering multiple ways of defining one on the fly, per-query: for example, (i) single basin at a requested scale level, (ii) immediate siblings, (iii) basins overlapping a user-supplied area or buffer, or (iv) basins within the containing watershed.

When a user supplies a polygon (e.g., a polity boundary, an urban footprint, or a drawn region), the polygon itself defines the neighborhood. EDOPS computes a composite signature by intersecting the polygon with hydrologic basins at a given level, applying area-weighted aggregation of environmental variables, and returning a structured signature. There are several open research questions regarding this step, including (i) which basin level/scale is most appropriate, (ii) how weighting of partial basins is computed, (iii) how the heterogeneity of a resulting set of multiple signatures is represented and computed over, and (iv) how scale sensitivity is evaluated.

### 3.3 Temporal scope

Most global environmental datasets, including BasinATLAS, are contemporary and not ideally suited for analyses that are often historical. For EDOPS, this temporal mismatch is addressed in two ways. First, the persistence bands provide coarse temporal scoping: Bands A and B are defensible historical baselines across centuries to millennia, while Band D markers require explicit suppression for pre-industrial queries. Second, and more directly, EDOPS will integrate historical climate data from two established datasets:

The **Last Millennium Reanalysis v2.1** (Tardif et al. 2019) is a spatially gridded paleoclimate reanalysis covering 1–2000 CE, drawn from a 20-member ensemble. Variables include the Palmer Drought Severity Index (PDSI), surface air temperature, and precipitation rate. For any query with a specified historical period, the service will return period-specific climate context alongside the baseline signature. For Kaifeng in 950–1000 CE, for instance, LMR data shows persistently above-average moisture conditions throughout the period of Northern Song territorial expansion — a concrete climate context for the territorial argument illustrated in Figure 2.

**eVolv2k v4** (Sigl & Toohey 2024) provides complementary event annotation: 256 volcanic eruptions from 500 BCE–1900 CE, with stratospheric sulfur injection magnitudes and hemispheric loading patterns. Its role is different from LMR — not a continuous climate variable but a sparse event catalog. It delivers context like: a major tropical eruption injected 28 Tg of sulfur into the stratosphere three years before your query period, with predominantly Northern Hemisphere loading. The 946 CE Changbaishan eruption — the largest in East Asia in the last 2,000 years, on the Korea/China border — falls just before the Song expansion period and is directly recoverable from the catalog.

Together these two datasets cover the full range of the project's primary historical research interests, from Roman antiquity through the early modern period, and substantially address the temporal mismatch inherent in applying contemporary environmental baselines to historical queries.

## 4. The EDOPS process orientation, more broadly

As mentioned above, a novel aspect of EDOPS signatures is the aim to summarize formally what a place *experiences*, not only what surrounds it&mdash;"action-at-a-distance" (Goodchild 2026). The upstream dimension of a signature captures what flows *to* a place. A complementary and equally important dimension captures what a place can *reach* — its connectivity downstream through the drainage network to the sea. Call this **coastality**: it operates through flow distance to marine outlet, outlet type (exorheic basins reach the sea; endorheic basins, roughly 16% of global land area, do not), and ultimately through the ecological and accessibility character of the coastal or marine setting reached.

Coastality matters because terrestrial and marine affordances are independent dimensions that can point in opposite directions, and settlement viability is a function of their combination. The Yaghan (Yamana) of Tierra del Fuego make this concrete in its sharpest form. Their territory — the Beagle Channel and the Cape Horn archipelago — has among the most forbidding terrestrial signatures in the inhabited world: extreme temperature variability, minimal agricultural potential, very low productivity. An EDOP signature based on terrestrial data alone would predict very low settlement viability. The Yaghan occupied this territory for millennia, because the marine affordance is extraordinary: the cold, nutrient-rich waters sustain dense shellfish, pinnipeds, and fish concentrations throughout the fjord systems. They were essentially aquatic in their subsistence. The terrestrial signature is not wrong — it correctly characterizes terrestrial conditions, but it is blind to the dimension that actually mattered.

The first-phase implementation of coastality draws from data already in BasinATLAS: flow distance to marine outlet and topological depth from the coast via the drainage network. These fields are already included in current signatures. A second phase will add adjacent marine climate context for coastal locations where sea conditions are environmentally significant. Two datasets are planned: **ICOADS** (International Comprehensive Ocean-Atmosphere Data Set, NCEI/NCAR), a gridded monthly marine climate record at 2°×2° resolution extending back to 1800 CE, providing sea surface temperature, air temperature, pressure, and wind; and seafloor topography, distinguishing continental shelf from deep water, which shapes both marine productivity and historical maritime accessibility. These are relevant for port cities, island societies, and any place where fisheries or maritime trade were primary affordances.

Beyond the hydrological case, other process types can follow the same logic: terrain slope and gradient as indicators of intrinsic movement cost and accessibility, or atmospheric conditions shaped by prevailing winds. Social connectivity structured by route networks is a longer-term possibility. Each process type has its own geometry and characteristic distance decay.

Spatial data and descriptive text from OneEarth ecoregion datasets--including Wikipedia-derived summaries for all 847 ecoregions--are already incorporated into <a href="https://cedop.kgeographer.org/edop" target="_blank">the EDOP prototype</a> and will be available as optional parameters in the EDOPS API.

## 5. The EDOP data infrastructure

The <a href="https://www.hydrosheds.org/hydroatlas" target="_blank">BasinATLAS</a> and <a href="https://www.oneearth.org/bioregions-2023/" target="_blank">OneEarth ecoregions</a> data are both available under open CC-BY licenses, as are Wikipedia ecoregion articles. The current EDOP prototype utilizes BasinATLAS Level 08 data, which partitions the terrestrial Earth surface into 190,675 nested drainage units (catchments). BasinATLAS defines a 12-level hierarchy (Levels 01--12), spanning scales from continental basins to fine-grained local catchments.

A well-known characteristic of spatial data is the *Modifiable Areal Unit Problem (MAUP)*</a>, where "the results of mapping or statistical analysis may differ when using different spatial units of aggregation." (cf. <a href="https://gistbok-ltb.ucgis.org/page/current/concept/FC-07-026" target="_blank">UCGIS Body Of Knowledge</a>). A signature computed for the watershed containing Rome looks different from one computed for the small sub-basin immediately beneath a single representative point given for the Capitoline Hill. A systematic scale sensitivity analysis across multiple BasinATLAS levels is the next planned analytical contribution, and will inform which level is most appropriate for which research contexts. When multiple levels are considered, sharp signature changes across them can provide useful information about a place's positioning at edges of ecological zones. Although providing real-time multi-level responses will require significant computing and storage capability, a one-time analysis across representative samples should provide useful guidelines for users' choice of level.

The _OneEarth_ project, self-described as "global network of climate strategists and storytellers," has incorporated data for the 845 "widely cited" ecoregions developed by an international consortium of conservation scientists (Dinerstein, et al, 2017) into a new *bioregion framework*, presented in maps and essays on their web platform. Ecoregions classify the terrestrial surface into biogeographically distinct areas sharing characteristic species assemblages and ecological conditions. The spatial data for these ecoregions is freely available. Comprehensive articles describing virtually all of them, authored during an earlier World Wildlife Fund effort, are available in Wikipedia, and will be incorporated into the EDOPS prototype as optional contextual outputs alongside numerical signatures.

Two additional open datasets extend the infrastructure into historical time. The **Last Millennium Reanalysis v2.1** (Tardif et al. 2019; NOAA/NSF-funded) provides spatially gridded paleoclimate reconstructions at 2°×2° resolution for 1–2000 CE, with variables including PDSI, surface air temperature, and precipitation rate. **eVolv2k v4** (Sigl & Toohey 2024) catalogs 256 volcanic eruptions from 500 BCE–1900 CE, with stratospheric sulfur injection magnitudes and hemispheric loading patterns. Both datasets are openly distributed and are now integrated into the EDOPS extraction pipeline. Together they cover the full temporal range of the project's primary research interests, from Roman antiquity through the early modern period.

## 6. Validation: do the signatures capture something real?

EDOPS signatures represent computable and configurable summarizations of environmental conditions at given locations utilizing rigorously developed data. In effect EDOP is a model of suitability for human occupation and settlement, which must itself must be validated. How do EDOP signatures correspond to known human settlements and regions of transitory occupation? The required methodology is similar to that used by ecologists in *species distribution modeling (SDM)* and by archaeologists predicting likely settlement locations from environmental variables.

Attempts to predict known settlement locations are sure to have mixed results, because humans have adapted to a great variety of environmental settings. The test is simple in principle: do environmentally favorable locations correspond to where people actually settled? Defining 'favorable' independently of the settlement record itself is the methodological challenge --one the planned validation study will address using held-out data and established SDM techniques. Failure is diagnostic, success will build confidence in the model. The residuals&mdash;differences between predicted settlement probability and actual settlement record&mdash;will be a more revealing aspect than matches. In cases of genuine historical absence we can ask: Was there poor connectivity to diffusion networks? Competitive exclusion? Is there an explanatory variable the current signature doesn't provide? In cases of dense or persistent settlement but an apparently unfavorable signature, were there strategic imperatives like trade or defense? Were some localized resources not captured in the model, or was it sheer historical contingency?

Existing datasets identified for use in a validation process include (i) point locations of anthropological fieldwork in indigenous societies in <a href="https://d-place.org" target="_blank">*D-PLACE*</a>, (ii) polygon geometry for over 800 temporally scoped historical polities, from the recent <a href="https://github.com/Seshat-Global-History-Databank/cliopatria" target="_blank">Cliopatria dataset</a> developed by the <a href="https://seshatdatabank.info/" target="_blank">Seshat *Global History Databank* project</a>, and (iii) temporally scoped point locations for roughly 1700 historical settlements spanning 6,000 years, developed by Reba, et al (2016).

One important caveat is that given the dimensions of the current EDOP model, signatures are most likely to be predictive of fixed settlements relying on terrestrial resources. Hence there will be blind spots that need to be accounted for. We can expect signatures across the Eurasian steppe would read as unfavorable, despite it having been occupied intensively by mobile cultures whose movement was adaptive to apparently hostile conditions. Likewise, the terrestrial signature for Tierra del Fuego will correctly characterize harsh terrestrial conditions — yet the rich marine resources allowed the Yaghan to thrive there for millennia, and the presence of guanaco in the interior supported the Selknam societies. As described in Section 4, this is precisely the kind of anomaly that the coastality dimension is designed to resolve: the predictive failure points directly at the missing variable.

## 7. Culture, CDOP and the larger goal

<figure class="figure-inline">
<img src="{static}/images/CP_architecture.jpg" alt="Computing Place architecture diagram">
<figcaption>Figure 1 - Computing Place architecture. Lines indicate connections in prototype platform as of March, 2026</figcaption>
</figure>
The Cultural Dimensions of Place (CDOP) component of Computing Place complements EDOP, and the exploratory and analytical space linking them requires EDOP signatures. EDOP records environmental affordances and constraints; CDOP contributes what cultures have done within particular physical settings (Fig 1). CDOP work has begun by identifying and preparing spatialized datasets representing cultural phenomena of various kinds.

These core datasets, mentioned above as being integral to EDOP signature validation work, will see further use in seeking patterns of co-relation:

**<a href="https://d-place.org" target="_blank">D-PLACE</a>**: "...contains cultural, linguistic, environmental and geographic information for over 1400 human 'societies'. A 'society' in D-PLACE represents a group of people in a particular locality, who often share a language and cultural identity.

**<a href="https://github.com/Seshat-Global-History-Databank/cliopatria" target="_blank">Cliopatria</a>**: "...a comprehensive open-source [temporally scoped] geospatial dataset of worldwide states, political groups, events, and rulers from 3400BCE to the present day. It is part of the Seshat Global History Databank project."

**Chandler-Modelski historical population**: "...the first spatially explicit dataset of urban settlements from 3700 BC to AD 2000..." previously published by Reba et al (2016) derived from work by Chandler and Modelski."

Experiments have begun in the <a href="https://cedop.kgeographer.org" target="_blank">Computing Place platform prototype</a> with descriptive text for 258 UNESCO World Heritage Cities, and similar semantic embedding experiments are planned using nomination documents for Intangible Cultural Heritage listings.

The linking of EDOP and CDOP data can facilitate answering many kinds of questions, including but not limited to: Do cultural traits cluster in particular environmental regimes? How do environmental gradients correspond to linguistic, social, or economic variation? How stable are signatures across historical change?

One early demonstrator developed sets of signatures for the extents of Northern Song Dynasty over an 18-year period, as recorded in the Cliopatria dataset. Mapping the aridity value of contained basins illustrates what was arguably a deliberate move to acquire more arable territory (Fig 2). Period-specific LMR climate data for Kaifeng, the Song capital, shows consistently above-average moisture conditions throughout this expansion — consistent with the environmental picture and with Ruth Mostern's scholarship on Song agricultural strategies.

<figure class="figure-inline">
<img src="{static}/images/song_transition.jpg" alt="Northern Song Dynasty expansion map">
<figcaption>Figure 2: Expansion of Northern Song Dynasty into territory with greater moisture availability (isolating BasinATLAS 'Global Aridity Index'), 962-980CE</figcaption>
</figure>

## 8. Current state and next steps

The Computing Place project began in early January, 2026 and produced a prototype web platform to display work-in-progress a month later at <a href="https://cedop.kgeographer.org/edop/" target="_blank">cedop.kgeographer.org/edop</a>. Early work included developing:

- Three ways of specifying a place to obtain a basin signature: integrated WHG toponym lookup, small (97k) internal gazetteer lookup, and selecting one of 258 World Heritage Cities (WHC).

- Signature service returning a summary profile and full Band A-D attribute groupings per submitted place.

- Tool for finding and mapping cities with similar profiles in the WHC set of 258.

- Tool for browsing and mapping basin type clusters developed with principal components analysis.

- Tool for drilling down through the OneEarth bioregion/ecoregion hierarchy, displaying maps, and at the ecoregion level, Wikipedia summary descriptions.

- Experimental interface to D-PLACE data, mapping societies according to two of the many dimensions of its data: *dominant subsistence* and *high gods*.

- Search/browse for World Heritage Cities, returning signatures and optional lookup of cities with similar EDOP signatures and semantic content derived from Wikipedia article embeddings for four themes: *environment*, *history*, *culture*, and *'modern'.*

- A public API exposing documented endpoints

### Next steps

Refining the EDOP component of Computing Place is now the top priority--work that includes three efforts mentioned earlier: studies of scale sensitivity and upstream/downstream distance weighting, and validation against settlement datasets.

The signature's temporal reach is also actively expanding. Two recently integrated datasets extend EDOP beyond its contemporary baseline: the Last Millennium Reanalysis (LMR v2.1) will provide period-specific climate context for historical queries, covering 1–2000 CE at 2° spatial resolution; eVolv2k v4 provides volcanic event annotation for the same range, extended back to 500 BCE. These address the temporal mismatch inherent in applying contemporary climate baselines to historical queries — a problem the four persistence bands partially address but cannot fully resolve. Coastal enrichment, via gridded marine climate data (ICOADS) and seafloor topography, is the corresponding development for maritime and port-city signatures.

EDOP is intended to have broad utility to researchers in several disciplines, and is being developed in partnership with the Institute for Spatial History Innovation (ISHI) at the University of Pittsburgh, whose work with the World Historical Gazetteer provides a natural integration context: Computing Place will publish environmental signatures as linked annotations keyed to WHG place identifiers.

Feedback is most welcome on either of the Computing Place components, as well as on the overall project. A more technical overview is available on request.

## In closing

"An ordered presentation of the landscapes of the earth is a formidable undertaking." -- Carl Sauer (1925)

"Nothing for it but to do it" -- Karl Grossner (2026)

Computing Place is admittedly ambitious, perhaps overly so. It is driven by personal research questions about culture and geography that require a way of summarizing environmental settings efficiently but robustly--namely EDOP--so that is where the initial focus is. The CDOP work is so far only meanderings, a search for patterns that may or may not lead to empirical findings and even theory. But first things first, as the saying goes.

## References

Dinerstein, E., Olson, D., Joshi, A., Vynne, C., Burgess, N. D., Wikramanayake, E., & Saleem, M. (2017). An ecoregion-based approach to protecting half the terrestrial realm. *BioScience*, *67*(6), 534-545.

Goodchild, M. F. (2026, February). *Personal communication*.

Reba, M., Reitsma, F., & Seto, K. C. (2016). Spatializing 6,000 years of global urbanization from 3700 BC to AD 2000. *Scientific data*, *3*(1), 160034.

Sigl, M., & Toohey, M. (2024). eVolv2k v4: A global volcanic forcing reconstruction for the last two millennia. *Earth System Science Data*.

Tardif, R., et al. (2019). Last Millennium Reanalysis with an expanded proxy database and seasonal proxy modeling. *Climate of the Past*, *15*(4), 1251-1273.
