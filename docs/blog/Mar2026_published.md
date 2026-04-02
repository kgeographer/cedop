Title: Introducing Computing Place
Date: 2026-02-09
Slug: computing_place
Summary: Introduction to the personal Computing Place project
Category: research
Tags: place, landscape, culture, environment, geohumanities
Author: Karl Grossner
Status: published

Computing Place is a new research initiative aimed at building rich, computable descriptions of places, linking environmental and cultural data to support systematic analyses across those numerous dimensions. This work starts from a simple premise: places differ, and the quality of comparative analyses depends upon the quality and completeness of formal descriptions. Environment and culture are inextricably intertwined, as studied and understood from numerous disciplinary perspectives. I will be experimenting with ways to represent places computationally without collapsing them into a single metric or theory.

### Some background
My reading of geographer Carl Sauer's 1925 article, <a href="/pubs/Sauer_Morphology.pdf" target="_blank" rel="noopener noreferrer">The Morphology of Landscape</a> has had a significant influence on my conception of place as it developed over the years. Sauer introduced the term __cultural landscape__ to American readers, having borrowed it from the _Kulturlandschaft_ conception of earlier German geographers.
 
> "The content of landscape is found therefore in the physical qualities of area that are significant to man and in the forms of his use of the area, **in facts of physical background and facts of human culture**." (emphasis added, p.325)

Sauer's _morphological method_ was most concerned with the chorological description of the evidence of cultures' impact upon the natural landscape over time and less so with the impact of environment upon culture. He did however allow for other perspectives, noting that "the continued synthesis of phenomena by morphologic method has been employed with greatest success perhaps in anthropology (p. 327)"

That concession matters here because the blended conceptualization of place used in this project borrows from the phenomenological view of Yi-Fu Tuan ("place as experienced space" as I paraphrase it), and Doreen Massey's poetic framing of place as a "meeting up of histories." Computing Place is therefore not operationalizing Sauer's cultural landscape concept so much as extending it, treating place as a coupled record of environmental setting and cultural traces, supporting questions in both directions without reverting to determinism.

The development of the **Computing Place** platform has begun in stepwise fashion, first with an **EDOP** module (Environmental Dimensions of Place) and then with tentative steps for a **CDOP** module (Cultural Dimensions of Place). These datasets and their respective analytic and visualization tools will in time offer both distinct and unified API endpoints that can be consumed internally in features of a Computing Place platform, and by external applications.

### Environment and Culture (EDOP & CDOP)

#### EDOP (Environmental Dimensions of Place)
A prototype environmental signature has been developed using 42 of the roughly 300 properties for 190,000 Level 8 subbasins in the <a href="https://www.hydrosheds.org/hydroatlas" target="_blank">BasinAtlas v1.0 portion of the HydroAtlas dataset</a>. These have been grouped in four rough temporally scoped bands corresponding to relative persistence and applicability to successive historical eras: _A - Physiographic bedrock_, _B - Hydroclimatic baselines_, _C - Bioclimatic proxies_, and _D - Anthropocene markers_. Point locations for places can be submitted to a web tool in a few ways so far, including a <a href="https://whgazetteer.org" target="_blank">World Historical Gazetteer (WHG)</a> lookup. Lists of places similar in either environmental terms or in semantic dimensions derived from Wikipedia text embeddings are returned on request.

#### CDOP (Cultural Dimensions of Place)
A first step at integrating cultural data has been instantiated within the EDOP module, by linking the 1291 indigenous societies from the <a href="https://d-place.org" target="_blank">D-PLACE dataset</a> to their containing ecoregions on two sample attributes: "Dominant subsistence" and "High Gods."

An important next step for CDOP is determining what attributes of culture to work with. Evidence of culture is for me a very broad domain, including but not limited to descriptive narrative texts (travel writing, folklore, mythology, and other literature, encyclopedic sources, etc.), folk and "fine" art, and architectural motifs. That said, CDOP experiments will be constrained by what data may be readily available. 

### Linked Traces
In 2019 considerable work was done to develop the __Linked Traces annotation format (LTF)__ in coordination with the <a href="https://github.com/LinkedPasts/linked-places-format" target= "_blank">__Linked Places Format (LPF)__</a> that became a contribution and interconnection standard for World Historical Gazetteer and other projects associated with the <a href="https://pelagios.org" target = "_blank">Pelagios Network</a>.

LTF has seen limited uptake but is likely now applicable in the Computing Place platform architecture. A _trace_ in LTF is defined as a "web-published resource concerning historical entities of any kind, and conventionally, to the entities themselves." Trace data takes the form of W3C web annotations, as explained on the <a href="https://github.com/LinkedPasts/linked-traces-format" target= "_blank">LTF Github repository</a>. LTF follows Linked Open Data principles in extending the relatively constrained place descriptions of digital gazetteers with all manner of related thematic material. EDOP and CDOP data would seem to fit that framing well.

### Computing Place and World Historical Gazetteer
Computing Place is a research initiative that can also be understood as a downstream application in the ecosystem that <a href="https://whgazetteer.org" target="_blank">World Historical Gazetteer (WHG)</a> was designed to support. WHG’s core contribution is to provide stable, reconcilable place anchors—identifiers and attested names, geometries, and basic relations—while leaving richer thematic data and interpretive detail to external project contributors. Computing Place aligns with that division of labor. It will treat WHG place records as a reference layer, and attach additional evidence to them as linked “traces”: environmental signatures, cultural descriptors, and other place-referenced materials that can be analyzed, compared, and explored. These annotations will be patterned after the Linked Traces Format mentioned above, developed in 2019 under the aegis of the <a href="https://pelagios.org" target="_blank">Pelagios Network</a>.

Integration between the two can take several forms over time. In the simplest case, Computing Place’s EDOP module will provide API endpoints that WHG and other clients can call on demand&mdash;sending a representative geometry and retrieving environmental context in the form of a concise profile derived from EDOP’s basin-based signatures. Computing Place can also potentially contribute curated sets of place records to WHG that link back to rich Computing Place landing pages for those places; at a larger scale, it can publish an annotation index keyed to WHG identifiers.

In all cases, the intent is not to expand WHG into a thematic encyclopedia, but to use WHG’s place framework as the anchoring substrate linking to a variety of rich, computable descriptions of place, much as many WHG contributors do now.
