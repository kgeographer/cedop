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

## Completed in next session (2026-04-26)

Task 5b (L6 clustering) and Task 9 (HYDE basin aggregation) both completed. See `logs/session_log_20260426.md` for full notes and `logs/exploration_log.md` F9.1–F9.7 for findings.

**Up next: Task 10** — LMR v2.1 structure and coverage (`notebooks/edop/explore/10_lmr_structure.ipynb`). Read `docs/edop/exploration_bandT.md` Task 10 section before designing the notebook.
