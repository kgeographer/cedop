# Session Log — 27 April 2026

## Overview

Branch `explore02`. Completed Task 11 (LMR period and event fingerprints). Findings F11.1–F11.6 logged. Added Cell 12 (location-specific validation: Kaifeng and Central Europe across the Song dynasty with Samalas close-up) following discussion of global-sample limitations and the geographic proxy bias in LMR.

## Task 11 — LMR period and event fingerprints

Notebook: `notebooks/edop/explore/11_lmr_periods_volcanics.ipynb` (12 cells)
Detailed findings: `logs/exploration_log.md` F11.1–F11.6
Outputs: `output/edop/explore/11_*.{csv,png}` (6 files + 2 from Cell 12)

### Period anomalies (Cells 4–5)

- Global-sample MCA/LIA temperature anomalies near noise floor (~0.011 K median, IQR 5× larger) — full-record reference inverts MCA sign; reliable pre-industrial (1000–1850 CE) recovers correct direction (F11.1)
- Latitude-band plot shows NH cells carry most of the signal; tropical and SH cells dilute the global median — this is a methodological property of the test, not a statement about location-specific queries
- PDSI shows expected pattern (MCA wetter, LIA drier/mixed) but equally modest globally

### Baseline convention (Cell 10)

- Full record (0–1998 CE): contaminated by 20th-century warming, inappropriate for pre-industrial queries
- Reliable pre-industrial (1000–1850 CE): recovers correct MCA/LIA sign, avoids funnel zone and industrial era — **recommended convention** (F11.2)
- Surrounding 200yr: self-defeating for MCA (overlaps period itself), inconsistent for LIA PDSI

### Volcanic response (Cells 6–9)

- nhmt composite of 5 events ≥20 Tg shows no clear lag-0 cooling (−0.013 K, within noise floor) — composite underpowered at 5 events (F11.3)
- Individual cells: cooling detectable only for Samalas-class (59 Tg); events <50 Tg indistinguishable from noise at basin level
- LMR cannot reliably quantify volcanic forcing below ~50 Tg — eVolv2k and LMR must remain decoupled in Band T (F11.4)
- Pinatubo calibration (~20 Tg → ~0.5°C) confirmed as the right bridge reference for the narrative layer

### Cell 12 — Kaifeng/Song dynasty validation

Added following discussion that global-sample findings understate location-specific utility. Two cells: Kaifeng (~35°N, 114°E) and Central Europe (~48°N, 10°E), full Song dynasty (960–1280 CE) + Samalas close-up.

Key results:
- Central Europe 1257: −0.432 K — ~4× pre-eruption noise, convincingly detectable (F11.5)
- Kaifeng 1257: −0.132 K (within noise), followed by sustained cooling 1260–1264; both cells negative for 7+ years post-Samalas
- Song overview shows: cooler-than-baseline Northern Song at Kaifeng, MCA warm pulse ~1170–1220, cooling from ~1230 into Samalas — features invisible in global median but present at this location
- The two cells track distinct regional trajectories throughout the dynasty, converging on post-Samalas cooling

### F11.6 — Geographic proxy bias

Important finding that emerged from the Kaifeng/Europe comparison: LMR proxy coverage is systematically denser in Europe and North America than East Asia, South Asia, or SH. The stronger European signal reflects better-constrained reconstruction, not necessarily stronger physical forcing. This matters directly for Song dynasty and other East Asian research use cases and must be disclosed explicitly in API documentation, not buried in technical notes.

## Key design decisions confirmed

- Baseline convention: 1000–1850 CE for Band T anomaly reporting
- eVolv2k and LMR are non-substitutable; Pinatubo scaling note belongs in narrative layer
- Within-run spread is the right uncertainty field but does not capture geographic proxy bias — a qualitative disclosure is also needed
- Location-specific queries in NH Temperate band are more useful than global characterisation suggests

## Open items flagged

- Pinatubo calibration text for the narrative layer prompt (not yet written)
- LMR geographic bias disclosure for API documentation
- Whether additional eruptions in 1258–1264 compound the Samalas signal at Kaifeng (eVolv2k cross-check not yet done)

## Up next — Task 12

**Task 12**: Anthromes categorical typology over time (`notebooks/edop/explore/12_anthromes.ipynb`) — design specifics TBD before notebook implementation. See `docs/edop/exploration_bandT.md` Task 12 section.
