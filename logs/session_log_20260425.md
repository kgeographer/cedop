# Session Log — 25 April 2026

## Overview

Branch `explore02` opened. Band T characterization phase begins (Tasks 7–12), following completion of Tasks 1–6 on the static signature (Bands A–E).

## Branch and rename

- Created `explore02` branch from `main`
- Renamed Band F → Band T throughout: routes.py, sandbox.html, api_guide.html, CLAUDE.md, all docs
- Fixed three missed JS references in sandbox (checkbox value, `wantT`, accordion panel id, year-row toggle) after live test revealed T accordion not rendering
- Verified Kaifeng sandbox example with all bands including T: working, LLM narrative references T band data

## Planning

- Read and discussed `docs/edop/exploration_bandT.md` (drafted with Opus 4.7, 25 Apr revision)
- Confirmed task sequencing: eVolv2k (7) → HYDE (8–9) → LMR (10–11) → Anthromes (12, deferred)
- Key architectural point documented: Band T variables are functions of a (location, time) query, not fixed per-basin values — different characterization methodology from Tasks 1–6

## Task 7 — eVolv2k v4

Notebook: `notebooks/edop/explore/07_evolv2k_distribution.ipynb`
Detailed findings: `logs/exploration_log.md` F7.1–F7.9

High-level results:
- Catalog: 256 events, effective coverage 4–1890 CE within LMR window (211 events)
- 5 Tg confirmed as the right API default threshold; 10 Tg would exclude Krakatoa and Kuwae
- At 5 Tg + 100-yr window: 96.8% of query windows contain ≥1 event — reliable operating zone
- Three aggregations recommended: event count, sum-VSSI, years-since-last-major (complementary, not redundant)
- Hemispheric filtering ruled out: catalog is NH-biased by construction; asymmetry returned as per-event field only
- eVolv2k and LMR should be decoupled in the API — volcanic events are valid for ~500 BCE, LMR is not
- Kaifeng 1000–1100 sits at the end of the Medieval volcanic quiet; the 1200–1300 century (Samalas 1257, 59 Tg) is the most volcanically intense in the record — relevant to Song dynasty collapse and Mongol expansion narrative

## Task 8 — HYDE 3.4 per-epoch distributions and signal emergence

Notebook: `notebooks/edop/explore/08_hyde_distributions.ipynb`
Detailed findings: `logs/exploration_log.md` F8.1–F8.7

High-level results:
- Variables: cropland, grazing_land, urban_area, population_density, total_rice — 5 NetCDF files, 128 time steps, 5-arcmin grid (~9km)
- Grazing land emerges earliest and most extensively; cropland follows. Both follow log-linear growth (F8.1)
- Urban area and total rice are globally near-zero at distribution scale — not useful as default Band T fields; make opt-in (F8.2)
- Population density % zero is flat for 10,000 years — a HYDE model artifact, not empirical history; HYDE pre-populates all habitable cells regardless of era (F8.3)
- Population density shows a 20th-century hockey stick; land use variables do not — industrial-era population explosion is a distinct regime (F8.4)
- **Key finding**: Band C (WorldClim) is silently wrong for BCE queries — contemporary climatology returned for Neolithic sites with no warning. Needs `climate_note` field in API response (F8.5)
- 1000 BCE confirmed as global land-use baseline for anomaly reporting — ratios are interpretable (2.8×–23× for cropland) (F8.7)
- Open design questions flagged for October expert meeting: (a) does population density belong in an environmental signature? (b) should HYDE habitability be surfaced for BCE queries as a qualified signal? (F8.6)

## Completed in next session (2026-04-26)

Task 5b (L6 clustering) and Task 9 (HYDE basin aggregation) both completed. See `logs/session_log_20260426.md` for full notes and `logs/exploration_log.md` F9.1–F9.7 for findings.

**Up next: Task 10** — LMR v2.1 structure and coverage (`notebooks/edop/explore/10_lmr_structure.ipynb`). Read `docs/edop/exploration_bandT.md` Task 10 section before designing the notebook.
