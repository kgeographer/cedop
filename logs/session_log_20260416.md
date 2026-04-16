# Session Log — 2026-04-16

## Summary

Two threads: (1) sandbox UI polish and WHG discussion carried over from yesterday; (2) D-PLACE data exploration and database loading.

---

## 1. WHG reconcile — namespace discussion

Reviewed Stephen's suggestion to prefilter to `"namespaces": "wd,gn,tgn"` in the reconcile query. Decision: stay with post-filter approach (`place:(wd|osm|gn):` stripped after fetch). Rationale:

- Pre-filter can't express "no namespace" — would silently drop the 2M+ contributed `pl:` records, which are exactly the scholarly/ancient place content most valuable for the tool
- `tgn:` and no-namespace records are what we want; post-filter correctly passes both
- Tested "Santa Fe" and "Miami" via curl to understand failure modes:
  - Santa Fe: works with tight viewport bounds; wide bounds floods result with `gn:` records
  - Miami: all 50 WHG results are `place:gn:` — GeoNames saturates; TGN's Miami (if it exists) ranks below 50. Accepted as a known limitation — "pre-alpha" framing covers it

## 2. Sandbox UI — 15aprtweaks branch

Branch `15aprtweaks` created, merged to main, pushed. Changes:

- **Band list popovers**: `?` icons on each band in `#band-list` with `data-bs-toggle="popover" data-bs-trigger="hover focus"`; content drawn from edops_schema.json descriptions
- **Bootstrap popover init** added to JS (before main IIFE)
- **About modal** (`#aboutModal`): research preview text explaining EDOPS sandbox status, WHG WIP, future dashboard; includes obfuscated contact link (JS-assembled `mailto:` from split strings, never in HTML source)
- **Version badge**: `EDOPS v0.2 Alpha` flush right in header; "About" link to its left
- **JSON copy button**: mirrors URL copy button in API/JSON modal; copies formatted JSON payload to clipboard
- **Clear button**: replaced `&#x2715; clear` text with `bi-x-circle` icon

## 3. Civilizational centers comparison script

`scripts/edop/sig/civ_centers_compare.py` — compares EDOPS signatures (Bands A, B, C, E, Level 06) for 10 major civilizational centers. Fetches from local API, z-score normalizes numeric fields, outputs:

- Top 15 fields by coefficient of variation
- 10×10 pairwise Euclidean distance matrix
- 5 most similar and most distant pairs

Sites: Babylon, Memphis (Egypt), Mohenjo-daro, Anyang, Athens, Rome, Teotihuacan, Tiwanaku, Angkor, Aksum.

Notable results: Babylon↔Anyang and Anyang↔Rome closest pairs; Tiwanaku↔Angkor most distant. Discussion: s/u divergence (local aridity vs. upstream water delivery) may be more diagnostic of hydraulic civilizational centers than raw signature similarity.

## 4. D-PLACE data exploration

Explored D-PLACE GitHub repos (`dplace-data`, `dplace-cldf`, `dplace-cookbook`) and the downloaded CLDF v3.3.0 zip (`data/dplace/cldf/`).

Key findings:
- CLDF (Cross-Linguistic Data Formats) is a standardized CSV+JSON packaging format; D-PLACE uses the StructureDataset module
- `dplace-cldf` v3.3.0 is the canonical current distribution; `dplace-data` is legacy
- Local `data/dplace/` previously had only EA cultural data; `gaz.dplace_*` tables in cedop DB had 1,291 EA societies (with `basin_id`) and 94 cultural variables only
- D-PLACE environmental datasets (ecoclimate, MODIS NPP, GMTED, GSHHS, Jenkins biodiversity, Kreft plant diversity, TEOW biome/ecoregion) are in the CLDF package as separate contributions — ~24 env variables, ~1,988 societies covered
- EDOPS is richer hydrologically; D-PLACE env data useful as independent benchmark and for Colwell predictability indices (seasonality structure) not in EDOPS

