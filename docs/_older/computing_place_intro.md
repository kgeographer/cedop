# Computing Place: Toward Systematic Environmental Characterization for Cultural Research

*Karl Grossner, KGEO Research — draft, March 2026*

---

## 1. Opening: The question that motivates everything

*(~150 words)*

Start with Sauer's framing — land and life in terms of each other — as an intellectual anchor familiar to humanists. Then the pivot: historians, archaeologists, and anthropologists invoke environmental context constantly, but almost always qualitatively. What would it mean to make those invocations *computable and reproducible*? That's the question Computing Place is built around.

One sentence on the two-module structure (EDOP/CDOP), with the key dependency stated plainly: cultural analysis of the kind Computing Place envisions requires a very solid environmental foundation first.

---

## 2. What "computing place" means — and what it doesn't

*(~200 words)*

Address the "not new territory, new methods" framing directly. The scholarly tradition is deep — environmental history, historical ecology, archaeology, anthropology. The claim here isn't novelty of the question but novelty of the method: making those relations formally computable, at global scale, with explicit and reproducible parameters.

Brief note on what this is *not*: not environmental determinism, not a classificatory scheme. The framing is "bounded possibility spaces" — environment defines what a place affords and constrains; culture determines which possibilities are realized.

---

## 3. The environmental signature concept

*(~250 words)*

This is the core technical idea, explained accessibly. For any location, EDOP produces a structured vector of environmental dimensions drawn from globally consistent datasets — not a label ("Mediterranean climate") but a multidimensional characterization that supports comparison and analysis.

Introduce the four bands (physiographic bedrock, hydro-climatic baselines, bioclimatic proxies, Anthropocene markers) with one concrete example per band. The Timbuktu/Ur contrast works well here: same arid classification, very different signatures once you look at what's happening upstream.

Cover the two input types briefly: point locations (settlements, heritage sites, ethnographic societies) and area-based units (historical polities, regions) — and why the distinction matters for how the neighborhood is defined.

---

## 4. The key methodological idea: what a place *experiences*, not just what surrounds it

*(~300 words)*

This is where EDOP departs from existing tools and where both audiences need the clearest explanation. Commercial geographic enrichment (Esri et al.) overlays attributes from intersecting layers — purely local, no directionality. EDOP's goal is *process-aware environmental characterization*.

Introduce the local/upstream duality (s/u) as the concrete instantiation of this idea. Ur is the worked example: local aridity index of 5, 94mm/yr precipitation — a hyper-arid spot. But the catchment feeding it receives 258mm/yr. That divergence is not noise; it *is* the environmental characterization. Alluvial civilizations are definitionally places where s and u diverge sharply.

The planned extension: distance-weighted upstream profiles via the basin drainage network, where contributions decay with distance (proximity matters more than contributing area). This is the methodological novelty relative to HydroATLAS's pre-computed upstream values, and the most direct response to Goodchild's framing of action-at-a-distance as the undertheorized problem in spatial analysis.

---

## 5. The data infrastructure

*(~200 words)*

Brief, non-technical description of HydroBASINS/BasinATLAS (190k sub-basins globally, 281 attributes, 12 hierarchical levels) and the OneEarth ecoregion framework. Emphasize that both are open, globally consistent, CC-BY — not proprietary data.

The scale question: signatures change as you zoom in or out (MAUP). Rather than hiding this, EDOP treats scale sensitivity as a reportable property of the signature — a feature, not a bug. Where the signature changes sharply across levels, that tells you something about the location's environmental position (edge zones, confluences, ecotones).

---

## 6. Validation: do the signatures capture something real?

*(~200 words)*

This is important for the GIScience audience and reassuring for the humanists. The validation logic: if the signatures encode meaningful environmental information, then basins with signatures similar to known early urban hearths (Fertile Crescent, Indus, Yellow River, Niger Inland Delta) should themselves appear in the historical settlement record. Failure is diagnostic; success builds confidence.

Three validation datasets: early urban hearths (Reba et al., unambiguous positives), Cliopatria/Seshat historical polities (graduated complexity), D-PLACE ethnographic societies (lower end of the spectrum, direct cultural linkage). This is posed explicitly as an instrumental probe of the data, not a causal claim.

---

## 7. CDOP and the larger goal

*(~150 words)*

Once EDOP is solid, CDOP adds the cultural side: anthropological variables (D-PLACE), intangible and tangible heritage (UNESCO ICH, World Heritage), historical polities. The research questions that become systematically addressable: Do cultural traits cluster in particular environmental regimes? How do environmental gradients correspond to linguistic, social, or economic variation? How stable are signatures across historical change?

Frame this as infrastructure for a research community, not a finished answer to those questions.

---

## 8. Current state and next steps

*(~150 words)*

Honest status report: working prototype is publicly accessible at cedop.kgeographer.org. What's implemented vs. what's planned (the [\*] distinction from the outline). The scale sensitivity study as the designated first paper contribution. Pending: support from ISHI/Pitt collaboration.

Invite engagement — link to the live demo, note that a technical overview is available on request.

---

## Closing

Return to Sauer: *"An ordered presentation of the landscapes of the earth is a formidable undertaking."* A century later, the tools exist to begin.

---

## Notes for drafting

- Sections 3–4 do the heaviest lifting — where humanists could glaze over (too technical) or GIScientists could underestimate the novelty (sounds like enrichment). Both need care.
- Section 6 (validation) is important for credibility; it shows the work is falsifiable.
- The Ur/Timbuktu contrast is the best concrete anchor and should appear early enough to ground the abstractions.
- Word count target: ~1,500–2,000 words. Readable in 8–10 min.
- May eventually develop into a conference paper; keep claims precise and hedged where appropriate.
