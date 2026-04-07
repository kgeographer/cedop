# Session Log: 07 April 2026

## Summary
First session after public talk (06 Apr). Shifted from presentation mode to development.
Major conceptual work on signature design and validation framing, then first working
rev1 signatures generated for a 7-place personal test set.

## Conceptual / Design

- **Reframed EDOP as research instrument**, not predictive model. Quality evaluated
  through use; settlement correspondence is an existence proof, not an optimization target.
  Residuals are findings, not failures.
- **"Rich but bounded" variable selection**: include all variables with plausible
  theoretical connection to human activity; discover utility through testing.
- **Dimension terminology**: a dimension (e.g., `moisture_balance`) may be a composite
  of several variables; distinct from "variable" (a measurement) and "field" (JSON/DB shorthand).
- **Terminology settled**: *signature* = the data artifact; *setting* = what it characterizes.
  "A signature characterizes a setting."
- **Multi-set architecture**: place selection problem is separable from the generation
  pipeline. Define named sets; generator is agnostic to which set it runs.

## Schema / Codebook

- Created `docs/edop/edops_schema.json` — full JSON template instance for EDOPS signature,
  using Timbuktu as example. Includes planned (null) fields with `_note` documentation.
- Created `metadata/edops_codebook.tsv` — 90 variables across 23 named dimensions,
  with schema_key, band, basin08 columns (s+u), friendly name, type, units, status, atlas_id.
- Created `docs/edop/prospectus_20260407.md` — copy of 20260404 with rev07Apr changes
  flagged; validation section substantially rewritten.

## Database / View

- Discovered upstream climate columns already exist in basin08: `tmp_dc_uyr`, `pre_mm_uyr`,
  `ari_ix_uav` etc. — no DAG traversal needed.
- Created `sql/edop/sig/persist_view_rev1.sql` — extends `v_basin08_persist` with upstream
  climate/soil/hydro, coastality (dist_sink, endo, coast), wetland class. HDI /1000.0 in view.
  Original view left untouched for prototype GUI.
- Fixes applied: `dist_sink` is stored in km (not meters); HDI stored as integer ×1000;
  PostgreSQL Decimal type needs explicit float conversion in Python.

## Scripts

- `scripts/edop/sig/generate_signatures.py` — generates rev1 JSON signatures for named
  place sets from `v_basin08_persist_rev1`. Output to `output/edop/signatures/{set_name}/`.
- `scripts/edop/sig/place_sets.json` — defines `set_personal_v1` (7 places: Timbuktu,
  Buenos Aires, Vienna, Taos, Istanbul, Tashkent, Chang'an).
- `scripts/edop/sig/signature_distances.py` — pairwise Euclidean and cosine distance
  matrix over flattened z-score normalized numeric vectors.

## Distance Matrix Results (set_personal_v1, output not persisted)

Both metrics agreed closely. Key findings:
- **Buenos Aires ↔ Istanbul**: most similar (both coastal, temperate, low relief) — expected.
- **Timbuktu ↔ Vienna**: most different by Euclidean; second-most by cosine — expected.
- **Cosine/Euclidean divergence**: Buenos Aires ↔ Tashkent most different by cosine
  (very different structural profiles) but only middling by Euclidean (magnitudes not extreme).
  Cosine ~ "feels like"; Euclidean ~ "total environmental difference".
- **Taos**: consistently peripheral — headwater basin, near-zero s/u divergence,
  high elevation semi-arid plateau; doesn't closely resemble any other place in the set.
  Site of Taos Pueblo (~1000 CE), one of oldest continuously inhabited communities in N. America.
- **Tashkent ↔ Vienna** and **Chang'an ↔ Tashkent**: similar despite different continents —
  both semi-arid to sub-humid, significant upstream catchment contrast, endorheic/continental interior.

## s/u Divergence Highlights (from quick scan, not persisted)

- Tashkent: temp 11.8°C(s) / 3.2°C(u), aridity 46(s) / 92(u) — classic oasis city,
  Tian Shan snowmelt upstream.
- Vienna: precip 647(s) / 976(u)mm — Alps upstream doing significant work.
- Chang'an: aridity 44(s) / 65(u) — drier locally than the Wei/Yellow River catchment.
- Buenos Aires, Istanbul: dist_sink=0, coastal, near-zero divergence throughout — as expected.
- Taos: near-zero divergence on all dimensions — isolated headwater basin.

## Organisation

- New subdirectory structure: `scripts/edop/sig/`, `sql/edop/sig/` for signature
  build and analysis work. Parallel to existing `corpus/` subdirectory.
- Output: `output/edop/signatures/{set_name}/` (gitignored).

## Branch

All work on `sig_rev1`. Commits: codebook dimension column, rev1 view + generator +
place sets, reorganization into sig/ dirs, signature_distances.py.

## s/u Divergence Profile (completed)

- `scripts/edop/sig/su_divergence.py`: per-place ranked divergence with bar chart;
  cross-place mean absolute divergence by dimension.
- Key finding: karst and wetland show highest mean divergence (~100–130%) but partly
  a scale/sampling artifact. Documented in `docs/llm/karst_wetlands_su_divergence.md`.
- Taos: perfect zeros across all dimensions — isolated headwater, no upstream contrast.
- Tashkent: temp −115%, aridity +67% — classic mountain-fed oasis signature.
- Vienna: river_area +192%, precip +41% — Alps upstream doing significant work.

## Narratives (completed)

- `prompts/edop_narrative_rev1.md`: new prompt aligned with rev1 schema. Prior prompts
  (general/scientific) predate rev1 and reference non-existent fields — do not use for rev1.
- `scripts/edop/sig/generate_narratives.py`: Claude API call with --style flag
  (rev1/scientific/general), --place, --model, --tokens, --dry-run.
- Generated 7 narratives for set_personal_v1 at --style rev1. Quality good; scientific
  register, s/u story surfaced correctly. Chang'an/Vienna needed 650 tokens.
- Narratives written into signature JSON under narrative.text (gitignored output).

## WHG Portal Button (design only)

- Feasible: endpoint checks cache → calls API on miss (~2–4s + spinner) → fallback on error.
- Pre-generate for known place sets; on-demand + cache for arbitrary coordinates.
- `prompts/edop_narrative_whg_portal.md` exists but predates rev1 — needs revision before use.

## Next

1. GUI: signature inspection tab showing s/u pairs, coastality, key dimensions
2. WHG portal narrative button (endpoint + caching + rev1 prompt)
3. Add more place sets (WH Cities selection, D-PLACE correspondence experiment)
4. Temporal enrichment: LMR v2.1 integration
