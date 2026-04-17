# Follow-up Notes

Running list of contacts, leads, and potential connections worth revisiting.

---

## Federico (via Elton / Pelagios) — *April 2026*

**Contact**: Introduced by Elton Barker (Pelagios). Building a spatial Graph-RAG system for water infrastructure study (ancient texts). Plans to enrich place references in ancient texts with structured environmental context in a Neo4j graph, where each place node carries both textual attestations and environmental information. Has already tested the EDOP API. Presenting his work May 7. Based in Zurich.

**Status**: Meeting held — Zoom, Thursday April 16 2026, with Federico and ISHI director Ruth Mostern. He shared a project overview document (`docs/design/Federico_project-overview.txt`). Active API user: has already ingested EDOPS signatures for 2,140 ancient places (Pleiades-linked) into Neo4j as `EDOPSignature` nodes. Presenting NileGraphRAG at a Pelagios-oriented conference on May 7, 2026 — EDOPS will be featured.

**His explicit questions**:
1. How best to handle the chronological gap between modern environmental measurements and ancient conditions
2. What spatial unit works best for historically grounded analysis in river-valley settings

**Project**: NileGraphRAG — 244,000 ancient text passages (Greek/Latin literary + Egyptian papyri), 4,600 Pleiades-linked places, classified by evidential type (attestation / inference / framing) and tagged with 80 water infrastructure terms. EDOPS provides environmental context on each place node. Sample query: "Where is canal maintenance most attested, and what do those places look like environmentally?" — the Fayum / Nile delta gradient is his central use case.

**Integration model**: He extracts what ancient sources *say* about environmental conditions; EDOPS characterizes what conditions *were*. Complementary, not competing. WHG is the natural bridge (he's already targeting gazetteer-aligned identifiers + Pelagios/W3C Web Annotation). EDOPS signature as an enrichment layer on his Neo4j place nodes is the natural integration point.

**API note**: Currently ingesting Bands A and B (elevation, slope, discharge, basin area — stable / defensible for ancient contexts). Used Band C (aridity, precip, biome) as relative proxies. Raw JSON response preserved on each node. Notified of April 16 payload restructure (profile_groups) and rollback of flat fields for backwards compatibility.

**Pelagios context**: Karl is a founding partner of the Pelagios Network; Federico is a new partner. His May 7 presentation is a natural EDOPS debut in that community.

**Out of scope for now**: His broader NLP pipeline; not something to pursue under current ISHI scope.

---