Key architectural distinction noted: D-PLACE is society-centric (point samples at ~1,988 documented locations); EDOPS is space-first (190,675 basins, global). D-PLACE societies are best treated as a labeled training set; EDOPS supplies environmental features.

## 5. D-PLACE database loading

Designed and executed full CLDF load into new `dplace` schema. Existing `gaz.dplace_*` tables left untouched.

**Schema**: `sql/cdop/dplace_schema.sql`
- `dplace.contributions` — 128 rows (datasets + phylogenies)
- `dplace.societies` — 6,684 rows (all datasets + phylogeny languoids)
- `dplace.variables` — 3,341 rows (cultural + environmental, all datasets)
- `dplace.codes` — 16,158 rows
- `dplace.data` — 677,862 rows

**Loader**: `scripts/cdop/load_dplace_cldf.py`
- Reads from `data/dplace/cldf/` CSVs
- Loads in FK-safe order; batched inserts for `data` table
- `--truncate` flag for clean reload

**Pending (T5)**: Fix prototype references from `gaz.dplace_*` → `dplace.*` (side task, not urgent).

---

## Files added/changed

- `sql/cdop/dplace_schema.sql` — new dplace schema DDL
- `scripts/cdop/load_dplace_cldf.py` — CLDF loader
- `scripts/edop/sig/civ_centers_compare.py` — civilizational centers comparison
- `app/templates/sandbox.html` — 15aprtweaks UI changes
- `app/static/css/site.css` — minor style tweaks

## 6. Seshat data loading

Downloaded two Seshat Global History Databank exports to `data/seshat/` (pipe-delimited CSV, long format — one row per polity × variable × time slice):

- `general_data_*.csv` — 8,170 rows, 544 polities, 23 variables (identity, religion, language, capital, degree of centralization, etc.)
- `social_complexity_data_*.csv` — 26,164 rows, 621 polities, 77 variables across 9 subsections (Social Scale, Hierarchical Complexity, Information, Law, Professions, Bureaucracy, Transport, Specialized Buildings, Special-purpose Sites)

**Schema**: `sql/cdop/seshat_schema.sql` — `seshat.general` and `seshat.social` tables, indexed on `polity_new_id`, `variable_name`, and year columns.

**Loader**: `scripts/cdop/load_seshat.py`

**Join to gaz.clio_polities** via `seshatid = polity_new_id`:
- 329 distinct clio polities matched with seshat social data (of 621 seshat polities)
- 200 distinct polities with real `polity_population` values (annual series in many cases)
- Best-covered variables: `written_record`, `script`, `administrative_level`, `polity_territory`, `indigenous_coin`, `formal_legal_code` — all 260–314 matched polities
- Unmatched seshat polities are mostly prehistoric or sub-state societies (Yangshao, Longshan, West Burkina Faso chiefdoms, Tiwanaku) that Cliopatria doesn't cover

`polity_territory` and `polity_population` pair directly with clio spatial polygons and EDOPS basin signatures for territory + population density calculations over time.

## Commits

- `34019fd` — 15aprtweaks: sandbox UI polish (merged to main, pushed)
- `6c8cb82` — data branch: D-PLACE CLDF load, dplace schema, session logs
- `f3e5aec` — data branch: Seshat schema and loader

---

## Next up

### T5 — Retire gaz.dplace_* tables (branch: data)

The `gaz` schema has four dplace tables (`dplace_societies`, `dplace_data`, `dplace_codes`, `dplace_variables`) that are now superseded by the `dplace` schema. The only missing pieces are derived spatial attributes stored on `gaz.dplace_societies`: `bioregion_id`, `eco_id` (and `geom`, reconstructible from lat/lon). Plan:

1. Create `dplace.society_spatial (soc_id, bioregion_id, eco_id)` and populate via one-time PostGIS spatial join against `gaz."Bioregions2023"` and `gaz."Ecoregions2017"`
2. Update `/api/societies` route to use `dplace.*` exclusively (geom computed on-the-fly from lat/lon)
3. Grep and update any remaining `gaz.dplace_*` references in routes/scripts
4. Drop the four `gaz.dplace_*` tables

