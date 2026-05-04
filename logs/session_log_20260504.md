# Session Log — 4 May 2026

## Participants
Karl Grossner, Claude Sonnet 4.6 (CC)

## Context
One-day window before Karl travels for a week. Two detours before the spatial phase: prospectus revision and Cliopatria EDA.

---

## 1. Prospectus revision — docs/edop/prospectus_20260503.md

Revision guidance was in `docs/edop/prospectus_revision_guidance_20260503.md` (Opus-generated from 3 May working session). CC drafted the full new prospectus in one pass.

**Four [Rev. 03 May] additions:**
- **Section 7 bullet**: spatial-statistics characterization report as a v0.1/v1.0 deliverable (PySAL pipeline, coherence class calibrated empirically)
- **Section 8 paragraph**: audience scope — unmediated specialist audience is small but real; mediated layer reaches adjacent scholars; worked examples as recruiting filter
- **New Section 9**: "User-Facing Documentation and Development Trajectory" — worked examples genre (vs. cookbook), three-phase development (v0.1, v1.0, LLM-mediated); BYOK → "LLM access costs borne by dashboard users"; research-infrastructure register, not product roadmap
- **Sections 9–10 renumbered to 10–11** (content unchanged)

Terminology decisions: "casebook" → "worked examples" (relabelable later); "BYOK" → pithy one-liner.

File is gitignored (`docs/`); lives only locally.

---

## 2. Cliopatria EDA — gaz.clio_polities

### Background
Karl read Bennett et al. (Cliopatria paper) and now understands the parent/component structure: parenthesized names are parent/composite entities, not duplicates. Erin Mutch is a co-creator; transforms must be documented for disclosure.

### EDA findings

**Table structure**: 15,690 rows = 1,618 distinct names × time slices (fromyear/toyear). Average 9.7 slices/name, median 5, max 137.

**Entity type taxonomy** (96 paren entities, 1,522 non-paren polities):
- 50 pure singleton-self wrappers: `(X)` contains only `X` — a non-well-founded / reflexive set. Geometry identical to non-paren counterpart. Structural device for relational uniformity.
- 30 pure composites: genuine multi-component aggregates (Holy Roman Empire, British Empire, etc.)
- 15 mixed: singleton-self in some slices, true composite in others
- 1 singleton-other

**Three-level counting** — important distinction:
- 1,522 distinct polity names
- 11,178 distinct (name + geometry) configurations
- 12,987 total non-component time slices
- 1,809 rows where geometry didn't change between slices; 327 polities whose geometry never changes at all

**Geometry validity**: 2,239 rows (14.3%) have self-intersecting geometries inherited from source GeoJSON. `ST_MakeValid()` was tested but reverted — it "lopped off loops" that are real territory (British Empire 1820–1845: up to 23.8% area loss). Geometries left intact, flagged for upstream Cliopatria team repair.

**memberof/components**: semicolon-delimited varchar in source; discovered 302 non-paren polities have memberof, 1,255 are standalone with no parent. 93.5% of component name references resolve to actual polity rows within the time period; the 6.5% unresolved are paren-to-paren references, not missing data.

**seshatid**: 632 of 1,522 non-paren polities (41.5%) have seshatid linkage. Varies across time slices for some polities — per-slice resolution needed for Seshat joins.

### Schema changes applied to gaz.clio_polities

All documented in `data/cliopatria/cliopatria_eda.md` §7 for disclosure to Cliopatria team:

1. **Empty strings → NULL**: seshatid (6,474 rows), memberof (11,428), components (12,987)
2. **`is_component` boolean column**: true on 2,703 rows (96 distinct names); false on 12,987 (1,522 names)
3. **`geom_og` geometry(MultiPolygon,4326) column**: complete copy of all original geometries; `geom` remains canonical and unchanged
4. **`invalid_source_geom` boolean**: true on 2,239 rows with source self-intersections; geometries NOT repaired
5. **`memberof` and `components` → text[]**: converted from semicolon-delimited varchar using `string_to_array(col, ';')`; NULLs preserved

### Report: data/cliopatria/cliopatria_eda.md

Written and updated through the session. Sections:
1. What each row represents
2. Entity type taxonomy (with singleton-self / non-well-founded set explanation)
3. Temporal coverage
4. Metadata fields (seshatid, memberof, components) — marked fixed/open
5. Geometry validity — repair rationale, invalid_source_geom flag
6. Assessment of flattening — issues table with ✅/⚠️/🔲 status
7. Schema changes applied (complete SQL + row counts)
8. Query design considerations and rubric (new, final section):
   - Autocomplete: non-paren names only, time-filtered
   - Three query cases: standalone / composite-member / explicit aggregate
   - Roman Empire scenario (singleton-self, no disambiguation needed; sub-provincial limit)
   - British Empire scenario (true composite, aggregate vs. regional breakdown)
   - Component resolution algorithm (100% plain-name resolution rate)
   - Time-period sensitivity
   - API endpoint sketch (`/api/polity?name=X&year=Y&mode=...`)
9. EDOPS use-case implications (polity phase)

File is gitignored (`data/`); lives only locally.

---

## 3. Institutional context noted

- Ruth Mostern's ISHI center is on track to become Cliopatria publisher (also on WHG dev TODO, ISHI data manager)
- Erin Mutch (Cliopatria co-creator) is a future contact; the EDA report and transforms log are written with that disclosure in mind
- Karl's EDOPS use is parallel and may not wait for ISHI to publish — could share the EDA report with them when contact is made

---

## Commit

`89049e3` — docs: prospectus 03 May draft; Cliopatria EDA + schema fixes

19/19 tests passing. Karl to push and deploy.
