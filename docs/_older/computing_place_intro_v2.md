# Computing Place: Toward Systematic Environmental Characterization for Cultural Research

*Karl Grossner, KGEO Research — draft outline v2, March 2026*

*Changes from v1 marked* **[NEW]** *or* **[REVISED]**

---

## 1. Opening: The question that motivates everything

*(~175 words — slightly expanded)*

Start with Sauer's framing — land and life in terms of each other — as an intellectual anchor familiar to humanists. Then the pivot: historians, archaeologists, and anthropologists invoke environmental context constantly, but almost always qualitatively. What would it mean to make those invocations *computable and reproducible*? That's the question Computing Place is built around.

**[NEW]** One or two sentences on the longer intellectual ambition behind the project — circled from different directions for 25 years — without overcommitting to specific claims. The goal is pattern exposure: making environmental signatures available for others to discover things in, and for the builder to find patterns that may or may not resolve into formal arguments. The project doesn't presuppose its results.

One sentence on the two-module structure (EDOP/CDOP), with the key dependency stated plainly: cultural analysis of the kind Computing Place envisions requires a very solid environmental foundation first.

---

## 2. What "computing place" means — and what it doesn't

*(~200 words — unchanged)*

Address the "not new territory, new methods" framing directly. The scholarly tradition is deep — environmental history, historical ecology, archaeology, anthropology. The claim here isn't novelty of the question but novelty of the method: making those relations formally computable, at global scale, with explicit and reproducible parameters.

Brief note on what this is *not*: not environmental determinism, not a classificatory scheme. The framing is "bounded possibility spaces" — environment defines what a place affords and constrains; culture determines which possibilities are realized.

---

## 3. The environmental signature concept

*(~250 words — unchanged)*

This is the core technical idea, explained accessibly. For any location, EDOP produces a structured vector of environmental dimensions drawn from globally consistent datasets — not a label ("Mediterranean climate") but a multidimensional characterization that supports comparison and analysis.

Introduce the four bands (physiographic bedrock, hydro-climatic baselines, bioclimatic proxies, Anthropocene markers) with one concrete example per band. The Timbuktu/Ur contrast works well here: same arid classification, very different signatures once you look at what's happening upstream.

Cover the two input types briefly: point locations (settlements, heritage sites, ethnographic societies) and area-based units (historical polities, regions) — and why the distinction matters for how the neighborhood is defined.

---

## 4. The key methodological idea: what a place *experiences*, not just what surrounds it

*(~350 words — expanded)*

This is where EDOP departs from existing tools and where both audiences need the clearest explanation. Commercial geographic enrichment (Esri et al.) overlays attributes from intersecting layers — purely local, no directionality. EDOP's goal is *process-aware environmental characterization*.

Introduce the local/upstream duality (s/u) as the concrete instantiation of this idea. Ur is the worked example: local aridity index of 5, 94mm/yr precipitation — a hyper-arid spot. But the catchment feeding it receives 258mm/yr. That divergence is not noise; it *is* the environmental characterization. Alluvial civilizations are definitionally places where s and u diverge sharply.

The planned extension: distance-weighted upstream profiles via the basin drainage network, where contributions decay with distance (proximity matters more than contributing area). This is the methodological novelty relative to HydroATLAS's pre-computed upstream values, and the most direct response to Goodchild's framing of action-at-a-distance as the undertheorized problem in spatial analysis.

**[NEW]** The upstream direction is one half of a larger directional frame. Alongside local conditions, a complete signature also characterizes a location's *downstream* position — how far it sits from the marine outlet of its drainage system, whether its basin drains to the sea at all (exorheic) or terminates inland (endorheic). This third axis — upstream exposure / local conditions / downstream connectivity — positions a place within the full arc of the hydrologic cycle. Coastal locations with short drainage paths to the sea sit at one extreme; landlocked endorheic basins (the Central Asian interior, the Saharan chotts) sit at the other. Both are environmentally meaningful positions, and the contrast is not captured by any existing enrichment tool.

---

## 5. The data infrastructure

*(~200 words — unchanged)*

Brief, non-technical description of HydroBASINS/BasinATLAS (190k sub-basins globally, 281 attributes, 12 hierarchical levels) and the OneEarth ecoregion framework. Emphasize that both are open, globally consistent, CC-BY — not proprietary data.

The scale question: signatures change as you zoom in or out (MAUP). Rather than hiding this, EDOP treats scale sensitivity as a reportable property of the signature — a feature, not a bug. Where the signature changes sharply across levels, that tells you something about the location's environmental position (edge zones, confluences, ecotones).

---

## 6. Validation: do the signatures capture something real?

*(~350 words — substantially revised)*

**[REVISED]** This section needs to be more specific about the validation logic and what it reveals, not just that validation will happen.

The core question: if EDOP signatures encode meaningful environmental information, then basins with signatures similar to known early urban hearths (Fertile Crescent, Indus, Yellow River, Niger Inland Delta) should themselves appear in the historical settlement record. Failure is diagnostic; success builds confidence. Three validation datasets span the spectrum from sedentary agrarian complexity to mobile and small-scale: early urban hearths (Reba et al., unambiguous positives), Cliopatria/Seshat polities (graduated complexity), D-PLACE ethnographic societies (direct cultural linkage, lower complexity end).

