# ICH LLM Extraction: Analytical Prospectus

## Context

We have successfully extracted structured geographic and environmental data from all 566 UNESCO Intangible Cultural Heritage nomination documents using LLM-based information extraction. The extraction schema distinguishes:

- **Practice locations**: Where traditions are authentically performed (the "hearth")
- **Diaspora locations**: Where practitioners have migrated, carrying traditions with them
- **Environmental features**: Physical geography terms mentioned in nomination text
- **Explicit coordinates**: When lat/lon values appear in documents (31 of 566)

This document explores what these extracted data might enable.

---

## 1. Discontinuous Spatial Footprints with Semantic Qualifiers

A cultural practice rarely has a simple, contiguous geographic extent. The LLM extraction captures this complexity:

**Hearth geography**: Practice locations represent the primary spatial footprint—where a tradition emerged or is most deeply rooted. These locations carry implicit claims about environmental and cultural conditions that gave rise to the practice.

**Diaspora geography**: Diaspora locations with contextual annotations (e.g., "emigrant community in São Paulo," "spread via Silk Road trade") represent a secondary, derivative footprint. These are places where the tradition exists but is transplanted, maintained by people displaced from the hearth.

**Analytical implication**: Rather than treating ICH elements as having a single "location," we can model them as having qualified, multi-part spatial footprints. The hearth/diaspora distinction is not merely geographic—it encodes historical process (migration, trade, colonialism) and authenticity claims (where is the tradition "from" vs. where does it "exist").

---

## 2. Environmental Signatures and Cultural Hearths

With practice locations geocoded to coordinates, we can link ICH elements to EDOP environmental signatures. This enables:

**Environmental clustering**: Do practices with similar environmental signatures share other characteristics? Are mountain pastoralist traditions worldwide more similar to each other than to their lowland neighbors?

**Environmental constraints vs. portability**: Some traditions are tightly bound to environment (coastal fishing techniques, alpine herding). Others travel freely with diaspora communities (textile patterns, oral epics). The presence or absence of diaspora locations may correlate with environmental specificity.

**Triangulation**: The `environmental_features` extracted from nomination text provide a complementary signal to EDOP's computed signatures. These are the environmental terms that UNESCO nominators chose to emphasize—a kind of "folk environmental perception" that may or may not align with measured physical geography.

---

## 3. Diffusion Analysis

The hearth/diaspora structure directly encodes diffusion:

**Diffusion vectors**: For each element with both practice and diaspora locations, we have implicit vectors from hearth to diaspora. Aggregating these across the corpus could reveal:
- Major cultural migration corridors
- Asymmetries (which regions export vs. import traditions)
- Historical layers (colonial-era vs. recent labor migration)

**Diaspora context as mechanism**: The `context` field in diaspora locations captures why the tradition spread—emigrant communities, religious missions, trade networks, tourism. This is rare structured data about diffusion mechanisms.

**What doesn't diffuse**: Elements with zero diaspora locations may be environmentally constrained, linguistically bound, or dependent on local materials/landscapes. These "non-diffusing" traditions are analytically interesting in their own right.

---

## 4. Multi-Scale Spatial Analysis

The extracted location hierarchy (village → county → prefecture → province → country) enables multi-scale analysis:

**Precision gradient**: Some extractions yield specific villages; others only country-level claims. This precision itself is data—it may reflect the tradition's spatial extent, the nomination document's specificity, or political sensitivities.

**Aggregation flexibility**: We can analyze at any level—comparing traditions across provinces, countries, or UN subregions—without losing the finer-grained data.

**Nested environmental signatures**: A village has one EDOP signature; its province has a range. Multi-scale analysis could reveal whether traditions are tuned to local micro-environments or regional macroclimate.

---

## 5. Cross-Corpus Linkage

The geocoded ICH footprints could link to other CEDOP data:

**D-PLACE societies**: Where ICH practice locations overlap with D-PLACE society territories, we gain a bridge between UNESCO's "living heritage" and anthropological observations. Do D-PLACE subsistence types predict which ICH practices appear?

**World Heritage Sites**: Some ICH elements are explicitly tied to World Heritage Cities or Sites. The environmental signature comparison (ICH practice location vs. WH site) could reveal cultural-environmental nexus points.

**Historical gazetteers**: Linking to WHG could provide temporal depth—when did these place names exist? How have administrative boundaries shifted around enduring cultural practices?

---

## 6. Nomination Text as Environmental Perception

Beyond structured extraction, the nomination documents themselves encode how communities describe their environmental context. The `environmental_summary` field synthesizes this.

**Folk vs. measured geography**: How do nominators' environmental descriptions compare to EDOP's computed signatures? Discrepancies could reveal:
- Perceptual salience (features people notice vs. features that dominate statistics)
- Cultural framing (a "river valley" vs. a "floodplain" vs. a "fertile crescent")
- Historical memory (environmental conditions that no longer obtain)

**Embedding similarity**: With full nomination text, we could generate embeddings and find semantically similar traditions—not by location or concept tag, but by how they describe themselves. This complements the structured extraction.

---

## 7. Methodological Precedent

The LLM extraction pipeline itself is a methodological contribution:

**Hearth/diaspora distinction at scale**: This semantic separation is notoriously difficult with NER or rule-based extraction. The LLM's contextual understanding handled it effectively across 566 diverse documents.

**Multilingual robustness**: The corpus includes documents with place names in Chinese, Arabic, Persian, Spanish, and many other languages. The LLM handled romanization and transliteration issues that defeated earlier NER approaches.

**Replicable for other corpora**: The extraction schema and prompt could be applied to other cultural heritage documentation—national inventories, anthropological field notes, travel literature.

---

## Open Questions

1. **Geocoding strategy**: How to convert extracted place names to coordinates? Hierarchical context helps (village X in province Y), but ambiguity remains.

2. **Temporal anchoring**: ICH is "living heritage"—nominally continuous present. But the documents often reference historical origins. How to handle temporal claims?

3. **Political geography**: Country names change; administrative boundaries shift. The extractions reflect nomination-date geography. Link to historical gazetteers?

4. **Validation**: How to assess extraction quality beyond spot-checks? Ground truth is scarce for hearth/diaspora distinctions.

5. **Analytical framing**: Is the goal environmental determinism (do environments shape culture)? Cultural ecology? Diffusion studies? The data support multiple framings.

---

## Suggested Next Steps

1. **Geocoding pipeline**: Convert practice_locations to coordinates using hierarchical context + gazetteer matching
2. **EDOP linkage prototype**: For geocoded locations, retrieve environmental signatures and explore correlations
3. **Diffusion visualization**: Map hearth → diaspora vectors for elements with both
4. **Embedding generation**: Create embeddings from full nomination text for semantic similarity search
5. **D-PLACE bridge**: Identify geographic overlaps between ICH practice locations and D-PLACE society territories

---

*This prospectus is intended for collaborative reflection with human researchers and AI assistants. The extracted data is exploratory; the analytical framings are provisional.*
