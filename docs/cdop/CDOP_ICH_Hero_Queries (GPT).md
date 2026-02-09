# CDOP – ICH Hero Queries
*Proposed exploratory queries for positioning UNESCO Intangible Cultural Heritage within the Cultural Dimensions of Place (CDOP) module*

Date: 2026-01-30

---

## Purpose

These “hero queries” are designed to demonstrate how UNESCO Intangible Cultural Heritage (ICH) data can function productively inside CDOP **without** assuming precise practice locales or direct environmental causation.

The emphasis is on:
- Cultural **affiliation and diffusion** patterns
- **Environmental constraint vs portability** diagnostics (using country-level environmental envelopes)
- Semantic exploration of cultural practice families via text embeddings

Each query is intended to be:
- Epistemically defensible
- Computationally feasible with the current ICH + EDOP setup
- Visually and conceptually legible to collaborators and reviewers

---

## Hero Query 1: Environmental Portability of a Highly Diffused Practice

**Anchor Element:** Falconry (24 countries)

**Query:**  
> Among all multinational ICH elements, which ones show the *widest* environmental envelope across their recognized countries?

**Method Sketch:**
- Select Falconry and other elements with ≥10 countries
- Compute EDOP environmental signatures for each country
- Measure variance/spread across key dimensions (or PCs)
- Compare against null models (random country sets of same size)

**Interpretive Payoff:**
- Demonstrates practices that are culturally cohesive yet environmentally flexible
- Establishes a “high portability” end-member

---

## Hero Query 2: Environmentally Constrained Mobility Practices

**Anchor Element:** Transhumance (10 countries)

**Query:**  
> Do mobility-based agro-pastoral practices occupy a narrower environmental envelope than expected by chance?

**Method Sketch:**
- Use Transhumance and related agro-ecosystem elements
- Compute environmental diversity scores across member countries
- Compare to random draws matched by country count and region

**Interpretive Payoff:**
- Tests whether certain mobile practices are still environmentally selective
- Bridges EDOP (environmental signatures) and CDOP (cultural practice families)

---

## Hero Query 3: Cultural Sphere Detection via Multinational ICH

**Anchor Elements:** Nowruz, Nasreddin Hodja traditions, Sericulture

**Query:**  
> What coherent cultural spheres emerge when countries are linked by shared ICH elements?

**Method Sketch:**
- Build bipartite graph: (ICH element) ↔ (country)
- Project to country–country network (shared elements)
- Run community detection
- Label communities by dominant elements and concepts

**Interpretive Payoff:**
- Reveals Turkic, Persian, Mediterranean, MENA spheres
- Positions ICH as a diffusion-topology dataset inside CDOP

---

## Hero Query 4: Mountains as Rhetoric vs Constraint

**Anchor Concept:** “Mountains” (71 elements)

**Query:**  
> Do ICH elements tagged with “Mountains” actually occupy a distinct environmental signature space compared to non-mountain-tagged elements?

**Method Sketch:**
- Separate elements with the “Mountains” concept
- Aggregate environmental signatures of their recognized countries
- Compare distributions to non-mountain elements

**Interpretive Payoff:**
- Tests whether environmental concepts reflect material constraint or narrative framing
- Surfaces tagging bias vs ecological signal

---

## Hero Query 5: Music Everywhere — or Not?

**Anchor Concept:** Vocal music (144 elements)

**Query:**  
> Are music-related ICH practices environmentally agnostic, or do sub-families show constraint?

**Method Sketch:**
- Filter elements by music-related concepts
- Cluster by text embeddings (genres, performance contexts)
- Compare environmental envelopes across clusters

**Interpretive Payoff:**
- Moves beyond “music is everywhere” to detect patterned variation
- Demonstrates the power of combining embeddings with EDOP summaries

---

## Hero Query 6: Diaspora Signal Detection in ICH Texts

**Anchor Elements:** Safeguarding of folk music heritage (Hungary), similar cases

**Query:**  
> Which ICH elements show strong textual signals of diaspora and migration, and how does that affect their apparent environmental spread?

**Method Sketch:**
- Identify elements with many extra-regional toponyms (e.g., US, Australia, Canada)
- Classify toponyms by role (practice vs diaspora vs institution)
- Recompute environmental envelopes with and without diaspora-linked countries

**Interpretive Payoff:**
- Makes diaspora an explicit analytical layer rather than noise
- Demonstrates methodological restraint and transparency

---

## Hero Query 7: Recognition Politics vs Environment

**Anchor Comparison:** Representative List (RL) vs Urgent Safeguarding List (USL)

**Query:**  
> Do urgently safeguarded practices show different environmental or geographic patterns than representative ones?

**Method Sketch:**
- Compare environmental diversity scores by list type
- Examine geographic concentration vs dispersion
- Control for number of recognizing countries

**Interpretive Payoff:**
- Connects cultural endangerment, recognition regimes, and place
- Positions CDOP as relevant to heritage policy analysis

---

## Hero Query 8: From Similarity to Geography

**Anchor Element:** User-selected ICH element

**Query:**  
> What practices are semantically similar to this one, and do they share environmental or geographic characteristics?

**Method Sketch:**
- Use embedding similarity over `ich_summaries`
- Retrieve top-N similar elements
- Compare their geographic and environmental envelopes

**Interpretive Payoff:**
- Interactive, intuitive CDOP entry point
- Shows how meaning, place, and environment can be explored without overclaiming causation

---

## Closing Note

Taken together, these queries position UNESCO ICH data as:
- A **cultural diffusion and affiliation layer** within CDOP
- A foil and complement to EDOP’s more place-anchored datasets
- A means of exploring **portability vs constraint** rather than environmental determinism

They also surface, rather than conceal, the epistemic limits of the data — which is very much in the spirit of the Computing Place initiative.