**[NEW]** The interesting output isn't the match — it's the residual. The difference between predicted settlement probability and actual settlement record is where the intellectual action is.

Two types of anomaly emerge, and they tell different stories:

*Underperformers* — favorable signature, sparse or absent settlement. These flag either undiscovered sites (the use case familiar from predictive modeling in CRM archaeology), genuine historical absence (why? missing connectivity to diffusion networks? competitive exclusion?), or a variable the current signature can't see. Tierra del Fuego is a clean example of the third type — and it should not be conflated with Patagonia proper, whose semi-arid steppe signature is genuinely inhospitable in a different way. The Fuegian terrestrial signature is harsh in its own register: hyperhumid, wind-battered, with low growing-season temperatures and minimal agricultural potential. Yet the Yaghan sustained themselves in the Beagle Channel archipelago for millennia by exploiting the extraordinary productivity of the surrounding channels — cold-water circulation and tidal dynamics within a sheltered fjord system that EDOP's current variable set cannot see. The Selknam, who occupied the Fuegian interior with a purely terrestrial subsistence strategy, are the instructive contrast: same regional environment, different axis of adaptation, completely different cultural configuration. The residual produced by the Yaghan case doesn't flag a model failure; it flags precisely where the model's blind spot lies, and what kind of human strategy fills it.

*Overperformers* — unfavorable signature, dense or persistent settlement. These reveal the degree to which human agency escapes environmental constraint — strategic rationale (trade nodes, defensive positions), cultural or ideological imperatives (sacred sites), localized resources not captured at the basin scale, or sheer historical contingency. These cases are the empirical foundation of possibilism: not claimed as a theoretical position but demonstrated case by case.

**[NEW]** One important caveat: EDOP characterizes environmental affordance for *sedentary* occupation more than for human presence generally. Mobile pastoralist and hunter-gatherer land use is systematically underrepresented in sedentary archaeological records. The model would correctly predict that fixed settlements were unlikely across the Eurasian steppe — and they largely were. But the steppe was occupied, intensively, by mobile cultures for whom the signature's apparent hostility was an advantage rather than a barrier. Settlement and occupation are different things, and the anomaly analysis should distinguish them.

---

## 7. CDOP and the larger goal

*(~200 words — revised)*

**[REVISED]** The division of labor between EDOP and CDOP is cleaner than the v1 framing suggested.

Settlement presence/absence is a threshold question — does this environment cross the minimum bar for sustained human occupation? It sits entirely on the physical side. EDOP establishes that threshold globally, systematically, without requiring cultural data. This is the proof of premise: that the signatures capture something real about environmental affordance.

CDOP then studies variation *within* the space of realized settlements — conditioned on the occupancy threshold EDOP establishes. The research questions become tractable: Do cultural traits cluster in particular environmental regimes? How do environmental gradients correspond to linguistic, social, or economic variation? How stable are signatures across historical change?

This two-stage structure is a stronger argument against environmental determinism than simply disclaiming it. CDOP explicitly studies cultural variation among places that cleared the threshold — making clear that environment constrains but doesn't determine cultural form. The constraints are the subject of EDOP; what culture does within those constraints is the subject of CDOP.

Frame this as infrastructure for a research community, not a finished answer to these questions.

---

## 8. Current state and next steps

*(~150 words — unchanged)*

Honest status report: working prototype is publicly accessible at cedop.kgeographer.org. What's implemented vs. what's planned (the [*] distinction from the research outline). The scale sensitivity study as the designated first paper contribution. Pending: support from ISHI/Pitt collaboration.

Invite engagement — link to the live demo, note that a technical overview is available on request.

---

## Closing

**[REVISED]** Return to Sauer: *"An ordered presentation of the landscapes of the earth is a formidable undertaking."* A century later, the tools exist to begin — though part of what they may reveal is the shape of the boundary between what can be characterized computationally and what lies beyond it. The residuals are as interesting as the matches. The project doesn't presuppose its results.

---

## Notes for drafting

- Sections 3–4 do the heaviest lifting — where humanists could glaze over (too technical) or GIScientists could underestimate the novelty (sounds like enrichment). Both need care.
- Section 6 is now the most changed and probably needs the most drafting attention — the anomaly framing is the freshest idea and the most concrete demonstration of why the validation is scientifically interesting, not just a credibility check.
- The Ur/Timbuktu contrast remains the best anchor for Section 4. The Yaghan/Tierra del Fuego case is the best anchor for Section 6 — note that Tierra del Fuego is distinct from Patagonia and should not be described as such.
- The collective unconscious question and prospect-peril material from the 28 Mar session are motivational backdrop, not blog post content — but one sentence in the opening gesturing at the longer intellectual ambition is worth including.
- The settlement vs. occupation distinction (Section 6) needs to be stated carefully — it's a caveat, not a criticism of the approach.
- **Word count target: ~2,000–2,500 words.** Section 6's expansion warrants the additional budget.
- May eventually develop into a conference paper; keep claims precise and hedged where appropriate.

---

*v2 reflects ideas from session notes at docs/blog/session_ideas_28Mar2026.md*
